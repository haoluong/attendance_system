import numpy as np
import settings
import time
from datetime import datetime
import json
from _thread import start_new_thread
from modules.retinaface import RetinaFace
from modules.db_storage import StudentStatus, DBStorage
from modules.mobilenetv2 import MobileNetV2
from modules.db_redis import Rediser

def classify_process():
	# load the pre-trained Keras model (here we are using a model
	# pre-trained on ImageNet and provided by Keras, but you can
	# substitute in your own networks just as easily)
    db_redis = Rediser(settings)
    db_storage = DBStorage()
    print("*Database connected")
	# load the pre-trained Keras model (here we are using a model
	# pre-trained on ImageNet and provided by Keras, but you can
	# substitute in your own networks just as easily)
    detect_model = RetinaFace(settings.CFG_RETINA)
    recog_model = MobileNetV2(settings.CHECKPOINT_PATH, db_redis)
    print("*All model loaded")

	# continually pool for new images to classify
    while True:
        # attempt to grab a batch of images from the database, then
        # initialize the image IDs and batch of images themselves
        q = db_redis.pop_image()
        if q is None:
            continue
        frameID, image = q
        # import matplotlib.pyplot as plt
        # plt.imshow(image/255)
        # plt.show()
        # check to see if the batch list is None
        b_boxes, faces = detect_model.extract_faces(image)
        # inference the batch
        print("* Batch size: {}".format(faces.shape))
        results = recog_model.predict(faces)
        label, prob = results[0] if len(results)>0 else ('0',0)
        if prob < 0.5:
            label = "unknown"
        db_redis.db.set(frameID, json.dumps({"label":label, "prob": str(prob)}))


        # sleep for a small amount
        # time.sleep(settings.SERVER_SLEEP)

# if this is the main thread of execution start the model server
# process
if __name__ == "__main__":
	classify_process()