# backend/app.py ← FINAL WORKING VERSION
from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from smart_copilot import smart_support_copilot

# ONLY THIS LINE CHANGED:
app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app, resources={r"/*": {"origins": "*"}})

# Database init (same)
def get_db_connection():
    conn = sqlite3.connect('support_copilot.db')
    conn.row_factory = sqlite3.Row
    return conn

with app.app_context():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS qa_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            response TEXT,
            category TEXT,
            sentiment TEXT,
            priority TEXT,
            feedback TEXT,
            auto_reply INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Serve React App (same)
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")

# Your API routes (same)
@app.route("/ask", methods=["POST"])
def ask_question():
    data = request.get_json()
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "No question"}), 400

    result = smart_support_copilot(question)

    conn = get_db_connection()
    conn.execute('''
        INSERT INTO qa_history (question, response, category, sentiment, priority, auto_reply)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (question, result["auto_reply"], ', '.join(result["predicted_categories"]),
          result["sentiment"], result["priority"], 1 if result["can_auto_reply"] else 0))
    conn.commit()
    conn.close()

    return jsonify(result)

@app.route("/delete/<int:msg_id>", methods=["DELETE"])
def delete_message(msg_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM qa_history WHERE id = ?", (msg_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})

@app.route("/history", methods=["GET"])
def get_history():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM qa_history ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route("/feedback", methods=["POST"])
def feedback():
    data = request.get_json()
    qa_id = data.get("qa_id")
    feedback = data.get("feedback")
    if qa_id and feedback in ["positive", "negative"]:
        conn = get_db_connection()
        conn.execute("UPDATE qa_history SET feedback = ? WHERE id = ?", (feedback, qa_id))
        conn.commit()
        conn.close()
        return jsonify({"status": "ok"})
    return jsonify({"error": "invalid"}), 400

if __name__ == "__main__":
    print("AI Support Copilot → http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)