import cv2
import os
import numpy as np
import time
import settings
from modules.retinaface import RetinaFace
from modules.mobilenetv2 import MobileNetV2

def main():
    # init
    detect_model = RetinaFace(settings.CFG_RETINA)
    recog_model = MobileNetV2(settings.CHECKPOINT_PATH, settings.ANCHOR_PATH, settings.LABEL_PATH)
    print("*All model loaded")
    cam = cv2.VideoCapture("/home/hao/Videos/Webcam/1.webm") #(settings.RTSP_ADDR)
    start_time = time.time()
    b_box, label, prob = None, None, None
    while cam.isOpened():
        _, frame = cam.read()
        if frame is None:
            print("no cam input")
        # if time.time() - start_time < 1:
        #     if label is not None:
        #         cv2.rectangle(frame, (b_box[0], b_box[1]), (b_box[2], b_box[3]), (0, 255, 0), 2)
        #         cv2.putText(frame, label, (b_box[0], b_box[1]),
        #                     cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255))

        #         text = "{:.4f}".format(prob)
        #         cv2.putText(frame, text, (b_box[0], b_box[1]+15),
        #                     cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255))
        #     cv2.imshow('frame', frame)
        #     if cv2.waitKey(1) == ord('q'):
        #         exit()
        #     continue
        # else:
        #     start_time = time.time()
        frame_height, frame_width, _ = frame.shape
        b_boxes, faces = detect_model.extract_faces(frame)
        results = recog_model.predict(faces)
        # draw results
        for prior_index in range(len(b_boxes)):
            ann = b_boxes[prior_index]
            b_box = int(ann[0] * frame_width), int(ann[1] * frame_height), \
                        int(ann[2] * frame_width), int(ann[3] * frame_height)
            label, prob = results[prior_index]
            if prob < 0.5:
                label = "Unknown"
            
            cv2.rectangle(frame, (b_box[0], b_box[1]), (b_box[2], b_box[3]), (0, 255, 0), 2)
            cv2.putText(frame, label, (b_box[0], b_box[1]),
                        cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255))

            text = "{:.4f}".format(prob)
            cv2.putText(frame, text, (b_box[0], b_box[1]+15),
                        cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255))

        # calculate fps
        # fps_str = "FPS: %.2f" % (1 / (time.time() - start_time))
        # cv2.putText(frame, fps_str, (25, 25),
        #             cv2.FONT_HERSHEY_DUPLEX, 0.75, (0, 255, 0), 2)

        # show frame
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) == ord('q'):
            exit()

if __name__ == '__main__':
    main()
