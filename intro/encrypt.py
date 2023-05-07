#!/usr/bin/env python3
import random
from itertools import cycle

MESSAGE = open("./original-message.txt", "r").read()
SECRET = [chr(random.randint(0,0x2600) % 256) for i in range(16)]

def encrypt(message):
    return [str((ord(a) ^ ord(b))) for a, b in zip(message, cycle(SECRET))]


with open('./message-encrypted.txt', 'w') as f:
    f.write(','.join(encrypt(MESSAGE)))
