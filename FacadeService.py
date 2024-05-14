from flask import Flask, jsonify, request
import requests
import random
import uuid
from hazelcast import HazelcastClient
from consul_main import get_value_by_key, get_service, set_service


class FacadeService:
    def __init__(self, id, port):
        self.app = Flask(__name__)
        self.logging_service_urls = get_service("logging_service")
        self.messages_service_url = get_service("message_service")
        self.client = HazelcastClient(cluster_name=get_value_by_key("hazelcast_name"))
        self.queue = self.client.get_queue(get_value_by_key("hazelcast_queue")).blocking()
        self.setup_routes()
        set_service("facade_service", id, port)

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

            self.queue.offer(msg)

            logging_service_url = random.choice(self.logging_service_urls)
            response = requests.post(f"{logging_service_url}/log_message", json=payload)

            print(f'Msg sent to Message and Logging Service: {msg}')

            responses.append(response.json())

        return jsonify(responses)

    def get_messages(self):
        # Get messages from logging-service
        logging_response = requests.get(f"{self.logging_service_urls[0]}/get_all_messages")
        logging_messages = logging_response.json()

        # Get messages from messages-service
        messages_response_1 = requests.get(f"{self.messages_service_url[0]}/get_all_messages")
        messages_response_2 = requests.get(f"{self.messages_service_url[1]}/get_all_messages")
        messages_messages = [messages_response_1.json(), messages_response_2.json()]

        # Concatenate and return responses
        response = {"logging_messages": logging_messages, "messages_messages": messages_messages}

        print(f'All messages: {response}')
        return jsonify(response)

    def run(self, port):
        self.app.run(port=port)


if __name__ == "__main__":
    facade_service = FacadeService("facade_service_1", 5000)
