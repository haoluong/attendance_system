import cv2
import os
import settings
import time
import uuid
from utils.email_service import EmailService

def mkdir(folder_path):
    try:
        os.mkdir(folder_path)
    except FileExistsError as e:
        print(e)

class Pikachu():
    def __init__(self):
        self.path = settings.UNKNOWN_FOLDER
        mkdir(self.path)
        self.email_service = EmailService()

    def save(self, image_sequence, _time, status):
        unknown_id = str(uuid.uuid4())
        mkdir(self.path+unknown_id)
        for (i,image) in enumerate(image_sequence):
            cv2.imwrite(self.path + unknown_id + '/' + str(i)+'.jpeg', image)

        self.email_service.send_mail("{unknown_id} {action} at {_time}\n".format(
                unknown_id=unknown_id,
                action="IN KTX" if status else "OUT KTX",
                _time=_time), image_sequence)
        self.__write_logs(unknown_id, "IN KTX" if status else "OUT KTX", _time)

    @staticmethod
    def __write_logs(unknown_id, action, _time):
        with open("logs/unknown_log.txt", "a+") as f:
            f.write("{t} : {unknown_id} {action} at {_time}\n".format(
                t=time.strftime('%Y-%m-%d %H:%M:%S'),
                unknown_id=unknown_id,
                action=action,
                _time=_time)
                )
