# Simple Python PoW Blockchain Network

A lightweight, educational blockchain simulation written in Python. This project demonstrates core blockchain concepts including blocks, transactions, proof-of-work mining, and peer-to-peer consensus on a local network.

## Features

* **Block & Transaction Models**: Defined in `block.py` and `transaction.py`.
* **Peer Nodes**: Each `BlockchainPeer` can create a genesis block, submit transactions, and mine new blocks (`peer.py`).
* **Mainnet Simulator**: Orchestrates multiple peers, runs mining races, and resolves consensus (`mainnet.py`).
* **Proof-of-Work**: Simple PoW algorithm with adjustable difficulty.
* **Logging**: Activity and block events logged to `blockchain.log`.

## Requirements

* Python 3.7+

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/0xBoringWozniak/BlockchainExample
   cd BlockchainExample
   ```
2. (Optional) Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

## Usage

**Instantiate Peers** in a Python script:

   ```python
   from blockchain.transaction import Transaction
   from blockchain.peer  import BlockchainPeer
   from blockchain.mainnet import BlockchainMainnet
   
   
   if __name__ == '__main__':
       tx1 = Transaction('Alice', 'Bob', 100)
       tx2 = Transaction('Bob', 'Alice', 50)
       tx3 = Transaction('Alice', 'Charlie', 200)
   
       peers = [BlockchainPeer(f'Peer{i}') for i in range(3)]
       mainnet = BlockchainMainnet(peers)
   
       for _ in range(3):
           peers[0].add_new_transaction(tx1)
           peers[1].add_new_transaction(tx2)
           peers[2].add_new_transaction(tx3)
           blockchain.run_mining()

   # Inspect chain
   print(mainnet.get_chain())
   ```

## License

This project is released under the MIT License. Feel free to use and modify it for educational purposes.
