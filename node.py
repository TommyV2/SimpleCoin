from flask import Flask, request
import sys
import wallet

node = Flask(__name__)

if __name__ == '__main__':
    
    port = sys.argv[1]
    wallet.generate_keys(port)
    # Start server 
    print('=========================================')
    print(f'Running Node on port: {port}')
    print('=========================================')
    node.run(port=port)