from flask import Flask, request, jsonify

app = Flask(__name__)
messages = {}


@app.route('/log_message', methods=['POST'])
def log_message():
    data = request
    msg_uuid = data.json['UUID']
    msg = data.json['msg']

    # Save message to hash table
    messages[msg_uuid] = msg

    # Output to console
    print(f"Received message: {msg}")

    return jsonify({"status": "success"})


@app.route('/get_all_messages', methods=['GET'])
def get_all_messages():
    # Return all messages without keys
    all_messages = list(messages.values())
    return jsonify(all_messages)


if __name__ == '__main__':
    app.run(port=5001)
