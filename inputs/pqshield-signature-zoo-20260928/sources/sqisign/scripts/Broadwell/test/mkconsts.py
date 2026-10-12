import sys
c, t = int(sys.argv[1]), int(sys.argv[2])
p = c*(1<<t) - 1
N = (p.bit_length()+63)//64
def limbs(v): return ", ".join("0x%016xULL" % ((v >> (64*i)) & (2**64-1)) for i in range(N))
print('#include <stdint.h>')
print('const uint64_t p[%d]  = { %s };' % (N, limbs(p)))
print('const uint64_t p2[%d] = { %s };' % (N, limbs(2*p)))
print('const uint64_t R2[%d] = { %s };' % (N, limbs(pow(1 << (64*N), 2, p))))
