from sage.modules.free_module_integer import IntegerLattice
from Crypto.Util.number import long_to_bytes
from itertools import starmap
from operator import mul
import hashlib

datas = ""
with open("logs") as f:
  datas = f.read()

#datas = datas.split("CONNECTION #6")[1].split("CONNECTION #7")[0]
datas = datas.split("-------------------------")[:-1]
alices_pk = [int(data.split("Alice's public key: ")[1].split("User")[0].strip()) for data in datas]
bob_pk = [int(data.split(" public key: ")[2].split("encrypt")[0].strip()) for data in datas]
b_values = [int(data.split("'iv': '")[1].split("',")[0].strip(), 16) for data in datas]
ciphers = [int(data.split("encrypted_msg': '")[1].split("'}")[0].strip(), 16) for data in datas]
mod = 2551431067


# Babai's Nearest Plane algorithm
# from: http://mslc.ctf.su/wp/plaidctf-2016-sexec-crypto-300/
def Babai_closest_vector(M, G, target):
  small = target
  for _ in range(1):
    for i in reversed(range(M.nrows())):
      c = ((small * G[i]) / (G[i] * G[i])).round()
      small -= M[i] * c
  return target - small


q = 279622638356169037213136872013126932777
m = 100
n = 12
A = Matrix(GF(q), 1, n, [
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

p = 1552518092300708935130918131258481755631334049434514313202351194902966239949102107258669453876591642442910007680288864229150803718918046342632727613031282983744380820890196288509170691316593175367469551763119843371637221007210577919


A_values = [A[0]]

for b in b_values:
    A_values.append(Matrix(GF(q), 1, n, [
            int(x * b^(i+1)) % 2^65 for i, x in enumerate(A_values[-1])
        ])[0])


A = matrix(ZZ, m + n, m)
for i in range(m):
  A[i, i] = q
for x in range(m):
  for y in range(n):
    A[m + y, x] = A_values[x][y]
lattice = IntegerLattice(A, lll_reduce=True)
print("LLL done")
gram = lattice.reduced_basis.gram_schmidt()[0]
target = vector(ZZ, b_values)
res = Babai_closest_vector(lattice.reduced_basis, gram, target)
print("Closest Vector: {}".format(res))

R = IntegerModRing(q)
M = Matrix(R, A_values[:-1])
s = M.solve_right(res)

# print("s: {}".format(s))

noise_values = []

for row, b in zip(A_values, b_values):
  e = sum(starmap(mul, zip(map(int, s), row))) % q
  assert(abs(int(b) - int(e)) < mod)
  noise_values.append(abs(int(b - e)))

print("noise: {}".format(noise_values))

Z = Zmod(mod)

a = Z(noise_values[2] - noise_values[1]) / Z(noise_values[1] - noise_values[0])
c = noise_values[1] - a * noise_values[0]

def next_rand():
    noise_values.append(int((a * noise_values[-1] + c) % mod))
    rand = (sum(starmap(mul, zip(map(int, s), A_values[-1]))) + noise_values[-1]) % q
    A_values.append(Matrix(GF(q), 1, n, [
            int(x * rand^(i+1)) % 2^65 for i, x in enumerate(A_values[-1])
        ])[0])
    print(rand)
    return rand


private_key = (int(next_rand()) |
            int(next_rand() << 128) |
            int(next_rand() << 256) |
            int(next_rand() << 384) |
            int(next_rand() << 512) |
            int(next_rand() << 640))

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


def decrypt(shared_secret: int, iv: bytes, msg: bytes):
    sha1 = hashlib.sha1()
    sha1.update(str(shared_secret).encode('ascii'))
    key = sha1.digest()[:16]

    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(msg), 16)


bob = bob_pk[0]
shared = pow(bob, private_key, p)

print("secretk:", private_key)

# print(f"Alice: {pow(2, private_key, p)}")

iv = long_to_bytes(b_values[0])
cipher = long_to_bytes(ciphers[0])

print(decrypt(shared, iv, cipher))


