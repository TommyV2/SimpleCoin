# SimpleCoin

## Installation

`pip install -r requirements.txt`

## Node

To run node:

`python node.py port_number` - change `port_number` to actual number e.g. 5001

Node is used to mine and process transactions. To simulate simple peer-to-peer network you can run couple Nodes on different ports.
Each node will use Wallet to generate and store keys on start up.

## Node client

To run node client:

`python node_client.py port_number` - change `port_number` to the port number of a running Node e.g. 5001

Node Client is used to simulate actions of a Node (for example sending requests to other Nodes).

## Wallet

To run wallet:

`python wallet.py node_port_number` - change `node_port_number` to the port number of a running Node e.g. 5001

Wallet stores secret keys for all Nodes, we treat it as an external storage, normally it would be different app.
We can use it to send transactions between Nodes.
