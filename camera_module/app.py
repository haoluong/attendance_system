import flask
from flask import request,jsonify, send_file
from flask_cors import CORS, cross_origin
from pymongo import MongoClient
import requests
import os
from PIL import Image
import io
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

@app.route("/newstudent", methods=["POST"])
@cross_origin()
def add_stdinfo():
   # print(request.files)
   
   std_id = request.form['std_id']
   std_name = request.form['std_name']
   std_room = request.form['std_room']
   image = request.files["image"].read()
   new_student = {}
   new_student["std_id"] = std_id
   new_student["std_name"] = std_name
   new_student["std_room"] = std_room
   new_student["avatar"] = image
   # decoded_image = Image.open(io.BytesIO(image))
   # decoded_image.save("b.jpg")
   # decoded_image = decode_image(image, "float32", [160,160])
   # import pdb; pdb.set_trace()
   new_stdList = student_info.insert_one(new_student)
   return jsonify({"status": True})

@app.route("/avatar", methods=["GET"])
@cross_origin()
def get_avatar():
   print("Asfasdfasdfasfd")
   std_id = request.args.get('std_id')
   ##get avatar
   std_info = student_info.find_one({"std_id": std_id})
   avatar = std_info.get("avatar", "")
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

if __name__ == "__main__":
   print("* Starting web service...")
   app.run(port=9999,debug=True)