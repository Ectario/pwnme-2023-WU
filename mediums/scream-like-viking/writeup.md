# Notes

Author: Ectario

Files available:

- server.py

## Server Informations

- A new N generated at each connection to the server
- e = 17 static at each connection
- Possibility to encrypt and recover the cipher of the flag (-> it leaves just after)
- the message encrypted when we call the encrypt_flag function is pad on 50 chars

## Idea

_This is an Håstad's broadcast attack example_

- connect several times to recover a sufficient number of moduli (around 7 moduli for a good probability) then after to finish the connection we recover the cipher of the flag with the current modulus

- modulus possible to recover by sending 2 or 3 messages that we encrypt and we make a gcd of the `plaintext^17 - ciphertext`. Explanation :

    ```
    m^e = c[N] => m^e - c = 0 [N] => m^e - c = k*N with k in N => m^e - c divides N
    ```

   - So the gcd of the difference m^e - c gives us N _(with good probability but not sure if the differents m_i^e - c_i have a bigger common divisor than N)_


- sort the moduli that we have to keep: keep only those that are coprime (otherwise we cannot use the Chinese Remainder Theorem)

- then using the CRT we can decipher the flag:

    ```
    CRT with for example 7 moduli:

    c1 = m^17 [N1]
    c2 = m^17 [N2]
    .
    .
    .
    c7 = m^17 [N7]

    =>

    c = m^17 [N1 * N2 * N3 * ... * N7]
    ```

Let a = N1 * N2 * N3 * ... * N7

With a fairly high probability m^17 < a, so modular root in Z/aZ = root in N for m^17

```py
=> flag = nroot(m^17,17)
```

## Exploit

```py
from pwn import *
from Crypto.Util.number import *
from math import gcd
import libnum
from Crypto.Util.Padding import unpad, pad

host = ...
port = ...

context.log_level = "warning"

N_len = 7
N_list = []

def encrypt(m: int, n : int):
    e = 17
    return pow(m, e, n)

def get_flag(p : process) -> int:
    p.sendline(b"Flag")
    c = int(p.recvall(0.5).decode().split(": ")[1])
    p.close()
    return c

def get_n(p : process):
    """
    Compute the modulus value using the technique explained in the WU
    """
    answers = []
    # Messages are created with getPrime(150) here to get a message that is long enough and has a very low chance that the plaintext^17 - ciphertext gcd is anything other than N
    messages = [long_to_bytes(getPrime(150)), long_to_bytes(getPrime(150)), long_to_bytes(getPrime(150))]
    messages_in_server = [pad(messages[0], 50), pad(messages[1], 50), pad(messages[2], 50)]
    p.recvuntil(b'> ').decode()
    for i in range(len(messages)):
        p.sendline(b"Encrypt")
        p.recvuntil(b'> ').decode()
        p.sendline(str(bytes_to_long(messages[i])).encode())
        answer = p.recvuntil(b'> ').decode()
        answers.append(int(answer.splitlines()[1]))

    multiples = [(bytes_to_long(messages_in_server[i])**17) - int(answers[i]) for i in range(len(messages_in_server))]
    N = gcd(*multiples)
    return N

def delete_no_coprime(modulus, remainders) -> list:
    """
    It removes all the moduli that are not coprime to each other
    
    :param modulus: the modulus list
    :param remainders: the list of remainders
    :return: a list of modulus and remainders that are coprime to each other.
    """
    to_keep_modulus = []
    to_keep_remainders = []
    for i, e in enumerate(modulus):
        keep = True
        for e2 in modulus[i:]:
            if e != e2 and gcd(e, e2) != 1: 
                keep = False
                break
        if keep:
            to_keep_modulus.append(e)
            to_keep_remainders.append(remainders[i])
    return to_keep_modulus, to_keep_remainders


def get_modulus_and_remainders():
    modulus = []
    remainders = []

    for _ in range(N_len):
        p = remote(host, port)
        N = get_n(p)
        c = get_flag(p)
        p.close()
        remainders.append(c)
        modulus.append(N)

    modulus, remainders = delete_no_coprime(modulus, remainders)
    return modulus, remainders


if __name__ == '__main__':
    p = log.progress("Getting flag", level=logging.WARNING)
    while True:
        modulus, remainders = get_modulus_and_remainders()
        modulus, remainders = delete_no_coprime(modulus, remainders)
        res=libnum.solve_crt(remainders, modulus)
        val=libnum.nroot(res,17)
        flag = long_to_bytes(val)
        if b"PWNME" in flag:
            p.success(unpad(flag, 50).decode())
            break
```

_DISCLAIMER: the exploit script may take a little while, it's not instantaneous_

