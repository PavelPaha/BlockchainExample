import logging
import pickle
import time
import random

from typing import List, Dict
from copy import deepcopy

from blockchain.transaction import Transaction
from blockchain.block import Block


# Configure the logging system
logging.basicConfig(
    filename='blockchain.log',
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger('blockchain')


class BlockchainPeer:
    difficulty = 2  # difficulty of our PoW algorithm
    has_difficulty_bomb: bool = False  # whether the peer has a difficulty bomb or not

    def __init__(self, peer_name: str):
        self.peer_name: str = peer_name
        self.unconfirmed_transactions: List[Transaction] = [] # mempool
        self.chain: List[Block] = None
        self.__init_blockchain()

    def create_genesis_block(self) -> None:
        """
        A function to generate genesis block and appends it to
        the chain. The block has index 0, previous_hash as 0, and
        a valid hash.
        """
        genesis_block = Block(
            index=0, transactions=[],
            author='Satoshi', timestamp=0,
            nonce=0, previous_hash="0",
        )
        genesis_block.hash = self.proof_of_work(genesis_block)
        self.chain = []
        self.chain.append(genesis_block)
        logging.info(f"{self.peer_name} | Created genesis block {genesis_block.to_json()}")

    @property
    def last_block(self):
        return self.chain[-1]

    def _add_block(self, block: Block, proof: str):
        """
        A function that adds the block to the chain after verification.
        Verification includes:
        * Checking if the proof is valid.
        * The previous_hash referred in the block and the hash of latest block
          in the chain match.

        Args:
            block (Block): block to be added
            proof (str): proof of work result
        """
        logging.info(f"{self.peer_name} | Adding block {block.to_json()}")

        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            logging.error(f"{self.peer_name} | Previous hash {previous_hash} != {block.previous_hash}")
            raise Exception("Invalid block")

        if not BlockchainPeer.is_valid_proof(block, proof):
            logging.error(f"{self.peer_name} | Invalid proof {proof}")
            raise Exception("Invalid proof")

        # set the hash of the block after verification
        block.hash = proof
        self.chain.append(block)
        logging.info(f"{self.peer_name} | Added block {block}")

    @classmethod
    def proof_of_work(cls, block: Block) -> str:
        """
        Function that tries different values of nonce to get a hash
        that satisfies our difficulty criteria.

        Args:
            block (Block): block to be mined
        
        Returns:
            str: hash of the mined block
        """
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * BlockchainPeer.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
            # difficulty bomb
            if cls.has_difficulty_bomb:
                time.sleep(random.randint(0, 10) / 100)
        return computed_hash

    def add_new_transaction(self, transaction: Transaction):
        self.unconfirmed_transactions.append(transaction)
        logging.info(f"{self.peer_name} | Added transaction {transaction.to_json()}")

    def __init_blockchain(self):
        logging.info(f"{self.peer_name} | Initializing blockchain")
        self.chain: List[Block] = []
        self.create_genesis_block()

    def _get_chain(self) -> Dict:
        """
        A function that returns the chain and its length.

        Returns:
            Dict: {
                'length': int - length of the chain,
                'chain': List[Block] - list of blocks in the chain
                'current_mainnet_peer_name': str - name of the current mainnet peer
                'peers': List[str] - list of peers names
            }
        """
        chain_data = []
        for block in self.chain:
            chain_data.append(block)

        return {
            "length": len(chain_data),
            "chain": chain_data,
        }

    def _announce(self):
        """
        A function to announce to the network once a block has been mined.
        In this case we will send data to all peers to update the blockchain by file.
        """
        with open('the_longest_chain.pickle', 'wb') as storage:
            pickle.dump(self.peer_name, storage)

    def mine(self):
        """
        This function serves as an interface to add the pending
        transactions to the blockchain by adding them to the block
        and figuring out Proof Of Work.
        """
        logging.info(f"{self.peer_name} | Start mining")

        if not self.unconfirmed_transactions:
            logging.info(f"{self.peer_name} | No transactions to mine")
            return

        last_block: Block = self.last_block
        new_block = Block(
            index=last_block.index + 1,
            transactions=self.unconfirmed_transactions,
            author=self.peer_name,
            timestamp=time.time(),
            previous_hash=last_block.hash,
            nonce=0,
        )
        proof = self.proof_of_work(new_block)
        logging.info(f"{self.peer_name} | Found proof {proof}")
        self._add_block(new_block, proof)
        self.unconfirmed_transactions = []
        self._announce()

    @classmethod
    def is_valid_proof(cls, block: Block, block_hash: str) -> bool:
        """
        Check if block_hash is valid hash of block and satisfies
        the difficulty criteria.

        Args:
            block (Block): block to be verified
            block_hash (str): hash of the block to be verified
        
        Returns:
            bool: True if block_hash is valid, False otherwise
        """
        return (block_hash.startswith('0' * BlockchainPeer.difficulty) and
                block_hash == block.compute_hash())

    @classmethod
    def check_chain_validity(cls, chain: List[Block]) -> bool:
        result = True
        previous_hash = "0"

        try:
            chain_copy = deepcopy(chain)
        except TypeError: # some attr is a couroutine
            return False

        for block in chain_copy:
            block_hash = block.hash
            # remove the hash field to recompute the hash again
            # using `compute_hash` method.
            delattr(block, "hash")

            if not cls.is_valid_proof(block, block_hash):
                logging.error(f"Invalid proof {block_hash} for block {block.index} | valid proof {block.compute_hash()}")
                result = False
                break

            if previous_hash != block.previous_hash:
                logging.error(f"Invalid previous hash {block.previous_hash} != {previous_hash}")
                result = False
                break

            block.hash, previous_hash = block_hash, block_hash

        return result
