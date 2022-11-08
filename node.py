import os
import sys

import requests
from flask import Flask, request

import miner
import wallet_client.wallet as wallet_client

node = Flask(__name__)
PORT = 0
public_keys_list = []
transaction_pool = [
    {"signature": "my_priv_key", "timestamp": 1667876405.7358031},
    {"signature": "my_priv_key", "timestamp": 1667876421.7888396},
    {"signature": "my_priv_key", "timestamp": 1667876435.8473322},
]
mining = False


# Server methods
# [GET] - returns public_keys_list
# [POST] - recieves public_key of a sender and saves it in its public_keys_list
@node.route("/pub_key", methods=["GET", "POST"])
def pub_key():
    if request.method == "GET":
        return {"list": public_keys_list}
    elif request.method == "POST":
        params = request.get_json()
        add_pub_key_to_the_list(params["from"], params["pub_key"])
        print(f"Got public key from {params['from']}")
        return "Ok", 200


# [POST] - sets pub list recieved by sender
@node.route("/pub_list", methods=["POST"])
def pub_list():
    if request.method == "POST":
        params = request.get_json()
        global public_keys_list
        public_keys_list = params["list"]
        print("Set public list")
        return "Ok", 200


# [POST] - starts mining
@node.route("/mining", methods=["POST"])
def mining():
    if request.method == "POST":
        params = request.get_json()
        print(params)
        global mining
        mining = params["Mining"]
        miner.start_mining_instance(PORT)
        print("Starting mining")
        return "Ok", 200


# [POST] - recieves new message from sender, uses public key to verify signature
@node.route("/message", methods=["POST"])
def message():
    if request.method == "POST":
        params = request.get_json()
        if wallet_client.validate_signature(
            params["from"], params["signature"], params["message"]
        ):
            print("=========================================")
            print("MESSAGE")
            print(f"FROM: {params['from']}")
            print("-----------------------------------------")
            print(params["message"])
            print("=========================================")
            return f"Message recieved by Node: {PORT}", 200
        else:
            return "Bad signature", 404


# [POST] - update transaction pool
@node.route("/update_transaction_pool", methods=["GET", "POST", "DELETE"])
def update_transaction_pool():
    if request.method == "GET":
        return transaction_pool
    if request.method == "POST":
        params = request.get_json()
        message = params["message"]
        print("New message in the transaction pool")
        print("=========================================")
        print(message)
        print("=========================================")
        transaction_pool.append(message)
        return "Ok", 200
    if request.method == "DELETE":
        transaction_pool.pop(0)
        return "", 204


# Add new public key to the public_keys_list
def add_pub_key_to_the_list(host, pub_key):
    for item in public_keys_list:
        port, key = item
        if port == host:
            return
    public_keys_list.append((host, pub_key))


if __name__ == "__main__":
    PORT = sys.argv[1]
    wallet = wallet_client.Wallet(PORT)
    keylist = ["enc_priv_key", "encryption_key", "pub_key"]
    if all(
        os.path.exists(f"wallet_client/secrets_storage/secret_{PORT}/{file}")
        for file in keylist
    ):
        print("Keys already created, resuming node...")
        pass
    else:
        wallet.generate_keys()
    my_pub_key = wallet.key_load(PORT, "pub_key")
    my_priv_key = wallet.key_load(PORT, "enc_priv_key")
    add_pub_key_to_the_list(PORT, my_pub_key)
    if PORT == "5001":
        pass
    else:
        url = "http://localhost:5001/pub_key"
        payload = {
            "from": PORT,
            "pub_key": my_pub_key,
        }
        headers = {"Content-Type": "application/json"}
        requests.post(url, json=payload, headers=headers)

    # Start server
    print("=========================================")
    print(f"Running Node on port: {PORT}")
    print("=========================================")
    node.run(port=PORT, debug=True)
