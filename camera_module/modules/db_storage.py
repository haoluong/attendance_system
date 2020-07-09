from pymongo import MongoClient
import time

class StudentStatus():
   def __init__(self, student_id, inKTX, detected_at):
      self.student_id = student_id
      self.inKTX = bool(inKTX)
      self.detected_at = detected_at

   def __str__(self):
      return "student_id: {}, inKTX: {}, detected_at: {}".format(self.student_id, self.inKTX, self.detected_at)

class DBStorage():
    def __init__(self):
        self.client = MongoClient("mongodb+srv://thesis:thesis123@cluster0-849yn.mongodb.net/test?retryWrites=true&w=majority")
        self.db = self.client.attendance_system #lay database
        self.history = self.client.history
    
    def save(self, student_stt):
        status_collection = self.db.student_info  #lay bang users
        #update trang thai cua student
        query = {'std_id': student_stt.student_id}
        new_status = {
            '$set':
                {'std_id': student_stt.student_id, 'inKTX': student_stt.inKTX, 'detected_at': student_stt.detected_at}
            }
        results = status_collection.update_one(query, new_status, upsert=True)
        self.__write_logs("INSERT OR UPDATE STATUS", str(student_stt))
        
        std_history = self.history[student_stt.student_id] #lay bang history cua student
        new_history = {'inKTX': student_stt.inKTX, 'detected_at': student_stt.detected_at}
        his = std_history.insert_one(new_history)
        self.__write_logs("INSERT HISTORY", str(student_stt))
    
    def remove(self, student_id):
        student_info = self.db.student_info
        query = {'std_id': student_id}
        results = student_info.remove(query)
        self.__write_logs("REMOVE", "student id = " + str(student_id))

    @staticmethod
    def __write_logs(action,msg):
        with open("logs/db_log.txt", "a+") as f:
            f.write("{t} : {action} - {msg}\n".format(
                t=time.strftime('%Y-%m-%d %H:%M:%S'), 
                action=action,
                msg=msg)
                )