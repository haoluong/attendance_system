# import the necessary packages
import numpy as np
import settings
from utils.helpers import base64_decode_image
import redis
import base64
import time
import datetime
import json
import tensorflow as tf
from _thread import start_new_thread
from modules.retinaface import RetinaFace
from modules.db_storage import StudentStatus, DBStorage
from modules.mobilenetv2 import MobileNetV2
from modules.tracker import Tracker
# connect to Redis server
db = redis.StrictRedis(host=settings.REDIS_HOST,
	port=settings.REDIS_PORT, db=settings.REDIS_DB)

def classify_process():
	# load the pre-trained Keras model (here we are using a model
	# pre-trained on ImageNet and provided by Keras, but you can
	# substitute in your own networks just as easily)
    detect_model = RetinaFace(settings.CFG_RETINA)
    recog_model = MobileNetV2(settings.CHECKPOINT_PATH, settings.ANCHOR_PATH, settings.LABEL_PATH)
    tracker = Tracker()
    print("*All model loaded")
    db_storage = DBStorage()
    print("*Database connected")
    # continually pool for new images to classify
    while True:
        # attempt to grab a batch of images from the database, then
        # initialize the image IDs and batch of images themselves
        queue = db.lrange(settings.IMAGE_QUEUE, 0, 1)
        imageIDs = []
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
        faces = detect_model.extract_faces(image)
        # update the list of image IDs
        imageIDs += [q_json["id"] for _ in range(faces.shape[0])]

        # classify the batch
        print("* Batch size: {}".format(faces.shape))
        # preds = recog_model.predict(batch)
        # results = helpers.decode_predictions(preds)
        results = recog_model.inference(faces)
        # loop over the image IDs and their corresponding set of
        # results from our model
        outputs = tracker.add_ids(results)

        # remove the set of images from our queue
        db.ltrim(settings.IMAGE_QUEUE, 1, -1)
        for o in outputs:
            label, prob = recog_model.get_sequence_label(np.array(o))
            if prob <= 0.5:
                label = "Unknown"
            # element = datetime.datetime.strptime(imageIDs[0],'%Y-%m-%d %H:%M:%S')
            # timestamp = datetime.datetime.timestamp(element)
            # print("Processing time: ", time.time() - timestamp)
            print(label, prob)
            start_new_thread(db_storage.save, (StudentStatus(student_id=label, inKTX=True, detected_at=time.strftime('%Y-%m-%d %H:%M:%S')),))

        # sleep for a small amount
        # time.sleep(settings.SERVER_SLEEP)

# if this is the main thread of execution start the model server
# process
if __name__ == "__main__":
	classify_process()
