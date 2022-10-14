import sys
import requests
import wallet_client.wallet as wallet

BUTTONS = ['0', '1', '2', '3', '4', '5', '6'] #Add more options when needed
NODE_PORT = 0
pub_list = []

# Client methods
def send_pub_key(destination_port):
    pub_key = wallet.get_pub_key(NODE_PORT)
    url = f'http://localhost:{destination_port}/pub_key'
    payload = {
        "from": NODE_PORT,
        "pub_key": pub_key,
    }
    headers = {"Content-Type": "application/json"}
    res = requests.post(url, json=payload, headers=headers)

def get_pub_list(destination_port):
    url = f'http://localhost:{destination_port}/pub_key'
    res = requests.get(url)
    data = res.json()
    print(data['list'])
    global pub_list
    pub_list = data['list']

def set_pub_list(port):
    global pub_list
    url = f'http://localhost:{port}/pub_list'
    payload = {
        "list": pub_list,
    }
    headers = {"Content-Type": "application/json"}
    res = requests.post(url, json=payload, headers=headers)   

def update_pub_list():
    for host in pub_list:
        port, pub = host
        set_pub_list(port)

def print_pub_list():
    global pub_list
    print(pub_list)

def run_client(NODE_PORT):
    key_input = None
    while key_input not in BUTTONS:
        key_input = input("""
        0. Quit
        1. Send your public key
        2. Get public key list
        3. Print public key list
        4. Set public key list
        5. Update known hosts with new list
        """)
    if key_input == '0':
        quit()
    elif key_input == '1':
        destination_port = input('Provide destination port: ')
        send_pub_key(destination_port)
        run_client(NODE_PORT)
    elif key_input == '2':
        destination_port = input('Provide destination port: ')
        get_pub_list(destination_port)
        run_client(NODE_PORT)
    elif key_input == '3':
        print_pub_list()
        run_client(NODE_PORT)
    elif key_input == '4':
        set_pub_list(NODE_PORT)
        run_client(NODE_PORT)
    elif key_input == '5':
        update_pub_list()
        run_client(NODE_PORT)

if __name__ == '__main__':
    
    NODE_PORT = sys.argv[1]
    # Start server 
    print('=========================================')
    print(f'Running Client for Node: {NODE_PORT}')
    print('=========================================')
    run_client(NODE_PORT)