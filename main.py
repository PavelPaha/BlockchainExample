from blockchain.transaction import Transaction
from blockchain.peer  import BlockchainPeer
from blockchain.mainnet import BlockchainMainnet


if __name__ == '__main__':
    tx1 = Transaction('Alice', 'Bob', 100)
    tx2 = Transaction('Bob', 'Alice', 50)
    tx3 = Transaction('Alice', 'Charlie', 200)

    peers = [BlockchainPeer(f'Peer{i}') for i in range(3)]
    blockchain = BlockchainMainnet(peers)

    for _ in range(3):
        peers[0].add_new_transaction(tx1)
        peers[1].add_new_transaction(tx2)
        peers[2].add_new_transaction(tx3)
        blockchain.run_mining()
