import cv2
import numpy as np
import settings
from mtcnn import MTCNN
from models import mobilenet_v2
import os
detector = MTCNN()
anchor_dataset = np.load(settings.ANCHOR_PATH)['arr_0']
label_dataset = np.load(settings.LABEL_PATH)['arr_0']
mbv2 = mobilenet_v2.create_mbv2_model(image_shape=(settings.IMAGE_SIZE, settings.IMAGE_SIZE, 3))
def add_anchor(folder_path, student_id):
    flattens = []
    for path in os.listdir(folder_path):
        frame = cv2.imread(folder_path + path)
        frame = cv2.flip(frame, 1)
        result = detector.detect_faces(frame)
        for person in result:
            b_box = person['box']
            cropped = frame[b_box[0]-settings.MARGIN:b_box[0]+b_box[2]+settings.MARGIN, 
                            b_box[1]-settings.MARGIN:b_box[1]+b_box[3]+settings.MARGIN, :]
            scaled = cv2.resize(frame, (settings.IMAGE_SIZE, settings.IMAGE_SIZE), interpolation=cv2.INTER_CUBIC)
            scaled_reshape = scaled.reshape(-1, settings.IMAGE_SIZE, settings.IMAGE_SIZE, 3)
            embed_vector = mbv2(scaled_reshape/255.0)
            flattens.append(embed_vector.numpy())
    new_data = np.concatenate(tuple(flattens), axis=0)
    new_labels = np.array([student_id for _ in range(new_data.shape[0])])
    new_anchor_dataset = np.concatenate((anchor_dataset, new_data), axis=0)
    new_label_dataset = np.concatenate((label_dataset, new_labels), axis=0)
    np.savez_compressed(settings.ANCHOR_PATH, new_anchor_dataset)
    np.savez_compressed(settings.LABEL_PATH, new_label_dataset)
add_anchor('/home/hao/DCLV-HK191/data/1512571/', '1512571')