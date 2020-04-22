from absl import app, flags, logging
from absl.flags import FLAGS
import cv2
import os
import numpy as np
import tensorflow as tf
import time
from utils.align_face import FaceAligner
from models import mobilenet_v2
import settings
import socket
from _thread import *
from modules.network import RetinaFaceModel
from modules.utils import (set_memory_growth, load_yaml, draw_bbox_landm,
                           pad_input_image, recover_pad_output)


flags.DEFINE_string('cfg_path', './configs/retinaface_mbv2.yaml',
                    'config file path')
flags.DEFINE_string('gpu', '0', 'which gpu to use')
flags.DEFINE_string('img_path', '', 'path to input image')
flags.DEFINE_boolean('webcam', True, 'get image source from webcam or not')
flags.DEFINE_float('iou_th', 0.4, 'iou threshold for nms')
flags.DEFINE_float('score_th', 0.5, 'score threshold for nms')
flags.DEFINE_float('down_scale_factor', 1.0, 'down-scale factor for inputs')

def classify(embed, anchors, labels):
    dis_ = np.sqrt(np.sum(np.square(anchors - embed),axis=1))
    min_dis_idx = np.argmin(dis_)
    predict_label = labels[min_dis_idx]
    same_label_idx = np.where(labels == predict_label)[0]
    same_label_idx = np.delete(same_label_idx, np.where(same_label_idx == min_dis_idx)[0])
    filter_dis = np.delete(dis_,same_label_idx)
    func = np.vectorize(lambda x: np.exp(-x))
    prob = np.exp(-dis_[min_dis_idx])/np.sum(func(filter_dis))
    # return labels[np.argmin(dis_)], np.amin(dis_)
    return predict_label, prob

def send_msg(s, student_id):
    s.send('<MSG>student_id:{student_id},inKTX:True,detected_at:{detected_at}<MSG>'.format(student_id=student_id,detected_at= time.strftime('%Y-%m-%d %H:%M:%S')).encode('ascii'))

def main(_argv):
    # init
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    os.environ['CUDA_VISIBLE_DEVICES'] = FLAGS.gpu

    logger = tf.get_logger()
    logger.disabled = True
    logger.setLevel(logging.FATAL)
    set_memory_growth()

    cfg = load_yaml(FLAGS.cfg_path)
    aligner = FaceAligner()
    # define network
    model = RetinaFaceModel(cfg, training=False, iou_th=FLAGS.iou_th,
                            score_th=FLAGS.score_th)

    # load checkpoint
    checkpoint_dir = './checkpoints/' + cfg['sub_name']
    checkpoint = tf.train.Checkpoint(model=model)
    if tf.train.latest_checkpoint(checkpoint_dir):
        checkpoint.restore(tf.train.latest_checkpoint(checkpoint_dir))
        print("[*] load ckpt from {}.".format(
            tf.train.latest_checkpoint(checkpoint_dir)))
    else:
        print("[*] Cannot find ckpt from {}.".format(checkpoint_dir))
        exit()
    cam = cv2.VideoCapture("/home/hao/Videos/Webcam/3.webm")
    mbv2 = mobilenet_v2.create_mbv2_model(settings.CHECKPOINT_PATH)
    anchor_dataset = np.load(settings.ANCHOR_PATH)['arr_0']
    label_dataset = np.load(settings.LABEL_PATH)['arr_0']
    start_time = time.time()
    i = 0
    while cam.isOpened():
        _, frame = cam.read()
        if frame is None:
            print("no cam input")

        frame_height, frame_width, _ = frame.shape
        img = np.float32(frame.copy())
        if FLAGS.down_scale_factor < 1.0:
            img = cv2.resize(img, (0, 0), fx=FLAGS.down_scale_factor,
                                fy=FLAGS.down_scale_factor,
                                interpolation=cv2.INTER_LINEAR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # pad input image to avoid unmatched shape problem
        img, pad_params = pad_input_image(img, max_steps=max(cfg['steps']))

        # run model
        outputs = model(img[np.newaxis, ...]).numpy()

        # recover padding effect
        outputs = recover_pad_output(outputs, pad_params)
        
        # draw results
        for prior_index in range(len(outputs)):
            ann = outputs[prior_index]
            b_box = int(ann[0] * frame_width), int(ann[1] * frame_height), \
                     int(ann[2] * frame_width), int(ann[3] * frame_height)
            if (b_box[0]<0) or (b_box[1]<0) or (b_box[2]>=frame_width) or (b_box[3]>=frame_height):
                continue
            keypoints = {
                'left_eye': (ann[4] * frame_width,ann[5] * frame_height),
                'right_eye': (ann[6] * frame_width,ann[7] * frame_height),
                'nose': (ann[8], ann[9]),
                'left_mouth': (ann[10] * frame_width, ann[11] * frame_height),
                'right_mouth': (ann[12] * frame_width,ann[13] * frame_height),
            }
            out_frame = aligner.align(frame, keypoints, b_box)
            scaled = out_frame #cv2.resize(out_frame, (settings.IMAGE_SIZE, settings.IMAGE_SIZE), interpolation=cv2.INTER_CUBIC)
            scaled_reshape = scaled.reshape(-1, settings.IMAGE_SIZE, settings.IMAGE_SIZE, 3)
            embed_vector = mbv2(scaled_reshape/255.0)
            label, prob = classify(embed_vector, anchor_dataset, label_dataset)
            if prob < 0.5:
                label = "Unknown"
            cv2.rectangle(frame, (b_box[0], b_box[1]), (b_box[2], b_box[3]), (0, 255, 0), 2)
            cv2.putText(frame, label, (b_box[0], b_box[1]),
                        cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255))

            text = "{:.4f}".format(prob)
            cv2.putText(frame, text, (b_box[0], b_box[1]+15),
                        cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255))

        # calculate fps
        fps_str = "FPS: %.2f" % (1 / (time.time() - start_time))
        start_time = time.time()
        cv2.putText(frame, fps_str, (25, 25),
                    cv2.FONT_HERSHEY_DUPLEX, 0.75, (0, 255, 0), 2)
        i+=1
        # show frame
        cv2.imwrite('UNKNOWN/2/'+str(i)+'.jpeg', frame)
        if cv2.waitKey(1) == ord('q'):
            exit()


if __name__ == '__main__':
    try:
        app.run(main)
    except SystemExit:
        pass