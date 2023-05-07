# Write up

Author: Ectario

Files available:

- server.py
- output.txt

## Idea

According to the file `server.py` we notice that the key used is randomly generated as well as the initialization vector.

We must therefore look at how the ciphertext is constructed:

`iv.hex()[4:] + encrypted.hex() + signature`

In this information, we see that we can easily retrieve:

- part of the IV
- the cipher of the flag
- the signature

So what's the signature?

According to the line

```py
signature = [hex(a ^ b)[2:].zfill(2) for a, b in zip(iv, KEY[::-1])]
```

the signature is formed from the key (which has been __reversed!__) and the IV.

Since we know a huge part of the IV (from the 3rd byte to the 16th), we can therefore see that there are only 2 bytes that we do not know. Which gives us (0xFF+1) * (0xFF+1) ~= 65000 tests in the worst-case scenario, which is largely doable and is done in `exploit.py`.

_Note: in the server the slicing [4:] means that we keep from the 4th char to the last, but before this slicing we can see that the bytes are converted into hexadecimal, or 1 byte is encoded on 2 symbols in hexadecimal._

## Exploit

The idea of ​​the exploit is quite simple, just bruteforce the IV for the 2 bytes that are unknown to us. To do this, you just have to xor the signature and the new IV of the each iteration without forgetting to reverse the order of the hexadecimal that we obtained (because in `server.py` before the xoring the key is reversed `KEY[ ::-1]`)

Which gives us :

```py
key = [hex(a ^ b)[2:].zfill(2) for a, b in zip(signature, new_iv)][::-1]
```

Then from that we decrypt using the AES module of pycryptodome and we look if in the plaintext that we recover there is "PWNME", if so then the IV and the key that we test at this iteration are the right ones and we get the flag, otherwise we continue the bruteforce.

## Exploit Redacted

```py
#!/usr/bin/env python3
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDCOLOR = '\x1b[0m'


def bruteforce_IV(iv_known_part, signature, ciphertext):
    signature = bytes.fromhex(signature)
    for i in range(0xFF+1):
        for j in range(0xFF+1):
            unknown_part = str(hex(i)[2:].zfill(2))
            unknown_part += str(hex(j)[2:].zfill(2))
            new_iv = bytes.fromhex(unknown_part + iv_known_part)
            key = [hex(a ^ b)[2:].zfill(2) for a, b in zip(signature, new_iv)][::-1]
            key = "".join(key)
            cipher = AES.new(bytes.fromhex(key), AES.MODE_CBC, new_iv)
            plaintext = cipher.decrypt(bytes.fromhex(ciphertext))
            if b"PWNME" in plaintext:
                print("\n\tFlag: ", unpad(plaintext, 16).decode(),end="\n\n")

ciphertext = {"ciphertext":"ca92b5919084c02658a2e3d57ee3a37b8ab32e581d2615359cc7858e966090d328df2be8b5ad889561d9abce6f961fe03a95a2051e882db2373b33b5a43a1c13ff62af7f835df3cc1ccc64571e74f8b84587c727d56c4d37983e7b80ce3c"}["ciphertext"]

print(f"{bcolors.OKCYAN}cipher returned: {bcolors.ENDCOLOR}", ciphertext)
signature = ciphertext[-32:]
print(f"{bcolors.OKGREEN}signature returned: {bcolors.ENDCOLOR}", signature)
known_iv = ciphertext[:28]
print(f"{bcolors.OKGREEN}known_iv returned: {bcolors.ENDCOLOR}", known_iv)
ciphertext = ciphertext[28:-32]
print(f"{bcolors.FAIL}ciphertext returned: {bcolors.ENDCOLOR}", ciphertext)

bruteforce_IV(known_iv, signature, ciphertext)
```