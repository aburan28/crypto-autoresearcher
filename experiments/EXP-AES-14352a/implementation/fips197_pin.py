"""FIPS-197 known-answer pin against aes_reduced.py for EXP-AES-14352a."""

from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

EXPECTED_MODULE_SHA256 = (
    "2c76f3e5db83ec2500ce1010a392a135869d8b9dd1a534af817e06f15babb447"
)

# Recalled FIPS-197 Appendix B / C vectors (same as GOAL-AES-001 pin receipt).
# Provenance: recalled | cross-checked against aes_reduced + optional openssl/pycryptodome.
KATS = [
    {
        "vector_id": "FIPS197-AppB-AES128",
        "key_hex": "2b7e151628aed2a6abf7158809cf4f3c",
        "plaintext_hex": "3243f6a8885a308d313198a2e0370734",
        "expected_ciphertext_hex_recalled": "3925841d02dc09fbdc118597196a0b32",
        "key_bits": 128,
        "rounds": 10,
    },
    {
        "vector_id": "FIPS197-AppC1-AES128",
        "key_hex": "000102030405060708090a0b0c0d0e0f",
        "plaintext_hex": "00112233445566778899aabbccddeeff",
        "expected_ciphertext_hex_recalled": "69c4e0d86a7b0430d8cdb78070b4c55a",
        "key_bits": 128,
        "rounds": 10,
    },
    {
        "vector_id": "FIPS197-AppC2-AES192",
        "key_hex": "000102030405060708090a0b0c0d0e0f1011121314151617",
        "plaintext_hex": "00112233445566778899aabbccddeeff",
        "expected_ciphertext_hex_recalled": "dda97ca4864cdfe06eaf70a0ec0d7191",
        "key_bits": 192,
        "rounds": 12,
    },
    {
        "vector_id": "FIPS197-AppC3-AES256",
        "key_hex": "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f",
        "plaintext_hex": "00112233445566778899aabbccddeeff",
        "expected_ciphertext_hex_recalled": "8ea2b7ca516745bfeafc49904b496089",
        "key_bits": 256,
        "rounds": 14,
    },
]


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _try_pycryptodome(key: bytes, pt: bytes) -> Optional[str]:
    try:
        from Crypto.Cipher import AES as PCAES  # type: ignore
    except Exception:
        try:
            from Cryptodome.Cipher import AES as PCAES  # type: ignore
        except Exception:
            return None
    cipher = PCAES.new(key, PCAES.MODE_ECB)
    return cipher.encrypt(pt).hex()


def _try_openssl(key: bytes, pt: bytes) -> Optional[Dict[str, Any]]:
    key_bits = len(key) * 8
    if key_bits == 128:
        cipher = "aes-128-ecb"
    elif key_bits == 192:
        cipher = "aes-192-ecb"
    elif key_bits == 256:
        cipher = "aes-256-ecb"
    else:
        return None
    try:
        with tempfile.TemporaryDirectory() as td:
            tin = Path(td) / "in.bin"
            tout = Path(td) / "out.bin"
            tin.write_bytes(pt)
            proc = subprocess.run(
                [
                    "openssl",
                    "enc",
                    f"-{cipher}",
                    "-K",
                    key.hex(),
                    "-nopad",
                    "-in",
                    str(tin),
                    "-out",
                    str(tout),
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if proc.returncode != 0:
                return {
                    "ok": False,
                    "exit_status": proc.returncode,
                    "stderr": proc.stderr,
                }
            return {
                "ok": True,
                "ciphertext_hex": tout.read_bytes().hex(),
                "exit_status": 0,
                "stderr": proc.stderr,
            }
    except FileNotFoundError:
        return None
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": str(exc)}


def run_fips197_pin(aes_module_path: Path, aes_cls) -> Dict[str, Any]:
    file_sha = _file_sha256(aes_module_path)
    module_attr = getattr(aes_cls, "__module__", None)
    # Prefer imported MODULE_SHA256 if available
    try:
        import importlib

        mod = importlib.import_module(aes_cls.__module__)
        module_sha_attr = getattr(mod, "MODULE_SHA256", None)
    except Exception:
        module_sha_attr = None

    vectors: List[Dict[str, Any]] = []
    all_pass = True
    sha_ok = file_sha == EXPECTED_MODULE_SHA256

    for kat in KATS:
        key = bytes.fromhex(kat["key_hex"])
        pt = bytes.fromhex(kat["plaintext_hex"])
        expected = kat["expected_ciphertext_hex_recalled"]
        aes = aes_cls(key, rounds=kat["rounds"], final_mix_columns=False)
        ct = aes.encrypt_block(pt).hex()
        pt_back = aes.decrypt_block(bytes.fromhex(ct)).hex()
        pc = _try_pycryptodome(key, pt)
        ossl = _try_openssl(key, pt)
        ossl_hex = None
        if isinstance(ossl, dict) and ossl.get("ok"):
            ossl_hex = ossl.get("ciphertext_hex")

        comparisons = {
            "aes_reduced_vs_recalled_expected": ct == expected,
            "decrypt_roundtrip": pt_back == kat["plaintext_hex"],
            "is_fips197_flag": bool(getattr(aes, "is_fips197", False)),
        }
        if pc is not None:
            comparisons["aes_reduced_vs_pycryptodome"] = ct == pc
        if ossl_hex is not None:
            comparisons["aes_reduced_vs_openssl"] = ct == ossl_hex

        verdict = all(comparisons.values()) and comparisons["is_fips197_flag"]
        if not verdict:
            all_pass = False
        vectors.append(
            {
                **kat,
                "aes_reduced_ciphertext_hex": ct,
                "aes_reduced_decrypted_hex": pt_back,
                "pycryptodome_ciphertext_hex": pc,
                "openssl": ossl,
                "comparisons": comparisons,
                "verdict": "pass" if verdict else "fail",
            }
        )

    pin_pass = sha_ok and all_pass
    return {
        "experiment_id": "EXP-AES-14352a",
        "aes_reduced_path": str(aes_module_path),
        "file_sha256": file_sha,
        "expected_module_sha256": EXPECTED_MODULE_SHA256,
        "module_sha256_attr": module_sha_attr,
        "sha256_match": sha_ok,
        "vectors": vectors,
        "independent_checks_attempted": {
            "pycryptodome": any(v.get("pycryptodome_ciphertext_hex") for v in vectors),
            "openssl": any(
                isinstance(v.get("openssl"), dict) and v["openssl"].get("ok")
                for v in vectors
            ),
        },
        "pin_verdict": "pass" if pin_pass else "fail",
        "note": (
            "Expected ciphertext hex values are recalled FIPS-197 Appendix "
            "vectors; agreement with aes_reduced + optional independent "
            "implementations is the pin. Document text not re-read in this session."
        ),
    }


def write_pin_receipt(receipt: Dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
