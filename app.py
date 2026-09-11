from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path
import uuid

from database import init_database, create_report, get_reports
from ai_detector import detect_problem
from priority import calculate_priority

app=Flask(__name__)
CORS(app)

BASE_DIR=Path(__file__).resolve().parent
UPLOAD_FOLDER=BASE_DIR/"uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config["UPLOAD_FOLDER"]=str(UPLOAD_FOLDER)

init_database()

@app.route("/")
def home():
    return jsonify({"application":"NagarDrishti","status":"running","message":"Civic Intelligence API"})

@app.route("/api/analyze",methods=["POST"])
def analyze():
    if "image" not in request.files:
        return jsonify({"error":"No image provided"}),400
    image=request.files["image"]
    if not image.filename:
        return jsonify({"error":"Invalid image"}),400
    extension=Path(image.filename).suffix.lower()
    if extension not in [".jpg",".jpeg",".png",".webp"]:
        return jsonify({"error":"Unsupported image format"}),400
    filename=uuid.uuid4().hex+extension
    filepath=UPLOAD_FOLDER/filename
    image.save(filepath)
    result=detect_problem(str(filepath))
    priority=calculate_priority(result["severity"])
    return jsonify({
        "success":True,
        "problem_type":result["problem_type"],
        "severity":result["severity"],
        "confidence":result["confidence"],
        "priority_score":priority,
        "image":filename
    })

@app.route("/api/reports",methods=["POST"])
def create_new_report():
    data=request.get_json(silent=True)
    if not data:
        return jsonify({"error":"JSON data required"}),400
    for field in ["problem_type","severity","priority_score"]:
        if field not in data:
            return jsonify({"error":f"Missing field: {field}"}),400
    try:
        priority_score=int(data["priority_score"])
    except (TypeError,ValueError):
        return jsonify({"error":"priority_score must be a number"}),400
    report_id=create_report(
        data["problem_type"],data["severity"],priority_score,
        data.get("latitude"),data.get("longitude"),data.get("image")
    )
    return jsonify({"success":True,"message":"Report created successfully","report_id":report_id}),201

@app.route("/api/reports",methods=["GET"])
def reports():
    data=get_reports()
    return jsonify({"success":True,"count":len(data),"reports":data})

@app.route("/api/reports/<int:report_id>",methods=["GET"])
def single_report(report_id):
    for report in get_reports():
        if report["id"]==report_id:
            return jsonify({"success":True,"report":report})
    return jsonify({"error":"Report not found"}),404

@app.route("/api/reports/<int:report_id>/status",methods=["PUT"])
def update_status(report_id):
    data=request.get_json(silent=True)
    if not data or "status" not in data:
        return jsonify({"error":"Status required"}),400
    status=data["status"]
    allowed=["Pending","Assigned","In Progress","Resolved"]
    if status not in allowed:
        return jsonify({"error":"Invalid status"}),400
    import sqlite3
    from database import DB_PATH
    conn=sqlite3.connect(DB_PATH)
    cursor=conn.execute("UPDATE reports SET status=? WHERE id=?",(status,report_id))
    conn.commit()
    updated=cursor.rowcount
    conn.close()
    if not updated:
        return jsonify({"error":"Report not found"}),404
    return jsonify({"success":True,"message":"Status updated","status":status})

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"],filename)

if __name__=="__main__":
    print("================================")
    print("     NAGARDRISHTI SERVER")
    print("================================")
    print("Server: http://127.0.0.1:5000")
    print("================================")
    app.run(host="0.0.0.0",port=5000,debug=True)