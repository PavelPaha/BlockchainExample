import json

from typing import Optional
from hashlib import sha256


class Transaction:
    """
    A class to represent a transaction in a blockchain.
    """
    def __init__(self,
                 sender_address: str, recipient_address: str,
                 value: float = 0, data: Optional[str] = '',
                ):
        """

        Args:
            sender_address (str): sender's address
            recipient_address (str): recipient's address
            value (float): value of the transaction
            data (str, optional): data of the transaction. Defaults to None.
        """
        self.sender_address = sender_address
        self.recipient_address = recipient_address
        self.value = value
        self.data: str = data
        self.tx_hash: str = sha256(self.to_json().encode()).hexdigest()

    def to_json(self) -> str:
        """
        Convert object to json string

        Returns:
            str: json string
        """
        return json.dumps(self.__dict__, sort_keys=True)

    def __str__(self) -> str:
        return self.to_json()
    
    def __repr__(self) -> str:
        return self.to_json()

    def __hash__(self) -> str:
        return hash(self.to_json())

    def __eq__(self, other) -> bool:
        return self.__hash__() == other.__hash__()
