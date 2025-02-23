import json

from typing import List
from hashlib import sha256

from blockchain.transaction import Transaction


class Block:
    """
    A class to represent a block in a blockchain.
    """
    def __init__(self,
                 index: int, transactions: List[Transaction], author: str,
                 timestamp: float, previous_hash: str, nonce: int = 0
                ):
        """

        Args:
            index (int): index of the block
            transactions (List[Transaction]): list of transactions in the block
            timestamp (datetime): timestamp of the block
            previous_hash (str): hash of the previous block
            nonce (int, optional): Nonce. Defaults to 0.
        """
        self.index: int = index
        self.author: str = author
        self.transactions: str = str(transactions)
        self.timestamp: float = timestamp
        self.previous_hash: str = previous_hash
        self.nonce: int = nonce

    def compute_hash(self) -> str:
        """
        A function that return the hash of the block contents.
        """
        return sha256(self.to_json().encode()).hexdigest()

    def to_json(self):
        return json.dumps(self.__dict__, sort_keys=True)
    
    def __str__(self):
        return str(self.__dict__)
    
    def __repr__(self):
        return str(self.__dict__)
