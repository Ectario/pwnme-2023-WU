# Reconstruction de seed

from sage.all import Matrix, ZZ, QQ, mod
from sage.matrix.berlekamp_massey import berlekamp_massey

B = [
    0x07dbf2ecf811a9eb23ca250dda08bfec,
    0x955543311a9d6ef1b088f92972d7c93b,
    0x90965f3b910c06d34bc18c761ddfee70,
    0xc93bde6abb33d8ee9a37465b9efa92ba,
    0x21a9215984fd9513654b880c89e3586a,
    0xaae7bf0d2678fb3ca606d1904cd5a5e7,
    0x0ef36ac5f5b69d9182b2e26400a2a93a,
    0x7008b5800ef4b18d3d95c6272c3bcd62,
    0x1d3811ee484ac900e004d6a5b6ec8693,
    0x1cd782e2a089127c41bee85467ae44c8,
    0x99dbd8974d66f6829ee82be9204ed874,
    0x9ebb68bb26ee609b1e83d39760f1ae72,
    0xcc067a2923a7b15b87634fe553b28478,
    0xa61579000c348474006c26a9d6d9c00b,
    0x687e5599bbc7a3663db5c418038bbe1e,
    0x8a3d64984b936919da65a64e98b12439,
    0xbc8a8eb4139eae18410447805b488d1b,
    0x1d773f7f32598c94d147149e450ea3ee,
]
B = B[:14]

p = 2551431067
q = 279622638356169037213136872013126932777

A0 = [
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
]

size = 12 + len(B) + 1
M = Matrix(ZZ, size, size)
for i in range(12):
    M[i,i] = 1
A = A0
for j, b in enumerate(B):
    # Equation somme(seedi Ai) = b + epsilon
    for i in range(12):
        M[i,12+j] = A[i]
    # Modulo q
    M[12+j,12+j] = q
    # Résultat (négatif décalé de 2^31)
    M[12 + len(B), 12+j] = -b - 2**31
    M[12 + len(B), 12 + len(B)] = 1
    A = [((a * pow(b, i+1, q)) % q) % 2**65 for i, a in enumerate(A)]

# 12 colonnes 2^102
# B colonnes 2^30
for i in range(len(B)):
    M.rescale_col(12 + i, 2**70)
# 1 colonne 1
M.rescale_col(12 + len(B), 2**102)

ML = M.LLL().change_ring(QQ)
for i in range(len(B)):
    ML.rescale_col(12 + i, 1/QQ(2**70))
ML.rescale_col(12 + len(B), 1/QQ(2**102))

r = []
for r in ML.rows():
    if abs(r[-1]) == 1:
        print(r)
        print([int(x).bit_length() for x in r])
        break

seed = []
for i in range(12):
    assert 0 < r[i] < q
    assert int(r[i]).bit_length() <= 102
    print(r[i])
    seed.append(int(r[i]))

A = A0
epss = []
for j, b in enumerate(B):
    epsilon = (b - sum(a*s for a,s in zip(A, seed))) % q
    A = [((a * pow(b, i+1, q)) % q) % 2**65 for i, a in enumerate(A)]
    print(epsilon)
    epss.append(mod(epsilon,p))

char = berlekamp_massey(epss)
print(char)
print(char.roots())
for a, _ in char.roots():
    if a != 1:
        break
for x, y in zip(epss, epss[1:]):
    print("c", (y - a * x) % p)
