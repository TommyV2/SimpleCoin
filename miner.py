import hashlib
import json
import os
import time

import requests


class Block:
    def __init__(self, index, data, nonce, previous_hash):
        self.index = index
        self.data = data
        self.nonce = nonce
        self.previous_hash = previous_hash
        self.hash = self.hash_block()

    def hash_block(self):
        hash = hashlib.sha256(
            str(self.data).encode("utf-8")
            + str(self.nonce).encode("utf-8")
            + str(self.previous_hash).encode("utf-8")
        ).hexdigest()

        return hash

    def describe(self):
        block = {
            "index": self.index,
            "data": self.data,
            "nonce": self.nonce,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
        }

        return block


def create_genesis_block():
    return Block(index=0, data="genesis", nonce=0, previous_hash="0")


def save_blockchain(blockchain):
    blockchain_json = list(map(lambda block: block.describe(), blockchain))
    with open("blockchain.json", "w") as f:
        json.dump(blockchain_json, f, indent=4)


def get_blockchain():
    with open("blockchain.json") as json_file:
        blockchain = json.load(json_file)

    return blockchain


def add_new_block_to_the_blockchain(blockchain, block):
    block_json = block.describe()
    blockchain.append(block_json)
    with open("blockchain.json", "w") as f:
        json.dump(blockchain, f, indent=4)


def proof_of_work(header, difficulty_bits):
    # calculate the difficulty target
    target = 2 ** (256 - difficulty_bits)
    max_nonce = 2**32  # 4 billion
    for nonce in range(max_nonce):
        hash_result = hashlib.sha256(
            str(header).encode("utf-8") + str(nonce).encode("utf-8")
        ).hexdigest()
        # check if this is a valid result, below the target
        if int(hash_result, 16) < target:
            print(f"Success with nonce {nonce}")
            print(f"Hash is {hash_result}")
            return (hash_result, nonce)
    print(f"Failed after {nonce} tries")
    return nonce


def get_transaction_pool(destination_port):
    url = f"http://localhost:{destination_port}/update_transaction_pool"
    res = requests.get(url)
    data = res.json()
    transaction_pool = data["transaction_pool"]
    return transaction_pool


def pop_transaction_pool(destination_port):
    url = f"http://localhost:{destination_port}/update_transaction_pool"
    requests.delete(url)


def start_mining(blockchain, PORT):
    # difficulty from 0 to 24 bits
    for i in range(24):
        difficulty = 2**i
        print(f"Difficulty: {difficulty} ({i})")
        print("Starting search...")
        # checkpoint the current time
        start_time = time.time()
        # make a new block which includes the hash from the previous block
        # we fake a block of transactions - just a string
        previous_block = blockchain[i]
        previous_hash = previous_block["hash"]

        while not get_transaction_pool(PORT):
            time.sleep(5)
        data = str(get_transaction_pool(PORT).pop(0))
        pop_transaction_pool(PORT)
        new_block = data + previous_hash
        # find a valid nonce for the new block
        (hash_result, nonce) = proof_of_work(new_block, i)
        new_block = Block(i + 1, data, nonce, previous_hash)
        add_new_block_to_the_blockchain(blockchain, new_block)
        # TODO send message to other nodes
        # checkpoint how long it took to find a result
        end_time = time.time()
        elapsed_time = end_time - start_time
        print("Elapsed Time: %.4f seconds" % elapsed_time)
        if elapsed_time > 0:
            # estimate the hashes per second
            hash_power = float(nonce / elapsed_time)
            print("Hashing Power: %ld hashes per second" % hash_power)


def is_valid_blockchain(blockchain):
    max_index = 0
    for block in blockchain:
        index = block["index"]
        if max_index < index:
            max_index = index
        elif max_index > index:
            print(f"Error new index {index} less than max index")
            return False
        expected_hash = block["hash"]
        calculated_hash = hashlib.sha256(
            str(block["data"]).encode("utf-8")
            + str(block["nonce"]).encode("utf-8")
            + str(block["previous_hash"]).encode("utf-8")
        ).hexdigest()
        if calculated_hash != expected_hash:
            print(f"Error in block #{index}")
            return False

    return True


def start_mining_instance(PORT):
    if os.path.isfile("blockchain.json"):
        start_mining(get_blockchain(), PORT)
    else:
        BLOCKCHAIN = [create_genesis_block()]
        save_blockchain(BLOCKCHAIN)
        start_mining(BLOCKCHAIN)


# Just for debugging (remove later)

# save_blockchain([create_genesis_block()])
# BLOCKCHAIN = get_blockchain()
# start_mining(BLOCKCHAIN)
# print(is_valid_blockchain(BLOCKCHAIN))
