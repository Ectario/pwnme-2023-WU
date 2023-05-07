from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import os

FLAG = "PWNME{0mg_Cr34t1ng_4n_4lg0_l1ke_th4t_wtf_br0}"
KEY = os.urandom(16)

def encrypt_flag():
    iv = os.urandom(16)
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(FLAG.encode(), 16))
    signature = [hex(a ^ b)[2:].zfill(2) for a, b in zip(iv, KEY[::-1])]
    signature = "".join(signature)
    ciphertext = iv.hex()[4:] + encrypted.hex() + signature
    return {"ciphertext": ciphertext}

print(encrypt_flag())