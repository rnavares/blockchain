import json
import uuid


from backend.config import STARTING_BALANCE
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import (
    encode_dss_signature,
    decode_dss_signature,
)
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization


class Wallet:
    """
    An individual wallet for a miner.
    Keeps track of miners balance
    Allows a miner to authorize transactions
    """

    def __init__(self, blockchain=None):
        self.blockchain = blockchain
        self.address = str(uuid.uuid4())[0:8]
        self.private_key = ec.generate_private_key(ec.SECP256K1(), default_backend())
        self.public_key = self.private_key.public_key()
        self.serialize_public_key()

    @property
    def balance(self):
        return Wallet.calculate_balance(self.blockchain, self.address)

    def sign(self, data):
        """
        Generate a signature based on data using local private key
        """

        return decode_dss_signature(
            self.private_key.sign(
                json.dumps(data).encode("utf-8"), ec.ECDSA(hashes.SHA256())
            )
        )

    def serialize_public_key(self):
        """
        Reset the public key to its serialized version
        """
        self.public_key = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

    @staticmethod
    def verify(public_key, data, signature):
        """
        Verify a signature based on the original public key and data
        """
        deserialized_public_key = serialization.load_pem_public_key(
            public_key.encode("utf-8"), default_backend()
        )

        (r, s) = signature

        try:
            deserialized_public_key.verify(
                encode_dss_signature(r, s),
                json.dumps(data).encode("utf-8"),
                ec.ECDSA(hashes.SHA256()),
            )
            return True
        except InvalidSignature:
            return False

    @staticmethod
    def calculate_balance(blockchain, address):
        """
        Calculate th balance of a given address consider the transaction data
        within the blockchain.

        The balance is found by adddindg the output values that belong to the
        address since the most recent transaction by that address
        """

        balance = STARTING_BALANCE

        if not blockchain:
            return balance

        for block in blockchain.chain:
            for transaction in block.data:
                if transaction["input"]["address"] == address:
                    # Any time the address conduct a new transaction it resets its balance
                    balance = transaction["output"][address]
                elif address in transaction["output"]:
                    balance += transaction["output"][address]
        return balance


def main():
    wallet = Wallet()
    print(f"wallet: {wallet.__dict__}")

    data = {"foo": "bar"}

    signature = wallet.sign(data)
    print(f"signature: {signature}")

    # valid
    should_be_valid = Wallet.verify(wallet.public_key, data, signature)
    print(f"should_be_valid: {should_be_valid}")

    # not valid
    should_be_valid = Wallet.verify(Wallet().public_key, data, signature)
    print(f"should_be_valid: {should_be_valid}")


if __name__ == "__main__":
    main()
