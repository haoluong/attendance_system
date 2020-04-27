IMAGE_SIZE = 160
MARGIN = 16
CHECKPOINT_PATH = "weights/ktx_model.h5" #"weights/arc_mbv2.h5" 
ANCHOR_PATH = "weights/anchor_1.npz"
LABEL_PATH = "weights/label_anchor_1.npz"
CFG_RETINA = "configs/retinaface_mbv2.yaml"
RTSP_ADDR = "rtsp://192.168.1.183:554"
# initialize Redis connection settings
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
 
# initialize constants used to control image spatial dimensions and
# data type
IMAGE_WIDTH = 160
IMAGE_HEIGHT = 160
IMAGE_CHANS = 3
IMAGE_DTYPE = "float32"
 
# initialize constants used for server queuing
IMAGE_QUEUE = "image_queue"
BATCH_SIZE = 32
SERVER_SLEEP = 0.25
CLIENT_SLEEP = 0.25

#initialize ultilities
#CHECKPOINT_PATH = "/home/hao/DCLV-HK191/experiment_on_ktx/ktx-checkpoint/cp.ckpt"

#unknown people storage
UNKNOWN_FOLDER = "UNKNOWN/"

#Email service
SENDER = "plhao2904@gmail.com"
PASSWORD = "konoh@83"
RECEIVER = "1610885@hcmut.edu.vn"
