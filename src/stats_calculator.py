import hashlib
import math


class StatsCalculator:

    def __init__(self):
        self.counts = [0] * 256
        self.md5_digest = hashlib.md5()

    def update(self, _bytes: bytes):
        for b in _bytes:
            self.counts[b] += 1
        self.md5_digest.update(_bytes)

    def compute_shannon_entropy(self) -> float:
        n = 0
        for c in self.counts:
            n += c
        ent = 0
        n_inv = 1.0 / n
        for c in self.counts:
            if c > 0:
                p = c * n_inv
                ent += (p * math.log2(p))
        return math.fabs(ent)

    def compute_md5_bytes(self) -> bytes:
        return self.md5_digest.digest()

    def compute_md5_hex(self) -> str:
        return self.md5_digest.hexdigest()
