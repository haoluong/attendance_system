# import the necessary packages
import numpy as np
import settings
import time
from datetime import datetime
import json
from _thread import start_new_thread
from modules.retinaface import RetinaFace
from modules.db_storage import StudentStatus, DBStorage
from modules.mobilenetv2 import MobileNetV2
from modules.tracker import Tracker
from modules.db_redis import Rediser
from utils.unknown_processing import Pikachu

def classify_process():
    # connect to Redis server   
    db_redis = Rediser(settings)
    db_storage = DBStorage()
    print("*Database connected")
	# load the pre-trained Keras model (here we are using a model
	# pre-trained on ImageNet and provided by Keras, but you can
	# substitute in your own networks just as easily)
    detect_model = RetinaFace(settings.CFG_RETINA)
    recog_model = MobileNetV2(settings.CHECKPOINT_PATH, db_redis)
    print("*All model loaded")
    tracker = Tracker()
    pikachu = Pikachu()
    print("*Tracker connected")
    # continually pool for new images to classify
    while True:
        # attempt to grab a batch of images from the database, then
        # initialize the image IDs and batch of images themselves
        q = db_redis.pop_image()
        if q is None:
            continue
        frameID, image = q
        # check to see if the batch list is None
        b_boxes, faces = detect_model.extract_faces(image)
        # inference the batch
        print("* Batch size: {}".format(faces.shape))
        results = recog_model.inference(faces)
        # loop over the image IDs and their corresponding set of
        # results from our model
        outputs = tracker.add_ids(faces, b_boxes, results)
        for o in outputs:
            obj_sequence = o["seq"]
            inKTX = o["inKTX"] 
            label, prob = recog_model.get_sequence_label(np.array(obj_sequence))
            element = datetime.strptime(frameID,'%Y-%m-%d %H:%M:%S')
            lastseen_ts = datetime.timestamp(element) - 5
            lastseen_dt = datetime.fromtimestamp(lastseen_ts)
            if prob <= 0.5:
                label = "Unknown"
                start_new_thread(pikachu.save, (o["tracker_images"], lastseen_dt.strftime('%Y-%m-%d %H:%M:%S'), inKTX))
            else:
                start_new_thread(db_storage.save, (StudentStatus(student_id=label, inKTX=inKTX, detected_at=lastseen_dt.strftime('%Y-%m-%d %H:%M:%S')),))
            print(label, prob)

# if this is the main thread of execution start the model server
# process
if __name__ == "__main__":
	classify_process()
