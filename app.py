from flask import Flask, jsonify, request
from search import generate_completion

app = Flask(__name__)

@app.route('/api/chat', methods=['POST'])
def greet():
    data = request.get_json()
    query = data.get("query", "Hi")
    history = data.get("history", [])
    res = generate_completion(query, history)
    return jsonify(res)

if __name__ == '__main__':
    app.run(debug=True)
