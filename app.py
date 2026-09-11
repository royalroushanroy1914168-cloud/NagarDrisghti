from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash
from pathlib import Path
from functools import wraps
from datetime import datetime, timezone
import sqlite3, os, secrets

app=Flask(__name__)
CORS(app, supports_credentials=True, origins=os.getenv("FRONTEND_ORIGIN","*"))
BASE=Path(__file__).parent
DB=BASE/"nagar.db"
UPLOADS=BASE/"uploads"; UPLOADS.mkdir(exist_ok=True)
DEPT_USER=os.getenv("DEPT_USER","roushan")
DEPT_HASH=os.getenv("DEPT_PASSWORD_HASH",generate_password_hash("1914168"))
TOKENS=set()

def db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row
    c.execute("""CREATE TABLE IF NOT EXISTS reports(
      id INTEGER PRIMARY KEY AUTOINCREMENT,citizen_name TEXT,contact TEXT,
      problem_type TEXT,description TEXT,latitude TEXT,longitude TEXT,
      image_path TEXT,priority_score INTEGER,status TEXT,created_at TEXT)""")
    c.commit(); return c

def auth(f):
    @wraps(f)
    def w(*a,**kw):
        t=request.headers.get("Authorization","").replace("Bearer ","",1)
        if not t or t not in TOKENS:return jsonify(error="Department login required"),401
        return f(*a,**kw)
    return w

@app.get("/api/health")
def health(): return jsonify(status="online")

@app.post("/api/login")
def login():
    d=request.get_json() or {}
    if d.get("username")==DEPT_USER and check_password_hash(DEPT_HASH,d.get("password","")):
        token=secrets.token_urlsafe(32); TOKENS.add(token)
        return jsonify(token=token)
    return jsonify(error="Invalid department credentials"),401

@app.post("/api/reports")
def create():
    f=request.form
    required=["citizen_name","contact","problem_type","description"]
    if any(not f.get(x) for x in required): return jsonify(error="Fill all required fields"),400
    image=request.files.get("image")
    image_path=""
    if image and image.filename:
        safe=secrets.token_hex(8)+"_"+Path(image.filename).name
        image.save(UPLOADS/safe); image_path="/uploads/"+safe
    severity={"Pothole":80,"Broken Footpath":70,"Streetlight":60,"Garbage":55,"Blocked Drain":75,"Water Leak":75}.get(f.get("problem_type"),50)
    score=severity
    c=db(); cur=c.execute("""INSERT INTO reports
    (citizen_name,contact,problem_type,description,latitude,longitude,image_path,priority_score,status,created_at)
    VALUES(?,?,?,?,?,?,?,?,?,?)""",(f["citizen_name"],f["contact"],f["problem_type"],f["description"],f.get("latitude",""),f.get("longitude",""),image_path,score,"Pending",datetime.now(timezone.utc).isoformat()))
    c.commit(); rid=cur.lastrowid;c.close()
    return jsonify(id=rid,priority_score=score,status="Pending"),201

@app.get("/api/reports")
@auth
def reports():
    c=db(); rows=[dict(r) for r in c.execute("SELECT * FROM reports ORDER BY priority_score DESC,id DESC")];c.close()
    return jsonify(rows)

@app.get("/api/reports/<int:rid>")
def one(rid):
    c=db(); r=c.execute("SELECT * FROM reports WHERE id=?",(rid,)).fetchone();c.close()
    return (jsonify(dict(r)) if r else (jsonify(error="Report not found"),404))

@app.put("/api/reports/<int:rid>/status")
@auth
def update_status(rid):
    s=(request.get_json() or {}).get("status")
    if s not in ["Pending","Assigned","In Progress","Resolved"]: return jsonify(error="Invalid status"),400
    c=db(); cur=c.execute("UPDATE reports SET status=? WHERE id=?",(s,rid));c.commit();c.close()
    if cur.rowcount==0:return jsonify(error="Report not found"),404
    return jsonify(message="Status updated",status=s)

@app.get("/uploads/<path:name>")
def upload(name): from flask import send_from_directory; return send_from_directory(UPLOADS,name)

if __name__=="__main__":
    db().close()
    app.run(host="0.0.0.0",port=int(os.getenv("PORT",5000)))
