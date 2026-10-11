#!/usr/bin/env python3
"""Regression tests for the EXP-SCURVE-647ade v3 sorted-root verifier."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import yaml


sys.path.insert(0, str(Path(__file__).resolve().parent))
import p192_cm_sorted_root as root


REPOSITORY = Path(__file__).resolve().parent.parent
AMENDMENT = (
    REPOSITORY
    / "experiments"
    / root.EXPERIMENT_ID
    / "amendments"
    / "v2_to_v3.yaml"
)


def fixture_members() -> list[bytes]:
    vectors = [
        [0] * 13,
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, -1, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]
    return sorted(root.encode_member(vector) for vector in vectors)


class EncodingContractTests(unittest.TestCase):
    def test_domain_and_dimensions_are_frozen(self) -> None:
        self.assertEqual(root.DOMAIN, b"p192-cm-canonical-set-root/v1\0")
        self.assertEqual(len(root.DOMAIN), 30)
        self.assertEqual(root.VECTOR_LENGTH, 13)
        self.assertEqual(root.MEMBER_SIZE, 26)
        self.assertEqual(root.EXPECTED_STREAM_BYTES, 129_333_048)

    def test_signed_i16_little_endian_encoding_is_exact(self) -> None:
        vector = [-32768, 32767, -1, 0] + [0] * 9
        encoded = root.encode_member(vector)
        self.assertEqual(len(encoded), 26)
        self.assertEqual(encoded[:8].hex(), "0080ff7fffff0000")
        self.assertEqual(root.decode_member(encoded), tuple(vector))

    def test_wrong_vector_length_and_i16_overflow_are_rejected(self) -> None:
        with self.assertRaisesRegex(root.VerificationError, "expected 13"):
            root.encode_member([0] * 12)
        with self.assertRaisesRegex(root.VerificationError, "outside signed i16"):
            root.encode_member([32768] + [0] * 12)

    def test_hard_coded_cross_implementation_small_set_root(self) -> None:
        # Generated independently with Node.js crypto + Buffer.writeInt16LE.
        self.assertEqual(
            root.root_for_sorted_members(fixture_members()),
            "a582b4872385f6a075bb3e77b5b3bc42c5245a0377fe7e14738c1b1b057811a0",
        )

    def test_duplicate_and_unsigned_byte_disorder_are_rejected(self) -> None:
        members = fixture_members()
        with self.assertRaisesRegex(root.VerificationError, "duplicate"):
            root.root_for_sorted_members([members[0], members[0]])
        with self.assertRaisesRegex(root.VerificationError, "out-of-order"):
            root.root_for_sorted_members([members[1], members[0]])


class AmendmentBindingTests(unittest.TestCase):
    def test_amendment_and_verifier_share_the_exact_contract(self) -> None:
        amendment = yaml.safe_load(AMENDMENT.read_text(encoding="utf-8"))[
            "protocol_amendment"
        ]
        self.assertEqual(amendment["experiment_id"], root.EXPERIMENT_ID)
        self.assertEqual(amendment["version_from"], 2)
        self.assertEqual(amendment["version_to"], root.PROTOCOL_VERSION)
        self.assertEqual(amendment["affected_runs"], [])
        changes = "\n".join(amendment["changes"])
        for frozen_text in (
            "4,974,348",
            "129,333,048",
            'ASCII("p192-cm-canonical-set-root/v1") || 0x00',
            "u64LE(member_count)",
            root.LEGACY_BLAKE3_DIAGNOSTIC,
            "legacy_canonical_set_digest",
            "canonical_set_root_sha256",
        ):
            with self.subTest(frozen_text):
                self.assertIn(frozen_text, changes)


class SemanticMembershipTests(unittest.TestCase):
    def test_negative_ramified_exponent_is_rejected(self) -> None:
        with self.assertRaisesRegex(root.VerificationError, "negative ramified"):
            root.validate_member(root.encode_member([-1] + [0] * 12))

    def test_first_nonzero_split_must_be_positive(self) -> None:
        with self.assertRaisesRegex(root.VerificationError, "first-nonzero"):
            root.validate_member(root.encode_member([0, 0, 0, -1] + [0] * 9))
        accepted = [0, 0, 0, 1, -1] + [0] * 8
        self.assertEqual(root.validate_member(root.encode_member(accepted)), tuple(accepted))

    def test_norm_boundary_is_exact(self) -> None:
        root.validate_member(root.encode_member([20] + [0] * 12))
        with self.assertRaisesRegex(root.VerificationError, r"2\^48"):
            root.validate_member(root.encode_member([21] + [0] * 12))


class StreamVerificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary.name)
        self.members = fixture_members()
        self.expected_root = (
            "a582b4872385f6a075bb3e77b5b3bc42c5245a0377fe7e14738c1b1b057811a0"
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write(self, name: str, members: list[bytes]) -> Path:
        path = self.directory / name
        path.write_bytes(b"".join(members))
        return path

    def test_valid_stream_binds_count_bytes_and_expected_root(self) -> None:
        path = self.write("members.bin", self.members)
        result = root.verify_sorted_stream(
            path,
            expected_count=len(self.members),
            expected_root=self.expected_root,
        )
        self.assertEqual(result.member_count, 4)
        self.assertEqual(result.stream_bytes, 104)
        self.assertEqual(result.zero_member_count, 1)
        self.assertEqual(result.canonical_set_root_sha256, self.expected_root)

    def test_stream_rejects_count_truncation_order_duplicates_and_missing_zero(self) -> None:
        path = self.write("count.bin", self.members)
        with self.assertRaisesRegex(root.VerificationError, "expected 5"):
            root.verify_sorted_stream(path, expected_count=5)

        truncated = self.directory / "truncated.bin"
        truncated.write_bytes(b"x" * 27)
        with self.assertRaisesRegex(root.VerificationError, "not divisible"):
            root.verify_sorted_stream(truncated, expected_count=1)

        disorder = self.write("disorder.bin", [self.members[1], self.members[0]])
        with self.assertRaisesRegex(root.VerificationError, "out-of-order"):
            root.verify_sorted_stream(disorder, expected_count=2)

        duplicate = self.write("duplicate.bin", [self.members[0], self.members[0]])
        with self.assertRaisesRegex(root.VerificationError, "duplicate"):
            root.verify_sorted_stream(duplicate, expected_count=2)

        no_zero = self.write("no-zero.bin", self.members[1:])
        with self.assertRaisesRegex(root.VerificationError, "all-zero"):
            root.verify_sorted_stream(no_zero, expected_count=3)

    def test_pair_requires_equal_roots(self) -> None:
        forward = self.write("forward.bin", self.members)
        reverse = self.write("reverse.bin", self.members)
        report = root.verify_pair(
            forward,
            reverse,
            expected_count=4,
            expected_root=self.expected_root,
        )
        self.assertTrue(report["roots_match"])
        self.assertEqual(report["legacy_digest_role"],
                         "producer diagnostic only; not recomputed or authoritative")

        replacement = root.encode_member([2] + [0] * 12)
        changed = sorted(self.members[:-1] + [replacement])
        different = self.write("different.bin", changed)
        with self.assertRaisesRegex(root.VerificationError, "roots differ"):
            root.verify_pair(forward, different, expected_count=4)

    def test_pair_rejects_one_file_or_hardlink_as_two_traversals(self) -> None:
        forward = self.write("forward.bin", self.members)
        with self.assertRaisesRegex(root.VerificationError, "distinct files"):
            root.verify_pair(forward, forward, expected_count=4)
        hardlink = self.directory / "hardlink.bin"
        hardlink.hardlink_to(forward)
        with self.assertRaisesRegex(root.VerificationError, "hardlink"):
            root.verify_pair(forward, hardlink, expected_count=4)

    def test_expected_root_format_and_value_are_rejected_before_acceptance(self) -> None:
        path = self.write("members.bin", self.members)
        with self.assertRaisesRegex(root.VerificationError, "lowercase"):
            root.verify_sorted_stream(path, expected_count=4, expected_root="A" * 64)
        with self.assertRaisesRegex(root.VerificationError, "does not match"):
            root.verify_sorted_stream(path, expected_count=4, expected_root="0" * 64)


if __name__ == "__main__":
    unittest.main()
