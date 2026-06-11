from flask import Flask, request, jsonify,send_file
from flask_cors import CORS

from rag_engine import ask

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "RAG Chatbot Backend Running"

@app.route("/chat", methods=["POST"])

def chat():

    data = request.get_json()

    question = data.get("question")

    if not question:
        return jsonify({
            "error": "Question is required"
        }), 400

    result = ask(question)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)