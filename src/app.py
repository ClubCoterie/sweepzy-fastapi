from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Welcome to the API!"

@app.route('/receive-url-id', methods=['POST'])
def receive_data():
    if request.is_json:
        data = request.get_json()
        print(data)  # Process the data as needed
        return jsonify({"message": "Data received successfully", "data": data}), 200
    else:
        return jsonify({"error": "Invalid data format. JSON expected."}), 400

if __name__ == '__main__':
    app.run(debug=True)
