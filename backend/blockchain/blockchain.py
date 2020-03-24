from backend.blockchain.block import Block
from backend.wallet.transaction import Transaction
from backend.config import MINING_REWARD_INPUT
from backend.wallet.wallet import Wallet


def lightning_hash(data):
    return data + "*"


class Blockchain:
    """
        A public ledger of transactions implemented as
        a list of blocks - data set of transactions
    """

    def __init__(self):
        # the genesis is needed to start a Blockchain
        # as ahc block needs a last hash
        self.chain = [Block.genesis()]

    def add_block(self, data):
        self.chain.append(Block.mine_block(self.chain[-1], data))

    def __repr__(self):
        return f"Blockchain: {self.chain}"

    def replace_chain(self, chain):
        """
        Replace local chain with the incoming on if:
        - the incoming chain is longer hat the local one
        - the incoming chain is formatted properly
        """
        if len(chain) <= len(self.chain):
            raise Exception("Cannot replace. Incoming chain must be longer")

        try:
            Blockchain.is_valid_chain(chain)
        except Exception as e:
            raise Exception(f"Cannot replace. The incoming chain is invalid: {e}")

        self.chain = chain

    def to_json(self):
        """
        Serialize the blockchain into a list of blocks
        """
        return list(map(lambda block: block.to_json(), self.chain))

    @staticmethod
    def from_json(chain_json):
        """
        Deserialize a lost of serialize blocks into blockchain instance
        """
        blockchain = Blockchain()
        blockchain.chain = list(
            map(lambda block_json: Block.from_json(block_json), chain_json)
        )

        return blockchain

    @staticmethod
    def is_valid_chain(chain):
        """
        Validate incoming chain.
        Enforce the followin rules:
        - chain must start with a genesis block
        - block must be formatted correctly
        """

        if chain[0] != Block.genesis():
            raise Exception("Genesis block must be valid")

        for i in range(1, len(chain)):  # skip genesis
            block = chain[i]
            last_block = chain[i - 1]
            Block.is_valid_block(last_block, block)

        Blockchain.is_valid_transaction_chain(chain)

    @staticmethod
    def is_valid_transaction_chain(chain):
        """
        Enforca the rules of a chain composed of blocks of transaction:
        - Each transaction must only appear once in the chain
        - There can only be one mining reward per block
        - Each transaction must be valid
        """
        transaction_ids = set()

        for i in range(len(chain)):
            block = chain[i]

            has_mining_reward = False

            for transaction_json in block.data:
                transaction = Transaction.from_json(transaction_json)

                if transaction.id in transaction_ids:
                    raise Exception(f"Transaction {transaction.id} is not unique")

                transaction_ids.add(transaction.id)

                if transaction.input == MINING_REWARD_INPUT:
                    if has_mining_reward:
                        raise Exception(
                            "There can only be 1 mining reward per block,"
                            f"Check block with hash: {block.hash}"
                        )
                    has_mining_reward = True
                else:
                    historic_blockchain = Blockchain()
                    historic_blockchain.chain = chain[0:i]
                    historic_balance = Wallet.calculate_balance(
                        historic_blockchain, transaction.input["address"]
                    )

                    if historic_balance != transaction.input["amount"]:
                        raise Exception(
                            f"Transaction {transaction.id} has an invalid input amount"
                        )

                Transaction.is_valid_transaction(transaction)


def main():
    blockchain = Blockchain()
    blockchain.add_block("one")
    blockchain.add_block("two")

    print(blockchain)
    print(f"blockchain.py ___name__: {__name__}")


if __name__ == "__main__":
    main()
