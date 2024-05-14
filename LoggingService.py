from flask import Flask, jsonify, request
from hazelcast import HazelcastClient
import sys
from consul_main import get_value_by_key, set_service


class LoggingService:
    def __init__(self, id, port):
        self.app = Flask(__name__)
        self.client = HazelcastClient(cluster_name=get_value_by_key("hazelcast_name"))
        self.map = self.client.get_map(get_value_by_key("hazelcast_map")).blocking()
        self.setup_routes()
        set_service("logging_service", id, port)

    def setup_routes(self):
        self.app.route('/log_message', methods=['POST'])(self.log_message)
        self.app.route('/get_all_messages', methods=['GET'])(self.get_all_messages)

    def log_message(self):
        data = request.json
        msg_uuid = data.get('UUID')
        msg = data.get('msg')
        if not msg_uuid or not msg:
            return jsonify({"error": "UUID or Message is missing"}), 400

        # Save message
        self.map.put(msg_uuid, msg)
        # Output to console
        print(f"Received message: {msg}")

        return jsonify({"status": "success"})

    def get_all_messages(self):
        # Return all messages without keys
        all_messages = list(self.map.values())
        return jsonify(all_messages)

    def run(self, port):
        self.app.run(port=port)


if __name__ == '__main__':
    logging_service_1 = LoggingService("logging_service_1", 5001)
    logging_service_2 = LoggingService("logging_service_2", 5002)
    logging_service_3 = LoggingService("logging_service_3", 5003)
