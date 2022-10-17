import sys
import requests
import ecdsa
import os
import base64

class Wallet:
    def __init__(self, port):
        self.NODE_PORT = port # Port of a node we run this wallet for
        self.BUTTONS = BUTTONS = ['0', '1'] # Add more options if needed
    
    # Main program loop
    def run_wallet(self):
        key_input = None
        while key_input not in self.BUTTONS:
            key_input = input("""
            0. Quit
            1. Generate new wallet
            """)
        if key_input == '0':
            quit()
        elif key_input == '1':
            self.generate_keys()
            self.run_wallet()

    # To generate public and private key using ECDSA with SECP256k1 curve
    def generate_keys(self):
        signing_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)  # signing key
        private_key = signing_key.to_string().hex()  # private key in hex
        verification_key = signing_key.get_verifying_key()  # verification key
        public_key = verification_key.to_string().hex()
        public_key = base64.b64encode(bytes.fromhex(public_key))

        storage_path = 'wallet_client/secrets_storage'
        self.create_folder(storage_path)
        self.create_folder(f'{storage_path}/secret_{self.NODE_PORT}')
        with open(f'{storage_path}/secret_{self.NODE_PORT}/pub_key', "w") as f:
            f.write(F'{public_key.decode()}')
        with open(f'{storage_path}/secret_{self.NODE_PORT}/priv_key', "w") as f:
            f.write(F'{private_key}')

        print('=========================================')
        print('New keys generated in the "secret" folder')
        print('=========================================')

    # Get public key for Node with chosen port
    def get_pub_key(self, port):
        storage_path = 'wallet_client/secrets_storage'
        with open(f'{storage_path}/secret_{port}/pub_key', "r") as f:
            pub_key = f.read()
        
        return pub_key

    # Helper Wallet methods
    
    def create_folder(self, path):
        exists = os.path.exists(path)
        if not exists:
            os.mkdir(path)

# Start Wallet for chosen Node
if __name__ == '__main__':
    port = sys.argv[1]
    wallet = Wallet(port)
    print('=========================================')
    print(f'SimpleCoin Wallet for Node: {wallet.NODE_PORT}')
    print('=========================================')
    wallet.run_wallet()