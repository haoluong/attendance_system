import socket
from _thread import *
from pymongo import MongoClient
import re
client = MongoClient("mongodb+srv://thesis:thesis123@cluster0-849yn.mongodb.net/test?retryWrites=true&w=majority")
PREFIX = '<MSG>'

class StudentStatus():
   def __init__(self, student_id, inKTX, detected_at):
      self.student_id = student_id
      self.inKTX = bool(inKTX)
      self.detected_at = detected_at

   def __str__(self):
      return "student_id: {}, inKTX: {}, detected_at: {}".format(self.student_id, self.inKTX, self.detected_at)

def get_record_from_msg(message):
   attributes = message.split(',')
   values = [attr[attr.find(':')+1:] for attr in attributes]
   return StudentStatus(*values)

def process_msg(message):
   message_content = re.search('<MSG>(.*)<MSG>', str(message)).group(1)
   student_stt = get_record_from_msg(str(message_content))
   db = client.attendance_system #lay database
   status_collection = db.student_status  #lay bang users
   #update trang thai cua student
   query = {'std_id': student_stt.student_id}
   new_status = {
      '$set':
         {'std_id': student_stt.student_id, 'inKTX': student_stt.inKTX, 'detected_at': student_stt.detected_at}
      }
   results = status_collection.update_one(query, new_status, upsert=True)
   print(results)
   print(str(student_stt))

def server_thread(connection):
   result = b''
   while True:
      data = connection.recv(1024)
      if data:
         result += data
      index_prefix = str(result).find(PREFIX, len(PREFIX), -1)
      if index_prefix != -1:
         start_new_thread(process_msg, (result[:index_prefix+3],))
         result = result[index_prefix+3:]
   connection.close()


socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind(('',45678))
socket.listen(1)
print("Server started")
while True:
   conn, address = socket.accept()
   if address:
      start_new_thread(server_thread, (conn,))
   else:
      print('None')
socket.close()