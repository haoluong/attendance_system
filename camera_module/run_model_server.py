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
	# continually pool for new images to classify
	while True:
		# attempt to grab a batch of images from the database, then
		# initialize the image IDs and batch of images themselves
		queue = db.lrange(settings.IMAGE_QUEUE, 0, settings.BATCH_SIZE - 1)
		imageIDs = []
		batch = None
		frame_have_face_numbers = 0
		# loop over the queue
		for q in queue:
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
			if faces.shape[0] == 0:
				db.lrem(settings.IMAGE_QUEUE,1,q)
				continue
			if batch is None:
				batch = faces

			# otherwise, stack the data
			else:
				batch = np.vstack([batch, faces])

			# update the list of image IDs
			imageIDs += [q_json["id"] for _ in range(faces.shape[0])]
			frame_have_face_numbers += 1

		# check to see if we need to process the batch
		if len(imageIDs) > 0:
			# classify the batch
			print("* Batch size: {}".format(batch.shape))
			# preds = recog_model.predict(batch)
			# results = helpers.decode_predictions(preds)
			results = recog_model.predict(batch)
			# loop over the image IDs and their corresponding set of
			# results from our model
			for (imageID, resultSet) in zip(imageIDs, results):
				# loop over the results and add them to the list of
				# output predictions
				label, prob = resultSet
				if prob <= 0.5:
					label = "Unknown"
				element = datetime.datetime.strptime(imageID,'%Y-%m-%d %H:%M:%S')
				timestamp = datetime.datetime.timestamp(element)
				print("Processing time: ", time.time() - timestamp)
				start_new_thread(db_storage.save, (StudentStatus(student_id=label, inKTX=True, detected_at=imageID),))

				# store the output predictions in the database, using
				# the image ID as the key so we can fetch the results

			# remove the set of images from our queue
			db.ltrim(settings.IMAGE_QUEUE, frame_have_face_numbers, -1)

		# sleep for a small amount
		# time.sleep(settings.SERVER_SLEEP)

# if this is the main thread of execution start the model server
# process
if __name__ == "__main__":
	classify_process()
