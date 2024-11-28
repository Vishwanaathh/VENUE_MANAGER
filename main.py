from flask import Flask,request,jsonify
import mysql.connector
from flask_jwt_extended import JWTManager,jwt_required,create_access_token,get_jwt_identity
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

conn=mysql.connector.connect(
    host='localhost',
    port=3306,
    user='root',
    password='',
    database='users'

)
cursor=conn.cursor()



app=Flask(__name__)
limiter=Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day","50 per hour"],
    storage_uri="memory://"
)

app.config["JWT_SECRET_KEY"]="77777"
jwt=JWTManager(app)
CORS(app)
@app.route("/login",methods=["POST"])
def login():
    credentials=request.get_json()
    name=credentials.get("name")
    password=credentials.get("password")
    cursor.execute("SELECT * FROM names")
    data=cursor.fetchall()
    for i in data:
        if(name==i[0] and password==i[1]):
            access=create_access_token(identity=name)
            return jsonify(access_token=access),200
    else:
        return jsonify({"message":"access denied"}),401
@app.route("/")
@limiter.limit("3 per minute")
def home():
    return "Welcome to Venues"
@app.route("/all")
@limiter.limit("3 per minute")
def all():
    cursor.execute("SELECT * FROM venue")
    data=cursor.fetchall()
    return jsonify(data)
@app.route("/name/<name>")
@limiter.limit("3 per minute")
def search(name):
    try:
        cursor.execute("SELECT * FROM venue WHERE NAME=%s",(name,))
        data=cursor.fetchall()
        return jsonify(data)
    except Exception as e:
        return "NOT FOUND"
@app.route("/free")
@limiter.limit("3 per minute")
def search1():
    try:
        cursor.execute("SELECT * FROM venue WHERE OCCUPIED=%s",(0,))
        data=cursor.fetchall()
        return jsonify(data)
    except Exception as e:
        return "EVERYTHING IS FULL"
@app.route("/at/<location>")
@limiter.limit("3 per minute")
def locationn(location):
    try:
        cursor.execute("SELECT * FROM venue WHERE LOCATION=%s",(location,))
        data=cursor.fetchall()
        return jsonify(data)
    except Exception as e:
        return "NO AVAILABLE SPOTS AT THAT LOCATION"
@app.route("/admin/create",methods=["POST"])
@jwt_required()
def create():
    try:
        data=request.get_json()
        name=data.get("name")
        location=data.get("location")
        capacity=data.get("capacity")
        occupied=data.get("occupied")
        cursor.execute("INSERT INTO venue (NAME,LOCATION,CAPACITY,OCCUPIED) VALUES (%s,%s,%s,%s)",(name,location,capacity,occupied))
        return "INSERTED"
    except Exception as e:
        return "FAILED"
@app.route("/admin/update/<name>/<occupied>",methods=["PUT"])
@jwt_required()
def toggle(name,occupied):
    try:
        cursor.execute("UPDATE venue SET OCCUPIED=%s WHERE NAME=%s",(occupied,name))
        return "UPDATED"
    except Exception as e:
        return "FAILURE"




if(__name__=="__main__"):
    app.run(debug=True)