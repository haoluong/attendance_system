import cv2
import numpy as np
import settings
import os
from modules.retinaface import RetinaFace
from modules.mobilenetv2 import MobileNetV2
from modules.db_redis import Rediser

def read_image(folder_path):
    images = []
    for path in os.listdir(folder_path):
        frame = cv2.imread(folder_path+path)
        if frame is not None:
            # print("Read image from ", folder_path+path)
            images.append(frame)
    return images

def add_embeds(images, student_id):
    # connect to Redis server   
    db_redis = Rediser(settings)
    print("*Database connected")
    # load the pre-trained Keras model (here we are using a model
    # pre-trained on ImageNet and provided by Keras, but you can
    # substitute in your own networks just as easily)
    detect_model = RetinaFace(settings.CFG_RETINA)
    recog_model = MobileNetV2(settings.CHECKPOINT_PATH, db_redis)
    print("*All model loaded")
    embeds = None
    labels = []
    for image in images:
        # detect faces
        b_boxes, faces = detect_model.extract_faces(image)
        print("* Batch size: {}".format(faces.shape))
        #get largest face
        # largest_box = max(b_boxes, key=lambda x: (x[2]-x[0])*(x[3]-x[1]))
        if len(b_boxes) > 0:
            box_areas = list(map(lambda x: (x[2]-x[0])*(x[3]-x[1]), b_boxes))
            largest_face = faces[box_areas.index(max(box_areas))]
            # inference the batch
            results = recog_model.inference(largest_face[np.newaxis,...])
            if embeds is None:
                embeds = results
            else:
                embeds = np.vstack((embeds, results))
            labels.append(student_id)
    # add to db
    db_redis.add_embeds(embeds, labels)

def main(folder_path, student_id):
    images = read_image(folder_path)
    add_embeds(images, student_id)
    
def sign_student_web(pil_images, student_id):
    images = [np.array(img) for img in pil_images]
    add_embeds(images, student_id)

def remove_student(student_id):
    db_redis = Rediser(settings)
    print("*Database connected")
    return db_redis.remove_student(student_id)
