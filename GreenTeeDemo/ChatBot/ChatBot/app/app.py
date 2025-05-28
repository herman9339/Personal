from flask import Flask, request, jsonify
from chatbot import run_conversation

app = Flask(__name__)
conversation = [{"role": "system", "content": "You are GreenTee’s virtual customer‑service agent."}]

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("message", "")
    reply = run_conversation(user_input, conversation)
    return jsonify({"reply": reply})

@app.route("/")
def root():
    # Serve the HTML file directly for quick local dev
    return open("index.html").read()

if __name__ == "__main__":
    app.run(debug=True, port=5001)