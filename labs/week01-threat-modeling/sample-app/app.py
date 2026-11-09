"""
Tiny sample web app for Week 1 threat modeling.
"""
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import sqlite3, os, uuid

app = Flask(__name__)
DB = "notes.db"
UPLOAD_DIR = "uploads"
ALLOWED_EXT = {".txt", ".png", ".jpg", ".pdf"}
os.makedirs(UPLOAD_DIR, exist_ok=True)

def init_db():
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, owner TEXT, body TEXT)")
    con.commit(); con.close()

@app.route("/notes", methods=["GET", "POST"])
def notes():
    con = sqlite3.connect(DB)
    if request.method == "POST":
        owner = request.json.get("owner", "anon")
        body = request.json.get("body", "")
        con.execute("INSERT INTO notes (owner, body) VALUES (?, ?)", (owner, body))
        con.commit()
    rows = con.execute("SELECT id, owner, body FROM notes").fetchall()
    con.close()
    return jsonify(rows)

@app.route("/upload", methods=["POST"])
def upload():
    f = request.files["file"]
    name = secure_filename(f.filename or "")
    ext = os.path.splitext(name)[1].lower()
    if not name or ext not in ALLOWED_EXT:
        return {"error": "file type not allowed"}, 400
    stored = uuid.uuid4().hex + ext
    f.save(os.path.join(UPLOAD_DIR, stored))
    return {"saved": stored}

@app.route("/files/<n>")
def files(n):
    return send_from_directory(UPLOAD_DIR, n)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)