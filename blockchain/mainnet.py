import logging
import time
import threading
import pickle

from typing import List, Set, Optional
from copy import deepcopy

from blockchain.transaction import Transaction
from blockchain.peer import BlockchainPeer


# Configure the logging system
logging.basicConfig(
    filename='blockchain.log',
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger('blockchain')


class BlockchainMainnet:

    def __init__(self, peers: List[BlockchainPeer]):
        self.peers: List[BlockchainPeer] = peers
        self.blockchain: BlockchainPeer = peers[0]
        self.blockchain._announce()
        self.the_longest_chain: Optional[BlockchainPeer] = None

    # Function to query unconfirmed transactions
    def get_pending_txs(self) -> List[str]:
        mempool: Set[Transaction] = []
        for peer in self.peers:
            mempool.extend(peer.unconfirmed_transactions)
        return [tr.to_json() for tr in mempool]

    def consensus(self):
        """
        Our naive consnsus algorithm. If a longer valid chain is
        found, our chain is replaced with it.
        """
        logging.info(f"Mainnet | Consensus started")
        longest_blockchain = self.the_longest_chain

        if not BlockchainPeer.check_chain_validity(longest_blockchain.chain):
            logging.error(f"Mainnet | Invalid longest chain {self.the_longest_chain.peer_name}")
            return
        else:
            self.blockchain = longest_blockchain
            logging.info(f"Mainnet | Consensus done with new chain {self.blockchain.peer_name} | Announcing new block {self.blockchain.last_block}")

    def __sync_peers(self):
        """
        A function to announce to the network once a block has been mined.
        Other blocks can simply verify the proof of work and add it to their
        respective chains.
        """
        for peer in self.peers:
            peer.chain = deepcopy(self.blockchain.chain)
        self.the_longest_chain = None

    def run_mining(self):
        """
        A function to simulate mining of new block by adding
        it to the blockchain and announcing to the network.
        Announcing to the network is done by consensus - the first peer
        that finishes mining will announce the new block to the network and all other sync with it.
        """
        tasks = []
        for peer in set(self.peers):
            tasks.append(threading.Thread(target=peer.mine, daemon=True, args=()))

        for task in set(tasks):
            task.start()

        while not self.the_longest_chain:
            for task in set(tasks):
                if not task.is_alive(): # the first peer that finishes mining will announce the new block to the network
                    time.sleep(1)       # wait for the file to be written (announced)
                    with open('the_longest_chain.pickle', 'rb+') as storage:
                       new_peer = pickle.load(storage)
                       self.the_longest_chain = self.__find_peer_by_name(new_peer)
                    break

        for task in tasks:
            task.join()

        self.consensus()
        self.__sync_peers()

    def __find_peer_by_name(self, peer_name: str) -> BlockchainPeer:
        for peer in self.peers:
            if peer.peer_name == peer_name:
                return peer
        raise Exception(f"Peer {peer_name} not found")

    def get_chain(self):
        chain = self.blockchain._get_chain()
        chain.update({'current_mainnet_peer_name': self.blockchain.peer_name})
        chain.update({'peers': [peer.peer_name for peer in self.peers]})
        return chain
