import json
import os
import sys
import threading

import requests
from flask import Flask, request

import miner as miner_client
import wallet_client.wallet as wallet_client
from miner import Miner, start_mining_instance

node = Flask(__name__)
PORT = 0
public_keys_list = []
transaction_pool = []
miner = None
my_priv_key = ""
fee_pool = 0
flat_payout = 150
fee = 0.05


# Server methods
# [GET] - returns remaining fee_pool amount
# [POST] - updates amount remaining in fee_pool
@node.route("/fee_pool", methods=["GET", "POST"])
def fee_pool():
    global fee_pool
    if request.method == "GET":
        return {"fee pool left": fee_pool}
    elif request.method == "POST":
        params = request.get_json()
        fee_pool = fee_pool + update_fee_pool(
            fee_pool, params("action"), params("amount")
        )
        print(
            f"Updating remaining fee pool {params('action')}, remaining fees {fee_pool}"
        )
        return "Ok", 200


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
        mining = params["mining"]
        if "stop" in params:
            if params["stop"] == "True":
                miner.stop_minig = True
            else:
                miner.stop_minig = False
        if mining == "True":
            miner_thread = threading.Thread(target=lambda: start_mining_instance(miner))
            miner_thread.daemon = True
            miner_thread.start()
        else:
            miner.mining = False
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


@node.route("/request_payout", methods=["GET"])
def request_payout():
    if request.method == "GET":
        last_transaction_sender = "something"  # todo
        params = request.get_json()
        if params["requester"] == last_transaction_sender:
            global flat_payout
            global fee
            add_from_fee_pool = get_fee_amount()  # TODO
            transaction = {
                "sender": "COINBASE",
                "receiver": params["requester"],
                "amount": flat_payout + add_from_fee_pool,
                "fee": fee,
                "receiver's change": flat_payout + add_from_fee_pool - fee,
            }
            update_transaction_pool(transaction)


# [POST] - update transaction pool
@node.route("/update_transaction_pool", methods=["GET", "POST", "DELETE"])
def update_transaction_pool():
    global transaction_pool
    global my_priv_key
    if request.method == "GET":
        return {"transaction_pool": transaction_pool}
    if request.method == "POST":
        params = request.get_json()
        transaction = params["transaction"]

        transaction_json = json.loads(transaction)
        saved_transactions = miner_client.get_saved_transactions(PORT)
        if not wallet_client.validate_new_transaction(
            saved_transactions, transaction_json, PORT
        ):
            return "Wrong transaction", 404
        # elif not wallet_client.validate_signature( # TODO: nie dziala
        #     transaction_json["sender"], my_priv_key, transaction_json
        # ):
        #     return "Wrong signature", 404
        else:
            print("New message in the transaction pool")
            transaction_pool.append(transaction)
            return "OK", 200
    if request.method == "DELETE":
        transaction_pool = []
        return "", 204


# [POST] - validate_candidate_block
@node.route("/validate", methods=["POST"])
def validate():
    if request.method == "POST":
        params = request.get_json()
        candidate_block = params["candidate_block"]
        is_valid = miner.verify_candidate_block(candidate_block)

        if is_valid:
            miner.add_new_block_to_the_blockchain(candidate_block, mined_by_me=False)
            return "Ok", 200
        else:
            return "Bad candidate block", 404


def get_fee_amount():
    # TODO
    fee_amount = 0
    return fee_amount


# Add new public key to the public_keys_list
def add_pub_key_to_the_list(host, pub_key):
    for item in public_keys_list:
        port, key = item
        if port == host:
            return
    public_keys_list.append((host, pub_key))


def update_fee_pool(fee_pool, action, amount):
    update = 0
    if action == "PAY":
        update = (-1) * fee_pool * 0.1
    elif action == "RECIEVE":
        update = amount
    else:
        print(f"Incorrect actiong {action}")
    return update


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

    miner = Miner(PORT, ["5001", "5002", "5003"])
    # Start server
    print("=========================================")
    print(f"Running Node on port: {PORT}")
    print("=========================================")
    node.run(port=PORT, debug=True)
