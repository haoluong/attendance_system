import flask
from flask import request,jsonify, send_file
from flask_cors import CORS, cross_origin
from pymongo import MongoClient
import requests
import os
from PIL import Image
import io
from _thread import start_new_thread
# from sign_student import sign_student_web
from modules.db_redis import Rediser
from utils.helpers import base64_decode_image,base64_encode_image
import settings
import redis, uuid, json
import base64, cv2
import numpy as np
# from helpers import decode_image
app = flask.Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
client = MongoClient("mongodb+srv://thesis:thesis123@cluster0-849yn.mongodb.net/test?retryWrites=true&w=majority")
db = client.attendance_system
user = db.users
student_status = db.student_status
student_info = db.student_info
history = client.history
redis_db = redis.StrictRedis(host=settings.REDIS_HOST,
	port=settings.REDIS_PORT, db=settings.REDIS_DB)
@app.route("/login", methods=["POST"])
@cross_origin()
def login():
   username = request.get_json()['username'] 
   password = request.get_json()['password']
   login_query = {'username': username}
   login_results = user.find_one(login_query) 
   data = {"success": False}
   if login_results:
      if login_results['password'] == password:
         data["success"] = True
         return jsonify(data)
   return jsonify(data)

# @app.route("/home", methods=["POST"])
# @cross_origin()
# def get_camera():
#    image = request.files["image"].read()

@app.route("/studentlist", methods=["GET"])
@cross_origin()
def get_studentList():
   std_name = request.args.get('std_name')
   std_id = request.args.get('std_id')
   std_room = request.args.get('std_room')
   sort_column = request.args.get('sort')
   direction = request.args.get('direction')
   number_of_rows = request.args.get('number_of_rows')
   page = request.args.get('page')
   and_expr = [{ '$eq': [ "$std_id",  "$$std_id" ] }]
   if len(std_name) > 0:
      and_expr.append({ '$gt': [{'$indexOfBytes': ["$std_name",std_name] }, -1]})
   if len(std_id) > 0:
      and_expr.append({ '$gt': [{'$indexOfBytes': ["$std_id",std_id] }, -1]})
   if len(std_room) > 0:
      and_expr.append({ '$gt': [{'$indexOfBytes': ["$std_room",std_room] }, -1]})
   expr = [
      {
         '$lookup': 
         {
            'from': "student_info",
            'let': { 'std_id': "$std_id", 'std_name': "$std_name", 'std_room': "$std_room"},
            'as': "student",
            'pipeline': [
               { '$match':
                  { '$expr':
                     { '$and':
                        and_expr
                     }
                  }
               }
            ],
         }
      }
   ]
   if direction is not None:
      expr.append({'$sort':{sort_column: 1 if direction == 'ascending' else -1}})
   student_records = list(student_status.aggregate(expr))
   data = []
   for c in student_records:
      if (len(c["student"]) > 0):
         new_record = {}
         new_record["std_id"] = c["student"][0]["std_id"]
         new_record["std_name"] = c["student"][0]["std_name"]
         new_record["std_room"] = c["student"][0]["std_room"]
         new_record["detected_at"] = c["detected_at"]
         new_record["inKTX"] = c["inKTX"]
         data.append(new_record)
   total = len(data)
   if number_of_rows and page:
      number_of_rows = int(number_of_rows)
      page = int(page)
      end = None if number_of_rows * page > len(data) else number_of_rows * page
      data = data[number_of_rows*(page-1):end]
   return jsonify({"data": data, "total": total})

def read_img_buffer(buffer):
   imagePIL = Image.open(io.BytesIO(buffer))
   image_arr = np.array(imagePIL)
   return cv2.resize(image_arr, (640,480), interpolation=cv2.INTER_LINEAR)

@app.route("/newstudent", methods=["POST"])
@cross_origin()
def add_stdinfo():
   std_id = request.form['std_id']
   std_name = request.form['std_name']
   std_room = request.form['std_room']
   avatar = request.files["avatar"].read()
   num_image = int(request.form['num_image'])
   images = [read_img_buffer(request.files["image"+str(i)].read()) for i in range(num_image)]
   new_student = {}
   new_student["std_id"] = std_id
   new_student["std_name"] = std_name
   new_student["std_room"] = std_room
   new_student["avatar"] = avatar
   k = "sign_"+std_id
   for img in images:
      encoded_image = base64_encode_image(img.astype(np.float32))
      d = {"id": k, "image": encoded_image}
      redis_db.rpush(settings.IMAGE_QUEUE, json.dumps(d))
   new_stdList = student_info.insert_one(new_student)
   return jsonify({"status": True})

@app.route("/avatar", methods=["GET"])
@cross_origin()
def get_avatar():
   std_id = request.args.get('std_id')
   ##get avatar
   std_info = student_info.find_one({"std_id": std_id})
   avatar = std_info.get("avatar", "")
   if avatar == "":
      return jsonify({})
   return send_file(io.BytesIO(avatar),
                     attachment_filename='avatar.jpeg',
                     mimetype='image/jpeg')

@app.route("/stdhistory", methods=["GET"])
@cross_origin()
def get_std_history():
   std_id = request.args.get('std_id')
   std_history = history.get_collection(std_id)
   number_of_rows = int(request.args.get('number_of_rows'))
   page = int(request.args.get('page'))
   data = list(std_history.find({},{'_id': 0}))
   total = len(data)
   end = None if number_of_rows * page > len(data) else number_of_rows * page
   data = data[number_of_rows*(page-1):end]
   return jsonify({"data":data, "total":total})

@app.route("/attend", methods=["POST"])
@cross_origin()
def attend():
   # initialize the data dictionary that will be returned from the
   # view
   data = {"success": False}
   # read the image in PIL format and prepare it for
   # classification
   # import pdb; pdb.set_trace()
   image = request.form.get("image", '')
   captured_image = True
   if image == '':
      captured_image = False
      image = request.files["image"].read()
   else:
      image = image[22:]  #ignore 'data:image/jpeg;base64'
      image = base64.b64decode(str(image))
   imagePIL = Image.open(io.BytesIO(image))
   image_arr = np.array(imagePIL)
   image_arr = cv2.resize(image_arr, (640,480), interpolation=cv2.INTER_LINEAR)
   # if captured_image:
   #    image_arr = image_arr[:,:,::-1]#cv2.flip(image_arr,1)
   # import matplotlib.pyplot as plt
   # plt.imshow(image_arr)
   # plt.show()
   k = str(uuid.uuid4())
   decoded_image = base64_encode_image(image_arr.astype(np.float32))
   d = {"id": k, "image": decoded_image}
   redis_db.rpush(settings.IMAGE_QUEUE, json.dumps(d))

   # keep looping until our model server returns the output
   # predictions
   while True:
      # attempt to grab the output predictions
      output = redis_db.get(k)

      # check to see if our model has classified the input
      # image
      if output is not None:
         # add the output predictions to our data
         # dictionary so we can return it to the client
         output = json.loads(output.decode("utf-8"))
         print("RESULTS", output["label"])
         if output["label"] != 'unknown':
            std = student_info.find_one({"std_id":output["label"]})
            data["std_id"] = output["label"]
            data["std_name"] = std["std_name"] if std is not None else "not filled"
            data["std_room"] = std["std_room"] if std is not None else "not filled"
            data["avatar"] = base64.encodestring(std["avatar"]) if std is not None else "bk1.png"
         else:
            data["std_id"] = "unknown"
            data["std_name"] = "unknown"
            data["std_room"] = "unknown"
            data["avatar"] = 'bk1.png'
         # delete the result from the database and break
         # from the polling loop
         redis_db.delete(k)
         break

      # sleep for a small amount to give the model a chance
      # to classify the input image
      # time.sleep(settings.CLIENT_SLEEP)

   # indicate that the request was a success
   data["success"] = True

   # return the data dictionary as a JSON response
   return jsonify(data)
if __name__ == "__main__":
   print("* Starting web service...")
   app.run(port=9999,debug=True)
