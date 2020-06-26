IMAGE_SIZE = 160
MARGIN = 16
CHECKPOINT_PATH = "weights/arc_mbv2_ccrop.h5" #"weights/arc_mbv2.h5" 
ANCHOR_PATH = "weights/arc_mbv2_crop_embed.npz"
LABEL_PATH = "weights/arc_mbv2_crop_label.npz"
CFG_RETINA = "configs/retinaface_mbv2.yaml"
RTSP_ADDR = "rtsp://192.168.1.183:554"
EMBED_SIZE = 512
# initialize Redis connection settings
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
 
# initialize constants used to control image spatial dimensions and
# data type
IMAGE_WIDTH = 128
IMAGE_HEIGHT = 128
IMAGE_CHANS = 3
IMAGE_DTYPE = "float32"
 
# initialize constants used for server queuing
IMAGE_QUEUE = "image_queue"
EMBED_QUEUE = "base64_embeds"
LABEL_QUEUE = "labels1"
BATCH_SIZE = 32
SERVER_SLEEP = 0.25
CLIENT_SLEEP = 0.25

#initialize ultilities
#CHECKPOINT_PATH = "/home/hao/DCLV-HK191/experiment_on_ktx/ktx-checkpoint/cp.ckpt"

#unknown people storage
UNKNOWN_FOLDER = "UNKNOWN/"

#Email service
SENDER = "plhao2904@gmail.com"
RECEIVER = "1610885@hcmut.edu.vn"