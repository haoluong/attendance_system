import cv2
import os
import numpy as np
import time
import settings
from modules.retinaface import RetinaFace
from modules.mobilenetv2 import MobileNetV2

def main(_argv):
    # init
    detect_model = RetinaFace(settings.CFG_RETINA)
	recog_model = MobileNetV2(settings.CHECKPOINT_PATH, settings.ANCHOR_PATH, settings.LABEL_PATH)
	print("*All model loaded")
	db_storage = DBStorage()
	print("*Database connected")
    cam = cv2.VideoCapture(settings.RTSP_ADDR)
    start_time = time.time()
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
            keypoints = {
                'left_eye': (int(ann[4] * frame_width),int(ann[5] * frame_height)),
                'right_eye': (int(ann[6] * frame_width),int(ann[7] * frame_height)),
            }
            out_frame = aligner.align(frame, keypoints, b_box)
            scaled = out_frame #cv2.resize(out_frame, (settings.IMAGE_SIZE, settings.IMAGE_SIZE), interpolation=cv2.INTER_CUBIC)
            scaled_reshape = scaled.reshape(-1, settings.IMAGE_SIZE, settings.IMAGE_SIZE, 3)
            embed_vector = mbv2(scaled_reshape/255.0)
            label, prob = classify(embed_vector, anchor_dataset, label_dataset)
            if prob < 0.5:
                label = "Unknown"
            start_new_thread(send_msg, (s, label,))
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

        # show frame
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) == ord('q'):
            exit()


if __name__ == '__main__':
    try:
        app.run(main)
    except SystemExit:
        pass
