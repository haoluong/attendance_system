import numpy as np
import settings
from utils.helpers import base64_encode_image
import redis
import uuid
import time
import cv2
import json

# tf.enable_eager_execution()
db = redis.StrictRedis(host=settings.REDIS_HOST,
	port=settings.REDIS_PORT, db=settings.REDIS_DB)

def streaming():
    cam = cv2.VideoCapture(0) #(settings.RTSP_ADDR)
    start = time.time()
    while cam.isOpened():
        _, image = cam.read()
        cv2.imshow('{}-{}'.format(image.shape[0], image.shape[1]), image)
        if cv2.waitKey(1) == ord('q'):
            exit()
        if time.time() - start < 1:
            continue
        else:
            start = time.time()
        img_height, img_width,_ = image.shape
        image = cv2.resize(image, (640,480),
                                interpolation=cv2.INTER_LINEAR)
        image = image.astype(np.float32)

        # generate an ID for the classification then add the
        # classification ID + image to the queue
        k = time.strftime('%Y-%m-%d %H:%M:%S')#str(uuid.uuid4())
        image = base64_encode_image(image)
        d = {"id": k, "image": image}
        db.rpush(settings.IMAGE_QUEUE, json.dumps(d))
        print(time.time()-start)
streaming()