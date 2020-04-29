import cv2
import os
import numpy as np
import time
import settings
import sys
from modules.retinaface import RetinaFace
from modules.mobilenetv2 import MobileNetV2
from modules.db_redis import Rediser

def main(argv):
    # init
    db_redis = Rediser(settings)
    detect_model = RetinaFace(settings.CFG_RETINA)
    recog_model = MobileNetV2(settings.CHECKPOINT_PATH, db_redis)
    print("*All model loaded")
    if len(argv) <= 1:
        input_stream = 0
    elif argv[1] == 'rtsp':
        input_stream = settings.RTSP_ADDR
    else:
        input_stream = argv[1]
    cam = cv2.VideoCapture(input_stream)
    start_time = time.time()
    b_box, label, prob = None, None, None
    i = 0
    while cam.isOpened():
        _, frame = cam.read()
        if frame is None:
            print("no cam input")
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
        fps_str = "FPS: %.2f" % (1 / (time.time() - start_time))
        cv2.putText(frame, fps_str, (25, 25),
                    cv2.FONT_HERSHEY_DUPLEX, 0.75, (0, 255, 0), 2)
        start_time = time.time()
        # show frame
        i+=1
        # cv2.imwrite('UNKNOWN/3/'+str(i)+'.jpeg', frame)
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) == ord('q'):
            exit()

if __name__ == '__main__':
    main(sys.argv)
