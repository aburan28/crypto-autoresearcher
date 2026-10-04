"""Program-local P_RD and F_fp predicates for EXP-AES-14352a Stage 1.

Byte numbering: AES state column-major 0..15.
Predicates are PROGRAM-LOCAL; do not claim published ACC/ACP figures.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

# Diagonals D (Shin POINTER / AES literature)
D: Tuple[frozenset[int], ...] = (
    frozenset({0, 5, 10, 15}),  # D0
    frozenset({1, 6, 11, 12}),  # D1
    frozenset({2, 7, 8, 13}),  # D2
    frozenset({3, 4, 9, 14}),  # D3
)

# Inverse diagonals ID
ID: Tuple[frozenset[int], ...] = (
    frozenset({3, 6, 9, 12}),  # ID0
    frozenset({2, 5, 8, 15}),  # ID1
    frozenset({1, 4, 11, 14}),  # ID2
    frozenset({0, 7, 10, 13}),  # ID3
)

D0 = D[0]
INACTIVE = frozenset(range(16)) - D0


@dataclass
class QueryCounter:
    plaintext_queries: int = 0
    ciphertext_queries: int = 0
    encrypt_ops: int = 0
    decrypt_ops: int = 0

    def charge_encrypt(self, n: int = 1) -> None:
        self.encrypt_ops += n
        self.plaintext_queries += n

    def charge_decrypt(self, n: int = 1) -> None:
        self.decrypt_ops += n
        self.ciphertext_queries += n

    def as_dict(self) -> Dict[str, int]:
        return {
            "plaintext_queries": self.plaintext_queries,
            "ciphertext_queries": self.ciphertext_queries,
            "encrypt_ops": self.encrypt_ops,
            "decrypt_ops": self.decrypt_ops,
            "r_round_aes_ops": self.encrypt_ops + self.decrypt_ops,
        }


@dataclass
class PredicateResult:
    accept: bool
    inactive_diagonals: List[int] = field(default_factory=list)
    idj: Optional[int] = None


def xor16(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def inactive_diagonals(diff: bytes) -> List[int]:
    """Return indices k where diagonal Dk is fully inactive (all 4 bytes zero)."""
    out: List[int] = []
    for k, positions in enumerate(D):
        if all(diff[i] == 0 for i in positions):
            out.append(k)
    return out


def exchange_idj(c1: bytes, c2: bytes, idj: int) -> Tuple[bytes, bytes]:
    """Exchange values on inverse-diagonal IDj between C1 and C2 → (C3, C4)."""
    positions = ID[idj % 4]
    b1 = bytearray(c1)
    b2 = bytearray(c2)
    for i in positions:
        b1[i], b2[i] = b2[i], b1[i]
    return bytes(b1), bytes(b2)


def build_structure_plaintext(
    d0_values: Sequence[int],
    inactive_constants: bytes,
    free_byte_index: int = 0,
    free_byte_value: int = 0,
) -> bytes:
    """Build a 16-byte plaintext: D0 from template + free byte; inactive fixed.

    d0_values: length-4 template for sorted(D0) positions; the free_byte_index
    position within sorted(D0) is overwritten by free_byte_value.
    inactive_constants: 16 bytes (only inactive positions used).
    """
    if len(inactive_constants) != 16:
        raise ValueError("inactive_constants must be 16 bytes")
    d0_sorted = sorted(D0)
    if free_byte_index < 0 or free_byte_index >= 4:
        raise ValueError("free_byte_index must be in 0..3")
    out = bytearray(16)
    for i in INACTIVE:
        out[i] = inactive_constants[i]
    vals = list(d0_values)
    if len(vals) != 4:
        raise ValueError("d0_values must have length 4")
    vals[free_byte_index] = free_byte_value & 0xFF
    for pos, val in zip(d0_sorted, vals):
        out[pos] = val & 0xFF
    return bytes(out)


def structure_texts(
    d0_fixed: Sequence[int],
    inactive_constants: bytes,
    structure_size: int = 256,
    free_byte_index: int = 0,
) -> List[bytes]:
    """Enumerate structure_size plaintexts by varying one D0 byte (default state[0])."""
    if structure_size > 256:
        raise ValueError("pilot structure_size max 256 for single-byte free")
    return [
        build_structure_plaintext(
            d0_fixed, inactive_constants, free_byte_index, v
        )
        for v in range(structure_size)
    ]


def check_p_rd_for_idj(
    aes,
    p1: bytes,
    p2: bytes,
    idj: int,
    counter: Optional[QueryCounter] = None,
) -> PredicateResult:
    """Encrypt pair, exchange IDj, decrypt, test inactive-diagonal predicate."""
    if p1 == p2:
        return PredicateResult(accept=False, inactive_diagonals=[], idj=idj)
    c1 = aes.encrypt_block(p1)
    c2 = aes.encrypt_block(p2)
    if counter is not None:
        counter.charge_encrypt(2)
    c3, c4 = exchange_idj(c1, c2, idj)
    p3 = aes.decrypt_block(c3)
    p4 = aes.decrypt_block(c4)
    if counter is not None:
        counter.charge_decrypt(2)
    diffs = xor16(p3, p4)
    inactive = inactive_diagonals(diffs)
    return PredicateResult(accept=len(inactive) > 0, inactive_diagonals=inactive, idj=idj)


def friend_plaintext(
    base: bytes,
    inactive_constants: bytes,
) -> bytes:
    """Friend: same D0 bytes as base; inactive diagonals from inactive_constants."""
    out = bytearray(base)
    for i in INACTIVE:
        out[i] = inactive_constants[i]
    return bytes(out)


def check_f_fp_for_idj(
    aes,
    p1: bytes,
    p2: bytes,
    idj: int,
    friend_inactive_list: Sequence[bytes],
    counter: Optional[QueryCounter] = None,
) -> bool:
    """F_fp ACCEPT iff ALL friends in the list succeed under the same IDj predicate."""
    if not friend_inactive_list:
        return False
    for inactive in friend_inactive_list:
        f1 = friend_plaintext(p1, inactive)
        f2 = friend_plaintext(p2, inactive)
        # Friends must differ from base on inactive diagonals
        if f1 == p1 and f2 == p2:
            return False
        res = check_p_rd_for_idj(aes, f1, f2, idj, counter=counter)
        if not res.accept:
            return False
    return True


def evaluate_pair(
    aes,
    p1: bytes,
    p2: bytes,
    idj_subset: Sequence[int],
    friend_inactive_list: Sequence[bytes],
    *,
    aligned: bool = True,
    counter: Optional[QueryCounter] = None,
) -> Dict[str, object]:
    """Evaluate P_RD alone and joint P_RD∧F_fp over idj_subset.

    If aligned=False (sibling), use IDj' = (IDj + 1) mod 4 for exchanges.
    """
    p_rd_accept = False
    joint_accept = False
    details: List[Dict[str, object]] = []
    for idj in idj_subset:
        use_idj = idj if aligned else (idj + 1) % 4
        pr = check_p_rd_for_idj(aes, p1, p2, use_idj, counter=counter)
        fp = False
        if pr.accept:
            p_rd_accept = True
            fp = check_f_fp_for_idj(
                aes, p1, p2, use_idj, friend_inactive_list, counter=counter
            )
            if fp:
                joint_accept = True
        details.append(
            {
                "idj_declared": idj,
                "idj_used": use_idj,
                "aligned": aligned,
                "p_rd": pr.accept,
                "inactive_diagonals": pr.inactive_diagonals,
                "f_fp": fp,
            }
        )
    return {
        "p_rd_accept": p_rd_accept,
        "joint_accept": joint_accept,
        "details": details,
    }
