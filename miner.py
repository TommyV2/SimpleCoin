import hashlib
import json
import os
import time
import requests

from block import Block


class Miner:

    def __init__(self, port):
        self.port = port
        self.mining = False
        self.blockchain = get_blockchain()


    def create_genesis_block(self):
        return Block(index=0, data="genesis", nonce=0, previous_hash="0")


    def save_blockchain(self, blockchain):
        blockchain_json = list(map(lambda block: block.describe(), blockchain))
        with open("blockchain.json", "w") as f:
            json.dump(blockchain_json, f, indent=4)
        self.blockchain = get_blockchain()


    def add_new_block_to_the_blockchain(self, block):
        block_json = block.describe()
        blockchain = get_blockchain()
        blockchain.append(block_json)
        if is_valid_blockchain(blockchain):
            with open("blockchain.json", "w") as f:
                json.dump(blockchain, f, indent=4)
        else:
            mined_index = block.index
            print(f"Block #{mined_index} was already mined!")


    def proof_of_work(self, header, difficulty_bits):
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


    def get_transaction_pool(self):
        url = f"http://localhost:{self.port}/update_transaction_pool"
        res = requests.get(url)
        data = res.json()
        transaction_pool = data["transaction_pool"]
        return transaction_pool


    def pop_transaction_pool(self):
        url = f"http://localhost:{self.port}/update_transaction_pool"
        requests.delete(url)


    #TODO only 1st block mines, because it starts before everyone else
    def start_mining(self): # TODO: start mining on all nodes
        # difficulty from 0 to 24 bits
        self.mining = True
        difficulty = 2**5 # modify if needed 
        while(self.mining):
            print("Starting search...")
            # checkpoint the current time
            start_time = time.time()
            # make a new block which includes the hash from the previous block
            previous_block = get_blockchain()[-1]
            previous_block_index = previous_block["index"]
            previous_hash = previous_block["hash"]

            while not self.get_transaction_pool():
                time.sleep(5)
            transaction_pool = self.get_transaction_pool()
            data = str(transaction_pool)
            self.pop_transaction_pool()
            new_block = data + previous_hash
            # find a valid nonce for the new block
            (hash_result, nonce) = self.proof_of_work(new_block, previous_block_index )
            new_block = Block(previous_block_index  + 1, data, nonce, previous_hash)

            self.add_new_block_to_the_blockchain(new_block)
            # TODO send message to other nodes
            # checkpoint how long it took to find a result
            end_time = time.time()
            elapsed_time = end_time - start_time
            print("Elapsed Time: %.4f seconds" % elapsed_time)
            if elapsed_time > 0:
                # estimate the hashes per second
                hash_power = float(nonce / elapsed_time)
                print("Hashing Power: %ld hashes per second" % hash_power)
        print("Stopped mining")


def get_blockchain():
    try:
        with open("blockchain.json") as json_file:
            blockchain = json.load(json_file)

        return blockchain
    except:
        return False


def is_valid_blockchain(blockchain):
    max_index = 0
    for i,block in enumerate(blockchain):
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
        if i != 0:  
            previous_hash = blockchain[i - 1]["hash"]
            current_block_previous_hash =  block["previous_hash"]
            if current_block_previous_hash != previous_hash:
                print(f"Previous hash of block #{i} in not equal to the hash of block #{i - 1}")
                return False

    return True


def start_mining_instance(miner):
    if os.path.isfile("blockchain.json"):
        miner.start_mining()
        miner.blockchain = get_blockchain()
    else:
        BLOCKCHAIN = [miner.create_genesis_block()]
        miner.save_blockchain(BLOCKCHAIN)
        miner.start_mining()