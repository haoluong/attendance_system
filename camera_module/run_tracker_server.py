# import the necessary packages
import numpy as np
import settings
from utils.helpers import base64_decode_image
import redis
import base64
import time
from datetime import datetime
import json
import tensorflow as tf
from _thread import start_new_thread
from modules.retinaface import RetinaFace
from modules.db_storage import StudentStatus, DBStorage
from modules.mobilenetv2 import MobileNetV2
from modules.tracker import Tracker
from utils.unknown_processing import Pikachu
# connect to Redis server
db = redis.StrictRedis(host=settings.REDIS_HOST,
	port=settings.REDIS_PORT, db=settings.REDIS_DB)

def classify_process():
	# load the pre-trained Keras model (here we are using a model
	# pre-trained on ImageNet and provided by Keras, but you can
	# substitute in your own networks just as easily)
    detect_model = RetinaFace(settings.CFG_RETINA)
    recog_model = MobileNetV2(settings.CHECKPOINT_PATH, settings.ANCHOR_PATH, settings.LABEL_PATH)
    print("*All model loaded")
    db_storage = DBStorage()
    print("*Database connected")
    tracker = Tracker()
    pikachu = Pikachu()
    print("*Tracker connected")
    # continually pool for new images to classify
    while True:
        # attempt to grab a batch of images from the database, then
        # initialize the image IDs and batch of images themselves
        queue = db.lrange(settings.IMAGE_QUEUE, 0, 1)
        # loop over the queue
        if len(queue) == 0:
            continue
        q = queue[0]
        # deserialize the object and obtain the input image
        q_json = json.loads(q.decode("utf-8"))
        # image = helpers.base64_decode_image(q["image"],
        # 	settings.IMAGE_DTYPE,
        # 	(1, settings.IMAGE_HEIGHT, settings.IMAGE_WIDTH,
        # 		settings.IMAGE_CHANS))
        image = base64_decode_image(q_json["image"],
            settings.IMAGE_DTYPE,
            (480, 640, settings.IMAGE_CHANS))
        # check to see if the batch list is None
        b_boxes, faces = detect_model.extract_faces(image)
        # update the list of image IDs
        frameID = q_json["id"]
        # classify the batch
        print("* Batch size: {}".format(faces.shape))
        results = recog_model.inference(faces)
        # loop over the image IDs and their corresponding set of
        # results from our model
        outputs = tracker.add_ids(faces, b_boxes, results)

        # remove the set of images from our queue
        db.ltrim(settings.IMAGE_QUEUE, 1, -1)
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
        # sleep for a small amount
        # time.sleep(settings.SERVER_SLEEP)

# if this is the main thread of execution start the model server
# process
if __name__ == "__main__":
	classify_process()
