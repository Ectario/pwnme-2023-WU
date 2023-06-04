from Crypto.Util.Padding import pad, unpad
import os

FLAG = ""
# with open("flag.txt") as f:
#     FLAG = f.read()
KEY = os.urandom(16)
BLOCK_SIZE = 16

infras = {"CTFCafe": "PwnHub", "PwnHub": "CTFCafe"}
actual_infra = "PwnHub"


def padding(pt):
    if len(pt) % BLOCK_SIZE != 0:
        pt = pad(pt, BLOCK_SIZE)
    return pt


def unpadding(pt):
    plaintext = pt
    try:
        plaintext = unpad(pt, BLOCK_SIZE)
    except ValueError:  # already unpadded
        pass
    return plaintext


def blockify(message):
    block = [message[i : i + BLOCK_SIZE] for i in range(0, len(message), BLOCK_SIZE)]
    return block


def xor(a, b):
    return bytes([aa ^ bb for aa, bb in zip(a, b)])
