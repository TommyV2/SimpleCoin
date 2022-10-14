import sys
import requests
import ecdsa
import os

buttons = ['0', '1'] #Add more options when needed

def run_wallet(NODE_PORT):
    key_input = None
    while key_input not in buttons:
        key_input = input("""
        0. Quit
        1. Generate new wallet
        """)
    if key_input == '0':
        quit()
    elif key_input == '1':
        generate_keys(NODE_PORT)
        run_wallet(NODE_PORT)

def generate_keys(NODE_PORT):
    signing_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)  # signing key
    private_key = signing_key.to_string().hex()  # private key in hex
    verification_key = signing_key.get_verifying_key()  # verification key
    public_key = verification_key.to_string().hex()

    storage_path = 'wallet_client/secrets_storage'
    create_folder(storage_path)
    create_folder(f'{storage_path}/secret_{NODE_PORT}')
    with open(f'{storage_path}/secret_{NODE_PORT}/pub_key', "w") as f:
        f.write(F'{public_key}')
    with open(f'{storage_path}/secret_{NODE_PORT}/priv_key', "w") as f:
        f.write(F'{private_key}')

    print('=========================================')
    print('New keys generated in the "secret" folder')
    print('=========================================')

def create_folder(path):
    exists = os.path.exists(path)
    if not exists:
        os.mkdir(path)

if __name__ == '__main__':
    NODE_PORT = sys.argv[1]
    print('=========================================')
    print(f'SimpleCoin Wallet for Node: {NODE_PORT}')
    print('=========================================')
    run_wallet(NODE_PORT)