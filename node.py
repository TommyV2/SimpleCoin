import json
from flask import Flask, request
import sys

import requests
import wallet_client.wallet as wallet
import base64
import ecdsa

node = Flask(__name__)


PORT = 0
public_keys_list = []

# Server methods
@node.route('/pub_key', methods=['GET', 'POST'])
def pub_key():
    if request.method == 'GET':  
        return {'list': public_keys_list}
    elif request.method == 'POST':
        params = request.get_json()
        add_pub_key_to_the_list(params['from'], params['pub_key'])
        print(f"Got public key from {params['from']}")
        return "Ok", 200

def validate_signature(public_key, signature, message):
    public_key = (base64.b64decode(public_key)).hex()
    signature = base64.b64decode(signature)
    verifying_key = ecdsa.VerifyingKey.from_string(bytes.fromhex(public_key), curve=ecdsa.SECP256k1)
    try:
        return verifying_key.verify(signature, message.encode())
    except:
        return False

def add_pub_key_to_the_list(host, pub_key):
    for item in public_keys_list:
        port, key = item
        if port == host:
            return
    public_keys_list.append((host, pub_key))

if __name__ == '__main__':
    PORT = sys.argv[1]
    wallet.generate_keys(PORT)
    my_pub_key = wallet.get_pub_key(PORT)
    add_pub_key_to_the_list(PORT, my_pub_key)

    # Start server 
    print('=========================================')
    print(f'Running Node on port: {PORT}')
    print('=========================================')
    node.run(debug=True, port=PORT)