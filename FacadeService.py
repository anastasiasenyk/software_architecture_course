from flask import Flask, jsonify, request
import requests
import random
import uuid


class FacadeService:
    def __init__(self, logging_service_urls, messages_service_url):
        self.app = Flask(__name__)
        self.logging_service_urls = logging_service_urls
        self.messages_service_url = messages_service_url
        self.setup_routes()

    def setup_routes(self):
        self.app.route('/post_message', methods=['POST'])(self.post_message)
        self.app.route('/get_messages', methods=['GET'])(self.get_messages)

    def post_message(self):
        msgs = request.json.get('msg')
        if not msgs:
            return jsonify({"error": "Message is missing"}), 400

        responses = []
        for msg in msgs:
            msg_uuid = str(uuid.uuid4())
            payload = {"UUID": msg_uuid, "msg": msg}

            # Forward {UUID, msg} to a random logging-service
            logging_service_url = random.choice(self.logging_service_urls)
            response = requests.post(f"{logging_service_url}/log_message", json=payload)
            responses.append(response.json())

        return jsonify(responses)

    def get_messages(self):
        # Get messages from logging-service
        logging_response = requests.get(f"{self.logging_service_urls[0]}/get_all_messages")
        logging_messages = logging_response.json()

        # Get messages from messages-service
        messages_response = requests.get(f"{self.messages_service_url}/get_static_message")
        messages_message = messages_response.text

        # Concatenate and return responses
        response = {"logging_messages": logging_messages, "messages_message": messages_message}

        print(f'All messages: {messages_message}')
        return jsonify(response)

    def run(self, port):
        self.app.run(port=port)


if __name__ == "__main__":
    logging_service_urls = [
        "http://localhost:5002",
        "http://localhost:5003",
        "http://localhost:5004"
    ]
    messages_service_url = "http://localhost:5001"

    facade_service = FacadeService(logging_service_urls, messages_service_url)
    facade_service.run(5000)