import hashlib

class Block:
    def __init__(self, data, nonce, previous_hash):
        self.data = data
        self.nonce = nonce
        self.previous_hash = previous_hash
        self.hash = self.hash_block()

    # Calculate current hash of a block
    def hash_block(self):
        hash = hashlib.sha256(
            str(self.data).encode("utf-8")
            + str(self.nonce).encode("utf-8")
            + str(self.previous_hash).encode("utf-8")
        ).hexdigest()

        return hash

    # Get block's params in a dict
    def describe(self):
        block = {
            "data": self.data,
            "nonce": self.nonce,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
        }

        return block