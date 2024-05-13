from flask import Flask, request, jsonify
from hazelcast import HazelcastClient
import threading
import uuid
import requests
import sys


class MessageService:
    def __init__(self):
        self.app = Flask(__name__)
        self.client = HazelcastClient(cluster_name="dev")
        self.queue = self.client.get_queue("message-queue").blocking()
        self.messages = []
        self.mutex = threading.Lock()
        self.setup_routes()

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


if __name__ == "__main__":
    service = MessageService()
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5001
    service.run(port)