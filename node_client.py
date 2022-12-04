import base64
import sys
import threading
from datetime import datetime

import ecdsa
import requests

import messanger as msg
import miner
from wallet_client.wallet import Wallet


# Treat it as a helper program, it's only used to demonstrate how does our network work
class NodeClient:
    def __init__(self, port):
        self.NODE_PORT = port  # Port of a node we run this wallet for
        self.BUTTONS = [
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "a",
            "q",
            "b",
            "c",
        ]  # Add more options when needed
        self.pub_list = []
        self.wallet = Wallet(port)  # Connect to the wallet of chosen Node

    # NodeClient methods

    # Send public key from Node A to Node B
    def send_pub_key(self, destination_port):
        pub_key = self.wallet.key_load(NODE_PORT, "pub_key")
        url = f"http://localhost:{destination_port}/pub_key"
        payload = {
            "from": NODE_PORT,
            "pub_key": pub_key,
        }
        headers = {"Content-Type": "application/json"}
        requests.post(url, json=payload, headers=headers)

    # Get public key list from Node B as a Node A
    def get_pub_list(self, destination_port):
        url = f"http://localhost:{destination_port}/pub_key"
        res = requests.get(url)
        data = res.json()
        print(data["list"])
        self.pub_list = data["list"]

    # Update public key list on chosen Node
    def set_pub_list(self, destination_port):
        url = f"http://localhost:{destination_port}/pub_list"
        payload = {
            "list": self.pub_list,
        }
        headers = {"Content-Type": "application/json"}
        requests.post(url, json=payload, headers=headers)

    # Update public key list on all known Nodes from Node A
    def update_pub_list(self):
        for host in self.pub_list:
            port, pub = host
            self.set_pub_list(port)

    # Start mining on chosen Node
    def start_mining(self, destination_port):
        url = f"http://localhost:{destination_port}/mining"
        payload = {"mining": "True", "stop": "False"}
        headers = {"Content-Type": "application/json"}
        requests.post(url, json=payload, headers=headers)

    # Start mining all known Nodes from Node A
    def start_mining_on_all_nodes(self):
        for host in self.pub_list:
            port, pub = host
            self.start_mining(port)
        current_active_nodes_ports = [item[0] for item in self.pub_list]
        return current_active_nodes_ports

    # Stop mining on chosen Node
    def stop_mining(self, destination_port):
        url = f"http://localhost:{destination_port}/mining"
        payload = {"mining": "False", "stop": "True"}
        headers = {"Content-Type": "application/json"}
        requests.post(url, json=payload, headers=headers)

    def send_transaction(
        self, current_active_nodes_ports, message, destination_key, amount
    ):
        private_key = self.wallet.key_load(NODE_PORT, "enc_priv_key")
        pub_key = self.wallet.key_load(NODE_PORT, "pub_key")
        my_key_list = dict(self.pub_list)
        for (
            miner_port,
            key,
        ) in (
            my_key_list.items()
        ):  # for name, age in dictionary.iteritems():  (for Python 2.x)
            if key == destination_key:
                date_time = datetime.now()
                signature, message = self.sign_ECDSA_msg(private_key.decode(), message)
                encoded_signature = signature.decode()
                amount = float(amount)
                transaction_body = {
                    "message": message,
                    "signature": encoded_signature,
                    "amount": amount,
                    "receiver's change": amount - 0.05,
                    "sender": pub_key,
                    "receiver": destination_key,
                    "fee": 0.05,
                    "timestamp": str(date_time),
                }
                payload = {"transaction": transaction_body}
                headers = {"Content-Type": "application/json"}

                for port in current_active_nodes_ports:
                    url = f"http://localhost:{port}/update_transaction_pool"
                    requests.post(url, json=payload, headers=headers)
                    res = requests.post(url, json=payload, headers=headers)
                    print("=========================================")
                    print(res.text)
                    print("=========================================")

    def match_pub_key_to_port(self, public_key):
        tuple_list = self.pub_list
        pub_dict = dict((pub_key, port) for port, pub_key in tuple_list)
        try:
            port = pub_dict[public_key]
            return port
        except:
            print("No such Public key in known hosts list")
            return 0

    # Print public key list
    def print_pub_list(self):
        print(self.pub_list)

    # Send message from Node A to Node B
    def send_message(self, destination_port, private_key, message):
        pub_key = self.wallet.key_load(NODE_PORT, "pub_key")
        signature, message = self.sign_ECDSA_msg(private_key, message)
        url = f"http://localhost:{destination_port}/message"
        payload = {"from": pub_key, "signature": signature.decode(), "message": message}
        headers = {"Content-Type": "application/json"}
        res = requests.post(url, json=payload, headers=headers)
        print("=========================================")
        print("RESPONSE:")
        print("-----------------------------------------")
        print(res.text)
        print("=========================================")

    # Sign message with ECDSA key
    def sign_ECDSA_msg(self, private_key, message):
        bmessage = message.encode()
        signature_key = ecdsa.SigningKey.from_string(
            bytes.fromhex(private_key), curve=ecdsa.SECP256k1
        )
        signature = base64.b64encode(signature_key.sign(bmessage))
        return signature, message

    def get_balance(self, destination_port):
        if destination_port == 0:
            pass
        else:
            balance = 0
            url = f"http://localhost:{destination_port}/balance"
            res = requests.get(url)
            data = res.json()
            print(f"Current balance is {data['Balance']}")
            return balance

    # Main program loop
    def run_client(self):
        key_input = None
        current_active_nodes_ports = [item[0] for item in self.pub_list]
        current_active_nodes_keys = [item[1] for item in self.pub_list]
        while key_input not in self.BUTTONS:
            key_input = input(
                """
            0. Quit
            1. Send your public key
            2. Get public key list
            3. Print public key list
            4. Set public key list
            5. Update known hosts with new list
            6. Send message to another Host
            7. Validation of blockchain
            8. Start messanger
            9. Start mining on one node
            a. Start mining on all nodes
            q. Stop mining on all nodes
            b. Send coins to target
            c. Show balance on one node
            """
            )
        if key_input == "0":
            quit()
        elif key_input == "1":
            destination_port = input("Provide destination port: ")
            self.send_pub_key(destination_port)
            self.run_client()
        elif key_input == "2":
            destination_port = input("Provide destination port: ")
            self.get_pub_list(destination_port)
            self.run_client()
        elif key_input == "3":
            self.print_pub_list()
            self.run_client()
        elif key_input == "4":
            self.set_pub_list(self.NODE_PORT)
            self.run_client()
        elif key_input == "5":
            self.update_pub_list()
            self.run_client()
        elif key_input == "6":
            print("=========================================")
            destination_port = input("Provide destination port: ")
            private_key = input("Provide your private key: ")
            message = input("Write your message: ")
            print("=========================================")
            print("...")
            self.send_message(destination_port, private_key, message)
            self.run_client()
        elif key_input == "7":
            destination_port = input("Provide port: ")
            if miner.get_blockchain(destination_port):
                print(
                    miner.is_valid_blockchain(miner.get_blockchain(destination_port))[1]
                )
            else:
                print("No blockchain created yet")
            self.run_client()
        elif key_input == "8":
            print(f"messaging to these hosts {current_active_nodes_ports}")
            for port in current_active_nodes_ports:
                priv_key = self.wallet.key_load(port, "enc_priv_key")
                pub_key = self.wallet.key_load(port, "pub_key")
                messanger = msg.Messanger(
                    priv_key,
                    current_active_nodes_ports,
                    pub_key,
                    current_active_nodes_keys,
                )
                messanger_thread = threading.Thread(target=lambda: messanger.start())
                messanger_thread.daemon = True
                messanger_thread.start()
                print(f"messenger started on {port}")
            self.run_client()
        elif key_input == "9":
            destination_port = input("Provide destination port: ")
            self.start_mining(destination_port)
            self.run_client()
        elif key_input == "a":
            miners = self.start_mining_on_all_nodes()
            print(f"Mining started on these hosts {miners}")
            self.run_client()
        elif key_input == "q":
            for port in current_active_nodes_ports:
                self.stop_mining(port)
            self.run_client()
        elif key_input == "b":
            print("=========================================")
            destination_key = input("Provide destination key: ")
            amount = input("Specify Amount of coins: ")
            message = input("Message: ")
            print("=========================================")
            print("...")
            self.send_transaction(
                current_active_nodes_ports, message, destination_key, amount
            )
            self.run_client()
        elif key_input == "c":
            destination_key = input("Provide destination key: ")
            port = self.match_pub_key_to_port(destination_key)
            self.get_balance(port)
            self.run_client()


# Start Client for Node with chosen port
if __name__ == "__main__":
    NODE_PORT = sys.argv[1]
    node_client = NodeClient(NODE_PORT)
    print("=========================================")
    print(f"Running Client for Node: {NODE_PORT}")
    print("=========================================")
    node_client.get_pub_list(NODE_PORT)
    node_client.run_client()
