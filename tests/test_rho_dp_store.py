"""Unit tests for DP store encoding helpers (no live Postgres required)."""
from __future__ import annotations

from harness.rho_dp_store import (
    be_bytes_to_int,
    coeff_bytes,
    int_to_be_bytes,
    point_key_ecc2k_limbs,
    point_key_from_affine,
    point_key_sec1_compressed,
)


def test_sec1_compressed_parity():
    even = point_key_sec1_compressed(0xABC, 0x10, 2)
    odd = point_key_sec1_compressed(0xABC, 0x11, 2)
    assert even[0] == 0x02 and odd[0] == 0x03
    assert even[1:] == odd[1:] == bytes.fromhex("0abc")


def test_point_key_from_affine_rejects_infinity():
    try:
        point_key_from_affine(None, 17)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_coeff_bytes_mod_n():
    assert coeff_bytes(18, 17) == coeff_bytes(1, 17)
    assert be_bytes_to_int(coeff_bytes(0x1234)) == 0x1234


def test_ecc2k_limb_roundtrip_shape():
    pk = point_key_ecc2k_limbs(1, (1 << 130) + 7)
    assert len(pk) == 48
    assert int_to_be_bytes(0) == b"\x00"
