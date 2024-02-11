from flask import Flask, request, jsonify
import requests
import uuid

app = Flask(__name__)
logging_service_url = "http://localhost:5001"
messages_service_url = "http://localhost:5002"


@app.route('/send_message', methods=['POST'])
def send_message():
    msg = request.json['msg']
    msg_uuid = str(uuid.uuid4())
    payload = {"UUID": msg_uuid, "msg": msg}

    # Forward {UUID, msg} to logging-service
    requests.post(f"{logging_service_url}/log_message", json=payload)
    return jsonify({"UUID": msg_uuid, "msg": msg})


@app.route('/get_messages', methods=['GET'])
def get_messages():
    # Get messages from logging-service
    logging_response = requests.get(f"{logging_service_url}/get_all_messages")
    logging_messages = logging_response.json()

    print(f"All logging_messages: {logging_messages}")

    # Get messages from messages-service
    messages_response = requests.get(f"{messages_service_url}/get_static_message")
    messages_message = messages_response.text

    # Concatenate and return responses
    response = {"logging_messages": logging_messages, "messages_message": messages_message}
    return jsonify(response)


if __name__ == '__main__':
    app.run(port=5000)
