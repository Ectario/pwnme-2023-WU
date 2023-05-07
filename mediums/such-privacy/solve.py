import struct
import random
from z3 import *

MASK = 0xFFFFFFFFFFFFFFFF

# Symbolic execution of xs128p
def sym_xs128p(slvr, sym_state0, sym_state1, generated):
    s1 = sym_state0 
    s0 = sym_state1 
    s1 ^= (s1 << 23)
    s1 ^= LShR(s1, 17)
    s1 ^= s0
    s1 ^= LShR(s0, 26) 
    sym_state0 = sym_state1
    sym_state1 = s1
    calc = sym_state0
    
    condition = Bool('c%d' % int(generated * random.random()))
    impl = Implies(condition, LShR(calc, 12) == int(generated))

    slvr.add(impl)
    return sym_state0, sym_state1, [condition]

def to_double(out):
    double_bits = (out >> 12) | 0x3FF0000000000000
    double = struct.unpack('d', struct.pack('<Q', double_bits))[0] - 1
    return double


def main():
    dubs = [
        0.9994088125992486,
        0.8258436683972712,
        0.9529505815730472,
        0.08190908488360704,
        0.549252440965251
    ]
    
    dubs = dubs[::-1]

    # from the doubles, generate known piece of the original uint64 
    generated = []
    for idx in range(len(dubs)):
        recovered = struct.unpack('<Q', struct.pack('d', dubs[idx] + 1))[0] & (MASK >> 12)
        generated.append(recovered)

    # setup symbolic state for xorshift128+
    ostate0, ostate1 = BitVecs('ostate0 ostate1', 64)
    sym_state0 = ostate0
    sym_state1 = ostate1
    slvr = Solver()
    conditions = []

    # run symbolic xorshift128+ algorithm for 5 iterations
    # using the recovered numbers as constraints
    for ea in range(len(dubs)):
        sym_state0, sym_state1, ret_conditions = sym_xs128p(slvr, sym_state0, sym_state1, generated[ea])
        conditions += ret_conditions

    if slvr.check(conditions) == sat:
        # get a solved state
        m = slvr.model()
        state0 = m[ostate0].as_long()
        state1 = m[ostate1].as_long()
        slvr.add(Or(ostate0 != m[ostate0], ostate1 != m[ostate1]))
        if slvr.check(conditions) == sat:
            print('WARNING: multiple solutions found! use more dubs!')
        print('state', state0, state1)

        print("next Math.random() =", to_double(state0))
    else:
        print('UNSAT')

if __name__ == "__main__":
    main()
