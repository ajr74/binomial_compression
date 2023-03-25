class Binomial:

    def __init__(self, max_n):
        # Populate lookup table with Pascal's Rule. (We only need to store less than half thanks to symmetry.)
        self.cache = []
        self.half_n_vals = []
        for n in range(2, max_n):
            half_n = n // 2
            self.half_n_vals.append(half_n)
            row = []  # don't store k = 0 because we know the value is 1.
            for k in range(1, half_n + 1):
                nm1 = n-1
                row.append(self.get(nm1, k-1) + self.get(nm1, k))
            self.cache.append(row)

    def get(self, n: int, k: int) -> int:
        """
        Fetches the (N, k) binomial coefficient from a precomputed cache.

        :param n: the N parameter of interest.
        :param k: the k parameter of interest.
        :return: the binomial coefficient (N, k), or 0 if k > N.
        """
        if k > n:
            return 0
        if k == 0 or n == k:
            return 1
        nm2 = n-2
        return self.cache[nm2][n - k - 1 if k > self.half_n_vals[nm2] else k - 1]
