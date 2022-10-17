import base64
import logging

# import json, requests
import sys

import ecdsa
from flask import Flask, request

from wallet_client.wallet import Wallet

node = Flask(__name__)
PORT = 0
public_keys_list = []

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


# [POST] - resieves new message from sender, uses public key to verify signature
@node.route("/message", methods=["POST"])
def message():
    if request.method == "POST":
        params = request.get_json()
        if validate_signature(params["from"], params["signature"], params["message"]):
            print("=========================================")
            print("MESSAGE")
            print(f"FROM: {params['from']}")
            print("-----------------------------------------")
            print(params["message"])
            print("=========================================")
            return f"Message recieved by Node: {PORT}", 200
        else:
            return "Bad signature", 404


# Helper functions

# Validate if signature is correct
def validate_signature(public_key, signature, message):
    public_key = (base64.b64decode(public_key)).hex()
    print("--------------------------------------")
    print(public_key)
    print("--------------------------------------")
    signature = base64.b64decode(signature)
    verifying_key = ecdsa.VerifyingKey.from_string(
        bytes.fromhex(public_key), curve=ecdsa.SECP256k1
    )
    try:
        return verifying_key.verify(signature, message.encode())
    except:
        logging.error("Could not verify signature")
        return False


# Add new publick key to the public_keys_list
def add_pub_key_to_the_list(host, pub_key):
    for item in public_keys_list:
        port, key = item
        if port == host:
            return
    public_keys_list.append((host, pub_key))


if __name__ == "__main__":
    PORT = sys.argv[1]
    wallet = Wallet(PORT)
    wallet.generate_keys()
    my_pub_key = wallet.key_load(PORT, "pub_key")
    add_pub_key_to_the_list(PORT, my_pub_key)

    # Start server
    print("=========================================")
    print(f"Running Node on port: {PORT}")
    print("=========================================")
    node.run(debug=True, port=PORT)
