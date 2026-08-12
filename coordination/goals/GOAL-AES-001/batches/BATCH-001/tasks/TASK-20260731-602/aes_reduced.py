#!/usr/bin/env python3
"""aes_reduced.py -- reduced-round-capable AES ground truth for GOAL-AES-001.

Task:    TASK-20260731-602 (executor)
Scope:   instrument only. This module makes NO cryptanalytic claim.
Ceiling: any result obtained with this module is toy / reduced-round tier
         (RQ-AES-001 claim_tier_ceiling). Nothing here supports a statement
         about full-round or deployed AES.

=============================================================================
INDEPENDENCE
=============================================================================
This module imports nothing outside the Python standard library. It never
calls pycryptodome, the openssl CLI, or any other AES implementation on the
computation path. Cross-implementation agreement (see check_vectors.py /
vector_check_receipt.json) is therefore meaningful in the sense required by
docs/claims-and-verification.md: the code paths are independent.

The S-box, its inverse, the MixColumns matrices and the Rcon constants are
DERIVED here from the GF(2^8) field definition rather than transcribed from a
table. This is deliberate: a transcribed table is a recall artifact, a derived
table is a computation whose correctness is demonstrated by agreement with two
independent reference implementations at full rounds.

=============================================================================
REDUCED-ROUND CONVENTION  (READ THIS BEFORE USING THE MODULE)
=============================================================================
FIPS-197 defines AES only at Nr = 10/12/14 rounds for 128/192/256-bit keys.
It does NOT define what "r-round AES" means for r < Nr. The convention below
is a CHOICE made by this module. It is the single most important parameter of
this campaign: a reduced-round result obtained under a silently different
convention is an artifact about a different cipher, not a fact about AES.

Adopted convention -- `AES(key, rounds=r)` with default `final_mix_columns=False`:

    s  = P
    s ^= RK[0]                                   # initial AddRoundKey
    for i in 1 .. r-1:                           # "full" rounds
        s = SubBytes(s)
        s = ShiftRows(s)
        s = MixColumns(s)
        s ^= RK[i]
    s = SubBytes(s)                              # round r == the final round
    s = ShiftRows(s)
    # MixColumns OMITTED in round r
    s ^= RK[r]
    return s

Three decisions, stated explicitly:

  (C1) FINAL ROUND DROPS MixColumns. Round r -- whatever r is -- is the final
       round and omits MixColumns, exactly as FIPS-197's round Nr does. At
       r = Nr this reproduces FIPS-197 AES bit-for-bit (verified, see the
       receipt). Set `final_mix_columns=True` to obtain the OTHER variant, in
       which all r rounds are full rounds including round r. That variant is
       NOT FIPS-197 AES at r = Nr and the constructor is explicit about it.

  (C2) THE INITIAL AddRoundKey IS NOT COUNTED AS A ROUND. It is key whitening.
       So `rounds=4` means four S-box layers, and RK[0] is applied before the
       first of them. `rounds=0` is legal and denotes whitening only.

  (C3) ROUND KEYS COME FROM THE UNTRUNCATED FIPS-197 KEY SCHEDULE FOR THE
       KEY SIZE, indexed 0..r. The key schedule is a function of the key
       length (Nk), NOT of the reduced round count: for a 128-bit key the
       expansion is the standard one and the r-round cipher uses its first
       r+1 round keys, discarding the rest. The schedule is NOT re-derived,
       re-seeded, or shortened for the truncated cipher, and Rcon indices are
       NOT renumbered. (Note the consequence for AES-192/256: because Nk > 4,
       round key RK[i] of the reduced cipher is byte-for-byte the RK[i] of the
       full cipher, so a reduced AES-256 at r rounds still consumes key
       material from the standard schedule in the standard order.)

Which convention does the literature use? UNVERIFIED-FROM-MEMORY. No primary
source is reachable from this environment (csrc.nist.gov, eprint.iacr.org and
arxiv.org are blocked under this harness's network policy), so the following
is recollection and must be treated as such: reduced-round AES cryptanalysis
papers conventionally mean (C1)+(C2)+(C3) -- r rounds, last round without
MixColumns, whitening key not counted -- and papers that keep MixColumns in
the last round normally say so explicitly, because dropping it is a linear,
key-dependent-only change that most attacks absorb into the final key guess.
That recollection has NOT been checked against any read document. Any later
comparison against a recalled literature number MUST state, in the same
sentence, both that the baseline is unverified-from-memory AND which of the
two conventions the comparison assumes. If a later result depends on the
choice, that dependence is a finding to report, not a detail to smooth over.

=============================================================================
NULL-OBJECT CONTROLS
=============================================================================
`docs/inventor-protocol.md` requires that any reported signal be measured
against a null object of the same shape before it is believed. This module
supports that directly: any component can be replaced while keeping the rest
of the cipher and the key schedule intact.

    AES(key, rounds=4).with_random_sbox(seed=1234)     # non-AES S-box
    AES(key, rounds=4).with_identity_sbox()            # no S-box at all
    AES(key, rounds=4).with_identity_mixcolumns()      # no column mixing
    AES(key, rounds=4).with_random_mixcolumns(seed=99) # random invertible MDS-less matrix
    AES(key, rounds=4).with_identity_shiftrows()

All replacements are seeded and the seed is retained in `.provenance` so a
control run is reproducible from the receipt. Replacement components are
always invertible, so `decrypt_block` remains exact for controls.
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass, field, replace
from typing import Callable, Dict, List, Optional, Sequence, Tuple

__all__ = [
    "AES",
    "Components",
    "GF",
    "aes_sbox",
    "aes_inv_sbox",
    "key_expansion",
    "MODULE_SHA256",
]

# ---------------------------------------------------------------------------
# GF(2^8) with the AES modulus x^8 + x^4 + x^3 + x + 1 = 0x11B
# ---------------------------------------------------------------------------


class GF:
    """Arithmetic in GF(2^8) with the AES reduction polynomial 0x11B."""

    MODULUS = 0x11B

    @staticmethod
    def mul(a: int, b: int) -> int:
        a &= 0xFF
        b &= 0xFF
        r = 0
        while b:
            if b & 1:
                r ^= a
            b >>= 1
            a <<= 1
            if a & 0x100:
                a ^= GF.MODULUS
        return r & 0xFF

    @staticmethod
    def inv(a: int) -> int:
        """Multiplicative inverse; inv(0) = 0 by the AES convention."""
        a &= 0xFF
        if a == 0:
            return 0
        # a^254 == a^-1 in GF(2^8)^*
        r = 1
        for _ in range(254):
            r = GF.mul(r, a)
        return r


def _affine(b: int) -> int:
    """AES S-box affine map: b_i' = b_i ^ b_{i+4} ^ b_{i+5} ^ b_{i+6} ^ b_{i+7} ^ c_i,
    indices mod 8, c = 0x63."""
    out = 0
    for i in range(8):
        bit = (
            ((b >> i) & 1)
            ^ ((b >> ((i + 4) % 8)) & 1)
            ^ ((b >> ((i + 5) % 8)) & 1)
            ^ ((b >> ((i + 6) % 8)) & 1)
            ^ ((b >> ((i + 7) % 8)) & 1)
            ^ ((0x63 >> i) & 1)
        )
        out |= bit << i
    return out


def _build_sbox() -> Tuple[Tuple[int, ...], Tuple[int, ...]]:
    sbox = tuple(_affine(GF.inv(x)) for x in range(256))
    inv = [0] * 256
    for x, y in enumerate(sbox):
        inv[y] = x
    return sbox, tuple(inv)


_SBOX, _INV_SBOX = _build_sbox()


def aes_sbox() -> Tuple[int, ...]:
    """The derived FIPS-197 S-box as a 256-tuple."""
    return _SBOX


def aes_inv_sbox() -> Tuple[int, ...]:
    return _INV_SBOX


# MixColumns matrices, circulant over GF(2^8).
AES_MIX = (
    (0x02, 0x03, 0x01, 0x01),
    (0x01, 0x02, 0x03, 0x01),
    (0x01, 0x01, 0x02, 0x03),
    (0x03, 0x01, 0x01, 0x02),
)
AES_INV_MIX = (
    (0x0E, 0x0B, 0x0D, 0x09),
    (0x09, 0x0E, 0x0B, 0x0D),
    (0x0D, 0x09, 0x0E, 0x0B),
    (0x0B, 0x0D, 0x09, 0x0E),
)
IDENTITY_MIX = tuple(tuple(1 if i == j else 0 for j in range(4)) for i in range(4))


def mat_mul(a: Sequence[Sequence[int]], b: Sequence[Sequence[int]]) -> Tuple[Tuple[int, ...], ...]:
    n = len(a)
    return tuple(
        tuple(
            _xor_all(GF.mul(a[i][k], b[k][j]) for k in range(n))
            for j in range(n)
        )
        for i in range(n)
    )


def _xor_all(vals) -> int:
    r = 0
    for v in vals:
        r ^= v
    return r


def mat_inv(m: Sequence[Sequence[int]]) -> Optional[Tuple[Tuple[int, ...], ...]]:
    """Gauss-Jordan inverse of an n x n matrix over GF(2^8). None if singular."""
    n = len(m)
    aug = [list(row) + [1 if i == j else 0 for j in range(n)] for i, row in enumerate(m)]
    for col in range(n):
        piv = next((r for r in range(col, n) if aug[r][col] != 0), None)
        if piv is None:
            return None
        aug[col], aug[piv] = aug[piv], aug[col]
        pinv = GF.inv(aug[col][col])
        aug[col] = [GF.mul(pinv, v) for v in aug[col]]
        for r in range(n):
            if r != col and aug[r][col]:
                f = aug[r][col]
                aug[r] = [x ^ GF.mul(f, y) for x, y in zip(aug[r], aug[col])]
    return tuple(tuple(row[n:]) for row in aug)


# Verify at import time that the derived inverse matrix really inverts AES_MIX.
assert mat_mul(AES_MIX, AES_INV_MIX) == IDENTITY_MIX, "AES MixColumns matrices inconsistent"


def rcon(i: int) -> int:
    """Rcon[i] = x^(i-1) in GF(2^8), for i >= 1."""
    v = 1
    for _ in range(i - 1):
        v = GF.mul(v, 0x02)
    return v


# ---------------------------------------------------------------------------
# Components (the replaceable pieces, for null-object controls)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Components:
    """The replaceable primitive components of the cipher.

    `sbox` is used in the DATA path. `key_sbox` is used in the KEY SCHEDULE.
    They are separate on purpose: replacing the data-path S-box while leaving
    the key schedule at AES is a different null object from replacing both,
    and a distinguisher experiment must be able to say which it did.
    """

    sbox: Tuple[int, ...] = _SBOX
    inv_sbox: Tuple[int, ...] = _INV_SBOX
    key_sbox: Tuple[int, ...] = _SBOX
    mix: Tuple[Tuple[int, ...], ...] = AES_MIX
    inv_mix: Tuple[Tuple[int, ...], ...] = AES_INV_MIX
    shift_offsets: Tuple[int, int, int, int] = (0, 1, 2, 3)
    label: str = "aes"

    def describe(self) -> Dict[str, object]:
        return {
            "label": self.label,
            "sbox_is_aes": self.sbox == _SBOX,
            "key_sbox_is_aes": self.key_sbox == _SBOX,
            "mix_is_aes": self.mix == AES_MIX,
            "shift_offsets": list(self.shift_offsets),
            "sbox_sha256": hashlib.sha256(bytes(self.sbox)).hexdigest(),
            "mix_flat": [x for row in self.mix for x in row],
        }


def random_permutation_sbox(seed: int) -> Tuple[Tuple[int, ...], Tuple[int, ...]]:
    """A seeded random bijection on 8 bits, with its inverse."""
    rng = random.Random(seed)
    perm = list(range(256))
    rng.shuffle(perm)
    inv = [0] * 256
    for x, y in enumerate(perm):
        inv[y] = x
    return tuple(perm), tuple(inv)


def random_invertible_mix(seed: int) -> Tuple[Tuple[Tuple[int, ...], ...], Tuple[Tuple[int, ...], ...]]:
    """A seeded random invertible 4x4 matrix over GF(2^8), with its inverse.

    Random, hence generically NOT MDS: branch number is not controlled. That is
    the point of a null object -- it has the same shape as MixColumns without
    its diffusion guarantee.
    """
    rng = random.Random(seed)
    for _ in range(1000):
        m = tuple(tuple(rng.randrange(256) for _ in range(4)) for _ in range(4))
        inv = mat_inv(m)
        if inv is not None:
            return m, inv
    raise RuntimeError("failed to sample an invertible matrix")  # pragma: no cover


# ---------------------------------------------------------------------------
# Key schedule
# ---------------------------------------------------------------------------


def key_expansion(key: bytes, n_round_keys: int, key_sbox: Tuple[int, ...] = _SBOX) -> List[bytes]:
    """FIPS-197 key expansion, returning `n_round_keys` 16-byte round keys.

    Convention (C3): the schedule is the standard one for the key length. The
    caller asks for the first `n_round_keys` of it; nothing is renumbered.
    """
    nk = len(key) // 4
    if nk not in (4, 6, 8):
        raise ValueError(f"key must be 16, 24 or 32 bytes, got {len(key)}")
    total_words = 4 * n_round_keys
    w: List[List[int]] = [list(key[4 * i: 4 * i + 4]) for i in range(nk)]
    for i in range(nk, total_words):
        temp = list(w[i - 1])
        if i % nk == 0:
            temp = temp[1:] + temp[:1]                       # RotWord
            temp = [key_sbox[b] for b in temp]               # SubWord
            temp[0] ^= rcon(i // nk)                         # Rcon
        elif nk == 8 and i % nk == 4:
            temp = [key_sbox[b] for b in temp]               # SubWord only, AES-256
        w.append([a ^ b for a, b in zip(w[i - nk], temp)])
    return [bytes(b for word in w[4 * r: 4 * r + 4] for b in word) for r in range(n_round_keys)]


# ---------------------------------------------------------------------------
# State transformations.  State layout: bytes[0..15] in FIPS-197 column-major
# order, i.e. state[row][col] = data[col * 4 + row].
# ---------------------------------------------------------------------------


def sub_bytes(s: bytes, sbox: Tuple[int, ...]) -> bytes:
    return bytes(sbox[b] for b in s)


def shift_rows(s: bytes, offs: Tuple[int, int, int, int]) -> bytes:
    out = bytearray(16)
    for r in range(4):
        k = offs[r]
        for c in range(4):
            out[c * 4 + r] = s[((c + k) % 4) * 4 + r]
    return bytes(out)


def inv_shift_rows(s: bytes, offs: Tuple[int, int, int, int]) -> bytes:
    out = bytearray(16)
    for r in range(4):
        k = offs[r]
        for c in range(4):
            out[((c + k) % 4) * 4 + r] = s[c * 4 + r]
    return bytes(out)


def mix_columns(s: bytes, m: Sequence[Sequence[int]]) -> bytes:
    out = bytearray(16)
    for c in range(4):
        col = s[4 * c: 4 * c + 4]
        for r in range(4):
            out[4 * c + r] = _xor_all(GF.mul(m[r][k], col[k]) for k in range(4))
    return bytes(out)


def add_round_key(s: bytes, rk: bytes) -> bytes:
    return bytes(a ^ b for a, b in zip(s, rk))


# ---------------------------------------------------------------------------
# The cipher
# ---------------------------------------------------------------------------

FULL_ROUNDS = {16: 10, 24: 12, 32: 14}


class AES:
    """Reduced-round-capable AES.

    Parameters
    ----------
    key : bytes
        16, 24 or 32 bytes.
    rounds : int or None
        Number of rounds under convention (C2): the initial AddRoundKey is NOT
        one of them. None means the FIPS-197 value for the key size
        (10 / 12 / 14). 0 <= rounds is required; rounds may exceed the FIPS-197
        value, in which case the key schedule is simply expanded further (that
        is an extrapolation, not AES, and `is_fips197` reports False).
    final_mix_columns : bool
        False (default, convention C1): round `rounds` omits MixColumns, as
        FIPS-197's last round does. True: every round is a full round. At
        rounds == FULL_ROUNDS[len(key)] only False reproduces FIPS-197 AES.
    components : Components
        Replaceable primitives, for null-object controls.
    """

    def __init__(
        self,
        key: bytes,
        rounds: Optional[int] = None,
        final_mix_columns: bool = False,
        components: Components = Components(),
    ) -> None:
        key = bytes(key)
        if len(key) not in FULL_ROUNDS:
            raise ValueError(f"key must be 16, 24 or 32 bytes, got {len(key)}")
        self.key = key
        self.key_bits = len(key) * 8
        self.full_rounds = FULL_ROUNDS[len(key)]
        self.rounds = self.full_rounds if rounds is None else int(rounds)
        if self.rounds < 0:
            raise ValueError("rounds must be >= 0")
        self.final_mix_columns = bool(final_mix_columns)
        self.components = components
        self.round_keys = key_expansion(key, self.rounds + 1, components.key_sbox)
        self.provenance: Dict[str, object] = {"base": "aes", "controls": []}

    # -- identity of the configured cipher ---------------------------------

    @property
    def is_fips197(self) -> bool:
        """True iff this exact configuration is FIPS-197 AES."""
        return (
            self.rounds == self.full_rounds
            and not self.final_mix_columns
            and self.components.sbox == _SBOX
            and self.components.key_sbox == _SBOX
            and self.components.mix == AES_MIX
            and self.components.shift_offsets == (0, 1, 2, 3)
        )

    def describe(self) -> Dict[str, object]:
        return {
            "key_bits": self.key_bits,
            "rounds": self.rounds,
            "full_rounds": self.full_rounds,
            "final_mix_columns": self.final_mix_columns,
            "initial_addroundkey_counted_as_round": False,
            "key_schedule": "untruncated FIPS-197 expansion for the key size; "
                            "first rounds+1 round keys used (convention C3)",
            "is_fips197": self.is_fips197,
            "components": self.components.describe(),
            "provenance": self.provenance,
        }

    # -- null-object controls ---------------------------------------------

    def _derive(self, components: Components, control: Dict[str, object]) -> "AES":
        new = AES(self.key, self.rounds, self.final_mix_columns, components)
        new.provenance = {
            "base": self.provenance["base"],
            "controls": list(self.provenance["controls"]) + [control],
        }
        return new

    def with_random_sbox(self, seed: int, also_key_schedule: bool = False) -> "AES":
        sb, inv = random_permutation_sbox(seed)
        c = replace(
            self.components,
            sbox=sb,
            inv_sbox=inv,
            key_sbox=sb if also_key_schedule else self.components.key_sbox,
            label=f"{self.components.label}+random_sbox(seed={seed})",
        )
        return self._derive(c, {"kind": "random_sbox", "seed": seed,
                                "also_key_schedule": also_key_schedule})

    def with_identity_sbox(self, also_key_schedule: bool = False) -> "AES":
        ident = tuple(range(256))
        c = replace(
            self.components,
            sbox=ident,
            inv_sbox=ident,
            key_sbox=ident if also_key_schedule else self.components.key_sbox,
            label=f"{self.components.label}+identity_sbox",
        )
        return self._derive(c, {"kind": "identity_sbox",
                                "also_key_schedule": also_key_schedule})

    def with_identity_mixcolumns(self) -> "AES":
        c = replace(self.components, mix=IDENTITY_MIX, inv_mix=IDENTITY_MIX,
                    label=f"{self.components.label}+identity_mixcolumns")
        return self._derive(c, {"kind": "identity_mixcolumns"})

    def with_random_mixcolumns(self, seed: int) -> "AES":
        m, inv = random_invertible_mix(seed)
        c = replace(self.components, mix=m, inv_mix=inv,
                    label=f"{self.components.label}+random_mixcolumns(seed={seed})")
        return self._derive(c, {"kind": "random_mixcolumns", "seed": seed})

    def with_identity_shiftrows(self) -> "AES":
        c = replace(self.components, shift_offsets=(0, 0, 0, 0),
                    label=f"{self.components.label}+identity_shiftrows")
        return self._derive(c, {"kind": "identity_shiftrows"})

    def with_components(self, components: Components, note: str = "custom") -> "AES":
        return self._derive(components, {"kind": "custom_components", "note": note})

    # -- round machinery ---------------------------------------------------

    def _is_final_round(self, i: int) -> bool:
        return i == self.rounds and not self.final_mix_columns

    def round_forward(self, s: bytes, i: int) -> bytes:
        """Apply round i (1-based) to state s. Round `self.rounds` is final."""
        if not 1 <= i <= self.rounds:
            raise ValueError(f"round index {i} outside 1..{self.rounds}")
        c = self.components
        s = sub_bytes(s, c.sbox)
        s = shift_rows(s, c.shift_offsets)
        if not self._is_final_round(i):
            s = mix_columns(s, c.mix)
        return add_round_key(s, self.round_keys[i])

    def round_backward(self, s: bytes, i: int) -> bytes:
        """Invert round i (1-based)."""
        if not 1 <= i <= self.rounds:
            raise ValueError(f"round index {i} outside 1..{self.rounds}")
        c = self.components
        s = add_round_key(s, self.round_keys[i])
        if not self._is_final_round(i):
            s = mix_columns(s, c.inv_mix)
        s = inv_shift_rows(s, c.shift_offsets)
        return sub_bytes(s, c.inv_sbox)

    # -- partial encryption ------------------------------------------------
    #
    # State indexing for partial evaluation:
    #   level 0  = state after the initial AddRoundKey (i.e. P ^ RK[0])
    #   level i  = state after round i has been applied, for 1 <= i <= rounds
    # so encrypt_partial(x, 0, rounds) == the ciphertext, and
    #    encrypt_partial(P ^ RK0, a, b) chains: level a -> level b.

    def encrypt_partial(self, state: bytes, start_level: int, end_level: int) -> bytes:
        """Encrypt from `start_level` to `end_level` (see level indexing above)."""
        if not 0 <= start_level <= end_level <= self.rounds:
            raise ValueError(
                f"require 0 <= start <= end <= rounds ({start_level},{end_level},{self.rounds})"
            )
        s = bytes(state)
        for i in range(start_level + 1, end_level + 1):
            s = self.round_forward(s, i)
        return s

    def decrypt_partial(self, state: bytes, start_level: int, end_level: int) -> bytes:
        """Inverse of encrypt_partial: from `start_level` back to `end_level`."""
        if not 0 <= end_level <= start_level <= self.rounds:
            raise ValueError(
                f"require 0 <= end <= start <= rounds ({start_level},{end_level},{self.rounds})"
            )
        s = bytes(state)
        for i in range(start_level, end_level, -1):
            s = self.round_backward(s, i)
        return s

    def whiten(self, plaintext: bytes) -> bytes:
        """P -> level 0 (apply the initial AddRoundKey)."""
        return add_round_key(bytes(plaintext), self.round_keys[0])

    def unwhiten(self, level0: bytes) -> bytes:
        return add_round_key(bytes(level0), self.round_keys[0])

    # -- full block API ----------------------------------------------------

    def encrypt_block(self, plaintext: bytes) -> bytes:
        if len(plaintext) != 16:
            raise ValueError("block must be 16 bytes")
        return self.encrypt_partial(self.whiten(plaintext), 0, self.rounds)

    def decrypt_block(self, ciphertext: bytes) -> bytes:
        if len(ciphertext) != 16:
            raise ValueError("block must be 16 bytes")
        return self.unwhiten(self.decrypt_partial(bytes(ciphertext), self.rounds, 0))

    def encrypt_ecb(self, data: bytes) -> bytes:
        if len(data) % 16:
            raise ValueError("length must be a multiple of 16 (no padding is applied)")
        return b"".join(self.encrypt_block(data[i:i + 16]) for i in range(0, len(data), 16))

    def decrypt_ecb(self, data: bytes) -> bytes:
        if len(data) % 16:
            raise ValueError("length must be a multiple of 16 (no padding is applied)")
        return b"".join(self.decrypt_block(data[i:i + 16]) for i in range(0, len(data), 16))

    # -- intermediate states ----------------------------------------------

    def trace(self, plaintext: bytes) -> List[Tuple[str, bytes]]:
        """Every intermediate state of the encryption, labelled.

        Labels: 'input', 'ark0', and per round i: 'r{i}.sub', 'r{i}.shift',
        'r{i}.mix' (absent in the final round when MixColumns is dropped),
        'r{i}.ark'. 'r{i}.ark' == level i of the partial-encryption indexing.
        """
        c = self.components
        out: List[Tuple[str, bytes]] = [("input", bytes(plaintext))]
        s = self.whiten(plaintext)
        out.append(("ark0", s))
        for i in range(1, self.rounds + 1):
            s = sub_bytes(s, c.sbox)
            out.append((f"r{i}.sub", s))
            s = shift_rows(s, c.shift_offsets)
            out.append((f"r{i}.shift", s))
            if not self._is_final_round(i):
                s = mix_columns(s, c.mix)
                out.append((f"r{i}.mix", s))
            s = add_round_key(s, self.round_keys[i])
            out.append((f"r{i}.ark", s))
        return out

    def state_at(self, plaintext: bytes, label: str) -> bytes:
        for lab, st in self.trace(plaintext):
            if lab == label:
                return st
        raise KeyError(f"no such intermediate state: {label!r}")


# ---------------------------------------------------------------------------
# Self-hash, so a receipt can pin the exact source that produced it.
# ---------------------------------------------------------------------------

def _self_sha256() -> str:
    try:
        with open(__file__, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()
    except OSError:  # pragma: no cover
        return "unavailable"


MODULE_SHA256 = _self_sha256()


if __name__ == "__main__":  # pragma: no cover
    import json
    import sys

    a = AES(bytes(range(16)))
    ct = a.encrypt_block(bytes.fromhex("00112233445566778899aabbccddeeff"))
    print(json.dumps({
        "module_sha256": MODULE_SHA256,
        "sbox_sha256": hashlib.sha256(bytes(aes_sbox())).hexdigest(),
        "aes128_full_round_demo_ct": ct.hex(),
        "config": a.describe(),
    }, indent=2, default=str))
    sys.exit(0)
