import hashlib
import json
import os
import random
import time

import requests
from colorama import Fore, Style, init

from block import Block

init(convert=True)


class Miner:
    def __init__(self, port, pub_key, known_hosts):
        self.port = port
        self.pub_key = pub_key
        self.known_hosts = known_hosts
        self.mining = False
        self.restart = False
        self.stop_minig = False
        self.last_mined = 0
        self.blockchain = get_blockchain(port)

    # Create genesis block (1st block of a blockchain)
    def create_genesis_block(self):
        return Block(
            index=0,
            data=[
                {
                    "sender": "COINBASE",
                    "receiver": "/8zF7t8B4eaqrq+4LZO21El/CwcMCXGBjT1BJnyEpp5rY3MTPsEqwBsEtAkCfJxYy6iYFDcIr3BnPPgWo+ULxw==",
                    "amount": 1000,
                    "fee": 0.05,
                    "receiver_change": 999.95,
                },
                {
                    "sender": "COINBASE",
                    "receiver": "uIbTvhooA1SdQcZtbNXAi5Ww+Jf7+TlnwuZM/Nniic0CZ4Ifdpnher8sIhHmnUzKKDsYmN30B5gQ3CTKHCpDug==",
                    "amount": 1000,
                    "fee": 0.05,
                    "receiver_change": 999.95,
                },
                {
                    "sender": "COINBASE",
                    "receiver": "ZBmxoiQF5tH+oQK0UOVvTHKBEFAM4CYw+T4AgZNd/MSsX1jozOpITHXcFf/Rejqh3zqFWv83NFYZArAW57lBZQ==",
                    "amount": 1000,
                    "fee": 0.05,
                    "receiver_change": 999.95,
                },
            ],
            nonce=0,
            previous_hash="0",
        )

    # Save Blockchain to a file
    def save_blockchain(self, blockchain):
        blockchain_json = list(map(lambda block: block.describe(), blockchain))
        with open(f"blockchain{self.port}.json", "w") as f:
            json.dump(blockchain_json, f, indent=4)
        self.blockchain = get_blockchain(self.port)

    # Get random network delay
    def network_delay(self):
        if random.uniform(0, 100) < 40:
            random_delay_time = random.randint(0, 5)
            print(f"{Fore.YELLOW}DELAY: {random_delay_time}s{Style.RESET_ALL}")
            time.sleep(random_delay_time)

    def request_payout(self):
        requester = self.port
        url = f"http://localhost:{requester}/request_payout"
        payload = {"requester": requester}
        headers = {"Content-Type": "application/json"}
        requests.post(url, json=payload, headers=headers)

    # Add candidate block to the blockchain
    def add_new_block_to_the_blockchain(self, block, mined_by_me):
        if time.time() - self.last_mined < 5:
            return
        blockchain = get_blockchain(self.port)
        blockchain.append(block)
        with open(f"blockchain{self.port}.json", "w") as f:
            json.dump(blockchain, f, indent=4)
        self.last_mined = time.time()
        if mined_by_me:
            print(f"{Fore.GREEN}Node {self.port} mined a new block!{Style.RESET_ALL}")

    # Calculate pow for the candidate block
    def proof_of_work(self, header, difficulty_bits):
        # calculate the difficulty target
        target = 2 ** (256 - difficulty_bits)
        max_nonce = 2**32

        for nonce in range(max_nonce):
            # check if mining should be stopped every 1000 nodes
            if nonce % 1000 and self.mining is False:
                return (0, 0)
            hash_result = hashlib.sha256(
                str(header).encode("utf-8") + str(nonce).encode("utf-8")
            ).hexdigest()
            # check if this is a valid result, below the target
            if int(hash_result, 16) < target:
                return (hash_result, nonce)
        print(f"Failed after {nonce} tries")
        return nonce

    # Get pending transactions
    def get_transaction_pool(self):
        url = f"http://localhost:{self.port}/update_transaction_pool"
        res = requests.get(url)
        data = res.json()
        transaction_pool = data["transaction_pool"]
        parsed_transaction_pool = []
        for t in transaction_pool:
            parsed_t = json.loads(t)
            parsed_transaction_pool.append(parsed_t)
        return parsed_transaction_pool

    # Clear transaction pool
    def pop_transaction_pool(self):
        url = f"http://localhost:{self.port}/update_transaction_pool"
        requests.delete(url)

    # Verify candidate block
    def verify_candidate_block(self, candidate_block):
        previous_block = get_blockchain(self.port)[-1]
        expected_hash = candidate_block["hash"]
        calculated_hash = hashlib.sha256(
            str(candidate_block["data"]).encode("utf-8")
            + str(candidate_block["nonce"]).encode("utf-8")
            + str(candidate_block["previous_hash"]).encode("utf-8")
        ).hexdigest()
        if candidate_block["index"] != previous_block["index"] + 1:
            return False
        elif candidate_block["previous_hash"] != previous_block["hash"]:
            return False
        elif calculated_hash != expected_hash:
            return False
        else:
            return True

    def notify_other_nodes(self, candidate_block):
        responses = []
        print("@@@@@@@@@@@@@@@@")
        print(self.known_hosts)
        print("@@@@@@@@@@@@@@@@")
        for port in self.known_hosts:
            if port == self.port:
                continue
            url = f"http://localhost:{port}/mining"
            payload = {
                "mining": "False",
            }
            headers = {"Content-Type": "application/json"}
            res = requests.post(url, json=payload, headers=headers)
        for port in self.known_hosts:
            if port == self.port:
                continue
            url = f"http://localhost:{port}/validate"
            payload = {"candidate_block": candidate_block.describe()}
            headers = {"Content-Type": "application/json"}
            res = requests.post(url, json=payload, headers=headers)
            responses.append(res.status_code)
        if all(code == 200 for code in responses):
            return True
        else:
            return False

    # Start mining
    def start_mining(self):
        # difficulty from 0 to 24 bits
        self.mining = True
        difficulty_bits = 2**4 + 8  # modify if needed
        if self.stop_minig:
            return

        while self.mining:
            print("Starting search...")
            self.network_delay()
            # checkpoint the current time
            start_time = time.time()
            # make a new block which includes the hash from the previous block
            previous_block = get_blockchain(self.port)[-1]
            previous_block_index = previous_block["index"]
            previous_hash = previous_block["hash"]

            while not self.get_transaction_pool():
                time.sleep(5)
            transaction_pool = self.get_transaction_pool()
            data_string = str(transaction_pool)
            data = transaction_pool
            self.pop_transaction_pool()
            new_block = data_string + previous_hash
            # find a valid nonce for the new block
            (hash_result, nonce) = self.proof_of_work(new_block, difficulty_bits)
            if self.mining is False:
                break
            end_time = time.time()
            new_block = Block(previous_block_index + 1, data, nonce, previous_hash)
            is_valid = self.notify_other_nodes(new_block)
            if is_valid:  # and self.mining:
                self.restart = True
                self.add_new_block_to_the_blockchain(
                    new_block.describe(), mined_by_me=True
                )
                self.request_payout()
            else:
                self.restart = False
            self.mining = False

            # checkpoint how long it took to find a result
            elapsed_time = end_time - start_time
            print("Elapsed Time: %.4f seconds" % elapsed_time)
            if elapsed_time > 0:
                # estimate the hashes per second
                hash_power = float(nonce / elapsed_time)
                print("Hashing Power: %ld hashes per second" % hash_power)
        print("Stopped mining")

        if self.restart:
            print(f"{Fore.BLUE} 30 seconds until next mining starts{Style.RESET_ALL}")
            time.sleep(30)
            for port in self.known_hosts:
                # Stop mining on other nodes
                url = f"http://localhost:{port}/mining"
                payload = {
                    "mining": "True",
                }
                headers = {"Content-Type": "application/json"}
                res = requests.post(url, json=payload, headers=headers)


# Get Blockchain from file
def get_blockchain(port):
    try:
        with open(f"blockchain{port}.json") as json_file:
            blockchain = json.load(json_file)

        return blockchain
    except:
        return False


# Get all transactions saved on a blockchain
def get_saved_transactions(port):
    try:
        blockchain = get_blockchain(port)
        all_transactions = []
        for block in blockchain:
            block_transactions = block["data"]
            for transaction in block_transactions:
                print(transaction)
                all_transactions.append(transaction)
        return all_transactions
    except:
        return []


def get_current_balance(port):  # TODO
    try:
        blockchain = get_blockchain(port)
        all_transactions = []
        for block in blockchain:
            block_transactions = block["data"]
            for transaction in block_transactions:
                print(transaction)
                all_transactions.append(transaction)
                balance = 0
        return balance
    except:
        return 0


# Check if blockchain is valid
def is_valid_blockchain(blockchain):
    for i, block in enumerate(blockchain):
        index = block["index"]
        if index != i:
            return (
                False,
                f"{Fore.RED}Error wrong index in block #{i}{Style.RESET_ALL}",
            )
        expected_hash = block["hash"]
        calculated_hash = hashlib.sha256(
            str(block["data"]).encode("utf-8")
            + str(block["nonce"]).encode("utf-8")
            + str(block["previous_hash"]).encode("utf-8")
        ).hexdigest()
        if calculated_hash != expected_hash:
            return (False, f"{Fore.RED}Wrong hash in block #{i}{Style.RESET_ALL}")
        if i != 0:
            previous_hash = blockchain[i - 1]["hash"]
            current_block_previous_hash = block["previous_hash"]
            if current_block_previous_hash != previous_hash:
                return (
                    False,
                    f"{Fore.RED}Previous hash of block #{i} in not equal to the hash of block #{i - 1}{Style.RESET_ALL}",
                )
    return (True, f"{Fore.GREEN}Blockchain valid{Style.RESET_ALL}")


# Start mining process on an instance
def start_mining_instance(miner):
    if os.path.isfile(f"blockchain{miner.port}.json"):
        (is_valid, msg) = is_valid_blockchain(get_blockchain(miner.port))
        if not is_valid:
            print(msg)
            return
        miner.start_mining()
        miner.blockchain = get_blockchain(miner.port)
    else:
        BLOCKCHAIN = [miner.create_genesis_block()]
        miner.save_blockchain(BLOCKCHAIN)
        miner.start_mining()
