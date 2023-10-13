import random

def same_bytes(n: int, value: int) -> bytearray:
    result = bytearray(n)
    for i in range(n):
        result[i] = value
    return result

def all_bytes() -> bytearray:
    result = bytearray(256)
    for i in range(256):
        result[i] = i
    return result

def random_sparse_bytes(n: int) -> bytearray:
    result = bytearray(n)
    for i in range(0, n):
        if random.randint(1, 10) > 7:
            result[i] = random.randint(0, 255)
    return result