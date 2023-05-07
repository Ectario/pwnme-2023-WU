#!/bin/env sage

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from Crypto.Util.number import getStrongPrime, long_to_bytes, bytes_to_long

import hashlib

from os import getenv, urandom
from random import getrandbits


FLAG = getenv("FLAG", "PWNME{dummyflag}").encode()


class PRNG(object):
    def __init__(self):
        self._seed = None
        self.q = 279622638356169037213136872013126932777
        self.n = 12
        self.A = Matrix(GF(self.q), 1, self.n, [
                19159356164385140466,
                19848194065535878410,
                33461959522325830456,
                12213590058439028697,
                35299014249932143965,
                13327781436808877193,
                20921178705527762622,
                9371898426952684667,
                9769023908222006322,
                28712160343104144896,
                32272228797175569095,
                14666990089233663894
            ])

        # LCG props
        self.a = getrandbits(32)
        self.c = getrandbits(32)
        self._lcgseed = getrandbits(32)
        self.mod = 2551431067

    @property
    def noise(self):
        self._lcgseed = (self.a * self._lcgseed + self.c) % self.mod

        return self._lcgseed

    @property
    def seed(self):
        if self._seed is None:
            self._seed = Matrix(GF(self.q), self.n, 1, [
                    getrandbits(102) for i in range(self.n)
                ])

        return self._seed

    def randint(self):
        b = (self.A * self.seed + self.noise)[0][0]

        self.A = Matrix(GF(self.q), 1, self.n, [
                int(x * b^(i+1)) % 2^65 for i, x in enumerate(self.A[0])
            ])

        return b
            



def encrypt(shared_secret: int, iv: bytes, msg: bytes):
    sha1 = hashlib.sha1()
    sha1.update(str(shared_secret).encode('ascii'))
    key = sha1.digest()[:16]

    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(msg, 16))

    data = {}
    data['iv'] = iv.hex()
    data['encrypted_msg'] = ciphertext.hex()
    return data


def main():
    # Initialize PRNG:
    rng = PRNG()

    g = 2
    p = 1552518092300708935130918131258481755631334049434514313202351194902966239949102107258669453876591642442910007680288864229150803718918046342632727613031282983744380820890196288509170691316593175367469551763119843371637221007210577919

    n = 100

    ivs = [
        long_to_bytes(int(rng.randint())).ljust(16, b'\0') for _ in range(n)
    ]

    secret_keys = [
        int(rng.randint()) | 
            int(rng.randint() << 128) |
            int(rng.randint() << 256) |
            int(rng.randint() << 384) |
            int(rng.randint() << 512) |
            int(rng.randint() << 640) for _ in range(n)
    ]

    public_keys = [
        pow(g, sk, p) for sk in secret_keys
    ]

    for i, e in enumerate(zip(ivs, secret_keys, public_keys)):
        iv, sk, pk = e
        print(f"Alice's public key: { pk }")

        pk2 = bytes_to_long(urandom(0x60))
        print(f"User #{i} public key: { pk2 }")

        shared_secret = pow(pk2, sk, p)

        print(f"{encrypt(shared_secret, iv, FLAG) = }")

        print("-------------------------")


if __name__ == '__main__':
    main()


