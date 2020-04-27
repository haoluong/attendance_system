import redis
import json
import numpy as np
import time
from utils.helpers import base64_encode_image, base64_decode_image

EMBED_QUEUE = "base64_embeds"
LABEL_QUEUE = "labels"
class Rediser():
    def __init__(self, settings):
        self.db = redis.StrictRedis(host=settings.REDIS_HOST,
	        port=settings.REDIS_PORT, db=settings.REDIS_DB)
        self.settings = settings

    def init_db(self):
        embeds = np.load(self.settings.ANCHOR_PATH)["arr_0"]
        labels = np.load(self.settings.LABEL_PATH)["arr_0"]
        self.add_embeds(embeds, labels)

    def pop_image(self):
        q = self.db.lpop(self.settings.IMAGE_QUEUE)
        if q is None:
            return None
        q_json = json.loads(q.decode("utf-8"))
        image = base64_decode_image(q_json["image"],
            self.settings.IMAGE_DTYPE,
            (480, 640, self.settings.IMAGE_CHANS))
        frameID = q_json["id"]
        return frameID, image

    def push_image(self, id, image):
        image = base64_encode_image(image)
        d = {"id": id, "image": image}
        return self.db.rpush(self.settings.IMAGE_QUEUE, json.dumps(d))

    def get_embeds(self):
        embeds = self.db.lrange(EMBED_QUEUE,0,-1)
        embeds = [base64_decode_image(e, self.settings.IMAGE_DTYPE, (1, 1280), byte_convert=False) for e in embeds]
        return np.vstack(tuple(embeds)) if len(embeds) > 0 else []

    def get_labels(self):
        return np.array(self.db.lrange(LABEL_QUEUE,0,-1)).astype(str)

    def add_embeds(self, embeds, labels):
        base64_embeds = [base64_encode_image(e) for e in embeds]
        self.db.rpush(EMBED_QUEUE, *base64_embeds)
        self.db.rpush(LABEL_QUEUE, *labels)
        self.__write_logs("INSERT", "{} embeds of {}".format(len(embeds), labels[0]))
        return self.update_reload_status(value=True)
    
    def remove_student(self, student_id):
        #get index of student
        labels = self.get_labels()
        student_indexes = np.where(labels == student_id)[0]
        #delete student
        [self.db.lset(EMBED_QUEUE, int(idx), "REMOVE") for idx in student_indexes]
        embed_remove = self.db.lrem(EMBED_QUEUE, 0, "REMOVE")
        label_remove = self.db.lrem(LABEL_QUEUE, 0, student_id)
        if label_remove == embed_remove:
            self.__write_logs("REMOVE", "{} embeds from {}".format(embed_remove, student_id))
        else:
            self.__write_logs("REMOVE WARNING", "{} embeds, {} labels from {}".format(embed_remove, label_remove, student_id))
        return self.update_reload_status(value=True)

    def check_reload_status(self):
        return True if self.db.get("reload") == b"True" else False

    def update_reload_status(self, value=False):
        return self.db.set("reload", str(value))

    @staticmethod
    def __write_logs(action,msg):
        with open("logs/db_log.txt", "a+") as f:
            f.write("{t} : {action} - {msg}\n".format(
                t=time.strftime('%Y-%m-%d %H:%M:%S'), 
                action=action,
                msg=msg)
                )