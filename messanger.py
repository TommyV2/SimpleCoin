import json
import time
import random
import requests

class Messanger:
    def __init__(self, signature, ports):
        self.signature = signature
        self.ports = ports

    # Adding random message to the blockchain
    def add_message_to_the_transaction_pool(self):
        time_stamp = time.time()
        message = {
            "signature": self.signature,
            "timestamp": time_stamp
        }
        message_json = json.dumps(message)

        url = f"http://localhost:{5003}/update_transaction_pool" # TODO change to sending to all nodes in the pool
        payload = {"message": message_json}
        headers = {"Content-Type": "application/json"}
        res = requests.post(url, json=payload, headers=headers)

    def start(self):
        while True:
            random_interval = random.randint(10, 30)
            time.sleep(random_interval)
            self.add_message_to_the_transaction_pool()