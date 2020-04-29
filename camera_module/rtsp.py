import numpy as np
import settings
import time
import cv2
import sys
from modules.db_redis import Rediser

def streaming(argv):
    if len(argv) <= 1:
        input_stream = 0
    elif argv[1] == 'rtsp':
        input_stream = settings.RTSP_ADDR
    else:
        input_stream = argv[1]
    db_redis = Rediser(settings)
    cam = cv2.VideoCapture(input_stream)
    start = time.time()
    while cam.isOpened():
        _, image = cam.read()
        img_height, img_width,_ = image.shape
        image = cv2.resize(image, (640,480),
                                interpolation=cv2.INTER_LINEAR)
        image = image.astype(np.float32)
        cv2.imshow('{}-{}'.format(image.shape[0], image.shape[1]), np.uint8(image))
        if cv2.waitKey(1) == ord('q'):
            exit()
        if time.time() - start < 1:
            continue
        else:
            start = time.time()
        # generate an ID for the classification then add the
        # classification ID + image to the queue
        k = time.strftime('%Y-%m-%d %H:%M:%S')#str(uuid.uuid4())
        print("Pushed {}-th frame in {}".format(db_redis.push_image(k, image), time.time()-start))
if __name__ == "__main__":
    streaming(sys.argv)