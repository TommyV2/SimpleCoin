import hashlib

class Block:
    def __init__(self, index, data, nonce, previous_hash):
        self.index = index
        self.data = data
        self.nonce = nonce
        self.previous_hash = previous_hash
        self.hash = self.hash_block()

    def hash_block(self):
        hash = hashlib.sha256(
            str(self.data).encode("utf-8")
            + str(self.nonce).encode("utf-8")
            + str(self.previous_hash).encode("utf-8")
        ).hexdigest()

        return hash

    def describe(self):
        block = {
            "index": self.index,
            "data": self.data,
            "nonce": self.nonce,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
        }

        return block