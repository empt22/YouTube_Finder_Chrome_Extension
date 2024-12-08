from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

# will listen for GET requests at /hello endpoint
@app.route('/hello', methods=['GET'])
def hello_world():
    current_time = datetime.now().strftime('%I:%M %p')
    return jsonify({'message': f'Hello world - {current_time}'})

if __name__ == '__main__':
    app.run()
