import hashlib
import math


class BytesAnalyser:
    """
    A bytes analyser for computing an MD5 hash and Shannon entropy value.
    """

    def __init__(self):
        self.counts = [0] * 256
        self.md5_digest = hashlib.md5()
        self.num_bytes = 0

    def update(self, _bytes: bytes):
        """
        Updates the analyser with the bytes provided.

        :param _bytes: the bytes for the update.
        """
        for b in _bytes:
            self.counts[b] += 1
        self.md5_digest.update(_bytes)
        self.num_bytes += len(_bytes)

    def compute_shannon_entropy(self) -> float:
        """
        Computes the Shannon entropy value for the accumulated bytes. A value in [0.0, 8.0].

        :return: the Shannon entropy value for the accumulated bytes.
        """
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
        """
        Computes the MD5 digest for the accumulated bytes.

        :return: the MD5 digest for the accumulated bytes as bytes.
        """
        return self.md5_digest.digest()

    def compute_md5_hex(self) -> str:
        """
        Computes the MD5 digest for the accumulated bytes.

        :return: the MD5 digest for the accumulated bytes as a hex string.
        """
        return self.md5_digest.hexdigest()
