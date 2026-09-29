"""Reference MD5, SHA-1 and SHA-0 step functions and message expansions.

Sources, stated exactly (EXP-DIFFP-fe894e inputs.specifications):

  MD5    RFC 1321.  The committed pin at
         coordination/goals/GOAL-MD5-001/batches/BATCH-1f30fe/inputs/rfc1321-md5.txt
         is the source of the Appendix A.5 test vectors; this module is GATED on
         them by `md5_selfcheck()` in the CTL-BASE driver.  The constant table K
         is COMPUTED here from floor(abs(sin(i+1)) * 2**32) rather than
         transcribed, so no constant is populated from recollection.
  SHA-1  FIPS 180-4.  NO PINNED COPY EXISTS IN THIS REPOSITORY and the Executor
         holds no web capability (IR-10), so the implementation is written from
         the specification and GATED on the two digests declared in the frozen
         contract, which are marked `recalled` there, AND cross-checked against
         hashlib.sha1, an implementation independent of this file.
  SHA-0  FIPS 180.  ONLY the message expansion is used, and only as the
         nearby-object control (CTL-NEARBY).  NO claim is made here about SHA-0
         digest values or SHA-0 security.

Every function is pure and deterministic.  Nothing in this module performs I/O.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

MASK32 = 0xFFFFFFFF


def rotl(x: int, n: int) -> int:
    n &= 31
    x &= MASK32
    return ((x << n) | (x >> (32 - n))) & MASK32


def rotr(x: int, n: int) -> int:
    return rotl(x, (32 - (n & 31)) & 31)


def add32(*xs: int) -> int:
    t = 0
    for x in xs:
        t += x
    return t & MASK32


def sub32(a: int, b: int) -> int:
    return (a - b) & MASK32


# ---------------------------------------------------------------------------
# MD5 (RFC 1321)
# ---------------------------------------------------------------------------

# K[i] = floor(abs(sin(i+1)) * 2**32); COMPUTED, not transcribed.
MD5_K = tuple(int(abs(math.sin(i + 1)) * (2 ** 32)) & MASK32 for i in range(64))

MD5_S = (
    7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
    5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20,
    4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
    6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21,
)

MD5_IV = (0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476)


def md5_word_index(i: int) -> int:
    if i < 16:
        return i
    if i < 32:
        return (5 * i + 1) % 16
    if i < 48:
        return (3 * i + 5) % 16
    return (7 * i) % 16


def md5_f(i: int, b: int, c: int, d: int) -> int:
    if i < 16:
        return (b & c) | (~b & d) & MASK32
    if i < 32:
        return (d & b) | (~d & c) & MASK32
    if i < 48:
        return b ^ c ^ d
    return c ^ (b | (~d & MASK32))


@dataclass
class Trace:
    """One compression-function trace.

    q[i]   the NEW state word produced by step i (MD5: the updated B;
           SHA-1/SHA-0: the new A).  This is "the working state" the path
           object records per-step differences on.
    t[i]   the pre-rotation modular sum computed at step i.  Conditions are
           pinned on the bits of t (and of the outer addend), because that is
           where the carry behaviour that a differential path depends on lives.
    """
    primitive: str
    q: list[int]
    t: list[int]
    cv_in: tuple[int, ...]
    cv_out: tuple[int, ...]


def md5_compress(cv: tuple[int, int, int, int], m: list[int]) -> Trace:
    assert len(m) == 16
    a, b, c, d = cv
    q: list[int] = []
    t: list[int] = []
    for i in range(64):
        f = md5_f(i, b, c, d) & MASK32
        ti = add32(a, f, m[md5_word_index(i)], MD5_K[i])
        nb = add32(b, rotl(ti, MD5_S[i]))
        t.append(ti)
        q.append(nb)
        a, b, c, d = d, nb, b, c
    out = (add32(cv[0], a), add32(cv[1], b), add32(cv[2], c), add32(cv[3], d))
    return Trace("md5", q, t, tuple(cv), out)


def _md5_pad(msg: bytes) -> bytes:
    ml = len(msg) * 8
    msg = msg + b"\x80"
    while len(msg) % 64 != 56:
        msg += b"\x00"
    return msg + (ml & ((1 << 64) - 1)).to_bytes(8, "little")


def md5_digest(msg: bytes) -> str:
    cv = MD5_IV
    data = _md5_pad(msg)
    for off in range(0, len(data), 64):
        blk = data[off:off + 64]
        m = [int.from_bytes(blk[j:j + 4], "little") for j in range(0, 64, 4)]
        cv = md5_compress(cv, m).cv_out
    return b"".join(w.to_bytes(4, "little") for w in cv).hex()


# ---------------------------------------------------------------------------
# SHA-1 (FIPS 180-4) and SHA-0 (FIPS 180) -- expansions side by side
# ---------------------------------------------------------------------------

SHA1_IV = (0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0)
SHA1_K = (0x5A827999, 0x6ED9EBA1, 0x8F1BBCDC, 0xCA62C1D6)


def sha1_kt(i: int) -> int:
    return SHA1_K[i // 20]


def sha1_ft(i: int, b: int, c: int, d: int) -> int:
    if i < 20:
        return ((b & c) | (~b & d)) & MASK32
    if i < 40:
        return b ^ c ^ d
    if i < 60:
        return (b & c) | (b & d) | (c & d)
    return b ^ c ^ d


def sha1_expand(w16: list[int], steps: int = 80) -> list[int]:
    """SHA-1 message expansion: W[t] = ROTL1(W[t-3]^W[t-8]^W[t-14]^W[t-16])."""
    w = list(w16[:16])
    for t in range(16, steps):
        w.append(rotl(w[t - 3] ^ w[t - 8] ^ w[t - 14] ^ w[t - 16], 1))
    return w[:steps]


def sha0_expand(w16: list[int], steps: int = 80) -> list[int]:
    """SHA-0 message expansion -- NEARBY_OBJECT_CONTROL.

    Identical to SHA-1's except for the missing one-bit rotation.  Used ONLY by
    CTL-NEARBY.  No claim is made about SHA-0 digests or SHA-0 security.
    """
    w = list(w16[:16])
    for t in range(16, steps):
        w.append((w[t - 3] ^ w[t - 8] ^ w[t - 14] ^ w[t - 16]) & MASK32)
    return w[:steps]


NEARBY_OBJECT_CONTROL = "sha0_expand"


def sha1_expand_back(w: list[int], k: int) -> list[int]:
    """Extend a SHA-1 codeword k steps BACKWARD.

    Inverse of the expansion recursion:
        W[t-16] = ROTR1(W[t]) ^ W[t-3] ^ W[t-8] ^ W[t-14]
    Returns the k prepended words followed by w.  This is what makes E1's
    "same codeword read at a different offset" computable in both directions
    rather than only forward.
    """
    cur = list(w)
    for _ in range(k):
        # produce the word one position before cur[0], i.e. index -1 relative
        # to cur; it is W[t-16] for t = 15 in cur's own indexing.
        t = 15
        prev = rotr(cur[t], 1) ^ cur[t - 3] ^ cur[t - 8] ^ cur[t - 14]
        cur = [prev & MASK32] + cur
    return cur


def sha1_in_linearized_code(words: list[int]) -> bool:
    """COMPUTED, never assumed (contract sha1_variant `in_linearized_code`)."""
    if len(words) < 16:
        return False
    return sha1_expand(words[:16], len(words)) == list(words)


def sha1_compress(cv: tuple[int, ...], m: list[int], expand=sha1_expand) -> Trace:
    assert len(m) == 16
    w = expand(m, 80)
    a, b, c, d, e = cv
    q: list[int] = []
    t: list[int] = []
    for i in range(80):
        ti = add32(rotl(a, 5), sha1_ft(i, b, c, d), e, w[i], sha1_kt(i))
        t.append(ti)
        q.append(ti)
        a, b, c, d, e = ti, a, rotl(b, 30), c, d
    out = tuple(add32(cv[j], v) for j, v in enumerate((a, b, c, d, e)))
    return Trace("sha1", q, t, tuple(cv), out)


def _sha1_pad(msg: bytes) -> bytes:
    ml = len(msg) * 8
    msg = msg + b"\x80"
    while len(msg) % 64 != 56:
        msg += b"\x00"
    return msg + (ml & ((1 << 64) - 1)).to_bytes(8, "big")


def sha1_digest(msg: bytes) -> str:
    cv = SHA1_IV
    data = _sha1_pad(msg)
    for off in range(0, len(data), 64):
        blk = data[off:off + 64]
        m = [int.from_bytes(blk[j:j + 4], "big") for j in range(0, 64, 4)]
        cv = sha1_compress(cv, m).cv_out
    return b"".join(w.to_bytes(4, "big") for w in cv).hex()


COMPRESS = {"md5": md5_compress, "sha1": sha1_compress}
STEPS = {"md5": 64, "sha1": 80}
CV_WORDS = {"md5": 4, "sha1": 5}
DEFAULT_IV = {"md5": MD5_IV, "sha1": SHA1_IV}
