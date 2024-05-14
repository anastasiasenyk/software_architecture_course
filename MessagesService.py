from flask import Flask, request, jsonify
from hazelcast import HazelcastClient
import threading
import uuid
import requests
import sys
from consul_main import get_value_by_key, set_service


class MessageService:
    def __init__(self, id, port):
        self.app = Flask(__name__)
        self.client = HazelcastClient(cluster_name=get_value_by_key("hazelcast_name"))
        self.queue = self.client.get_queue(get_value_by_key("hazelcast_queue")).blocking()
        self.messages = []
        self.mutex = threading.Lock()
        self.setup_routes()
        set_service("message_service", id, port)

    def setup_routes(self):
        self.app.route('/get_all_messages', methods=['GET'])(self.get_messages)

    def run_consumer(self):
        # Start the consumer in a new thread
        consumer_thread_1 = threading.Thread(target=self.consume_messages)
        consumer_thread_2 = threading.Thread(target=self.consume_messages)
        consumer_thread_1.start()
        consumer_thread_2.start()

    def consume_messages(self):
        # Consumer loop
        while True:
            with self.mutex:
                msg = self.queue.take()
                print(f'----consuming: {msg}')
                self.messages.append(msg)

    def get_messages(self):
        return jsonify(self.messages)

    def run(self, port):
        self.run_consumer()
        self.app.run(port=port)


if __name__ == '__main__':
    message_service_1 = MessageService("message_service_1", 5004)
    message_service_2 = MessageService("message_service_2", 5005)