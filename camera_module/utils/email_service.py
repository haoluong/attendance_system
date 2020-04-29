import smtplib
import numpy as np
import base64
import settings
from PIL import Image
from io import BytesIO
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email.mime.image import MIMEImage

class EmailService():
    def __init__(self):
        self.sender = settings.SENDER
        self.password = input("Type password for "+self.sender+" : ")
        self.receiver = settings.RECEIVER

    def send_mail(self, text, images=None):
        msg = MIMEMultipart()
        msg['From'] = self.sender
        msg['To'] = self.receiver
        msg['Subject'] = '[ATTENDANCE SYSTEM] Unknown people has just appeared in our dorm'

        msg.attach(MIMEText(text))

        for (i,img) in enumerate(images) or []:
            image = Image.fromarray(img.astype(np.uint8)[:,:,::-1])
            buffered = BytesIO()
            image.save(buffered, format="JPEG")     
            part = MIMEImage(buffered.getvalue(),
                name=str(i),
                _subtype="jpeg"
            )
            msg.attach(part)


        smtp = smtplib.SMTP("smtp.gmail.com", 587)
        smtp.starttls()
        smtp.login(self.sender, self.password)
        smtp.sendmail(self.sender, self.receiver, msg.as_string())
        smtp.quit()