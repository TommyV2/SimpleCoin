import hashlib
import json


class Block:
    def __init__(self, data, nonce, previous_hash):
        self.data = data
        self.nonce = nonce
        self.previous_hash = previous_hash
        self.hash = self.hash_block()

    def hash_block(self):
        hash = hashlib.sha256(str(self.data).encode('utf-8') + str(self.nonce).encode('utf-8') + str(self.previous_hash).encode('utf-8')).hexdigest()

        return hash
    
    def describe(self):
        block = {
            "data": self.data,
            "nonce": self.nonce,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }

        return block

def create_genesis_block():
    return Block(data = "genesis", nonce = 0, previous_hash="0")

def save_blockchain(blockchain):
    blockchain_json = list(map(lambda block: block.describe(), blockchain))
    with open(f"blockchain.json", "w") as f:
        json.dump(blockchain_json, f, indent = 4)

BLOCKCHAIN = [create_genesis_block(), create_genesis_block(), create_genesis_block()]
save_blockchain(BLOCKCHAIN)