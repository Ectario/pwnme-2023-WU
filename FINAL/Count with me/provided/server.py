from Crypto.Cipher import AES
from Crypto.Util import Counter
from Crypto.Random import get_random_bytes
from random import randrange
from pwn import xor

def blockify(message, block_size):
    block = [message[i : i + block_size] for i in range(0, len(message), block_size)]
    return block

def randomised_blocks_splitting(text):
    splits = [randrange(4,len(text)//10), randrange(len(text)//10,len(text)//7), randrange(len(text)//7,len(text)//4), randrange(len(text)//4,len(text)//2), randrange(len(text)//2,len(text))-5]
    return [text[:splits[0]], text[splits[0]:splits[1]], text[splits[1]:splits[2]], text[splits[2]:splits[3]], text[splits[3]:splits[4]], text[splits[4]:]]


class ENC:
    def __init__(self, key, nonce):
        self.key = key
        self.nonce = nonce
        self.iv = get_random_bytes(16)
        self.update()

    def update(self):
        self.ctr = Counter.new(128)
        self.cipher = AES.new(self.key, AES.MODE_CTR, counter=self.ctr)
    
    def encrypt(self, plaintext):
        ciphertext = self.cipher.encrypt(plaintext)
        return ciphertext.hex(), self.checksum(ciphertext.hex()).hex()

    # def decrypt(self, ciphertext):
    #     if self.checking(ciphertext):
    #         ctr = Counter.new(128, initial_value=int.from_bytes(self.iv, byteorder='big'))
    #         cipher = AES.new(self.key, AES.MODE_CTR, counter=ctr)
    #         decrypted_data = cipher.decrypt(bytes.fromhex(ciphertext[:-16]))
    #         return decrypted_data

    def checksum(self, ciphertext):
        blocks = blockify(ciphertext, 32)
        blocks = [bytes.fromhex(b) for b in blocks]
        blocks.extend([self.nonce])
        return xor(*blocks)

    def checking(self, ciphertext):
        return ciphertext[-16:] == self.checksum(ciphertext[:-16]) if len(ciphertext) > 16 else False

    def hash(self, ciphertext):
        self.update()
        c = AES.new(self.nonce*2, AES.MODE_CTR, counter=self.ctr)
        self.update()
        c2 = AES.new(self.nonce*2, AES.MODE_CTR, counter=self.ctr)
        h1 = c.encrypt(ciphertext)
        h2 = c2.encrypt(self.key)
        return xor(h1, h2)



enc = ENC(get_random_bytes(16), get_random_bytes(8))

flag = open("flag.txt", "rb").read()

rd_b_s = randomised_blocks_splitting(flag)

with open("output.txt", "w") as f:
    for i in rd_b_s:
        ct, checksum = enc.encrypt(i)
        f.write(ct)
        f.write(" | ")
        f.write(checksum)
        f.write("\n")
    enc.update()
    ct = enc.encrypt(flag)[0]
    f.write(ct)
    f.write("\n")
    f.write(enc.hash(bytes.fromhex(ct)).hex())