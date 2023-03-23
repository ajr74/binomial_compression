import math

from binomial import Binomial


def test_get():
    max_n = 256
    c = Binomial(max_n)
    for n in range(0, max_n):
        for k in range(0, n):
            assert c.get(n, k) == math.comb(n, k)
