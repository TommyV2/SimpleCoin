import json
import random
import time
import requests
from datetime import datetime


class Messanger:
    def __init__(self, signature, ports):
        self.signature = signature
        self.ports = ports  # all known hosts

    # Adding random message to the transaction pool
    def add_message_to_the_transaction_pool(self):
        time_stamp = time.time()
        date_time = datetime.now()
        encoded_signature = self.signature.decode()
        message = {"signature": encoded_signature, "timestamp": str(date_time)}
        message_json = json.dumps(message)
        payload = {"message": message_json}
        headers = {"Content-Type": "application/json"}

        for port in self.ports:
            url = f"http://localhost:{port}/update_transaction_pool"
            requests.post(url, json=payload, headers=headers)

    # Start sending messages
    def start(self):
        while True:
            random_interval = random.randint(3, 10)
            time.sleep(random_interval)
            self.add_message_to_the_transaction_pool()
