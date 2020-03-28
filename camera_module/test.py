import cv2
import numpy as np
import settings
from mtcnn import MTCNN
import os
from utils.align_face import FaceAligner

def mkdir(folder_path):
    try:
        os.mkdir(folder_path)
    except FileExistsError as e:
        print(e)

detector = MTCNN()
def align(folder_path, destination_dir):
    mkdir(destination_dir)
    face_aligner = FaceAligner()
    with open('log.txt', 'a+') as log_txt:
        total = 0
        processed_total = 0
        for f in os.listdir(folder_path):
            processed_image = 0
            items = os.listdir(folder_path+f)
            for path in items:
                frame = cv2.imread(folder_path + f +'/'+ path)
                frame = cv2.flip(frame, 1)
                result = detector.detect_faces(frame)
                for person in result:
                    b_box = person['box']
                    cropped = frame[b_box[0]:b_box[0]+b_box[2], 
                                    b_box[1]:b_box[1]+b_box[3], :]
                    output = face_aligner.align(frame, person['keypoints'], b_box)
                    # cv2.imshow('original', frame)
                    # cv2.imshow('croped', cropped)
                    # cv2.imshow('aligned', output)
                    # if cv2.waitKey(0) & 0xFF == ord('q'):
                    #     continue
                    mkdir(destination_dir + f)
                    try:
                        cv2.imwrite(destination_dir + f +'/'+ path, output)
                        log_txt.write(destination_dir + f +'/'+ path+"\n")
                        processed_image += 1
                    except FileExistsError as e:
                        print(e)
            log_txt.write(f + " Processed: " + str(processed_image) + ' / ' + str(len(items)) +"\n")
            total += len(items)
            processed_total += processed_image
        log_txt.write( "Processed total: " + str(processed_total) + ' / ' + str(total))

align('/home/hao/DCLV-HK191/faces-gallery-ktx-500-nblur/','/home/hao/DCLV-HK191/processed_data/' )