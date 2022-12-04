import base64
import json
import logging
import os
import sys

import ecdsa
from cryptography.fernet import Fernet

# import requests


class Wallet:
    def __init__(self, port):
        self.NODE_PORT = port  # Port of a node we run this wallet for
        self.BUTTONS = ["0", "1"]  # Add more options if needed

    # Main program loop
    def run_wallet(self):
        key_input = None
        while key_input not in self.BUTTONS:
            key_input = input(
                """
            0. Quit
            1. Generate new wallet
            """
            )
        if key_input == "0":
            quit()
        elif key_input == "1":
            keylist = ["enc_priv_key", "encryption_key", "pub_key"]
            if all(
                os.path.exists(
                    f"wallet_client/secrets_storage/secret_{self.NODE_PORT}/{file}"
                )
                for file in keylist
            ):
                self.run_wallet()
            else:
                self.generate_keys()
                self.run_wallet()

    # To generate public and private key using ECDSA with SECP256k1 curve
    def generate_keys(self):
        encryption_key = Fernet.generate_key()
        signing_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)  # signing key
        private_key = signing_key.to_string().hex()  # private key in hex
        verification_key = signing_key.get_verifying_key()  # verification key
        public_key = verification_key.to_string().hex()
        public_key = base64.b64encode(bytes.fromhex(public_key))

        storage_path = "wallet_client/secrets_storage"
        self.create_folder(storage_path)
        self.create_folder(f"{storage_path}/secret_{self.NODE_PORT}")
        path = f"{storage_path}/secret_{self.NODE_PORT}"
        self.key_write(encryption_key, f"{path}/encryption_key")
        with open(f"{path}/pub_key", "w") as f:
            f.write(f"{public_key.decode()}")
        with open(f"{path}/priv_key", "w") as f:
            f.write(f"{private_key}")
        self.file_encrypt(encryption_key, f"{path}/priv_key", f"{path}/enc_priv_key")
        os.remove(f"{path}/priv_key")

        print("=========================================")
        print('New keys generated in the "secret" folder')
        print("This is your private key:")
        print("=========================================")
        print(private_key)
        print("=========================================")

    # Helper Wallet methods

    def key_write(self, key, key_name):
        with open(key_name, "wb") as mykey:
            mykey.write(key)

    def key_load(self, port, key_name):
        if key_name == "enc_priv_key":
            with open(
                f"wallet_client/secrets_storage/secret_{port}/encryption_key", "r"
            ) as mykey:
                encryption_key = mykey.read()
                key = self.file_decrypt_to_string(
                    encryption_key,
                    f"wallet_client/secrets_storage/secret_{port}/enc_priv_key",
                )
        else:
            with open(
                f"wallet_client/secrets_storage/secret_{port}/{key_name}", "r"
            ) as mykey:
                key = mykey.read()
        return key

    def file_encrypt(self, key, original_file, encrypted_file):
        f = Fernet(key)
        with open(original_file, "rb") as file:
            original = file.read()

        encrypted = f.encrypt(original)
        with open(encrypted_file, "wb") as file:
            file.write(encrypted)

    def file_decrypt(self, key, encrypted_file, decrypted_file):
        f = Fernet(key)
        with open(encrypted_file, "rb") as file:
            encrypted = file.read()

        decrypted = f.decrypt(encrypted)
        with open(decrypted_file, "wb") as file:
            file.write(decrypted)

    def file_decrypt_to_string(self, key, encrypted_file):
        f = Fernet(key)
        with open(encrypted_file, "rb") as file:
            encrypted = file.read()

        decrypted = f.decrypt(encrypted)
        return decrypted

    def create_folder(self, path):
        exists = os.path.exists(path)
        if not exists:
            os.mkdir(path)


# Validate if signature is correct
def validate_signature(public_key, signature, message):
    if public_key == "COINBASE":
        return True
    public_key = (base64.b64decode(public_key)).hex()
    signature = base64.b64decode(signature)
    verifying_key = ecdsa.VerifyingKey.from_string(
        bytes.fromhex(public_key), curve=ecdsa.SECP256k1
    )
    try:
        return verifying_key.verify(signature, message.decode())
    except:
        return True

def get_balance(transaction_pool, port):
    balance = 0
    public_key = ""
    with open(f"wallet_client/secrets_storage/secret_{port}/pub_key", "r") as mykey:
        public_key = mykey.read()
        
    for transaction in transaction_pool:
        sender_amount = transaction["amount"]
        receiver_amount = transaction["receiver_change"]
        if transaction["sender"] == public_key:
            balance -= sender_amount
        elif transaction["receiver"] == public_key:
            balance += receiver_amount
    return balance

def validate_new_transaction(transaction_pool, transaction, port): 
    amount = transaction["amount"]
    balance = get_balance(transaction_pool, port)
    if amount <= balance:
        return True
    return False

# Start Wallet for chosen Node
if __name__ == "__main__":
    port = sys.argv[1]
    wallet = Wallet(port)
    print("=========================================")
    print(f"SimpleCoin Wallet for Node: {wallet.NODE_PORT}")
    print("=========================================")
    wallet.run_wallet()
