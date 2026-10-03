#!/usr/bin/env python3
import sys, itertools, os, re, glob
from math import ceil, floor, log
import sage.all
from parameters import ibz_num_limbs


def _ref_field_radix(word_size):
    """Radix modarith chose for the current variant's reference field code.

    Read straight from the generated gf field file so it always matches the
    runtime field arithmetic, for any prime — no per-prime table needed. Run
    from the variant's precomp dir (src/precomp/ref/<variant>), as the precomp
    sage scripts are."""
    if word_size == 16:
        return 13  # SQIsign has no 16-bit field impl; the RADIX==16 branch is never compiled
    variant = os.path.basename(os.getcwd())
    pattern = os.path.join('..', '..', '..', 'gf', 'ref', variant, f'fp_*_{word_size}.inc')
    for path in sorted(glob.glob(pattern)):
        m = re.search(r'#define\s+Radix\s+(\d+)', open(path).read())
        if m:
            return int(m.group(1))
    raise ValueError(f'could not read field radix for word size {word_size} from '
                     f'{pattern}; is the gf/ref/{variant} field code generated?')

class Ibz:
    def __init__(self, v):
        self.v = int(v)
    def _literal(self, sz):
        val = int(self.v)
        bit_len = val.bit_length()+1
        num_limbs = (bit_len + sz-1) // sz if val else 0
        negative_bit = bit_len * num_limbs
        sgn = val < 0
        if sgn: val += (1 << negative_bit) #esures the value is positive
        limbs = [(val >> sz*i) & (2**sz-1) for i in range(num_limbs or 1)]
        if sgn: limbs[num_limbs-1] |= (1 << sz) #recover the negative-valued bit if needed
        limbs = limbs + [0 for _ in range (0,ibz_num_limbs*(64//sz)-len(limbs))]
        for l in limbs: 
            assert(l < (2**sz))
        data = {
                '.bitlen': str(bit_len),
                '.limbs': '{' + ','.join(map(hex,limbs)) + '}',
            }
        return '{'+ ','.join(f'{k} = {v}' for k,v in data.items()) + '}'

class FpEl:
    ref_p5248_radix_map  = { 16: 13, 32: 29, 64: 51 }
    ref_p65376_radix_map = { 16: 13, 32: 28, 64: 55 }
    ref_p27500_radix_map = { 16: 13, 32: 29, 64: 57 }
    def __init__(self, n, p, montgomery=True):
        self.n = n
        self.p = p
        self.montgomery = montgomery
    def __get_radix(self, word_size, arith=None):
        if arith == "ref" or arith is None:
            # read the radix modarith wrote into the field file
            return _ref_field_radix(word_size)
        elif arith == "broadwell":
            return word_size
        raise ValueError(f'Invalid arithmetic implementation type \"{arith}\"')
    def _literal(self, sz, arith=None):
        radix = self.__get_radix(sz, arith=arith)
        l = 1 + floor(log(self.p, 2**radix))
        # If we're using Montgomery representation, we need to multiply
        # by the Montgomery factor R = 2^nw (n = limb number, w = radix)
        if self.montgomery:
            R = 2**(radix * ceil(log(self.p, 2**radix)))
        else:
            R = 1
        el = (self.n * R) % self.p
        vs = [(int(el) >> radix*i) % 2**radix for i in range(l)]
        return '{' + ', '.join(map(hex, vs)) + '}'

class Object:
    def __init__(self, ty, name, obj):
        if '[' in ty:
            idx = ty.index('[')
            depth = ty.count('[]')
            def rec(os, d):
                assert d >= 0
                if not d:
                    return ()
                assert isinstance(os,list) or isinstance(os,tuple)
                r, = {rec(o, d-1) for o in os}
                return (len(os),) + r
            dims = rec(obj, depth)
            self.ty = ty[:idx], ''.join(f'[{d}]' for d in dims)
        else:
            self.ty = ty, ''
        self.name = name
        self.obj = obj

    def _declaration(self):
        return f'extern const {self.ty[0]} {self.name}{self.ty[1]};'

    def _literal(self):
        def rec(obj):
            if isinstance(obj, int):
                if obj < 256: return str(obj)
                else: return hex(obj)
            if isinstance(obj, sage.all.Integer):
                if obj < 256: return str(obj)
                else: return hex(obj)
            if isinstance(obj, Ibz):
                literal = "\n#if 0"
                for sz in (16, 32, 64):
                    literal += f"\n#elif RADIX == {sz}"
                    literal += f"\n{obj._literal(sz)}"
                return literal + "\n#endif\n"
            if isinstance(obj, FpEl):
                literal = "\n#if 0"
                for sz in (16, 32, 64):
                    literal += f"\n#elif RADIX == {sz}"
                    if sz in (32, 64):
                        # 'broadwell' means saturated limbs (radix = word size); at 32 bits that is the
                        # layout of the m4-modarith armv7e-m code, guarded by SQISIGN_GF_IMPL_SAT32.
                        guard = "SQISIGN_GF_IMPL_SAT64" if sz == 64 else "SQISIGN_GF_IMPL_SAT32"
                        literal += f"\n#if defined({guard})"
                        literal += f"\n{obj._literal(sz, 'broadwell')}"
                        literal += "\n#else"
                        literal += f"\n{obj._literal(sz, 'ref')}"
                        literal += "\n#endif"
                    else:
                        literal += f"\n{obj._literal(sz, 'ref')}"
                return literal + "\n#endif\n"
            if isinstance(obj, list) or isinstance(obj, tuple):
                return '{' + ', '.join(map(rec, obj)) + '}'
            if isinstance(obj, str):
                return obj
            raise NotImplementedError(f'unknown type {type(obj)} in Formatter')
        return rec(self.obj)

    def _definition(self):
        return f'const {self.ty[0]} {self.name}{self.ty[1]} = ' + self._literal() + ';'

class ObjectFormatter:
    def __init__(self, objs):
        self.objs = objs

    def header(self, file=None):
        for obj in self.objs:
            assert isinstance(obj, Object)
            print(obj._declaration(), file=file)

    def implementation(self, file=None):
        for obj in self.objs:
            assert isinstance(obj, Object)
            print(obj._definition(), file=file)
