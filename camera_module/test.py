from utils.align_face import FaceAligner
from absl import app, flags, logging
from absl.flags import FLAGS
import cv2
import os
import numpy as np
import tensorflow as tf
import time
import settings
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
flags.DEFINE_string('folder_path', '', 'which folder to align')
flags.DEFINE_string('destination_dir', '', 'which destination folder after aligning')
def mkdir(folder_path):
    try:
        os.mkdir(folder_path)
    except FileExistsError as e:
        print(e)

def main(_argv):
    mkdir(FLAGS.destination_dir)
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
    with open('log.txt', 'a+') as log_txt:
        total = 0
        processed_total = 0
        for f in os.listdir(FLAGS.folder_path):
            processed_image = 0
            items = os.listdir(FLAGS.folder_path+f)
            for path in items:
                frame = cv2.imread(FLAGS.folder_path + f +'/'+ path)
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
                for prior_index in range(len(outputs)):
                    ann = outputs[prior_index]
                    b_box = int(ann[0] * frame_width), int(ann[1] * frame_height), \
                            int(ann[2] * frame_width), int(ann[3] * frame_height)
                    keypoints = {
                        'left_eye': (int(ann[4] * frame_width),int(ann[5] * frame_height)),
                        'right_eye': (int(ann[6] * frame_width),int(ann[7] * frame_height)),
                    }
                    # print(keypoints)
                    out_frame = aligner.align(frame, keypoints, b_box)
                    # cv2.imshow('original', frame)
                    # cv2.imshow('aligned', out_frame)
                    # if cv2.waitKey(0) & 0xFF == ord('q'):
                    #     continue
                    mkdir(FLAGS.destination_dir + f)
                    try:
                        cv2.imwrite(FLAGS.destination_dir + f +'/'+ path, out_frame)
                        log_txt.write(FLAGS.destination_dir + f +'/'+ path+"\n")
                        processed_image += 1
                    except FileExistsError as e:
                        print(e)
            log_txt.write(f + " Processed: " + str(processed_image) + ' / ' + str(len(items)) +"\n")
            total += len(items)
            processed_total += processed_image
        log_txt.write( "Processed total: " + str(processed_total) + ' / ' + str(total))

if __name__ == '__main__':
    try:
        app.run(main)
    except SystemExit:
        pass
# align('/home/hao/DCLV-HK191/faces-gallery-ktx-500-nblur/','/home/hao/DCLV-HK191/processed_data/' )