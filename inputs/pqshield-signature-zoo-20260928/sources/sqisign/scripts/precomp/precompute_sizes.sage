#!/usr/bin/env sage
proof.all(False)  # faster

from sage.misc.banner import require_version
if not require_version(9, 8, print_message=True):
    exit('')

################################################################

from parameters import f, p, hash_iterations, security_bits, response_bits, challenge_bits, ibz_num_limbs

################################################################

logp = p.nbits()  # == ceil(log(p,2)) for a prime; the latter fails at 256-bit precision for near-2^n p

defs = dict()

SECURITY_BITS = security_bits
RESPONSE_LENGTH = response_bits
RESPONSE_BYTES = (RESPONSE_LENGTH + 9) // 8
CHALLENGE_BITS = challenge_bits
CHALLENGE_BYTES = (challenge_bits//8)

fpsz = (logp + 7) // 8
fp2sz = 2 * fpsz
defs['SECURITY_BITS'] = SECURITY_BITS
defs['CHALLENGE_BITS'] = CHALLENGE_BITS
defs['RESPONSE_BITS'] = RESPONSE_LENGTH
defs['RESPONSE_BYTES'] = RESPONSE_BYTES
defs['HASH_ITERATIONS'] = hash_iterations
defs['FP_ENCODED_BYTES'] = fpsz
defs['FP2_ENCODED_BYTES'] = fp2sz
defs['CHALLENGE_BYTES'] = CHALLENGE_BYTES

defs['EC_CURVE_ENCODED_BYTES'] = fp2sz  # just the A
defs['EC_POINT_ENCODED_BYTES'] = fp2sz  # just the x
defs['EC_BASIS_ENCODED_BYTES'] = 3 * defs['EC_POINT_ENCODED_BYTES']

defs['PUBLICKEY_BYTES'] = defs['EC_CURVE_ENCODED_BYTES'] + 1  # extra byte for hint
defs['SECRETKEY_BYTES'] = defs['PUBLICKEY_BYTES'] + 3*defs['FP_ENCODED_BYTES'] + 4*CHALLENGE_BYTES
defs['SIGNATURE_BYTES'] = defs['EC_CURVE_ENCODED_BYTES'] + 4*RESPONSE_BYTES + CHALLENGE_BYTES + 1 + 1

size_privkey = defs['SECRETKEY_BYTES']
size_pubkey = defs['PUBLICKEY_BYTES']
size_signature = defs['SIGNATURE_BYTES']

word_defs = dict()
word_defs['IBZ_NLIMBS'] = ibz_num_limbs

import os  # add_parameter_set: variant from cwd
variant = os.path.basename(os.getcwd())
algname = f'SQIsign_{variant}'

################################################################

with open('include/encoded_sizes.h','w') as hfile:
    print('#ifndef ENCODED_SIZES_H', file=hfile)
    print('#define ENCODED_SIZES_H', file=hfile)
    print('#include <tutil.h>', file=hfile)
    for k,v in defs.items():
        v = ZZ(v)
        print(f'#define {k} {v}', file=hfile) 
    print("#if 0", file=hfile)
    for sz in (16, 32, 64):
        print(f"#elif RADIX == {sz}",file=hfile)
        for k,v in word_defs.items():
            t = v*(64//sz)
            print(v,t,sz)
            print(f'#define {k} {t}'.format(k,t), file=hfile)
    print("#endif",file=hfile)
    print("#endif",file=hfile)

################################################################

api = f'''
// SPDX-License-Identifier: Apache-2.0

#ifndef api_h
#define api_h

#include <sqisign_namespace.h>

#define CRYPTO_SECRETKEYBYTES {size_privkey}
#define CRYPTO_PUBLICKEYBYTES {size_pubkey}
#define CRYPTO_BYTES {size_signature}

#define CRYPTO_ALGNAME "{algname}"

#if defined(ENABLE_SIGN)
SQISIGN_API
int crypto_sign_keypair(unsigned char *pk, unsigned char *sk);

SQISIGN_API
int crypto_sign_signature(unsigned char *sig,
                          unsigned long long *siglen,
                          const unsigned char *m,
                          unsigned long long mlen,
                          const unsigned char *sk);

SQISIGN_API
int crypto_sign(unsigned char *sm,
                unsigned long long *smlen,
                const unsigned char *m,
                unsigned long long mlen,
                const unsigned char *sk);
#endif

SQISIGN_API
int crypto_sign_verify(const unsigned char *sig,
                       unsigned long long siglen,
                       const unsigned char *m,
                       unsigned long long mlen,
                       const unsigned char *pk);

SQISIGN_API
int crypto_sign_open(unsigned char *m,
                     unsigned long long *mlen,
                     const unsigned char *sm,
                     unsigned long long smlen,
                     const unsigned char *pk);

#endif /* api_h */
'''.strip()

with open(f'../../../nistapi/{variant}/api.h', 'w') as f:
    print(api, file=f)

################################################################
# fp_constants.h — field/order limb layout. The ref NWORDS_FIELD must equal the
# modarith limb count, so read it from the generated field code (authoritative).

import re, glob

def _field_nlimbs(word_size):
    for path in sorted(glob.glob(f'../../../gf/ref/{variant}/fp_*_{word_size}.inc')):
        m = re.search(r'#define\s+Nlimbs\s+(\d+)', open(path).read())
        if m:
            return int(m.group(1))
    raise FileNotFoundError(f'no Nlimbs in ../../../gf/ref/{variant}/fp_*_{word_size}.inc')

order32 = (logp + 31) // 32
order64 = (logp + 63) // 64
log2p = (int(logp) - 1).bit_length()  # ceil(log2(logp)), integer-exact

with open('include/fp_constants.h', 'w') as hfile:
    hfile.write(f'''#if RADIX == 32
#if defined(SQISIGN_GF_IMPL_SAT32)
#define NWORDS_FIELD {order32}
#else
#define NWORDS_FIELD {_field_nlimbs(32)}
#endif
#define NWORDS_ORDER {order32}
#elif RADIX == 64
#if defined(SQISIGN_GF_IMPL_SAT64)
#define NWORDS_FIELD {order64}
#else
#define NWORDS_FIELD {_field_nlimbs(64)}
#endif
#define NWORDS_ORDER {order64}
#endif
#define BITS {order64 * 64}
#define LOG2P {log2p}
''')

