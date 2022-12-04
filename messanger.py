import json
import random
import time
from datetime import datetime

import requests
from datetime import datetime


class Messanger:
    def __init__(self, signature, ports, my_key, public_keys):
        self.signature = signature
        self.ports = ports  # all known hosts
        self.my_key = my_key
        self.public_keys = public_keys
        self.fee = 0.05

    # Adding random transaction to the transaction pool
    def add_message_to_the_transaction_pool(self):
        random_amount = random.randint(1, 100)
        receiver_address = self.my_key
        while receiver_address == self.my_key:
            random_receiver_index = random.randint(0, len(self.public_keys) - 1)
            receiver_address = self.public_keys[random_receiver_index]
        transaction = self.create_transaction_body(random_amount, receiver_address)
        transaction_json = json.dumps(transaction)
        payload = {"transaction": transaction_json}
        headers = {"Content-Type": "application/json"}

        for port in self.ports:
            url = f"http://localhost:{port}/update_transaction_pool"
            requests.post(url, json=payload, headers=headers)

    # Start sending messages
    def start(self):
        while True:
            random_interval = random.randint(10, 20)
            time.sleep(random_interval)
            self.add_message_to_the_transaction_pool()

    def create_transaction_body(self, amount, receiver_address):
        date_time = datetime.now()
        encoded_signature = self.signature.decode()
        transaction_body = {
            "signature": encoded_signature,
            "amount": amount,
            "receiver_change": amount - self.fee,
            "sender": self.my_key,
            "receiver": receiver_address,
            "fee": self.fee,
            "timestamp": str(date_time),
        }
        return transaction_body
