#!/usr/bin/env python3
"""Static and byte-level checks for the non-executing Role-2 BOX-0 interface.

This checker performs no elliptic-curve search and never authorizes execution.
It closes the interface package and exposes helpers that the native producer,
independent verifier, and supervisor conformance tests can use.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import re
import selectors
import signal
import stat
import struct
import subprocess
import sys
import time
import tomllib
import types
import unicodedata
from pathlib import Path
from typing import Any, Iterable

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research/p192-weighted-cm-20261007-v2-role2-box0-interface"
ADDENDUM = ROOT / "experiments/EXP-SCURVE-1a8daf/amendments/v2_addendum_role2_box0_interface.yaml"
OVERLAY = PACKAGE / "run-family.role2-box0-interface.yaml"
ARTIFACT_SCHEMA = PACKAGE / "schemas/role2-artifacts.schema.json"
DECISION_SCHEMA = PACKAGE / "schemas/role2-dispatch-decision.schema.json"
SUMS = PACKAGE / "SHA256SUMS"

PROTECTED_PROTOCOL_PATHS = {
    "specification.v2.yaml": ROOT / "experiments/EXP-SCURVE-1a8daf/amendments/specification.v2.yaml",
    "protocol-amendment.v2.yaml": ROOT / "experiments/EXP-SCURVE-1a8daf/amendments/protocol-amendment.v2.yaml",
    "run-family.yaml": ROOT / "research/p192-weighted-cm-20261007-v2/run-family.yaml",
    "v2_addendum_role1_interface.yaml": ROOT / "experiments/EXP-SCURVE-1a8daf/amendments/v2_addendum_role1_interface.yaml",
    "v2_addendum_role2_box0_interface.yaml": ADDENDUM,
    "README.md": PACKAGE / "README.md",
    "check_role2_box0_interface.py": PACKAGE / "check_role2_box0_interface.py",
    "run-family.role2-box0-interface.yaml": OVERLAY,
    "role2-artifacts.schema.json": ARTIFACT_SCHEMA,
    "role2-dispatch-decision.schema.json": DECISION_SCHEMA,
    "SHA256SUMS": SUMS,
    "test_p192_wcm_role2_interface.py": ROOT / "tests/test_p192_wcm_role2_interface.py",
    ".gitkeep": ROOT / "experiments/EXP-SCURVE-1a8daf/controls/.gitkeep",
    "runs/.gitkeep": ROOT / "experiments/EXP-SCURVE-1a8daf/runs/.gitkeep",
    "role1-interface/README.md": ROOT / "research/p192-weighted-cm-20261007-v2-role1-interface/README.md",
    "role1-interface/SHA256SUMS": ROOT / "research/p192-weighted-cm-20261007-v2-role1-interface/SHA256SUMS",
    "role1-interface/check_role1_interface.py": ROOT / "research/p192-weighted-cm-20261007-v2-role1-interface/check_role1_interface.py",
    "role1-interface/run-family.role1-interface.yaml": ROOT / "research/p192-weighted-cm-20261007-v2-role1-interface/run-family.role1-interface.yaml",
    "role1-interface/role1-artifacts.schema.json": ROOT / "research/p192-weighted-cm-20261007-v2-role1-interface/schemas/role1-artifacts.schema.json",
    "role1-interface/role1-dispatch-decision.schema.json": ROOT / "research/p192-weighted-cm-20261007-v2-role1-interface/schemas/role1-dispatch-decision.schema.json",
    "role1-interface/test_p192_wcm_role1_interface.py": ROOT / "tests/test_p192_wcm_role1_interface.py",
}
PROTECTED_PROTOCOL_RELATIVE_PATHS = {
    name: str(path.relative_to(ROOT)) for name, path in PROTECTED_PROTOCOL_PATHS.items()
}
PROTOCOL_REPOSITORY = "https://github.com/aburan28/crypto-autoresearcher"
DECISION_RELATIVE_DIRECTORY = Path("ledger/decisions")
EXPERIMENT_RELATIVE_DIRECTORY = Path("experiments/EXP-SCURVE-1a8daf")
RUNS_RELATIVE_DIRECTORY = EXPERIMENT_RELATIVE_DIRECTORY / "runs"
CONTROLS_RELATIVE_DIRECTORY = EXPERIMENT_RELATIVE_DIRECTORY / "controls"

EXECUTION_CONTROLS = {
    "platform": "linux",
    "host_trust_model": "trusted_local_host",
    "workspace_custody": "exclusive",
    "supervisor_raw_argv0_equals_decision_path": True,
    "supervisor_current_exe_equals_decision_path": True,
    "supervisor_proc_self_exe_hash_required": True,
    "child_open_flags": ["O_RDONLY", "O_CLOEXEC", "O_NOFOLLOW"],
    "child_memfd_flags": ["MFD_CLOEXEC", "MFD_ALLOW_SEALING"],
    "child_memfd_seals": ["F_SEAL_WRITE", "F_SEAL_GROW", "F_SEAL_SHRINK", "F_SEAL_SEAL"],
    "child_launch_path": "/proc/self/fd/<retained-exec-fd>",
    "sealed_exec_fd_paths": {
        "producer": "/proc/self/fd/40",
        "verifier": "/proc/self/fd/41",
    },
    "predecessor_snapshot_fd_paths": {
        "factor-base.json": "/proc/self/fd/50",
        "factor-base.sha256": "/proc/self/fd/51",
        "verification.json": "/proc/self/fd/52",
        "independent-verification.json": "/proc/self/fd/53",
        "independent-agreement.json": "/proc/self/fd/54",
        "independent-verifier-receipt.json": "/proc/self/fd/55",
    },
    "directory_fd_paths": {
        "experiment_parent": "/proc/self/fd/60",
        "runs_parent": "/proc/self/fd/61",
        "controls_parent": "/proc/self/fd/62",
        "run_dir": "/proc/self/fd/63",
        "control_dir": "/proc/self/fd/64",
    },
    "retained_source_descriptors_cloexec": True,
    "child_target_fd_cloexec_cleared": True,
    "child_fd_handoff_order": [
        "sealed_executable", "predecessor_snapshots", "directory_descriptors",
        "clear_target_FD_CLOEXEC", "execve_retained_proc_self_fd_path",
    ],
    "child_directory_access": "inherited_fixed_fds_and_openat_only",
    "logical_path_argv_use": "identity_labels_only_no_child_path_open",
    "source_path_recheck": "before_each_launch_and_terminal",
    "directory_io": "retained_O_DIRECTORY_O_NOFOLLOW_fds_and_fd_relative_leaves",
    "control_cleanup": "out_of_band_after_terminal_validation_and_archival_only",
}

SOURCE_BUILD_OPTIONAL_ROOT_PATHS = (
    "Cargo.toml", "rust-toolchain", "rust-toolchain.toml",
    ".cargo/config", ".cargo/config.toml",
)
FORBIDDEN_DEPENDENCY_PACKAGES = {
    "p192-weighted-cm", "p192_weighted_cm", "crypto-lib", "crypto_lib",
}
REMOVED_COMMIT_VARIABLES = [
    "P192_WCM_PROTOCOL_COMMIT", "P192_WCM_SOURCE_COMMIT",
    "P192_WCM_VERIFIER_COMMIT",
]
LOADER_OVERRIDE_PREFIXES = ("LD_", "DYLD_")
GIT_EXECUTION_POLICY = {
    "executable": "/usr/bin/git",
    "environment_cleared": True,
    "minimal_environment_only": True,
    "global_config_disabled": True,
    "system_config_disabled": True,
    "replacement_objects_disabled": True,
    "grafts_disabled": True,
    "commit_graph_disabled": True,
    "lazy_fetch_disabled": True,
    "ext_protocol_disabled": True,
    "fsmonitor_disabled": True,
    "hooks_disabled": True,
    "external_diff_disabled": True,
    "literal_pathspecs": True,
    "raw_parent_ancestry": True,
    "raw_parent_walk_commit_cap": 1000000,
}
PROTOCOL_TOPOLOGY_ENTRY_CAP = 1000000
PROTOCOL_TOPOLOGY_DEPTH_CAP = 64
PROTOCOL_TOPOLOGY_PATH_BYTES_CAP = 4096
FILESYSTEM_WALK_AGGREGATE_PATH_BYTES_CAP = 268435456
GIT_COMMAND_TIMEOUT_SECONDS = 60
GIT_COMMAND_OUTPUT_CAP = 268435456
VERIFIER_TOOL_TIMEOUT_SECONDS = 60
VERIFIER_TOOL_OUTPUT_CAP = 67108864
VERIFIER_METADATA_EXECUTION_POLICY = {
    "timeout_seconds": VERIFIER_TOOL_TIMEOUT_SECONDS,
    "stdout_byte_cap": VERIFIER_TOOL_OUTPUT_CAP,
    "stderr_byte_cap": VERIFIER_TOOL_OUTPUT_CAP,
    "stdin": "DEVNULL",
    "environment": "exact_allowlist_only",
    "start_new_session": True,
    "kill_process_group_on_timeout_or_cap": True,
}
PROTOCOL_TOPOLOGY_AGGREGATE_BLOB_BYTES_CAP = 268435456
PROTOCOL_INDEX_BYTES_CAP = 268435456
REGULAR_FILE_BYTE_CAP = 1073741824
EVIDENCE_ARTIFACT_BYTE_CAP = 536870912
SMALL_PRODUCER_ARTIFACT_BYTE_CAP = 65536
PRODUCER_TREE_BYTE_CAP = 884998144
RUN_METADATA_BYTE_CAP = 67108864
EVIDENCE_TREE_BYTE_CAP = 939524096
EVIDENCE_COMBINED_BYTE_CAP = 1879048192
COMMITTED_DISTINCT_BLOB_BYTE_CAP = 1073741824
MINIMAL_STANDALONE_GIT_CONFIG = (
    b"[core]\n"
    b"\trepositoryformatversion = 0\n"
    b"\tfilemode = true\n"
    b"\tbare = false\n"
    b"\tlogallrefupdates = true\n"
    b"\thooksPath = /dev/null\n"
)
SOURCE_SPARSE_EXACT_PATHS = (
    "Cargo.toml", "Cargo.lock", "rust-toolchain", "rust-toolchain.toml",
    ".cargo/config", ".cargo/config.toml",
)
SOURCE_SPARSE_PREFIXES = (
    "tools/p192-weighted-cm", "tools/p192-weighted-cm-verify",
    "tools/p192-weighted-cm-supervisor",
)
VERIFIER_DEPENDENCY_SCAN = {
    "forbidden_packages": ["crypto-lib", "p192-weighted-cm"],
    "prohibited_dependency_sources": [
        "path", "git", "workspace-inheritance", "patch", "replace",
        "source-replacement", "alternate-registry",
    ],
    "path_manifest_policy": "canonical_recursive_target_inspection_then_reject",
    "registry_lock_policy": "exact_crates_io_source_and_lowercase_sha256_checksum_required",
    "target_name_tables": ["package", "lib", "bin", "example", "test", "bench"],
    "scopes": [
        "dependencies", "dev-dependencies", "build-dependencies",
        "target.dependencies", "target.dev-dependencies",
        "target.build-dependencies", "workspace-inheritance", "path-aliases",
        "git-sources", "recursive-path-manifests", "package-target-names",
        "patch-replace-source-registries", "Cargo.lock-registry-checksums",
    ],
    "findings": [],
}
CRATES_IO_REGISTRY_SOURCE = "registry+https://github.com/rust-lang/crates.io-index"
VERIFIER_BUILD_TRUST_MODEL = (
    "trusted_hash_bound_cargo_rustc_and_checksum_locked_crates_io_sources"
)
VERIFIER_BUILD_ALLOWED_DIRECTIVE_PREFIXES = [
    "cargo:rerun-if-changed=",
    "cargo:rerun-if-env-changed=",
    "cargo:rustc-env=",
    "cargo:warning=",
]
VERIFIER_BUILD_FORBIDDEN_ENV_PREFIXES = [
    "RUSTC_", "RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS", "CARGO_BUILD_",
    "CARGO_TARGET_", "CARGO_PROFILE_", "CARGO_REGISTRIES_", "CARGO_REGISTRY_",
    "CARGO_SOURCE_", "CC", "CFLAGS", "CXX", "CXXFLAGS", "AR", "LDFLAGS",
]

IMMUTABLE = {
    "experiments/EXP-SCURVE-1a8daf/amendments/specification.v2.yaml":
        "34fb190ff222a37f2a626d18ba26b3e710a96c2d6eb11a5ab12dd561a4317484",
    "experiments/EXP-SCURVE-1a8daf/amendments/protocol-amendment.v2.yaml":
        "af43c91b9ab941158dd8a589fa6115f49b917b693f8cd1655f625e14a08611e8",
    "research/p192-weighted-cm-20261007-v2/run-family.yaml":
        "4bbb9c81318dceeba93734fce50dd96574513afa0c31e8c9ea8f310d91e7c6d6",
}

PAYLOAD_PATHS = (
    "experiments/EXP-SCURVE-1a8daf/amendments/v2_addendum_role2_box0_interface.yaml",
    "research/p192-weighted-cm-20261007-v2-role2-box0-interface/README.md",
    "research/p192-weighted-cm-20261007-v2-role2-box0-interface/check_role2_box0_interface.py",
    "research/p192-weighted-cm-20261007-v2-role2-box0-interface/run-family.role2-box0-interface.yaml",
    "research/p192-weighted-cm-20261007-v2-role2-box0-interface/schemas/role2-artifacts.schema.json",
    "research/p192-weighted-cm-20261007-v2-role2-box0-interface/schemas/role2-dispatch-decision.schema.json",
    "tests/test_p192_wcm_role2_interface.py",
    "experiments/EXP-SCURVE-1a8daf/controls/.gitkeep",
    "experiments/EXP-SCURVE-1a8daf/runs/.gitkeep",
)

PRODUCER_TEMPLATE = [
    "p192_weighted_cm", "sieve", "--shell", "BOX-0", "--v-max", "8",
    "--x-max-inclusive", "65536", "--factor-base",
    "PREDECESSOR_DIR/factor-base.json", "--out", "RUN_DIR",
]
VERIFIER_TEMPLATE = [
    "p192_weighted_cm_verify", "verify-shell", "--shell", "BOX-0",
    "--predecessor", "PREDECESSOR_DIR", "--source", "RUN_DIR", "--out",
    "RUN_DIR/independent-verification.json",
]
FAULT_TEMPLATE = [
    *PRODUCER_TEMPLATE[:-1], "CONTROL_DIR",
    "--control-stop-after-committed-shard", "0",
]
RESUME_TEMPLATE = [*PRODUCER_TEMPLATE[:-1], "CONTROL_DIR", "--resume"]
SUPERVISOR_TEMPLATE = [
    "p192_wcm_box0_supervisor", "--protocol-repository",
    "PROTOCOL_REPOSITORY_PATH", "--decision", "DECISION_JSON", "--producer",
    "PRODUCER_BIN", "--verifier", "VERIFIER_BIN", "--producer-repository",
    "PRODUCER_REPOSITORY_PATH", "--producer-package", "PRODUCER_PACKAGE_PATH",
    "--verifier-repository", "VERIFIER_REPOSITORY_PATH", "--verifier-package",
    "VERIFIER_PACKAGE_PATH", "--supervisor-repository",
    "SUPERVISOR_REPOSITORY_PATH", "--supervisor-package",
    "SUPERVISOR_PACKAGE_PATH",
    "--predecessor", "PREDECESSOR_DIR", "--run-dir", "RUN_DIR",
    "--control-dir", "CONTROL_DIR", "--audit-out", "AUDIT_FILE",
]

APPEND_PATHS = [
    "disposition.bin", "retained-candidates.jsonl",
    "complete-relations.jsonl", "partial-relations.jsonl",
]
CONTROL_CHECKPOINT_PATHS = [
    "disposition-schema.json", *APPEND_PATHS, "checkpoint-chain.jsonl",
]
TEMPORARY_PATHS = [
    "disposition-schema.json.tmp", "checkpoint-chain.jsonl.tmp",
    "candidate-stream.json.tmp", "verification.json.tmp",
]
PRODUCER_PATHS = [
    "candidate-stream.json", "complete-relations.jsonl",
    "partial-relations.jsonl", "disposition.bin", "disposition-schema.json",
    "checkpoint-chain.jsonl", "retained-candidates.jsonl", "verification.json",
]
SMALL_PRODUCER_PATHS = {
    "candidate-stream.json", "disposition-schema.json",
    "checkpoint-chain.jsonl", "verification.json",
}
PREDECESSOR_PATHS = [
    "factor-base.json", "factor-base.sha256", "verification.json",
    "independent-verification.json", "independent-agreement.json",
    "independent-verifier-receipt.json",
]
SEALED_EXEC_FD_PATHS = EXECUTION_CONTROLS["sealed_exec_fd_paths"]
PREDECESSOR_SNAPSHOT_FD_PATHS = EXECUTION_CONTROLS["predecessor_snapshot_fd_paths"]
DIRECTORY_FD_PATHS = EXECUTION_CONTROLS["directory_fd_paths"]
ROLE1_CHECKER_PATH = ROOT / "research/p192-weighted-cm-20261007-v2-role1-interface/check_role1_interface.py"
ROLE1_ARCHIVE_PROTECTED_RELATIVE_PATHS = (
    "experiments/EXP-SCURVE-1a8daf/amendments/protocol-amendment.v2.yaml",
    "experiments/EXP-SCURVE-1a8daf/amendments/specification.v2.yaml",
    "experiments/EXP-SCURVE-1a8daf/amendments/v2_addendum_role1_interface.yaml",
    "research/p192-weighted-cm-20261007-v2/run-family.yaml",
    "research/p192-weighted-cm-20261007-v2-role1-interface/README.md",
    "research/p192-weighted-cm-20261007-v2-role1-interface/SHA256SUMS",
    "research/p192-weighted-cm-20261007-v2-role1-interface/check_role1_interface.py",
    "research/p192-weighted-cm-20261007-v2-role1-interface/run-family.role1-interface.yaml",
    "research/p192-weighted-cm-20261007-v2-role1-interface/schemas/role1-artifacts.schema.json",
    "research/p192-weighted-cm-20261007-v2-role1-interface/schemas/role1-dispatch-decision.schema.json",
    "research/p192-weighted-cm-20261007-v2-role2-box0-interface/check_role2_box0_interface.py",
    "tests/test_p192_wcm_role1_interface.py",
)
ROLE1_REQUIRED_PATHS = [
    "identity.json", "maximal-order.json", "factor-base.json", "factor-base.sha256",
    "controls.json", "reference-box.json", "verification.json",
    "independent-verification.json", "independent-verifier-receipt.json",
    "reference-box/candidate-records.bin", "reference-box/disposition.bin",
    "reference-box/certificates.bin", "independent-agreement.json",
    "dependency-audit.json", "manifest.yaml", "command.txt", "environment.json",
    "stdout.log", "stderr.log", "raw-result.json",
]
ROLE1_PRE_EXECUTION_CUSTODY_SUFFIX = \
    "-pre-execution-repository-custody.json"
SUPERVISOR_PATHS = [
    "checkpoint-resume-control.json", "independent-agreement.json",
    "dependency-audit.json", "independent-verifier-receipt.json",
]
TERMINAL_CUSTODY_PATH = "terminal-custody.json"
CUSTODY_PATHS = [
    "manifest.yaml", "command.txt", "environment.json", "stdout.log",
    "stderr.log", "raw-result.json",
]
STAGE_PATHS = [
    *PRODUCER_PATHS, "independent-verification.json", *SUPERVISOR_PATHS,
]
BASE_REQUIRED_OUTPUTS = [
    *PRODUCER_PATHS, "independent-verification.json",
    "independent-verifier-receipt.json",
]
ADDENDUM_CHILDREN = [
    "checkpoint-resume-control.json", "independent-agreement.json",
    "dependency-audit.json", TERMINAL_CUSTODY_PATH,
]
MANIFEST_ARTIFACT_PATHS = [
    *STAGE_PATHS, "command.txt", "environment.json", "stdout.log",
    "stderr.log", "raw-result.json",
]
FAILURE_PHASE_REQUIRED_PATHS = {
    "canonical_producer": PRODUCER_PATHS,
    "restart_control": [*PRODUCER_PATHS, "checkpoint-resume-control.json"],
    "independent_verifier": [
        *PRODUCER_PATHS, "checkpoint-resume-control.json",
        "independent-verification.json",
    ],
    "agreement": [
        *PRODUCER_PATHS, "checkpoint-resume-control.json",
        "independent-verification.json", "independent-agreement.json",
    ],
    "final_custody": [
        *PRODUCER_PATHS, "checkpoint-resume-control.json",
        "independent-verification.json", "independent-agreement.json",
        "dependency-audit.json", "independent-verifier-receipt.json",
        "command.txt", "environment.json",
    ],
}
FAILURE_PHASE_ARTIFACTS = {
    "canonical_producer": PRODUCER_PATHS,
    "restart_control": ["checkpoint-resume-control.json"],
    "independent_verifier": ["independent-verification.json"],
    "agreement": ["independent-agreement.json"],
    "final_custody": [
        "dependency-audit.json", "independent-verifier-receipt.json",
        "command.txt", "environment.json",
    ],
}
FAILURE_COMPLETION_ORDER = [
    path
    for phase_paths in FAILURE_PHASE_ARTIFACTS.values()
    for path in phase_paths
]
SUPERVISOR_LAUNCH_SEQUENCE = [
    "validate_dispatch_decision_and_clean_sources",
    "retain_parent_run_control_directory_fds",
    "snapshot_and_seal_six_predecessor_files",
    "open_copy_seal_distinct_producer_and_verifier_images",
    "launch_canonical_producer",
    "close_and_snapshot_all_producer_outputs",
    "launch_fault_control_expect_75",
    "inject_and_fsync_exact_uncommitted_suffixes",
    "launch_resume_control",
    "compare_all_producer_outputs_roots_counters_prefixes",
    "write_checkpoint_resume_control",
    "launch_isolated_independent_verifier",
    "prove_producer_sources_stable",
    "rehash_predecessor_sources_and_binaries",
    "write_independent_agreement",
    "write_dependency_audit",
    "write_supervisor_receipt_after_all_stage_artifacts",
    "write_command_environment_framed_streams_raw_result_and_manifest",
    "fsync_manifest_and_run_directory",
    "terminally_recheck_self_children_source_build_inputs_predecessor_snapshots_decision_protocol_run_and_control",
    "write_and_fsync_outer_terminal_custody_seal",
]
EXPECTED_JSON_SCHEMAS = {
    "candidate-stream.json": "p192-wcm-candidate-stream-v1",
    "disposition-schema.json": "p192-wcm-disposition-schema-v1",
    "verification.json": "p192-wcm-shell-verification-v1",
    "independent-verification.json": "p192-wcm-shell-independent-verification-v1",
    "checkpoint-resume-control.json": "p192-wcm-checkpoint-resume-control-v1",
    "independent-agreement.json": "p192-wcm-shell-independent-agreement-v1",
    "dependency-audit.json": "p192-wcm-role2-dependency-audit-v1",
    "independent-verifier-receipt.json": "p192-wcm-shell-supervisor-receipt-v1",
    "environment.json": "p192-wcm-role2-box0-environment-v1",
    "manifest.yaml": "role2-run-manifest-single-run-wrapper-v1",
}
EXPECTED_JSONL_SCHEMAS = {
    "complete-relations.jsonl": "p192-wcm-complete-relation-v1",
    "partial-relations.jsonl": "p192-wcm-partial-relation-v1",
    "checkpoint-chain.jsonl": "p192-wcm-checkpoint-v1",
    "retained-candidates.jsonl": "p192-wcm-retained-candidate-v1",
}

PRODUCER_CHECKS = [
    "predecessor_role1_pass", "factor_base_canonical_and_regenerated",
    "source_provenance_bindings_consistent", "box0_iterator_complete",
    "candidate_root_recomputed", "disposition_stream_reparsed",
    "disposition_root_recomputed", "status_conservation",
    "retained_certificates_replayed", "complete_relations_replayed",
    "partial_rows_replayed", "checkpoint_chain_replayed",
    "append_prefixes_rehashed", "invalid_zero", "unresolved_zero",
]
INDEPENDENT_CHECKS = [
    "source_inventory_complete", "source_hashes_stable",
    "predecessor_hashes_replayed",
    "source_provenance_bindings_independently_replayed",
    "factor_base_independently_regenerated",
    "box0_iterator_independently_regenerated",
    "candidate_root_independently_regenerated",
    "every_disposition_independently_regenerated",
    "disposition_root_independently_regenerated",
    "every_retained_certificate_independently_reencoded",
    "every_complete_relation_independently_reencoded",
    "every_partial_row_independently_reencoded",
    "checkpoint_chain_independently_replayed",
    "append_prefixes_independently_rehashed",
    "status_conservation_independently_recomputed", "invalid_zero",
    "unresolved_zero",
]
AGREEMENT_FIELDS = [
    "protocol_commit", "producer_commit", "producer_binary_sha256",
    "factor_base_source_commit", "factor_base_sha256", "shell_id",
    "candidate_shell_sha256", "disposition_shell_sha256",
    "disposition_schema_sha256", "status_counts_sha256", "retained_candidates_sha256",
    "complete_relations_sha256", "partial_relations_sha256",
    "checkpoint_chain_sha256",
]
SUPERVISOR_CHILDREN = [
    {"role": "canonical_producer", "expected_exit_code": 0},
    {"role": "checkpoint_fault_control", "expected_exit_code": 75},
    {"role": "checkpoint_resume_control", "expected_exit_code": 0},
    {"role": "isolated_independent_verifier", "expected_exit_code": 0},
]
FAILURE_FRAME_COUNT_BOUNDS = {
    "canonical_producer": (0, 1),
    "restart_control": (1, 3),
    "independent_verifier": (3, 4),
    "agreement": (4, 4),
    "final_custody": (4, 4),
}
RUST_KEYWORDS = [
    "as", "async", "await", "break", "const", "continue", "crate", "dyn",
    "else", "enum", "extern", "false", "fn", "for", "if", "impl", "in",
    "let", "loop", "match", "mod", "move", "mut", "pub", "ref", "return",
    "self", "Self", "static", "struct", "super", "trait", "true", "type",
    "union", "unsafe", "use", "where", "while", "abstract", "become", "box",
    "do", "final", "macro", "override", "priv", "typeof", "unsized",
    "virtual", "yield", "try",
]
RUST_MULTI_OPERATORS = [
    "<<=", ">>=", "..=", "...", "::", "->", "=>", "==", "!=", "<=",
    ">=", "&&", "||", "+=", "-=", "*=", "/=", "%=", "^=", "&=", "|=",
    "<<", ">>", "..",
]
CLONE_TOKEN_DOMAIN = b"P192-WCM-RUST-TOKENS-v1\0"
CLONE_TREE_DOMAIN = b"P192-WCM-RUST-SOURCE-TREE-v1\0"
FORBIDDEN_VERIFIER_SOURCE_MARKERS = [
    b"crypto_lib", b"include!", b"#[path", b"../producer/",
    b"p192-weighted-cm =", b"crypto-lib =", b"crypto_lib =",
]

STATUS_NAMES = {
    0: "nonprimitive_duplicate", 1: "complete", 2: "one_large_prime",
    3: "two_large_prime", 4: "rejected", 5: "invalid", 6: "unresolved",
}
ZERO64 = "0" * 64
TRACE_T = 31607402316713927207482677199
GROUP_ORDER_N = 6277101735386680763835789423176059013767194773182842284081


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _role1_pre_execution_custody_relative(run_id: str) -> str:
    if re.fullmatch(r"RUN-SCURVE-[0-9a-f]{6}", run_id) is None:
        raise ValueError("Role-1 predecessor run id is not canonical")
    return str(
        CONTROLS_RELATIVE_DIRECTORY
        / f"{run_id}{ROLE1_PRE_EXECUTION_CUSTODY_SUFFIX}"
    )


def _role1_pre_execution_retained_path(
    repository: Path, run_id: str,
) -> Path:
    """Return the canonical out-of-repository receipt retained across Role-1."""
    relative = Path(_role1_pre_execution_custody_relative(run_id)).name
    return (
        repository.parent / f"{repository.name}.role1-custody" / relative
    )


def _role1_terminal_retained_path(repository: Path, run_id: str) -> Path:
    if re.fullmatch(r"RUN-SCURVE-[0-9a-f]{6}", run_id) is None:
        raise ValueError("Role-1 predecessor run id is not canonical")
    return (
        repository.parent / f"{repository.name}.role1-custody"
        / f"{run_id}-terminal-archive-repository-custody.json"
    )


def _role1_pre_execution_profile(
    decision_path_relative: str, predecessor_run_id: str,
) -> dict[str, Any]:
    """Return the decision-independent sealed D1 profile used before Role-1."""
    custody_relative = _role1_pre_execution_custody_relative(
        predecessor_run_id,
    )
    run_relative = str(RUNS_RELATIVE_DIRECTORY / predecessor_run_id)
    exact = sorted({
        *ROLE1_ARCHIVE_PROTECTED_RELATIVE_PATHS,
        str(RUNS_RELATIVE_DIRECTORY / ".gitkeep"),
        str(CONTROLS_RELATIVE_DIRECTORY / ".gitkeep"),
        decision_path_relative,
    })
    return {
        "schema": "p192-wcm-sealed-selective-worktree-profile-v1",
        "profile_id": "role1_pre_execution_decision_v1",
        "mode": "sealed_full_index_skip_worktree_v1",
        "materialized_exact_paths": exact,
        "materialized_subtree_prefixes": [run_relative],
        "required_existing_subtree_prefixes": [],
        "mutable_output_subtree_prefixes": [run_relative],
        "mutable_output_exact_paths": [custody_relative],
        "index_policy": (
            "uppercase_H_materialized_uppercase_S_omitted_stage0_full_index"
        ),
        "omitted_special_entry_policy": (
            "mode120000_and_160000_inert_absent_S_only"
        ),
        "preparation_metadata_terminal_state": "absent",
    }


def _role1_terminal_archive_profile(
    decision_path_relative: str, predecessor_run_id: str,
) -> dict[str, Any]:
    custody_relative = _role1_pre_execution_custody_relative(
        predecessor_run_id,
    )
    run_relative = str(RUNS_RELATIVE_DIRECTORY / predecessor_run_id)
    exact = sorted({
        *ROLE1_ARCHIVE_PROTECTED_RELATIVE_PATHS,
        str(RUNS_RELATIVE_DIRECTORY / ".gitkeep"),
        str(CONTROLS_RELATIVE_DIRECTORY / ".gitkeep"),
        decision_path_relative,
        custody_relative,
    })
    return {
        "schema": "p192-wcm-sealed-selective-worktree-profile-v1",
        "profile_id": "role1_archive_predecessor_v1",
        "mode": "sealed_full_index_skip_worktree_v1",
        "materialized_exact_paths": exact,
        "materialized_subtree_prefixes": [run_relative],
        "required_existing_subtree_prefixes": [run_relative],
        "mutable_output_subtree_prefixes": [],
        "mutable_output_exact_paths": [],
        "index_policy": (
            "uppercase_H_materialized_uppercase_S_omitted_stage0_full_index"
        ),
        "omitted_special_entry_policy": (
            "mode120000_and_160000_inert_absent_S_only"
        ),
        "preparation_metadata_terminal_state": "absent",
    }


def selective_worktree_profiles(decision: dict[str, Any]) -> dict[str, Any]:
    """Return the exact sealed selective-worktree profiles."""
    paths = decision["paths"]
    decision_relative = str(
        DECISION_RELATIVE_DIRECTORY / f'{decision["decision_id"]}.json'
    )
    protocol_exact = sorted({
        *PROTECTED_PROTOCOL_RELATIVE_PATHS.values(),
        str(RUNS_RELATIVE_DIRECTORY / ".gitkeep"),
        str(CONTROLS_RELATIVE_DIRECTORY / ".gitkeep"),
        decision_relative,
    })
    protocol_prefixes = [
        Path(paths["run_dir"]).relative_to(
            Path(paths["protocol_repository_path"]),
        ).as_posix(),
        Path(paths["control_dir"]).relative_to(
            Path(paths["protocol_repository_path"]),
        ).as_posix(),
    ]
    predecessor_repository = Path(paths["predecessor_repository_path"])
    predecessor_decision_relative = Path(
        decision["predecessor_role1"]["decision_path"]
    ).relative_to(predecessor_repository).as_posix()
    source_exact = sorted(SOURCE_SPARSE_EXACT_PATHS)
    source_prefixes = sorted(SOURCE_SPARSE_PREFIXES)

    def record(
        profile_id: str, exact: list[str], prefixes: list[str],
        required_prefixes: list[str], mutable_prefixes: list[str],
    ) -> dict[str, Any]:
        return {
            "schema": "p192-wcm-sealed-selective-worktree-profile-v1",
            "profile_id": profile_id,
            "mode": "sealed_full_index_skip_worktree_v1",
            "materialized_exact_paths": exact,
            "materialized_subtree_prefixes": prefixes,
            "required_existing_subtree_prefixes": required_prefixes,
            "mutable_output_subtree_prefixes": mutable_prefixes,
            "mutable_output_exact_paths": [],
            "index_policy": "uppercase_H_materialized_uppercase_S_omitted_stage0_full_index",
            "omitted_special_entry_policy": "mode120000_and_160000_inert_absent_S_only",
            "preparation_metadata_terminal_state": "absent",
        }

    return {
        "protocol": record(
            "protocol_protected_decision_outputs_v1",
            protocol_exact, protocol_prefixes,
            [], protocol_prefixes,
        ),
        "source": record(
            "native_three_packages_and_root_build_inputs_v1",
            source_exact, source_prefixes, source_prefixes, [],
        ),
        "predecessor_pre_execution": _role1_pre_execution_profile(
            predecessor_decision_relative, decision["predecessor_run_id"],
        ),
        "predecessor": _role1_terminal_archive_profile(
            predecessor_decision_relative, decision["predecessor_run_id"],
        ),
    }


def sha256_path(path: Path) -> str:
    return sha256_bytes(_read_regular_file_bytes(path, "SHA-256 input"))


def _mode_string(metadata: os.stat_result) -> str:
    return "100755" if metadata.st_mode & 0o111 else "100644"


def _file_identity(path: Path, recorded_path: str | None = None) -> dict[str, Any]:
    """Return the closed identity used for retained executable/input FDs."""
    data, metadata = _regular_file_snapshot(path, "file identity")
    return {
        "path": str(path) if recorded_path is None else recorded_path,
        "device": str(metadata.st_dev),
        "inode": str(metadata.st_ino),
        "mode": _mode_string(metadata),
        "link_count": metadata.st_nlink,
        "byte_length": len(data),
        "sha256": sha256_bytes(data),
    }


def _directory_identity(path: Path) -> dict[str, Any]:
    metadata = os.lstat(path)
    if not stat.S_ISDIR(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode):
        raise ValueError(f"not a nofollow directory: {path}")
    return {
        "path": str(path),
        "device": str(metadata.st_dev),
        "inode": str(metadata.st_ino),
    }


def _owned_private_directory_identity(path: Path) -> dict[str, Any]:
    metadata = os.lstat(path)
    if (
        not stat.S_ISDIR(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode)
        or metadata.st_uid != os.geteuid()
        or stat.S_IMODE(metadata.st_mode) != 0o700
    ):
        raise ValueError(
            f"not a current-user-owned 0700 nofollow directory: {path}"
        )
    return {
        "path": str(path), "device": str(metadata.st_dev),
        "inode": str(metadata.st_ino), "uid": str(metadata.st_uid),
        "mode": "0700",
    }


def _source_input_digest(rows: list[dict[str, Any]]) -> str:
    digest = hashlib.sha256(b"P192-WCM-SOURCE-BUILD-INPUTS-v1\0")
    for row in rows:
        encoded = canonical_json_bytes(row)
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
    return digest.hexdigest()


def _recheck_source_input_rows(
    repository: Path, rows: list[dict[str, Any]], label: str,
    errors: list[str],
) -> None:
    """Recheck original source/build identities without invoking Git again."""
    for row in rows:
        relative = row.get("path")
        if not isinstance(relative, str):
            errors.append(f"{label}: source/build row path is invalid")
            continue
        try:
            identity = _file_identity(repository / relative)
        except (OSError, ValueError) as exc:
            errors.append(f"{label}: source/build input {relative} unavailable: {exc}")
            continue
        expected = {
            "mode": row.get("mode"), "device": row.get("device"),
            "inode": row.get("inode"), "link_count": row.get("link_count"),
            "byte_length": row.get("byte_length"), "sha256": row.get("sha256"),
        }
        actual = {key: identity.get(key) for key in expected}
        _exact(actual, expected, f"{label}: source/build terminal identity {relative}", errors)


def _terminal_immutable_input_errors(
    decision: dict[str, Any], *,
    decision_identity: dict[str, Any],
    protected_identities: dict[str, dict[str, Any]],
    binary_identities: dict[str, dict[str, Any]],
    source_build_rows: dict[str, list[dict[str, Any]]],
    predecessor_identities: dict[str, dict[str, Any]],
    repository_identities: dict[str, dict[str, Any]],
) -> list[str]:
    """Recheck every bound external input without spawning another process."""
    errors: list[str] = []

    def recheck(path: Path, expected: dict[str, Any], label: str) -> None:
        try:
            current = _file_identity(path, expected.get("path"))
        except (OSError, ValueError) as exc:
            errors.append(f"terminal immutable {label} unavailable: {exc}")
            return
        _exact(current, expected, f"terminal immutable {label}", errors)

    recheck(
        Path(decision["paths"]["decision_json"]), decision_identity,
        "decision identity",
    )
    _exact(
        decision_identity.get("sha256"),
        sha256_bytes(canonical_json_bytes(decision)),
        "terminal immutable decision/document hash", errors,
    )
    for name, relative in PROTECTED_PROTOCOL_RELATIVE_PATHS.items():
        expected = protected_identities.get(name)
        if expected is None:
            errors.append(f"terminal immutable protected identity missing: {name}")
            continue
        recheck(
            Path(decision["paths"]["protocol_repository_path"]) / relative,
            expected, f"protected {relative}",
        )
        _exact(
            expected.get("sha256"), decision["protected_protocol_blobs"].get(name),
            f"terminal immutable protected decision hash {relative}", errors,
        )
    for role in ("producer", "verifier", "supervisor"):
        expected = binary_identities.get(role)
        if expected is None:
            errors.append(f"terminal immutable {role} binary identity is missing")
        else:
            recheck(
                Path(decision["paths"][f"{role}_bin"]), expected,
                f"{role} binary",
            )
        rows = source_build_rows.get(role)
        if rows is None:
            errors.append(f"terminal immutable {role} source/build rows are missing")
        else:
            _recheck_source_input_rows(
                Path(decision["paths"][f"{role}_repository_path"]), rows,
                f"terminal immutable {role}", errors,
            )
    repository_paths = {
        "protocol": Path(decision["paths"]["protocol_repository_path"]),
        "predecessor": Path(decision["paths"]["predecessor_repository_path"]),
        **{
            role: Path(decision["paths"][f"{role}_repository_path"])
            for role in ("producer", "verifier", "supervisor")
        },
    }
    for name, path in repository_paths.items():
        expected = repository_identities.get(name)
        if expected is None:
            errors.append(f"terminal immutable {name} repository identity is missing")
            continue
        try:
            current = _directory_identity(path)
        except (OSError, ValueError) as exc:
            errors.append(
                f"terminal immutable {name} repository unavailable: {exc}"
            )
            continue
        _exact(
            current, expected,
            f"terminal immutable {name} repository identity", errors,
        )
    predecessor = Path(decision["paths"]["predecessor_dir"])
    for name in PREDECESSOR_PATHS:
        expected = predecessor_identities.get(name)
        if expected is None:
            errors.append(f"terminal immutable predecessor identity missing: {name}")
            continue
        recheck(predecessor / name, expected, f"predecessor {name}")
    retained_expected = predecessor_identities.get(
        "pre_execution_repository_custody",
    )
    if retained_expected is None:
        errors.append(
            "terminal immutable retained pre-execution custody identity is missing"
        )
    else:
        recheck(
            Path(decision["predecessor_repository_custody"][
                "pre_execution_retained_path"
            ]),
            retained_expected,
            "retained pre-execution repository custody receipt",
        )
    try:
        staging_parent = Path(decision["predecessor_repository_custody"][
            "pre_execution_retained_path"
        ]).parent
        _exact(
            _owned_private_directory_identity(staging_parent),
            decision["predecessor_repository_custody"].get(
                "pre_execution_staging_parent_identity"
            ),
            "terminal immutable retained-custody staging parent", errors,
        )
    except (KeyError, OSError, ValueError) as exc:
        errors.append(
            f"terminal immutable retained-custody staging parent unavailable: {exc}"
        )

    admission = decision.get("verifier_build_admission", {})
    for tool in ("cargo", "rustc"):
        expected = admission.get(f"{tool}_identity")
        if not isinstance(expected, dict):
            errors.append(f"terminal immutable verifier {tool} identity is missing")
            continue
        recheck(Path(str(expected.get("path", "/invalid"))), expected, f"verifier {tool} tool")
    recorded_directories = admission.get("config_search_directory_identities")
    current_directories: list[dict[str, Any]] = []
    if not isinstance(recorded_directories, list):
        errors.append("terminal immutable Cargo config-search identities are missing")
    else:
        for record in recorded_directories:
            if not isinstance(record, dict):
                errors.append("terminal immutable Cargo config-search identity is invalid")
                continue
            try:
                current_directories.append(_directory_identity(Path(str(record.get("path")))))
            except (OSError, ValueError) as exc:
                errors.append(f"terminal immutable Cargo config-search directory unavailable: {exc}")
        _exact(
            current_directories, recorded_directories,
            "terminal immutable Cargo config-search directory identities", errors,
        )
    for raw_candidate in admission.get("config_candidate_paths", []):
        _require(
            isinstance(raw_candidate, str) and not os.path.lexists(raw_candidate),
            f"terminal immutable Cargo config candidate exists: {raw_candidate}", errors,
        )
    dep_info = admission.get("selected_bin_dep_info", {})
    dep_info_identity = dep_info.get("identity") if isinstance(dep_info, dict) else None
    if isinstance(dep_info_identity, dict):
        recheck(
            Path(str(dep_info_identity.get("path", "/invalid"))), dep_info_identity,
            "selected-bin dep-info",
        )
    else:
        errors.append("terminal immutable selected-bin dep-info identity is missing")
    local_inputs = dep_info.get("local_inputs", []) if isinstance(dep_info, dict) else []
    if not isinstance(local_inputs, list):
        errors.append("terminal immutable dep-info local-input identities are invalid")
    else:
        for index, expected in enumerate(local_inputs):
            if not isinstance(expected, dict):
                errors.append(f"terminal immutable dep-info local input {index} is invalid")
                continue
            recheck(
                Path(str(expected.get("path", "/invalid"))), expected,
                f"dep-info local input {index}",
            )
    return errors


def _identity_bundle_digest(rows: list[dict[str, Any]]) -> str:
    return sha256_bytes(
        b"P192-WCM-RETAINED-IDENTITY-BUNDLE-v1\0" + canonical_json_bytes(rows)
    )


def _artifact_inventory_digest(rows: list[dict[str, Any]]) -> str:
    return sha256_bytes(
        b"P192-WCM-ARTIFACT-INVENTORY-v1\0" + canonical_json_bytes(rows)
    )


def _load_role1_checker(repository: Path) -> Any:
    checker_path = repository / PROTECTED_PROTOCOL_RELATIVE_PATHS[
        "role1-interface/check_role1_interface.py"
    ]
    source = _read_regular_file_bytes(
        checker_path, "protected Role-1 checker", byte_cap=16777216,
    )
    module = types.ModuleType("p192_role1_checker_for_role2")
    module.__file__ = str(checker_path)
    code = compile(source, str(checker_path), "exec", dont_inherit=True)
    exec(code, module.__dict__)
    return module


def _role1_predecessor_binding(
    predecessor: Path, repository: Path, errors: list[str], *, replay: bool = True,
) -> dict[str, Any] | None:
    """Replay the complete Role-1 admission and return its exact Role-2 binding."""
    initial_error_count = len(errors)
    for relative in ROLE1_REQUIRED_PATHS:
        path = predecessor / relative
        _validate_regular_file(path, f"Role-1 predecessor {relative}", errors)
        try:
            _require(
                os.lstat(path).st_nlink == 1,
                f"Role-1 predecessor {relative} is not a single-link file", errors,
            )
        except OSError as exc:
            errors.append(
                f"Role-1 predecessor {relative} link-count stat unavailable: {exc}"
            )
    if len(errors) != initial_error_count:
        return None
    try:
        receipt = decode_canonical_json(
            _read_regular_file_bytes(
                predecessor / "independent-verifier-receipt.json",
                "Role-1 predecessor receipt",
            )
        )
    except Exception as exc:
        errors.append(f"Role-1 predecessor receipt is invalid: {exc}")
        return None
    if not isinstance(receipt, dict):
        errors.append("Role-1 predecessor receipt root is not an object")
        return None
    decision_binding = receipt.get("decision_binding", {})
    if not isinstance(decision_binding, dict):
        errors.append("Role-1 predecessor decision binding is not an object")
        return None
    reported_repository = _normalized_absolute_path(
        decision_binding.get("protocol_repository_path"),
        "Role-1 predecessor protocol repository", errors,
    )
    decision_path = _normalized_absolute_path(
        decision_binding.get("decision_path"), "Role-1 predecessor decision path", errors,
    )
    decision_commit = decision_binding.get("decision_commit")
    protocol_commit = receipt.get("protocol_commit")
    decision_id = decision_binding.get("decision_id")
    if (
        reported_repository is None or decision_path is None
        or not isinstance(decision_commit, str)
        or not isinstance(protocol_commit, str)
        or not isinstance(decision_id, str)
    ):
        errors.append("Role-1 predecessor decision binding is incomplete")
        return None
    _exact(
        reported_repository, repository,
        "Role-1 predecessor receipt/admitted repository", errors,
    )
    if reported_repository != repository:
        # Never issue Git calls or load Python from a receipt-selected path.
        return None
    if (
        re.fullmatch(r"[0-9a-f]{40}", decision_commit) is None
        or re.fullmatch(r"[0-9a-f]{40}", protocol_commit) is None
        or re.fullmatch(r"DEC-[0-9]{8}-[0-9a-f]{6}", decision_id) is None
    ):
        errors.append("Role-1 predecessor receipt commit/decision identifiers are invalid")
        return None
    expected_decision_path = (
        repository / "ledger/decisions" / f"{decision_id}.yaml"
    )
    _exact(
        decision_path, expected_decision_path,
        "Role-1 predecessor canonical decision path", errors,
    )
    if decision_path != expected_decision_path:
        return None
    _validate_regular_file(decision_path, "Role-1 predecessor decision", errors)
    try:
        decision_raw = _read_regular_file_bytes(
            decision_path, "Role-1 predecessor decision",
        )
    except (OSError, ValueError) as exc:
        errors.append(f"Role-1 predecessor decision bytes unavailable: {exc}")
        return None
    _exact(
        sha256_bytes(decision_raw), decision_binding.get("decision_sha256"),
        "Role-1 predecessor decision raw hash", errors,
    )
    top = _git_stdout(
        repository, ["rev-parse", "--show-toplevel"],
        "Role-1 predecessor protocol Git top level", errors,
    )
    if top is not None:
        _exact(
            top.rstrip(b"\n").decode("utf-8", "replace"), str(repository),
            "Role-1 predecessor protocol Git top level", errors,
        )
    head_raw = _git_stdout(
        repository, ["rev-parse", "HEAD"], "Role-1 predecessor protocol HEAD", errors,
    )
    head = "" if head_raw is None else head_raw.rstrip(b"\n").decode("ascii", "replace")
    try:
        relative_decision = decision_path.relative_to(repository).as_posix()
    except ValueError:
        errors.append("Role-1 predecessor decision is outside its protocol repository")
        return None
    entry = _git_tree_entry(
        repository, decision_commit, relative_decision,
        "Role-1 predecessor decision Git entry", errors,
    )
    if entry is not None:
        mode, kind, object_id = entry
        _exact((mode, kind), ("100644", "blob"), "Role-1 predecessor decision mode/type", errors)
        committed = _git_blob(
            repository, object_id, "Role-1 predecessor committed decision", errors,
        )
        if committed is not None:
            _exact(committed, decision_raw, "Role-1 predecessor decision working bytes", errors)
    decision_parents = _raw_commit_parents(
        repository, decision_commit, "Role-1 predecessor decision", errors,
    )
    if decision_parents is not None:
        _exact(
            decision_parents, [protocol_commit],
            "Role-1 predecessor decision direct protocol parent", errors,
        )
    if head != decision_commit:
        archive_parents = _raw_commit_parents(
            repository, head, "Role-1 predecessor archive", errors,
        )
        if archive_parents is not None:
            _exact(
                archive_parents, [decision_commit],
                "Role-1 predecessor archive direct decision parent", errors,
            )
    _exact(
        receipt.get("run_dir"), str(predecessor),
        "Role-1 predecessor receipt/run-directory identity", errors,
    )
    if replay:
        try:
            checker_relative = PROTECTED_PROTOCOL_RELATIVE_PATHS[
                "role1-interface/check_role1_interface.py"
            ]
            protocol_topology = _raw_commit_tree_topology(
                repository, protocol_commit,
                "Role-1 replay protected protocol commit", errors,
            )
            if protocol_topology is None:
                return None
            checker_entry = protocol_topology.get(checker_relative)
            if checker_entry is None or checker_entry[:2] != ("100644", "blob"):
                errors.append(
                    "Role-1 replay checker is absent/nonregular in protected protocol commit"
                )
                return None
            checker_blob = _git_blob(
                repository, checker_entry[2],
                "Role-1 replay protected checker blob", errors,
            )
            if checker_blob is None:
                return None
            _exact(
                checker_blob,
                _read_regular_file_bytes(
                    repository / checker_relative,
                    "Role-1 replay current protected checker",
                    byte_cap=16777216,
                ),
                "Role-1 replay checker committed/current bytes", errors,
            )
            if errors:
                return None
            role1 = _load_role1_checker(repository)
            errors.extend(
                f"Role-1 run replay: {error}"
                for error in role1.validate_run_directory(predecessor)
            )
            errors.extend(
                f"Role-1 decision replay: {error}"
                for error in role1.validate_dispatch_decision(
                    decision_path, decision_commit, "post-run", predecessor.resolve(),
                    repository_root=repository, check_git=False,
                )
            )
        except Exception as exc:
            errors.append(f"Role-1 full checker replay failed: {exc}")
    inventory = [
        _artifact_record(predecessor / relative, relative)
        for relative in ROLE1_REQUIRED_PATHS
    ]
    return {
        "schema": "p192-wcm-role1-predecessor-binding-v1",
        "run_id": predecessor.name,
        "run_dir": str(predecessor),
        "decision_path": str(decision_path),
        "decision_commit": decision_commit,
        "archive_commit": head,
        "decision_sha256": sha256_bytes(decision_raw),
        "protocol_commit": protocol_commit,
        "source_commit": receipt.get("source_commit"),
        "verifier_commit": receipt.get("verifier_commit"),
        "receipt_sha256": sha256_path(
            predecessor / "independent-verifier-receipt.json"
        ),
        "receipt": receipt,
        "artifact_inventory": inventory,
        "artifact_tree_sha256": _artifact_inventory_digest(inventory),
    }


class _UniqueYamlLoader(yaml.SafeLoader):
    """Safe loader that rejects duplicate mapping keys."""


def _unique_yaml_mapping(
    loader: _UniqueYamlLoader, node: yaml.nodes.MappingNode, deep: bool = False,
) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    result: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in result
        except TypeError as exc:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping", node.start_mark,
                "found an unhashable key", key_node.start_mark,
            ) from exc
        if duplicate:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping", node.start_mark,
                f"found duplicate key {key!r}", key_node.start_mark,
            )
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_UniqueYamlLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _unique_yaml_mapping,
)


def load_yaml(path: Path) -> Any:
    return yaml.load(
        _read_regular_file_bytes(path, "YAML input").decode("utf-8"),
        Loader=_UniqueYamlLoader,
    )


def load_json(path: Path) -> Any:
    return json.loads(
        _read_regular_file_bytes(path, "JSON input").decode("utf-8"),
        object_pairs_hook=_object_without_duplicates,
    )


def _reject_noncanonical_numbers(value: Any) -> None:
    if isinstance(value, float):
        raise ValueError("floating-point JSON values are forbidden")
    if isinstance(value, int) and not isinstance(value, bool) and abs(value) > 9007199254740991:
        raise ValueError("JSON integer exceeds the interoperable range")
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                raise ValueError("JSON object keys must be strings")
            _reject_noncanonical_numbers(child)
    elif isinstance(value, list):
        for child in value:
            _reject_noncanonical_numbers(child)


def canonical_json_bytes(value: Any) -> bytes:
    """Canonical bytes for this ASCII-keyed, integer-only interface subset."""
    _reject_noncanonical_numbers(value)
    return json.dumps(
        value, ensure_ascii=False, allow_nan=False, sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _object_without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, child in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key: {key}")
        value[key] = child
    return value


def decode_canonical_json(data: bytes) -> Any:
    if data.startswith(b"\xef\xbb\xbf") or data.endswith(b"\n") or b"\r" in data:
        raise ValueError("JSON has BOM, CR, or trailing LF")
    value = json.loads(
        data.decode("utf-8"),
        parse_float=lambda _: (_ for _ in ()).throw(ValueError("float")),
        object_pairs_hook=_object_without_duplicates,
    )
    if canonical_json_bytes(value) != data:
        raise ValueError("JSON bytes are not canonical")
    return value


def decode_canonical_jsonl(data: bytes) -> list[Any]:
    if not data:
        return []
    if data.startswith(b"\xef\xbb\xbf") or b"\r" in data or not data.endswith(b"\n"):
        raise ValueError("JSONL framing is not canonical")
    records = []
    for line in data[:-1].split(b"\n"):
        if not line:
            raise ValueError("blank JSONL line")
        value = json.loads(
            line.decode("utf-8"),
            parse_float=lambda _: (_ for _ in ()).throw(ValueError("float")),
            object_pairs_hook=_object_without_duplicates,
        )
        if canonical_json_bytes(value) != line:
            raise ValueError("JSONL record is not canonical")
        records.append(value)
    return records


def box0_pairs() -> Iterable[tuple[int, int, int]]:
    index = 0
    for v in range(1, 9):
        for x in range(v & 1, 65537, 2):
            yield index, v, x
            index += 1


def box0_counts() -> tuple[int, int, int]:
    total = primitive = 0
    for _, v, x in box0_pairs():
        u = abs((x - TRACE_T * v) // 2)
        primitive += math.gcd(u, v) == 1
        total += 1
    return total, primitive, total - primitive


def parse_disposition_details(
    data: bytes, expected_count: int = 262148,
) -> tuple[dict[str, int], list[int], dict[int, tuple[str, str]]]:
    """Parse the frozen variable-width disposition stream, without arithmetic."""
    counts = {name: 0 for name in STATUS_NAMES.values()}
    statuses: list[int] = []
    retained_hashes: dict[int, tuple[str, str]] = {}
    offset = 0
    for expected_index in range(expected_count):
        if len(data) - offset < 10:
            raise ValueError(f"truncated disposition prefix at {expected_index}")
        status = data[offset]
        candidate_index = int.from_bytes(data[offset + 1:offset + 9], "big")
        has_certificates = data[offset + 9]
        offset += 10
        if status not in STATUS_NAMES:
            raise ValueError(f"unknown status {status}")
        if candidate_index != expected_index:
            raise ValueError("disposition candidate index is not contiguous")
        expected_flag = 1 if status in (1, 2, 3) else 0
        if has_certificates != expected_flag:
            raise ValueError("certificate flag disagrees with status")
        if expected_flag:
            if len(data) - offset < 64:
                raise ValueError("truncated disposition certificate hashes")
            retained_hashes[expected_index] = (
                data[offset:offset + 32].hex(), data[offset + 32:offset + 64].hex(),
            )
            offset += 64
        counts[STATUS_NAMES[status]] += 1
        statuses.append(status)
    if offset != len(data):
        raise ValueError("trailing disposition bytes")
    return counts, statuses, retained_hashes


def parse_disposition_bytes(data: bytes, expected_count: int = 262148) -> dict[str, int]:
    return parse_disposition_details(data, expected_count)[0]


def validate_checkpoint(checkpoint: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    counters = checkpoint.get("phase_counters", {})
    try:
        values = {key: int(value) for key, value in counters.items()}
        if values.get("seen") != 262148 or checkpoint.get("next_candidate_index") != 262148:
            errors.append("checkpoint does not commit all 262148 candidates")
        if values.get("seen") != values.get("duplicate", -1) + values.get("primitive", -1):
            errors.append("checkpoint seen conservation failed")
        rhs = sum(values.get(key, -10**9) for key in (
            "complete", "one_lp", "two_lp", "rejected", "invalid", "unresolved"
        ))
        if values.get("primitive") != rhs:
            errors.append("checkpoint primitive conservation failed")
    except (TypeError, ValueError):
        errors.append("checkpoint counters are not minimal decimal integers")
    return errors


def _exact(actual: Any, expected: Any, label: str, errors: list[str]) -> None:
    if actual != expected:
        errors.append(f"{label} differs from frozen value")


def _schema_validator(schema: dict[str, Any]) -> Draft202012Validator:
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _schema_errors(schema: dict[str, Any], value: Any) -> list[str]:
    validator = _schema_validator(schema)
    return [error.message for error in sorted(validator.iter_errors(value), key=lambda error: list(error.path))]


def validate_artifact_document(value: dict[str, Any], schema: dict[str, Any] | None = None) -> list[str]:
    schema = schema or load_json(ARTIFACT_SCHEMA)
    errors = _schema_errors(schema, value)
    if errors:
        return errors
    if "producer_commit" in value and "factor_base_source_commit" in value:
        _exact(
            value.get("producer_commit"), value.get("factor_base_source_commit"),
            "immutable producer/factor-base source commit equality", errors,
        )
    bindings = value.get("bindings")
    if isinstance(bindings, dict) and {
        "producer_commit", "factor_base_source_commit",
    }.issubset(bindings):
        _exact(
            bindings.get("producer_commit"), bindings.get("factor_base_source_commit"),
            "immutable producer/factor-base source commit binding equality", errors,
        )
    custody = value.get("decision_custody")
    if isinstance(custody, dict):
        checkout = custody.get("protocol_checkout", {})
        if "protocol_commit" in value:
            _exact(checkout.get("protocol_commit"), value.get("protocol_commit"), "decision custody protocol commit", errors)
        _exact(checkout.get("decision_commit"), custody.get("decision_commit"), "decision custody commit", errors)
    build_custody = value.get("verifier_build_custody")
    if isinstance(build_custody, dict):
        _exact(
            build_custody.get("tool_identities_after"),
            build_custody.get("tool_identities_before"),
            "verifier build tool identities changed", errors,
        )
        _exact(
            build_custody.get("config_search_directory_identities_after"),
            build_custody.get("config_search_directory_identities_before"),
            "verifier Cargo config-search directory identities changed", errors,
        )
    name = value.get("schema")
    if name == "p192-wcm-shell-verification-v1":
        _exact([item.get("check_id") for item in value.get("checks", [])], PRODUCER_CHECKS, "producer checks", errors)
        _exact([item.get("path") for item in value.get("artifacts", [])], PRODUCER_PATHS[:-1], "producer artifact order", errors)
        passed = all(item.get("status") == "PASS" for item in value.get("checks", []))
        _exact(value.get("overall_status"), "PASS" if passed else "FAIL", "producer overall status", errors)
    elif name == "p192-wcm-shell-independent-verification-v1":
        _exact([item.get("check_id") for item in value.get("checks", [])], INDEPENDENT_CHECKS, "independent checks", errors)
        _exact([item.get("path") for item in value.get("source_artifacts", [])], PRODUCER_PATHS, "verifier source artifact order", errors)
        passed = all(item.get("status") == "PASS" for item in value.get("checks", []))
        _exact(value.get("overall_status"), "PASS" if passed else "FAIL", "independent overall status", errors)
    elif name == "p192-wcm-shell-independent-agreement-v1":
        _exact([item.get("field") for item in value.get("comparisons", [])], AGREEMENT_FIELDS, "agreement field order", errors)
        for item in value.get("comparisons", []):
            _exact(item.get("equal"), item.get("producer") == item.get("verifier"), f'agreement equality {item.get("field")}', errors)
        passed = all(item.get("equal") is True for item in value.get("comparisons", []))
        _exact(value.get("overall_status"), "PASS" if passed else "FAIL", "agreement overall status", errors)
    elif name == "p192-wcm-checkpoint-resume-control-v1":
        _exact([item.get("field") for item in value.get("comparisons", [])], PRODUCER_PATHS, "restart comparison order", errors)
        _exact(value.get("injected_paths"), APPEND_PATHS, "restart injected path order", errors)
        _exact([item.get("path") for item in value.get("fault_state_artifacts", [])], CONTROL_CHECKPOINT_PATHS, "restart fault-state order", errors)
        _exact([item.get("path") for item in value.get("injected_state_artifacts", [])], CONTROL_CHECKPOINT_PATHS, "restart injected-state order", errors)
        _exact([item.get("path") for item in value.get("resumed_control_artifacts", [])], PRODUCER_PATHS, "restart resumed-control order", errors)
        for item in value.get("comparisons", []):
            _exact(item.get("equal"), item.get("fresh_sha256") == item.get("resumed_sha256"), f'restart equality {item.get("field")}', errors)
        passed = (
            all(item.get("equal") is True for item in value.get("comparisons", []))
            and value.get("roots_equal") is True and value.get("counters_equal") is True
            and value.get("prefixes_equal") is True
        )
        _exact(value.get("overall_status"), "PASS" if passed else "FAIL", "restart overall status", errors)
    elif name == "p192-wcm-shell-supervisor-receipt-v1":
        _exact(value.get("decision_id"), value.get("decision_custody", {}).get("decision_id"), "receipt decision id/custody", errors)
        _exact([item.get("path") for item in value.get("predecessor_artifacts_before", [])], PREDECESSOR_PATHS, "predecessor-before order", errors)
        _exact([item.get("path") for item in value.get("predecessor_artifacts_after", [])], PREDECESSOR_PATHS, "predecessor-after order", errors)
        _exact([item.get("path") for item in value.get("producer_artifacts_before_verifier", [])], PRODUCER_PATHS, "producer-before order", errors)
        _exact([item.get("path") for item in value.get("producer_artifacts_after_verifier", [])], PRODUCER_PATHS, "producer-after order", errors)
        _exact(
            [{"role": item.get("role"), "expected_exit_code": item.get("expected_exit_code")} for item in value.get("children", [])],
            SUPERVISOR_CHILDREN, "supervisor child order", errors,
        )
        children = value.get("children", [])
        if len(children) == 4:
            for item in children[:3]:
                _exact(item.get("commit"), value.get("producer_commit"), f'{item.get("role")} commit', errors)
            _exact(children[3].get("commit"), value.get("verifier_commit"), "verifier child commit", errors)
            if len({item.get("binary_sha256") for item in children[:3]}) != 1:
                errors.append("producer control children do not use one binary")
        predecessor_stable = value.get("predecessor_artifacts_before") == value.get("predecessor_artifacts_after")
        producer_stable = value.get("producer_artifacts_before_verifier") == value.get("producer_artifacts_after_verifier")
        passed = (
            all(item.get("expected_exit_code") == item.get("observed_exit_code") for item in children)
            and predecessor_stable and producer_stable
        )
        _exact(value.get("overall_status"), "PASS" if passed else "FAIL", "supervisor overall status", errors)
    elif name == "p192-wcm-candidate-stream-v1":
        predecessor = value.get("predecessor", {})
        predecessor_paths = [
            predecessor.get("factor_base", {}).get("path"),
            predecessor.get("factor_base_sidecar", {}).get("path"),
            predecessor.get("producer_verification", {}).get("path"),
            predecessor.get("independent_verification", {}).get("path"),
            predecessor.get("independent_agreement", {}).get("path"),
            predecessor.get("supervisor_receipt", {}).get("path"),
        ]
        _exact(predecessor_paths, PREDECESSOR_PATHS, "candidate-stream predecessor paths", errors)
        _exact(value.get("disposition", {}).get("artifact", {}).get("path"), "disposition.bin", "disposition artifact path", errors)
        _exact(value.get("disposition_schema", {}).get("path"), "disposition-schema.json", "disposition schema artifact path", errors)
        _exact(value.get("retained_candidates", {}).get("artifact", {}).get("path"), "retained-candidates.jsonl", "retained artifact path", errors)
        _exact(value.get("complete_relations", {}).get("artifact", {}).get("path"), "complete-relations.jsonl", "complete artifact path", errors)
        _exact(value.get("partial_relations", {}).get("artifact", {}).get("path"), "partial-relations.jsonl", "partial artifact path", errors)
        _exact(value.get("checkpoint_chain", {}).get("artifact", {}).get("path"), "checkpoint-chain.jsonl", "checkpoint artifact path", errors)
        counts = value.get("status_counts", {})
        retained = sum(counts.get(key, -10**9) for key in ("complete", "one_large_prime", "two_large_prime"))
        if sum(counts.values()) != 262148:
            errors.append("candidate-stream status total is not 262148")
        if counts.get("nonprimitive_duplicate") != 93158:
            errors.append("candidate-stream duplicate count is not 93158")
        if retained + sum(counts.get(key, -10**9) for key in ("rejected", "invalid", "unresolved")) != 168990:
            errors.append("candidate-stream primitive conservation failed")
        _exact(value.get("retained_candidates", {}).get("record_count"), retained, "retained record count", errors)
        _exact(value.get("complete_relations", {}).get("record_count"), counts.get("complete"), "complete record count", errors)
        _exact(value.get("partial_relations", {}).get("record_count"), counts.get("one_large_prime", -1) + counts.get("two_large_prime", -1), "partial record count", errors)
        _exact(value.get("checkpoint_chain", {}).get("record_count"), 1, "checkpoint record count", errors)
        _exact(value.get("disposition", {}).get("artifact", {}).get("byte_length"), 2621480 + 64 * retained, "disposition byte length", errors)
    elif name == "p192-wcm-retained-candidate-v1":
        try:
            candidate_bytes = bytes.fromhex(value["candidate_certificate_hex"])
            factor_bytes = bytes.fromhex(value["factorization_certificate_hex"])
            _exact(value.get("candidate_certificate_byte_length"), len(candidate_bytes), "candidate certificate length", errors)
            _exact(value.get("candidate_certificate_sha256"), sha256_bytes(candidate_bytes), "candidate certificate hash", errors)
            _exact(value.get("candidate_id"), sha256_bytes(candidate_bytes), "candidate id", errors)
            _exact(value.get("factorization_certificate_byte_length"), len(factor_bytes), "factorization certificate length", errors)
            _exact(value.get("factorization_certificate_sha256"), sha256_bytes(factor_bytes), "factorization certificate hash", errors)
        except (KeyError, ValueError):
            errors.append("retained certificate bytes are malformed")
    elif name == "p192-wcm-complete-relation-v1":
        try:
            relation_bytes = bytes.fromhex(value["relation_bytes_hex"])
            _exact(value.get("relation_byte_length"), len(relation_bytes), "relation byte length", errors)
            _exact(value.get("relation_id"), sha256_bytes(relation_bytes), "relation id", errors)
            _exact(value.get("candidate_id"), value.get("candidate_certificate_sha256"), "complete relation candidate id", errors)
            lam = int(value["lambda_mod_n"])
            lam_bar = int(value["lambda_bar_mod_n"])
            product = int(value["lambda_product_mod_n"])
            if not all(0 <= item < GROUP_ORDER_N for item in (lam, lam_bar, product)):
                errors.append("lambda residues are outside [0,n)")
            if product != (lam * lam_bar) % GROUP_ORDER_N:
                errors.append("lambda product residue is inconsistent")
        except (KeyError, ValueError):
            errors.append("relation bytes are malformed")
    elif name == "p192-wcm-partial-relation-v1":
        row = value.get("large_prime_row", [])
        keys = [(item.get("prime"), item.get("smaller_root"), item.get("larger_root")) for item in row]
        if keys != sorted(keys) or len(set(keys)) != len(keys):
            errors.append("large-prime row is not strictly sorted")
        _exact(value.get("large_prime_row_sha256"), sha256_bytes(canonical_json_bytes(row)), "large-prime row hash", errors)
        _exact(value.get("candidate_id"), value.get("candidate_certificate_sha256"), "partial relation candidate id", errors)
        magnitudes = [abs(int(item.get("coefficient", "0"))) for item in row]
        if value.get("status") == 2 and not (len(row) == 1 and magnitudes == [1]):
            errors.append("status-2 row is not one unit-magnitude large prime")
        if value.get("status") == 3 and not (
            (len(row) == 2 and magnitudes == [1, 1])
            or (len(row) == 1 and magnitudes == [2])
        ):
            errors.append("status-3 row is not two large-prime factors")
    elif name == "p192-wcm-checkpoint-v1":
        errors.extend(validate_checkpoint(value))
    elif name == "p192-wcm-role2-dependency-audit-v1":
        _exact(value.get("git_execution_policy"), GIT_EXECUTION_POLICY, "dependency-audit Git policy", errors)
        verifier_scan = value.get("verifier_forbidden_dependency_scan", {})
        for field, expected in VERIFIER_DEPENDENCY_SCAN.items():
            _exact(
                verifier_scan.get(field), expected,
                f"dependency-audit verifier forbidden dependency scan {field}", errors,
            )
        for field in ("producer_rust_sources", "verifier_rust_sources", "supervisor_rust_sources"):
            paths = [item.get("path") for item in value.get(field, [])]
            if paths != sorted(paths) or len(set(paths)) != len(paths):
                errors.append(f"{field} is not strictly path-sorted")
        for role in ("producer", "verifier", "supervisor"):
            before = value.get(f"{role}_source_build_inputs_before", [])
            after = value.get(f"{role}_source_build_inputs_after", [])
            paths = [item.get("path") for item in before]
            if paths != sorted(paths) or len(set(paths)) != len(paths):
                errors.append(f"{role} source/build inputs are not strictly path-sorted")
            _exact(after, before, f"{role} source/build inputs changed", errors)
            digest = _source_input_digest(before)
            _exact(value.get(f"{role}_source_build_tree_sha256_before"), digest, f"{role} source/build digest before", errors)
            _exact(value.get(f"{role}_source_build_tree_sha256_after"), digest, f"{role} source/build digest after", errors)
        screen = value.get("source_clone_screen", {})
        matches = screen.get("matches", [])
        ordered = sorted(matches, key=lambda item: (
            -item.get("token_count", 0), item.get("producer_path", ""),
            item.get("producer_token_start", 0), item.get("producer_token_end_exclusive", 0),
            item.get("verifier_path", ""), item.get("verifier_token_start", 0),
            item.get("verifier_token_end_exclusive", 0),
        ))
        _exact(matches, ordered, "source-clone match order", errors)
        _exact(screen.get("max_match_tokens"), max((item.get("token_count", 0) for item in matches), default=0), "source-clone maximum", errors)
    elif name == "p192-wcm-role2-box0-environment-v1":
        producer_build = value.get("producer_build", {})
        verifier_build = value.get("verifier_build", {})
        supervisor_build = value.get("supervisor_build", {})
        for build, label in (
            (producer_build, "producer"), (verifier_build, "verifier"),
            (supervisor_build, "supervisor"),
        ):
            _exact(build.get("embedded_protocol_commit"), value.get("protocol_commit"), f"environment {label} embedded protocol commit", errors)
        _exact(producer_build.get("embedded_role_commit"), value.get("producer_commit"), "environment embedded producer commit", errors)
        _exact(verifier_build.get("embedded_role_commit"), value.get("verifier_commit"), "environment embedded verifier commit", errors)
        _exact(supervisor_build.get("embedded_producer_commit"), value.get("producer_commit"), "environment supervisor embedded producer commit", errors)
        _exact(supervisor_build.get("embedded_verifier_commit"), value.get("verifier_commit"), "environment supervisor embedded verifier commit", errors)
        _exact(supervisor_build.get("embedded_supervisor_commit"), value.get("supervisor_commit"), "environment supervisor embedded supervisor commit", errors)
        for role, build in (("producer", producer_build), ("verifier", verifier_build), ("supervisor", supervisor_build)):
            _exact(build.get("binary_sha256"), value.get(f"{role}_binary_sha256"), f"environment {role} build binary hash", errors)
        _exact(value.get("execution_controls"), EXECUTION_CONTROLS, "environment execution controls", errors)
        _exact(value.get("removed_variable_names"), REMOVED_COMMIT_VARIABLES, "environment removed commit variables", errors)
        _exact(value.get("loader_override_prefixes"), list(LOADER_OVERRIDE_PREFIXES), "environment loader override prefixes", errors)
    elif name in {"p192-wcm-role2-box0-raw-result-v1", "p192-wcm-role2-box0-failure-v1"}:
        if Path(value.get("run_dir", "/invalid")).name != value.get("run_id"):
            errors.append("raw-result run_dir basename does not equal run_id")
    if name == "p192-wcm-role2-box0-failure-v1":
        _exact(value.get("control_state"), "retained", "failure control state", errors)
        _exact(value.get("control_retained"), True, "failure control retention", errors)
        _exact(value.get("control_created_before_failure"), True, "failure control creation", errors)
        failure_custody = value.get("terminal_failure_custody", {})
        if value.get("failed_phase") == "canonical_producer":
            _exact(
                failure_custody.get("control_entries"), [],
                "canonical-producer failure empty control inventory", errors,
            )
        _exact(
            failure_custody.get("stale_pass_manifest_removed"),
            failure_custody.get("stale_pass_manifest_present_before_finalization"),
            "failure stale PASS manifest removal truthfulness", errors,
        )
        phase = value.get("failed_phase")
        transition = failure_custody.get("pass_manifest_transition")
        early_phases = {
            "canonical_producer", "restart_control",
            "independent_verifier", "agreement",
        }
        if phase in early_phases or transition == "not_reached":
            _exact(
                (
                    transition,
                    failure_custody.get("provisional_pass_manifest"),
                    failure_custody.get("provisional_success_raw_result"),
                    failure_custody.get("stale_pass_manifest_present_before_finalization"),
                    failure_custody.get("stale_pass_manifest_removed"),
                ),
                ("not_reached", None, None, False, False),
                "failure PASS-manifest transition before final custody", errors,
            )
        elif transition == "post_manifest_failure_cleanup":
            _exact(phase, "final_custody", "post-manifest cleanup failure phase", errors)
            for record, expected_path, label in (
                (
                    failure_custody.get("provisional_pass_manifest"),
                    "manifest.yaml", "provisional PASS manifest",
                ),
                (
                    failure_custody.get("provisional_success_raw_result"),
                    "raw-result.json", "provisional success raw result",
                ),
            ):
                if isinstance(record, dict):
                    _exact(record.get("path"), expected_path, f"{label} path", errors)
                    _require(
                        isinstance(record.get("byte_length"), int)
                        and record["byte_length"] > 0,
                        f"{label} byte length is not positive", errors,
                    )
            _exact(
                (
                    failure_custody.get("stale_pass_manifest_present_before_finalization"),
                    failure_custody.get("stale_pass_manifest_removed"),
                ),
                (True, True), "post-manifest cleanup transition flags", errors,
            )
        completed = [item.get("path") for item in value.get("completed_artifacts", [])]
        order = {path: index for index, path in enumerate(FAILURE_COMPLETION_ORDER)}
        if any(path not in order for path in completed) or completed != sorted(set(completed), key=order.get):
            errors.append("failure completed-artifact inventory is not an ordered unique subset")
        if "raw-result.json" in completed:
            errors.append("failure raw result cannot hash itself")
    elif name is None and set(value) == {"run"}:
        paths = [item.get("path") for item in value.get("run", {}).get("artifacts", [])]
        _exact(paths, MANIFEST_ARTIFACT_PATHS, "manifest artifact order", errors)
    return errors


def resolved_argv(decision: dict[str, Any]) -> dict[str, list[str]]:
    paths = decision["paths"]
    producer = [paths["producer_bin"], *PRODUCER_TEMPLATE[1:]]
    producer[9] = paths["factor_base_json"]
    producer[11] = paths["run_dir"]
    fault = [*producer]
    fault[11] = paths["control_dir"]
    fault += ["--control-stop-after-committed-shard", "0"]
    resume = [*producer]
    resume[11] = paths["control_dir"]
    resume += ["--resume"]
    verifier = [paths["verifier_bin"], *VERIFIER_TEMPLATE[1:]]
    verifier[5] = paths["predecessor_dir"]
    verifier[7] = paths["run_dir"]
    verifier[9] = str(Path(paths["run_dir"]) / "independent-verification.json")
    supervisor = [paths["supervisor_bin"], *SUPERVISOR_TEMPLATE[1:]]
    replacements = {
        "PROTOCOL_REPOSITORY_PATH": paths["protocol_repository_path"],
        "DECISION_JSON": paths["decision_json"], "PRODUCER_BIN": paths["producer_bin"],
        "VERIFIER_BIN": paths["verifier_bin"],
        "PRODUCER_REPOSITORY_PATH": paths["producer_repository_path"],
        "PRODUCER_PACKAGE_PATH": paths["producer_package_path"],
        "VERIFIER_REPOSITORY_PATH": paths["verifier_repository_path"],
        "VERIFIER_PACKAGE_PATH": paths["verifier_package_path"],
        "SUPERVISOR_REPOSITORY_PATH": paths["supervisor_repository_path"],
        "SUPERVISOR_PACKAGE_PATH": paths["supervisor_package_path"],
        "PREDECESSOR_DIR": paths["predecessor_dir"],
        "RUN_DIR": paths["run_dir"], "CONTROL_DIR": paths["control_dir"], "AUDIT_FILE": paths["audit_file"],
    }
    supervisor = [replacements.get(token, token) for token in supervisor]
    return {
        "producer_fresh_argv": producer,
        "producer_fault_argv": fault,
        "producer_resume_argv": resume,
        "independent_verifier_argv": verifier,
        "supervisor_argv": supervisor,
    }


def _require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def _normalized_absolute_path(value: Any, label: str, errors: list[str]) -> Path | None:
    if not isinstance(value, str) or not value:
        errors.append(f"{label}: expected a nonempty path string")
        return None
    if any(ord(character) < 32 for character in value) or "<" in value or ">" in value:
        errors.append(f"{label}: control characters and placeholders are forbidden")
        return None
    path = Path(value)
    _require(path.is_absolute(), f"{label}: path must be absolute", errors)
    _require(not value.startswith("//"), f"{label}: double-slash root is forbidden", errors)
    _require(os.path.normpath(value) == value, f"{label}: path is not lexically normalized", errors)
    if not path.is_absolute() or value.startswith("//") or os.path.normpath(value) != value:
        return None
    return path


def _symlink_component(path: Path) -> Path | None:
    current = Path(path.anchor)
    for component in path.parts[1:]:
        current /= component
        try:
            metadata = os.lstat(current)
        except FileNotFoundError:
            return None
        if stat.S_ISLNK(metadata.st_mode):
            return current
    return None


def _regular_file_snapshot(
    path: Path, label: str, *, byte_cap: int = REGULAR_FILE_BYTE_CAP,
) -> tuple[bytes, os.stat_result]:
    """Read a stable, bounded regular file without following or blocking on a leaf.

    Every path-controlled read goes through this primitive.  O_NONBLOCK keeps a
    FIFO/device substitution from hanging admission; the pre/open/post identity
    comparisons turn a race or swap into a hard failure.
    """
    linked = _symlink_component(path)
    if linked is not None:
        raise ValueError(f"{label}: symlink path component forbidden: {linked}")
    try:
        before = os.lstat(path)
    except OSError as exc:
        raise ValueError(f"{label}: cannot lstat {path}: {exc}") from exc
    if not stat.S_ISREG(before.st_mode) or stat.S_ISLNK(before.st_mode):
        raise ValueError(f"{label}: not a regular nofollow file: {path}")
    if before.st_nlink != 1:
        raise ValueError(f"{label}: regular file link count is not one: {path}")
    if before.st_size > byte_cap:
        raise ValueError(f"{label}: regular file exceeds byte cap: {path}")
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise ValueError(f"{label}: cannot open nofollow file {path}: {exc}") from exc
    try:
        opened = os.fstat(descriptor)
        before_identity = (
            before.st_dev, before.st_ino, before.st_mode, before.st_nlink,
            before.st_size, before.st_mtime_ns, before.st_ctime_ns,
        )
        opened_identity = (
            opened.st_dev, opened.st_ino, opened.st_mode, opened.st_nlink,
            opened.st_size, opened.st_mtime_ns, opened.st_ctime_ns,
        )
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_nlink != 1
            or opened_identity != before_identity
        ):
            raise ValueError(f"{label}: file identity changed before read: {path}")
        chunks: list[bytes] = []
        byte_length = 0
        while True:
            chunk = os.read(descriptor, min(1024 * 1024, byte_cap + 1 - byte_length))
            if not chunk:
                break
            chunks.append(chunk)
            byte_length += len(chunk)
            if byte_length > byte_cap:
                raise ValueError(f"{label}: regular file exceeds byte cap: {path}")
        terminal = os.fstat(descriptor)
        terminal_identity = (
            terminal.st_dev, terminal.st_ino, terminal.st_mode, terminal.st_nlink,
            terminal.st_size, terminal.st_mtime_ns, terminal.st_ctime_ns,
        )
        if terminal_identity != opened_identity or byte_length != opened.st_size:
            raise ValueError(f"{label}: file changed during read: {path}")
    except OSError as exc:
        raise ValueError(f"{label}: cannot read file {path}: {exc}") from exc
    finally:
        os.close(descriptor)
    try:
        after = os.lstat(path)
    except OSError as exc:
        raise ValueError(f"{label}: cannot terminal-lstat {path}: {exc}") from exc
    after_identity = (
        after.st_dev, after.st_ino, after.st_mode, after.st_nlink,
        after.st_size, after.st_mtime_ns, after.st_ctime_ns,
    )
    if after_identity != opened_identity:
        raise ValueError(f"{label}: path identity changed after read: {path}")
    return b"".join(chunks), opened


def _read_regular_file_bytes(
    path: Path, label: str, *, byte_cap: int = REGULAR_FILE_BYTE_CAP,
) -> bytes:
    return _regular_file_snapshot(path, label, byte_cap=byte_cap)[0]


def _bounded_sorted_scandir(
    directory: Path, remaining_entries: int, label: str,
) -> list[os.DirEntry[str]]:
    """Stream at most the remaining entry budget before sorting a directory."""
    if remaining_entries < 0:
        raise ValueError(f"{label}: filesystem walk exceeds entry cap")
    entries: list[os.DirEntry[str]] = []
    try:
        with os.scandir(directory) as iterator:
            for entry in iterator:
                if len(entries) >= remaining_entries:
                    raise ValueError(f"{label}: filesystem walk exceeds entry cap")
                entries.append(entry)
    except OSError as exc:
        raise ValueError(f"{label}: cannot scan {directory}: {exc}") from exc
    entries.sort(key=lambda entry: entry.name)
    return entries


def _paths_overlap(first: Path, second: Path) -> bool:
    return first == second or first in second.parents or second in first.parents


def _rust_identifier_start(character: str) -> bool:
    return character == "_" or character.isalpha()


def _rust_identifier_continue(character: str) -> bool:
    return character == "_" or character.isalnum()


def _quoted_literal_end(text: str, quote_index: int, quote: str) -> int | None:
    index = quote_index + 1
    escaped = False
    while index < len(text):
        character = text[index]
        if escaped:
            escaped = False
        elif character == "\\":
            escaped = True
        elif character == quote:
            return index + 1
        elif character in "\r\n" and quote == "'":
            return None
        index += 1
    return None


def _raw_literal_end(text: str, start: int) -> int | None:
    index = start
    if text.startswith(("br", "cr"), index):
        index += 2
    elif text.startswith("r", index):
        index += 1
    else:
        return None
    hashes = 0
    while index < len(text) and text[index] == "#":
        hashes += 1
        index += 1
    if index >= len(text) or text[index] != '"':
        return None
    terminator = '"' + "#" * hashes
    end = text.find(terminator, index + 1)
    if end < 0:
        raise ValueError("unterminated raw Rust literal")
    return end + len(terminator)


def _rust_structural_tokens(
    raw: bytes, *, preserve_identifiers: bool = False,
) -> list[str]:
    """Tokenize Rust for clone normalization or security-channel inspection."""
    text = raw.decode("utf-8")
    tokens: list[str] = []
    index = 0
    while index < len(text):
        character = text[index]
        if character in " \t\n\r\v\f":
            index += 1
            continue
        if text.startswith("//", index):
            newline = text.find("\n", index + 2)
            index = len(text) if newline < 0 else newline + 1
            continue
        if text.startswith("/*", index):
            depth = 1
            index += 2
            while index < len(text) and depth:
                if text.startswith("/*", index):
                    depth += 1
                    index += 2
                elif text.startswith("*/", index):
                    depth -= 1
                    index += 2
                else:
                    index += 1
            if depth:
                raise ValueError("unterminated nested Rust block comment")
            continue
        raw_end = _raw_literal_end(text, index)
        if raw_end is not None:
            tokens.append("LITERAL")
            index = raw_end
            continue
        cooked_prefix = 1 if character in {"b", "c"} and index + 1 < len(text) else 0
        quote_index = index + cooked_prefix
        if quote_index < len(text) and text[quote_index] == '"':
            end = _quoted_literal_end(text, quote_index, '"')
            if end is None:
                raise ValueError("unterminated cooked Rust string literal")
            tokens.append("LITERAL")
            index = end
            continue
        if quote_index < len(text) and text[quote_index] == "'":
            end = _quoted_literal_end(text, quote_index, "'")
            if end is not None:
                tokens.append("LITERAL")
                index = end
                continue
        if text.startswith("r#", index) and index + 2 < len(text) and _rust_identifier_start(text[index + 2]):
            end = index + 3
            while end < len(text) and _rust_identifier_continue(text[end]):
                end += 1
            tokens.append(text[index + 2:end] if preserve_identifiers else "IDENT")
            index = end
            continue
        if _rust_identifier_start(character):
            end = index + 1
            while end < len(text) and _rust_identifier_continue(text[end]):
                end += 1
            identifier = text[index:end]
            tokens.append(
                identifier
                if preserve_identifiers or identifier in RUST_KEYWORDS
                else "IDENT"
            )
            index = end
            continue
        if character.isdigit():
            end = index + 1
            while end < len(text) and (text[end].isalnum() or text[end] == "_"):
                end += 1
            if (
                end < len(text) and text[end] == "."
                and not text.startswith("..", end)
                and end + 1 < len(text) and text[end + 1].isdigit()
            ):
                end += 1
                while end < len(text) and (text[end].isdigit() or text[end] == "_"):
                    end += 1
                if end < len(text) and text[end] in {"e", "E"}:
                    end += 1
                    if end < len(text) and text[end] in {"+", "-"}:
                        end += 1
                    while end < len(text) and (text[end].isdigit() or text[end] == "_"):
                        end += 1
                while end < len(text) and _rust_identifier_continue(text[end]):
                    end += 1
            tokens.append("NUMBER")
            index = end
            continue
        operator = next(
            (candidate for candidate in RUST_MULTI_OPERATORS if text.startswith(candidate, index)),
            None,
        )
        if operator is not None:
            tokens.append(operator)
            index += len(operator)
        else:
            tokens.append(character)
            index += 1
    return tokens


def _token_digest(tokens: list[str]) -> str:
    digest = hashlib.sha256(CLONE_TOKEN_DOMAIN)
    for token in tokens:
        encoded = token.encode("utf-8")
        digest.update(struct.pack(">I", len(encoded)))
        digest.update(encoded)
    return digest.hexdigest()


def _collect_rust_sources(
    root: Path, *, exclude_root_target: bool = False,
) -> list[tuple[str, bytes, list[str]]]:
    if not root.is_absolute() or _symlink_component(root) is not None:
        raise ValueError(f"source root must be absolute and non-symlink: {root}")
    try:
        metadata = os.lstat(root)
    except OSError as exc:
        raise ValueError(f"cannot stat source root {root}: {exc}") from exc
    if not stat.S_ISDIR(metadata.st_mode):
        raise ValueError(f"source root is not a directory: {root}")
    records: list[tuple[str, bytes, list[str]]] = []
    entry_count = 0
    aggregate_path_bytes = 0

    def visit(directory: Path, depth: int = 0) -> None:
        nonlocal entry_count, aggregate_path_bytes
        if depth > PROTOCOL_TOPOLOGY_DEPTH_CAP:
            raise ValueError(f"source directory depth exceeds cap: {directory}")
        entries = _bounded_sorted_scandir(
            directory, PROTOCOL_TOPOLOGY_ENTRY_CAP - entry_count,
            "Rust source inventory",
        )
        for entry in entries:
            entry_count += 1
            path = Path(entry.path)
            relative = path.relative_to(root).as_posix()
            encoded = relative.encode("utf-8")
            if len(encoded) > PROTOCOL_TOPOLOGY_PATH_BYTES_CAP:
                raise ValueError(f"source path exceeds byte cap: {relative}")
            aggregate_path_bytes += len(encoded)
            if aggregate_path_bytes > FILESYSTEM_WALK_AGGREGATE_PATH_BYTES_CAP:
                raise ValueError("source inventory exceeds aggregate path-byte cap")
            metadata = entry.stat(follow_symlinks=False)
            if stat.S_ISLNK(metadata.st_mode):
                raise ValueError(f"source symlink is forbidden: {path}")
            if exclude_root_target and directory == root and entry.name == "target":
                if not stat.S_ISDIR(metadata.st_mode):
                    raise ValueError(f"root target exclusion is not a directory: {path}")
                continue
            if stat.S_ISDIR(metadata.st_mode):
                visit(path, depth + 1)
            elif stat.S_ISREG(metadata.st_mode) and entry.name.endswith(".rs"):
                raw = _read_regular_file_bytes(path, "Rust source")
                records.append((relative, raw, _rust_structural_tokens(raw)))

    visit(root)
    records.sort(key=lambda record: record[0])
    if not records:
        raise ValueError(f"source root has no regular UTF-8 Rust source: {root}")
    return records


def _collect_rust_hash_rows(package: Path) -> list[dict[str, str]]:
    records = _collect_rust_sources(package, exclude_root_target=True)
    return [
        {"path": relative, "sha256": sha256_bytes(raw)}
        for relative, raw, _ in records
    ]


def _source_tree_digest(records: list[tuple[str, bytes, list[str]]]) -> str:
    digest = hashlib.sha256(CLONE_TREE_DOMAIN)
    for relative, raw, _ in records:
        encoded = relative.encode("utf-8")
        digest.update(struct.pack(">I", len(encoded)))
        digest.update(encoded)
        digest.update(struct.pack(">Q", len(raw)))
        digest.update(raw)
    return digest.hexdigest()


def compute_source_clone_screen(producer_root: Path, verifier_root: Path) -> dict[str, Any]:
    """Screen every Rust file in both package roots, excluding only root target/."""
    producer_records = _collect_rust_sources(producer_root, exclude_root_target=True)
    verifier_records = _collect_rust_sources(verifier_root, exclude_root_target=True)
    producer_windows: dict[str, list[tuple[int, int]]] = {}
    for file_index, (_, _, tokens) in enumerate(producer_records):
        for start in range(max(0, len(tokens) - 63)):
            producer_windows.setdefault(_token_digest(tokens[start:start + 64]), []).append((file_index, start))
    endpoints: set[tuple[int, int, int, int, int, int]] = set()
    for verifier_index, (_, _, verifier_tokens) in enumerate(verifier_records):
        for verifier_start in range(max(0, len(verifier_tokens) - 63)):
            window = verifier_tokens[verifier_start:verifier_start + 64]
            for producer_index, producer_start in producer_windows.get(_token_digest(window), []):
                producer_tokens = producer_records[producer_index][2]
                if producer_tokens[producer_start:producer_start + 64] != window:
                    continue
                p_start, v_start = producer_start, verifier_start
                while p_start and v_start and producer_tokens[p_start - 1] == verifier_tokens[v_start - 1]:
                    p_start -= 1
                    v_start -= 1
                p_end, v_end = producer_start + 64, verifier_start + 64
                while p_end < len(producer_tokens) and v_end < len(verifier_tokens) and producer_tokens[p_end] == verifier_tokens[v_end]:
                    p_end += 1
                    v_end += 1
                endpoints.add((producer_index, p_start, p_end, verifier_index, v_start, v_end))
    maximal: list[tuple[int, int, int, int, int, int]] = []
    for candidate in sorted(endpoints):
        p_file, p_start, p_end, v_file, v_start, v_end = candidate
        contained = any(
            other != candidate and other[0] == p_file and other[3] == v_file
            and other[1] <= p_start and p_end <= other[2]
            and other[4] <= v_start and v_end <= other[5]
            and other[2] - other[1] > p_end - p_start
            for other in endpoints
        )
        if not contained:
            maximal.append(candidate)
    matches: list[dict[str, Any]] = []
    for p_file, p_start, p_end, v_file, v_start, v_end in maximal:
        tokens = producer_records[p_file][2][p_start:p_end]
        matches.append({
            "producer_path": producer_records[p_file][0],
            "producer_token_start": p_start,
            "producer_token_end_exclusive": p_end,
            "verifier_path": verifier_records[v_file][0],
            "verifier_token_start": v_start,
            "verifier_token_end_exclusive": v_end,
            "token_count": p_end - p_start,
            "normalized_tokens_sha256": _token_digest(tokens),
        })
    matches.sort(key=lambda match: (
        -match["token_count"], match["producer_path"], match["producer_token_start"],
        match["producer_token_end_exclusive"], match["verifier_path"],
        match["verifier_token_start"], match["verifier_token_end_exclusive"],
    ))
    maximum = max((match["token_count"] for match in matches), default=0)
    return {
        "schema": "p192-wcm-source-clone-screen-v1",
        "normalization": "rust-structural-v1",
        "producer_root": str(producer_root),
        "verifier_root": str(verifier_root),
        "include": "**/*.rs",
        "excluded_components": [],
        "report_min_tokens": 64,
        "reject_at_tokens": 128,
        "producer_tree_sha256": _source_tree_digest(producer_records),
        "verifier_tree_sha256": _source_tree_digest(verifier_records),
        "matches": matches,
        "max_match_tokens": maximum,
        "claim_limit": "high_similarity_screen_not_proof_of_zero_conceptual_or_common_lineage",
        "overall_status": "PASS" if maximum < 128 else "FAIL",
    }


def _verifier_dependency_errors(
    manifest_bytes: bytes,
    lock_bytes: bytes,
    verifier_repository: Path,
    verifier_package: Path,
    producer_repository: Path,
    producer_package: Path,
) -> list[str]:
    """Fail closed over every verifier dependency source and Cargo target identity."""
    errors: list[str] = []
    try:
        manifest = tomllib.loads(manifest_bytes.decode("utf-8"))
        lock = tomllib.loads(lock_bytes.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        return [f"verifier Cargo provenance is not valid UTF-8 TOML: {exc}"]

    package_table = manifest.get("package")
    if not isinstance(package_table, dict):
        errors.append("verifier Cargo manifest lacks [package]")
    elif "workspace" in package_table:
        errors.append("verifier Cargo [package].workspace is forbidden")
    if manifest.get("workspace") != {}:
        errors.append("verifier Cargo workspace must be a literal empty standalone table")
    for forbidden_table in ("patch", "replace", "source", "registries", "registry"):
        if forbidden_table in manifest:
            errors.append(f"verifier Cargo [{forbidden_table}] source override is forbidden")

    def normalized_package_name(value: Any) -> str:
        return str(value).strip().lower().replace("_", "-")

    forbidden_normalized = {
        normalized_package_name(name) for name in FORBIDDEN_DEPENDENCY_PACKAGES
    }

    def canonical_root(value: Path, label: str) -> Path | None:
        if not value.is_absolute() or value != Path(os.path.abspath(value)):
            errors.append(f"{label} is not a normalized absolute path")
            return None
        linked = _symlink_component(value)
        if linked is not None:
            errors.append(f"{label} contains symlink component {linked}")
        try:
            resolved = value.resolve(strict=True)
        except OSError as exc:
            errors.append(f"{label} cannot be resolved: {exc}")
            return None
        if resolved != value:
            errors.append(f"{label} differs from its canonical path {resolved}")
        if not resolved.is_dir():
            errors.append(f"{label} is not a directory")
            return None
        return resolved

    verifier_repository = canonical_root(
        verifier_repository, "verifier dependency repository root",
    ) or verifier_repository
    verifier_package = canonical_root(
        verifier_package, "verifier dependency package root",
    ) or verifier_package
    producer_repository = canonical_root(
        producer_repository, "forbidden production-library repository root",
    ) or producer_repository
    producer_package = canonical_root(
        producer_package, "forbidden producer package root",
    ) or producer_package
    if verifier_repository not in verifier_package.parents:
        errors.append("verifier dependency package is outside its bound repository")
    if producer_repository not in producer_package.parents:
        errors.append("producer dependency package is outside its bound repository")

    def manifest_target_names(
        document: Any, package_root: Path, label: str, *, package_required: bool,
    ) -> set[str]:
        names: set[str] = set()
        if not isinstance(document, dict):
            errors.append(f"{label} Cargo manifest root is not a table")
            return names
        package_table = document.get("package")
        if package_table is None and package_required:
            errors.append(f"{label} Cargo manifest lacks [package]")
        elif package_table is not None:
            if not isinstance(package_table, dict) or not isinstance(package_table.get("name"), str):
                errors.append(f"{label} Cargo [package].name is missing or invalid")
            else:
                names.add(normalized_package_name(package_table["name"]))
        lib_table = document.get("lib")
        if lib_table is not None:
            if not isinstance(lib_table, dict):
                errors.append(f"{label} Cargo [lib] is not a table")
            elif "name" in lib_table:
                if not isinstance(lib_table["name"], str):
                    errors.append(f"{label} Cargo [lib].name is invalid")
                else:
                    names.add(normalized_package_name(lib_table["name"]))
        for target_kind in ("bin", "example", "test", "bench"):
            target_tables = document.get(target_kind, [])
            if not isinstance(target_tables, list):
                errors.append(f"{label} Cargo [[{target_kind}]] inventory is not an array")
                continue
            for index, target in enumerate(target_tables):
                if not isinstance(target, dict) or not isinstance(target.get("name"), str):
                    errors.append(
                        f"{label} Cargo [[{target_kind}]] entry {index} lacks a valid name"
                    )
                else:
                    names.add(normalized_package_name(target["name"]))
        # Cargo derives the default library target from package.name when
        # src/lib.rs exists and [lib].name is omitted. Normalization maps its
        # underscores to the same identity, but state it explicitly here.
        if (
            isinstance(package_table, dict)
            and isinstance(package_table.get("name"), str)
            and (package_root / "src/lib.rs").is_file()
        ):
            names.add(normalized_package_name(package_table["name"]))
        return names

    def load_manifest(path: Path, label: str, *, required: bool = True) -> dict[str, Any] | None:
        if not os.path.lexists(path):
            if required:
                errors.append(f"{label} Cargo.toml is missing")
            return None
        linked = _symlink_component(path)
        if linked is not None:
            errors.append(f"{label} Cargo.toml has symlink component {linked}")
            return None
        try:
            metadata = os.lstat(path)
            if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
                errors.append(f"{label} Cargo.toml is not a regular single-link file")
                return None
            return tomllib.loads(
                _read_regular_file_bytes(path, f"{label} Cargo.toml").decode("utf-8")
            )
        except (OSError, ValueError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
            errors.append(f"{label} Cargo.toml is invalid: {exc}")
            return None

    # Package and every explicit library/binary target identity from both the
    # production-library repository root and producer package are forbidden.
    producer_manifest_specs: dict[Path, tuple[str, bool]] = {}
    for root, label, required in (
        (producer_repository, "production-library repository root", False),
        (producer_package, "producer package", True),
    ):
        previous = producer_manifest_specs.get(root)
        producer_manifest_specs[root] = (
            label if previous is None else f"{previous[0]}/{label}",
            required or (False if previous is None else previous[1]),
        )
    producer_manifests: list[tuple[Path, dict[str, Any], str, bool]] = []
    for root, (label, required) in producer_manifest_specs.items():
        document = load_manifest(root / "Cargo.toml", label, required=required)
        if document is not None:
            producer_manifests.append((root, document, label, required))
    for root, document, label, required in producer_manifests:
        forbidden_normalized.update(
            manifest_target_names(
                document, root, label,
                package_required=required,
            )
        )

    declared_registry_names: set[str] = set()
    visited_path_manifests: set[Path] = {verifier_package}

    def dependency_tables(document: dict[str, Any], label: str) -> list[tuple[str, Any]]:
        tables: list[tuple[str, Any]] = [
            (section, document.get(section, {}))
            for section in ("dependencies", "dev-dependencies", "build-dependencies")
        ]
        target_tables = document.get("target", {})
        if not isinstance(target_tables, dict):
            errors.append(f"{label} Cargo [target] is not a table")
            return tables
        for target, target_document in target_tables.items():
            if not isinstance(target_document, dict):
                errors.append(f"{label} Cargo target.{target} is not a table")
                continue
            for section in ("dependencies", "dev-dependencies", "build-dependencies"):
                tables.append(
                    (f"target.{target}.{section}", target_document.get(section, {}))
                )
        return tables

    def scan_manifest_dependencies(
        document: dict[str, Any], package_root: Path, label: str,
    ) -> None:
        target_names = manifest_target_names(
            document, package_root, label, package_required=True,
        )
        forbidden_targets = target_names & forbidden_normalized
        if package_root != verifier_package and forbidden_targets:
            errors.append(
                f"{label} exposes forbidden Cargo package/target identity "
                f"{sorted(forbidden_targets)[0]}"
            )
        for scope, table in dependency_tables(document, label):
            if not isinstance(table, dict):
                errors.append(f"{label} Cargo {scope} is not a dependency table")
                continue
            for alias, specification in table.items():
                package_name: Any = alias
                dependency_path: Any = None
                has_git = False
                has_alternate_registry = False
                uses_workspace = False
                if isinstance(specification, dict):
                    package_name = specification.get("package", alias)
                    dependency_path = specification.get("path")
                    has_git = "git" in specification
                    has_alternate_registry = "registry" in specification
                    uses_workspace = specification.get("workspace") is True
                    if "workspace" in specification and not isinstance(
                        specification.get("workspace"), bool
                    ):
                        errors.append(
                            f"{label} Cargo dependency {scope}.{alias} has invalid workspace flag"
                        )
                elif not isinstance(specification, str):
                    errors.append(
                        f"{label} Cargo dependency {scope}.{alias} has invalid specification"
                    )
                if not isinstance(package_name, str):
                    errors.append(
                        f"{label} Cargo dependency {scope}.{alias} has invalid package name"
                    )
                    package_name = alias
                normalized_names = {
                    normalized_package_name(alias), normalized_package_name(package_name),
                }
                forbidden_names = normalized_names & forbidden_normalized
                if forbidden_names:
                    errors.append(
                        f"{label} Cargo dependency {scope}.{alias} directly names forbidden "
                        f"package/target {sorted(forbidden_names)[0]}"
                    )
                if uses_workspace:
                    errors.append(
                        f"{label} Cargo dependency {scope}.{alias} uses forbidden workspace inheritance"
                    )
                if has_git:
                    errors.append(
                        f"{label} Cargo dependency {scope}.{alias} uses forbidden git source"
                    )
                if has_alternate_registry:
                    errors.append(
                        f"{label} Cargo dependency {scope}.{alias} uses forbidden alternate registry"
                    )
                if dependency_path is None:
                    if not has_git and not uses_workspace and not has_alternate_registry:
                        declared_registry_names.add(normalized_package_name(package_name))
                    continue
                if not isinstance(dependency_path, str) or not dependency_path:
                    errors.append(
                        f"{label} Cargo dependency {scope}.{alias} has invalid path source"
                    )
                    continue
                errors.append(
                    f"{label} Cargo dependency {scope}.{alias} uses forbidden path source"
                )
                raw_candidate = Path(dependency_path)
                lexical = raw_candidate if raw_candidate.is_absolute() else package_root / raw_candidate
                lexical = Path(os.path.abspath(lexical))
                linked = _symlink_component(lexical)
                try:
                    resolved = lexical.resolve(strict=True)
                except OSError as exc:
                    errors.append(
                        f"{label} Cargo dependency {scope}.{alias} path cannot be resolved: {exc}"
                    )
                    continue
                if resolved == producer_repository:
                    errors.append(
                        f"{label} Cargo dependency {scope}.{alias} resolves to forbidden "
                        "production-library repository root"
                    )
                if resolved == producer_package or producer_package in resolved.parents:
                    errors.append(
                        f"{label} Cargo dependency {scope}.{alias} resolves to forbidden "
                        "producer source package"
                    )
                if linked is not None:
                    errors.append(
                        f"{label} Cargo dependency {scope}.{alias} path has symlink component {linked}"
                    )
                if not resolved.is_dir():
                    errors.append(
                        f"{label} Cargo dependency {scope}.{alias} path is not a directory"
                    )
                    continue
                path_document = load_manifest(
                    resolved / "Cargo.toml",
                    f"{label} Cargo dependency {scope}.{alias}",
                )
                if path_document is None:
                    continue
                path_targets = manifest_target_names(
                    path_document, resolved,
                    f"{label} Cargo dependency {scope}.{alias}",
                    package_required=True,
                )
                target_findings = path_targets & forbidden_normalized
                if target_findings:
                    errors.append(
                        f"{label} Cargo dependency {scope}.{alias} path exposes forbidden "
                        f"package/target {sorted(target_findings)[0]}"
                    )
                if resolved not in visited_path_manifests:
                    if len(visited_path_manifests) >= 256:
                        errors.append("verifier recursive path dependency graph exceeds 256 packages")
                        continue
                    visited_path_manifests.add(resolved)
                    scan_manifest_dependencies(
                        path_document, resolved,
                        f"{label} path dependency {scope}.{alias}",
                    )

    scan_manifest_dependencies(manifest, verifier_package, "verifier")

    packages = lock.get("package", [])
    if not isinstance(packages, list):
        errors.append("verifier Cargo.lock package inventory is not an array")
    else:
        root_package = manifest.get("package", {})
        root_name = root_package.get("name") if isinstance(root_package, dict) else None
        root_version = root_package.get("version") if isinstance(root_package, dict) else None
        root_entry_count = 0
        locked_names: set[str] = set()
        for index, package in enumerate(packages):
            if not isinstance(package, dict) or not isinstance(package.get("name"), str):
                errors.append(f"verifier Cargo.lock package entry {index} is malformed")
                continue
            name = package["name"]
            normalized_name = normalized_package_name(name)
            locked_names.add(normalized_name)
            if normalized_name in forbidden_normalized:
                errors.append(f"verifier Cargo.lock contains forbidden package {name}")
            is_root = (
                name == root_name
                and package.get("version") == root_version
                and package.get("source") is None
            )
            if is_root:
                root_entry_count += 1
                continue
            source = package.get("source")
            checksum = package.get("checksum")
            if source != "registry+https://github.com/rust-lang/crates.io-index":
                errors.append(
                    f"verifier Cargo.lock package {name} is not bound to the exact crates.io registry"
                )
            if not isinstance(checksum, str) or re.fullmatch(r"[0-9a-f]{64}", checksum) is None:
                errors.append(
                    f"verifier Cargo.lock package {name} lacks a lowercase SHA-256 registry checksum"
                )
        _exact(root_entry_count, 1, "verifier Cargo.lock root package entry count", errors)
        missing_registry = sorted(declared_registry_names - locked_names)
        if missing_registry:
            errors.append(
                f"verifier Cargo.lock lacks declared registry packages {missing_registry}"
            )
    return errors


def _verifier_dependency_scan_record(decision: dict[str, Any]) -> dict[str, Any]:
    record = copy.deepcopy(VERIFIER_DEPENDENCY_SCAN)
    record["canonical_forbidden_roots"] = {
        "producer_repository": decision["paths"]["producer_repository_path"],
        "producer_package": decision["paths"]["producer_package_path"],
    }
    return record


def _verifier_build_admission_sha256(admission: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json_bytes(admission))


def _cargo_config_search_directories(cwd: Path, cargo_home: Path) -> list[Path]:
    directories: set[Path] = {cargo_home}
    current = cwd
    while True:
        directories.add(current)
        if current == current.parent:
            break
        current = current.parent
    return sorted(directories, key=lambda path: str(path).encode("utf-8"))


def _cargo_config_candidate_paths(cwd: Path, cargo_home: Path) -> list[Path]:
    candidates = {
        cargo_home / "config",
        cargo_home / "config.toml",
    }
    current = cwd
    while True:
        candidates.add(current / ".cargo/config")
        candidates.add(current / ".cargo/config.toml")
        if current == current.parent:
            break
        current = current.parent
    return sorted(candidates, key=lambda path: str(path).encode("utf-8"))


def _metadata_root_target_rows(metadata: dict[str, Any], root_id: str) -> list[dict[str, Any]]:
    packages = metadata.get("packages", [])
    root = next(
        (
            package for package in packages
            if isinstance(package, dict) and package.get("id") == root_id
        ),
        None,
    )
    if not isinstance(root, dict):
        return []
    rows: list[dict[str, Any]] = []
    for target in root.get("targets", []):
        if not isinstance(target, dict):
            continue
        rows.append({
            "name": target.get("name"),
            "kind": target.get("kind"),
            "crate_types": target.get("crate_types"),
            "src_path": target.get("src_path"),
            "edition": target.get("edition"),
            "required_features": target.get("required-features", []),
        })
    return sorted(
        rows,
        key=lambda row: (
            str(row.get("name", "")), canonical_json_bytes(row),
        ),
    )


def _dep_info_input_tokens(raw: bytes) -> list[str]:
    """Parse the dependency side of the first Makefile-style dep-info rule."""
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("dep-info is not UTF-8") from exc
    if "\x00" in text or "\r" in text:
        raise ValueError("dep-info contains a forbidden NUL or carriage return")
    text = text.replace("\\\n", "")
    first_line = text.split("\n", 1)[0]
    escaped = False
    separator = -1
    for index, character in enumerate(first_line):
        if escaped:
            escaped = False
        elif character == "\\":
            escaped = True
        elif character == ":":
            separator = index
            break
    if separator < 1:
        raise ValueError("dep-info first rule lacks a nonempty target and colon")
    dependencies = first_line[separator + 1:]
    words: list[str] = []
    current: list[str] = []
    escaped = False
    for character in dependencies:
        if escaped:
            current.append(character)
            escaped = False
        elif character == "\\":
            escaped = True
        elif character in " \t":
            if current:
                words.append("".join(current))
                current = []
        else:
            current.append(character)
    if escaped:
        raise ValueError("dep-info ends with an incomplete escape")
    if current:
        words.append("".join(current))
    if not words or len(words) != len(set(words)):
        raise ValueError("dep-info input list is empty or contains duplicates")
    return words


def _selected_bin_dep_info_errors(
    decision: dict[str, Any], admission: dict[str, Any],
) -> list[str]:
    """Bind selected-bin compiler inputs to committed verifier-package files."""
    errors: list[str] = []
    package = Path(decision["paths"]["verifier_package_path"])
    repository = Path(decision["paths"]["verifier_repository_path"])
    target_dir = Path(str(admission.get("target_dir", "/invalid")))
    expected_path = target_dir / "release/p192_weighted_cm_verify.d"
    receipt = admission.get("selected_bin_dep_info", {})
    if not isinstance(receipt, dict):
        return ["verifier selected-bin dep-info receipt is missing"]
    recorded_identity = receipt.get("identity", {})
    _exact(
        recorded_identity.get("path") if isinstance(recorded_identity, dict) else None,
        str(expected_path), "verifier selected-bin dep-info path", errors,
    )
    _validate_regular_file(
        expected_path, "verifier selected-bin dep-info", errors,
    )
    try:
        current_identity = _file_identity(expected_path)
        _exact(
            current_identity, recorded_identity,
            "verifier selected-bin dep-info identity", errors,
        )
        _exact(
            current_identity.get("link_count"), 1,
            "verifier selected-bin dep-info link count", errors,
        )
        raw = _read_regular_file_bytes(
            expected_path, "verifier selected-bin dep-info",
        )
        tokens = _dep_info_input_tokens(raw)
    except (OSError, ValueError) as exc:
        errors.append(f"verifier selected-bin dep-info cannot be replayed: {exc}")
        return errors

    source_errors: list[str] = []
    committed_rows = _source_build_input_rows(
        repository, package, decision["verifier_commit"],
        "verifier dep-info", source_errors,
    )
    errors.extend(source_errors)
    if committed_rows is None:
        return errors
    committed_paths = {
        (repository / row["path"]).resolve()
        for row in committed_rows
        if isinstance(row, dict) and isinstance(row.get("path"), str)
    }
    observed: list[dict[str, Any]] = []
    for token in tokens:
        lexical = Path(token)
        if not lexical.is_absolute():
            lexical = package / lexical
        if _symlink_component(lexical) is not None:
            errors.append(f"verifier dep-info input contains a symlink component: {token}")
            continue
        try:
            resolved = lexical.resolve(strict=True)
        except OSError as exc:
            errors.append(f"verifier dep-info input cannot be resolved {token}: {exc}")
            continue
        if resolved == package or package not in resolved.parents:
            errors.append(f"verifier dep-info input escapes bound package: {resolved}")
            continue
        if resolved not in committed_paths:
            errors.append(f"verifier dep-info input is absent from committed inventory: {resolved}")
            continue
        try:
            identity = _file_identity(resolved)
        except (OSError, ValueError) as exc:
            errors.append(f"verifier dep-info input identity unavailable {resolved}: {exc}")
            continue
        _exact(identity.get("link_count"), 1, f"verifier dep-info input link count {resolved}", errors)
        observed.append(identity)
    observed.sort(key=lambda item: str(item.get("path", "")).encode("utf-8"))
    _exact(receipt.get("local_inputs"), observed, "verifier selected-bin dep-info local inputs", errors)
    return errors


def _verifier_build_admission_errors(
    decision: dict[str, Any], *, runtime: bool,
) -> list[str]:
    """Validate the scoped trusted Cargo/Rustc verifier build admission."""
    errors: list[str] = []
    admission = decision.get("verifier_build_admission")
    if not isinstance(admission, dict):
        return ["verifier_build_admission is missing or not an object"]
    paths = decision["paths"]
    package = Path(paths["verifier_package_path"])
    repository = Path(paths["verifier_repository_path"])
    manifest_path = package / "Cargo.toml"
    cargo_identity = admission.get("cargo_identity", {})
    rustc_identity = admission.get("rustc_identity", {})
    cargo_path = Path(str(cargo_identity.get("path", "/invalid")))
    rustc_path = Path(str(rustc_identity.get("path", "/invalid")))
    cargo_home = Path(str(admission.get("cargo_home", "/invalid")))
    target_dir = Path(str(admission.get("target_dir", "/invalid")))
    _exact(admission.get("trust_model"), VERIFIER_BUILD_TRUST_MODEL, "verifier build trust model", errors)
    _exact(admission.get("cwd"), str(package), "verifier build cwd", errors)
    _exact(
        admission.get("selected_target"),
        {
            "kind": "bin", "name": "p192_weighted_cm_verify",
            "src_path": str(package / "src/main.rs"), "features": [],
        },
        "verifier build selected target", errors,
    )
    expected_build_argv = [
        str(cargo_path), "build", "--frozen", "--locked", "--offline", "--release",
        "--manifest-path", str(manifest_path), "--bin", "p192_weighted_cm_verify",
        "--target-dir", str(target_dir),
    ]
    expected_metadata_argv = [
        str(cargo_path), "metadata", "--frozen", "--locked", "--offline",
        "--format-version", "1", "--manifest-path", str(manifest_path),
    ]
    _exact(admission.get("build_argv"), expected_build_argv, "verifier exact build argv", errors)
    _exact(admission.get("metadata_argv"), expected_metadata_argv, "verifier exact metadata argv", errors)
    _exact(
        admission.get("metadata_execution_policy"),
        VERIFIER_METADATA_EXECUTION_POLICY,
        "verifier metadata execution policy", errors,
    )
    expected_environment = {
        "CARGO_HOME": str(cargo_home),
        "CARGO_INCREMENTAL": "0",
        "CARGO_NET_OFFLINE": "true",
        "CARGO_TARGET_DIR": str(target_dir),
        "LC_ALL": "C",
        "P192_WCM_PROTOCOL_COMMIT": decision["protocol_commit"],
        "P192_WCM_VERIFIER_COMMIT": decision["verifier_commit"],
        "RUSTC": str(rustc_path),
    }
    _exact(admission.get("environment"), expected_environment, "verifier exact sanitized build environment", errors)
    _exact(
        admission.get("forbidden_environment_prefixes_absent"),
        VERIFIER_BUILD_FORBIDDEN_ENV_PREFIXES,
        "verifier forbidden build-environment prefixes", errors,
    )
    expected_candidates = [
        str(path) for path in _cargo_config_candidate_paths(package, cargo_home)
    ]
    _exact(
        admission.get("config_candidate_paths"), expected_candidates,
        "verifier Cargo config candidate path set", errors,
    )
    expected_directories = _cargo_config_search_directories(package, cargo_home)
    recorded_directories = admission.get("config_search_directory_identities")
    if not isinstance(recorded_directories, list):
        errors.append("verifier Cargo config search directory identities are missing")
    else:
        _exact(
            [item.get("path") for item in recorded_directories if isinstance(item, dict)],
            [str(path) for path in expected_directories],
            "verifier Cargo config search directory order", errors,
        )
    build_script = admission.get("build_script", {})
    build_rs = package / "build.rs"
    if os.path.lexists(build_rs):
        _exact(build_script.get("mode"), "committed_in_package", "verifier build.rs mode", errors)
        _exact(build_script.get("path"), str(build_rs), "verifier build.rs path", errors)
        try:
            _exact(build_script.get("sha256"), sha256_path(build_rs), "verifier build.rs hash", errors)
        except OSError as exc:
            errors.append(f"verifier build.rs cannot be hashed: {exc}")
        directives = build_script.get("observed_directives", [])
        if not isinstance(directives, list) or not all(isinstance(item, str) for item in directives):
            errors.append("verifier build.rs observed directives are invalid")
        else:
            for directive in directives:
                if not any(
                    directive.startswith(prefix)
                    for prefix in VERIFIER_BUILD_ALLOWED_DIRECTIVE_PREFIXES
                ):
                    errors.append(f"verifier build.rs emitted forbidden directive {directive}")
            required_env = {
                "cargo:rustc-env=P192_WCM_EMBEDDED_VERIFIER_DIRTY=false",
                "cargo:rustc-env=P192_WCM_EMBEDDED_BUILD_PROFILE=release",
                "cargo:rustc-env=P192_WCM_EMBEDDED_PROTOCOL_COMMIT=" + decision["protocol_commit"],
                "cargo:rustc-env=P192_WCM_EMBEDDED_VERIFIER_COMMIT=" + decision["verifier_commit"],
            }
            _require(
                required_env.issubset(set(directives)),
                "verifier build.rs output lacks exact embedded release/commit bindings", errors,
            )
        _exact(
            build_script.get("allowed_directive_prefixes"),
            VERIFIER_BUILD_ALLOWED_DIRECTIVE_PREFIXES,
            "verifier build.rs directive allowlist", errors,
        )
    else:
        _exact(
            build_script,
            {"mode": "absent", "path": None, "sha256": None,
             "allowed_directive_prefixes": [], "observed_directives": []},
            "verifier absent build.rs receipt", errors,
        )

    if not runtime:
        return errors
    for label, path, recorded in (
        ("cargo", cargo_path, cargo_identity),
        ("rustc", rustc_path, rustc_identity),
    ):
        _validate_regular_file(path, f"verifier build {label} tool", errors, executable=True)
        try:
            current = _file_identity(path)
            _exact(current, recorded, f"verifier build {label} identity", errors)
            _exact(current.get("link_count"), 1, f"verifier build {label} link count", errors)
        except (OSError, ValueError) as exc:
            errors.append(f"verifier build {label} identity unavailable: {exc}")
    for label, directory in (("CARGO_HOME", cargo_home), ("target dir", target_dir)):
        _require(directory.is_absolute(), f"verifier build {label} is not absolute", errors)
        _require(_symlink_component(directory) is None, f"verifier build {label} has a symlink component", errors)
        _require(directory.is_dir(), f"verifier build {label} is not a directory", errors)
    _require(
        repository not in target_dir.parents and target_dir != repository,
        "verifier build target dir is inside verifier repository", errors,
    )
    for candidate in _cargo_config_candidate_paths(package, cargo_home):
        _require(
            not os.path.lexists(candidate),
            f"verifier Cargo configuration/source override exists: {candidate}", errors,
        )
    current_directories: list[dict[str, Any]] = []
    for directory in expected_directories:
        try:
            current_directories.append(_directory_identity(directory))
        except (OSError, ValueError) as exc:
            errors.append(f"verifier Cargo config search directory unavailable {directory}: {exc}")
    _exact(
        recorded_directories, current_directories,
        "verifier Cargo retained config-search directory identities", errors,
    )
    metadata_error_count = len(errors)
    completed = _run_bounded_process(
        expected_metadata_argv, cwd=package, environment=expected_environment,
        timeout_seconds=VERIFIER_TOOL_TIMEOUT_SECONDS,
        output_cap=VERIFIER_TOOL_OUTPUT_CAP,
    )
    if completed is None:
        errors.append(
            "verifier bound cargo metadata exceeded its time/output cap or could not execute"
        )
        return errors
    _exact(completed.returncode, 0, "verifier bound cargo metadata exit code", errors)
    _exact(completed.stderr, b"", "verifier bound cargo metadata stderr", errors)
    _exact(len(completed.stdout), admission.get("cargo_metadata_byte_length"), "verifier cargo metadata byte length", errors)
    _exact(sha256_bytes(completed.stdout), admission.get("cargo_metadata_sha256"), "verifier cargo metadata hash", errors)
    if len(errors) != metadata_error_count:
        return errors
    try:
        metadata = json.loads(completed.stdout)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"verifier cargo metadata is invalid JSON: {exc}")
        return errors
    if not isinstance(metadata, dict):
        return errors + ["verifier cargo metadata root is not an object"]
    workspace_members = metadata.get("workspace_members")
    _require(
        isinstance(workspace_members, list) and len(workspace_members) == 1,
        "verifier cargo metadata does not have exactly one workspace member", errors,
    )
    if not isinstance(workspace_members, list) or len(workspace_members) != 1:
        return errors
    root_id = workspace_members[0]
    _exact(admission.get("cargo_metadata_root_package_id"), root_id, "verifier cargo metadata root package", errors)
    _exact(metadata.get("workspace_root"), str(package), "verifier cargo metadata workspace root", errors)
    target_rows = _metadata_root_target_rows(metadata, root_id)
    _exact(admission.get("cargo_metadata_root_targets"), target_rows, "verifier cargo metadata root targets", errors)
    _exact(
        admission.get("cargo_metadata_resolve_sha256"),
        sha256_bytes(canonical_json_bytes(metadata.get("resolve"))),
        "verifier cargo metadata resolve graph", errors,
    )
    selected = [
        row for row in target_rows
        if row.get("name") == "p192_weighted_cm_verify"
        and row.get("kind") == ["bin"]
    ]
    _exact(len(selected), 1, "verifier cargo metadata selected bin count", errors)
    if selected:
        _exact(selected[0].get("src_path"), str(package / "src/main.rs"), "verifier selected bin source", errors)
        _exact(selected[0].get("required_features"), [], "verifier selected bin required features", errors)
    for row in target_rows:
        src_path = Path(str(row.get("src_path", "/invalid")))
        _require(
            src_path == package or package in src_path.parents,
            f"verifier cargo metadata root target escapes package: {src_path}", errors,
        )
        try:
            identity = _file_identity(src_path)
            _exact(identity.get("link_count"), 1, f"verifier cargo target link count {src_path}", errors)
        except (OSError, ValueError) as exc:
            errors.append(f"verifier cargo target identity unavailable {src_path}: {exc}")
    errors.extend(_selected_bin_dep_info_errors(decision, admission))
    return errors


def _verifier_build_custody(decision: dict[str, Any]) -> dict[str, Any]:
    admission = decision["verifier_build_admission"]
    return {
        "admission_sha256": _verifier_build_admission_sha256(admission),
        "tool_identities_before": {
            "cargo": admission["cargo_identity"],
            "rustc": admission["rustc_identity"],
        },
        "tool_identities_after": {
            "cargo": admission["cargo_identity"],
            "rustc": admission["rustc_identity"],
        },
        "config_search_directory_identities_before": admission[
            "config_search_directory_identities"
        ],
        "config_search_directory_identities_after": admission[
            "config_search_directory_identities"
        ],
        "selected_bin_dep_info_before": admission["selected_bin_dep_info"],
        "selected_bin_dep_info_after": admission["selected_bin_dep_info"],
        "config_candidates_absent_before": True,
        "config_candidates_absent_after": True,
        "tools_opened_once_nofollow": True,
        "tool_fds_retained_through_terminal": True,
        "config_directory_fds_retained_through_terminal": True,
    }


def _run_bounded_process(
    command: list[str], *, cwd: Path, environment: dict[str, str],
    timeout_seconds: float, output_cap: int,
) -> subprocess.CompletedProcess[bytes] | None:
    """Run a bound tool with streaming output caps and process-group cleanup."""
    process: subprocess.Popen[bytes] | None = None
    selector = selectors.DefaultSelector()
    try:
        process = subprocess.Popen(
            command, cwd=cwd, env=environment, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            start_new_session=True,
        )
        assert process.stdout is not None and process.stderr is not None
        streams = {"stdout": bytearray(), "stderr": bytearray()}
        for name, stream in (("stdout", process.stdout), ("stderr", process.stderr)):
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ, name)
        deadline = time.monotonic() + timeout_seconds
        failed = False
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                failed = True
                break
            for key, _mask in selector.select(min(remaining, 0.1)):
                stream = key.fileobj
                name = key.data
                try:
                    chunk = os.read(stream.fileno(), 65536)
                except BlockingIOError:
                    continue
                if not chunk:
                    selector.unregister(stream)
                    stream.close()
                    continue
                streams[name].extend(chunk)
                if len(streams[name]) > output_cap:
                    failed = True
                    break
            if failed:
                break
        if failed:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            return None
        return_code = process.wait(timeout=max(0.0, deadline - time.monotonic()))
        return subprocess.CompletedProcess(
            command, return_code, bytes(streams["stdout"]), bytes(streams["stderr"]),
        )
    except (OSError, subprocess.TimeoutExpired):
        if process is not None and process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except OSError:
                pass
            process.wait()
        return None
    finally:
        selector.close()


def _git(
    repository: Path, arguments: list[str], *, input_bytes: bytes | None = None,
    literal_pathspecs: bool = True,
) -> subprocess.CompletedProcess[bytes] | None:
    command = [
        "/usr/bin/git", "--no-pager", "--no-replace-objects",
        "-c", "core.fsmonitor=false",
        "-c", "core.hooksPath=/dev/null",
        "-c", "core.attributesFile=/dev/null",
        "-c", "core.commitGraph=false",
        "-c", "protocol.ext.allow=never",
        "-c", "diff.external=",
        "-C", str(repository), *arguments,
    ]
    environment = {
        "LC_ALL": "C",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_NO_REPLACE_OBJECTS": "1",
        "GIT_OPTIONAL_LOCKS": "0",
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_PAGER": "cat",
        "GIT_ATTR_NOSYSTEM": "1",
        "GIT_GRAFT_FILE": "/dev/null",
        "GIT_NO_LAZY_FETCH": "1",
    }
    if literal_pathspecs:
        environment["GIT_LITERAL_PATHSPECS"] = "1"
    if input_bytes is not None and len(input_bytes) > GIT_COMMAND_OUTPUT_CAP:
        return None
    process: subprocess.Popen[bytes] | None = None
    selector = selectors.DefaultSelector()
    try:
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE if input_bytes is not None else subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=environment, start_new_session=True,
        )
        assert process.stdout is not None and process.stderr is not None
        streams = {"stdout": bytearray(), "stderr": bytearray()}
        for name, stream in (("stdout", process.stdout), ("stderr", process.stderr)):
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ, (name, None))
        input_offset = 0
        if input_bytes is not None:
            assert process.stdin is not None
            os.set_blocking(process.stdin.fileno(), False)
            selector.register(process.stdin, selectors.EVENT_WRITE, ("stdin", None))
        deadline = time.monotonic() + GIT_COMMAND_TIMEOUT_SECONDS
        failed = False
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                failed = True
                break
            events = selector.select(min(remaining, 0.1))
            for key, mask in events:
                name, _ = key.data
                stream = key.fileobj
                if name == "stdin":
                    assert input_bytes is not None
                    try:
                        count = os.write(
                            stream.fileno(), input_bytes[input_offset:input_offset + 65536],
                        )
                    except BlockingIOError:
                        continue
                    except BrokenPipeError:
                        selector.unregister(stream)
                        stream.close()
                        continue
                    input_offset += count
                    if input_offset == len(input_bytes):
                        selector.unregister(stream)
                        stream.close()
                elif mask & selectors.EVENT_READ:
                    try:
                        chunk = os.read(stream.fileno(), 65536)
                    except BlockingIOError:
                        continue
                    if not chunk:
                        selector.unregister(stream)
                        stream.close()
                        continue
                    streams[name].extend(chunk)
                    if len(streams[name]) > GIT_COMMAND_OUTPUT_CAP:
                        failed = True
                        break
            if failed:
                break
        if failed:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            return None
        return_code = process.wait(timeout=max(0.0, deadline - time.monotonic()))
        return subprocess.CompletedProcess(
            command, return_code, bytes(streams["stdout"]), bytes(streams["stderr"]),
        )
    except (OSError, subprocess.TimeoutExpired):
        if process is not None and process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except OSError:
                pass
            process.wait()
        return None
    finally:
        selector.close()


def _git_stdout(repository: Path, arguments: list[str], label: str, errors: list[str]) -> bytes | None:
    result = _git(repository, arguments)
    if result is None or result.returncode != 0:
        detail = "git unavailable" if result is None else result.stderr.decode("utf-8", "replace").strip()
        errors.append(f"{label}: {detail or 'Git command failed'}")
        return None
    if len(result.stdout) > GIT_COMMAND_OUTPUT_CAP or len(result.stderr) > GIT_COMMAND_OUTPUT_CAP:
        errors.append(f"{label}: Git command output exceeds frozen cap")
        return None
    return result.stdout


def _git_tree_entry(
    repository: Path, commit: str, relative: str, label: str, errors: list[str],
) -> tuple[str, str, str] | None:
    output = _git_stdout(repository, ["ls-tree", "-z", commit, "--", relative], label, errors)
    if output is None:
        return None
    records = [record for record in output.split(b"\0") if record]
    if len(records) != 1:
        errors.append(f"{label}: expected exactly one Git tree entry")
        return None
    try:
        header, encoded_path = records[0].split(b"\t", 1)
        mode, kind, object_id = header.decode("ascii").split(" ")
        path = encoded_path.decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        errors.append(f"{label}: malformed Git tree entry")
        return None
    _exact(path, relative, f"{label} path", errors)
    return mode, kind, object_id


def _git_object_id(kind: str, raw: bytes) -> str:
    return hashlib.sha1(
        kind.encode("ascii") + b" " + str(len(raw)).encode("ascii") + b"\0" + raw
    ).hexdigest()


def _object_custody_by_oid(
    rows: Iterable[dict[str, Any]], label: str, errors: list[str],
) -> dict[str, dict[str, Any]] | None:
    """Deduplicate only byte-identical custody rows for one advertised OID."""
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        object_id = row.get("object_id")
        if not isinstance(object_id, str):
            errors.append(f"{label}: object custody row lacks an object id")
            return None
        prior = result.get(object_id)
        if prior is not None and prior != row:
            errors.append(
                f"{label}: one Git object id has conflicting kind/length/SHA-256 "
                f"custody: {object_id}"
            )
            return None
        result[object_id] = row
    return result


def _historical_repository_object_custody(
    repository: Path,
    commit_profiles: Iterable[tuple[str, tuple[dict[str, Any], ...]]],
    label: str,
    errors: list[str],
) -> list[dict[str, Any]] | None:
    """Capture the exact historical object closure actually used by admission.

    Every listed commit and every tree reachable from it is admitted.  For a
    commit with one or more profiles, existing regular leaves selected by any
    profile and every committed ``.gitattributes`` policy blob are admitted as
    payloads too.  Ordinary omitted leaf payloads and gitlink targets remain
    deliberately outside the execution custody boundary.
    """
    rows: list[dict[str, Any]] = []
    payload_ids: set[str] = set()
    for commit, profiles in commit_profiles:
        topology = _raw_commit_tree_topology(
            repository, commit, f"{label} {commit}", errors,
            object_custody=rows,
        )
        if topology is None:
            return None
        if not profiles:
            continue
        leaf_tree = _leaf_tree(topology)
        for relative, (mode, object_id) in leaf_tree.items():
            if mode not in {"100644", "100755"}:
                continue
            if Path(relative).name == ".gitattributes":
                payload_ids.add(object_id)
                continue
            for profile in profiles:
                exact = set(profile.get("materialized_exact_paths", []))
                exact.update(profile.get("mutable_output_exact_paths", []))
                prefixes = tuple(profile.get("materialized_subtree_prefixes", []))
                if relative in exact or any(
                    relative == prefix or relative.startswith(prefix + "/")
                    for prefix in prefixes
                ):
                    payload_ids.add(object_id)
                    break
    payload_rows = _git_blob_payload_custody_map(
        repository, payload_ids, f"{label} selected/policy payloads", errors,
    )
    if payload_rows is None:
        return None
    rows.extend(payload_rows)
    by_oid = _object_custody_by_oid(rows, f"{label} object closure", errors)
    if by_oid is None:
        return None
    return [by_oid[object_id] for object_id in sorted(by_oid)]


def _git_objects(
    repository: Path, object_ids: Iterable[str], label: str, errors: list[str],
) -> dict[str, tuple[str, bytes]] | None:
    """Read and self-hash a deduplicated bounded set of raw Git objects."""
    ordered = sorted(set(object_ids))
    if not ordered:
        return {}
    if any(re.fullmatch(r"[0-9a-f]{40}", object_id) is None for object_id in ordered):
        errors.append(f"{label}: invalid Git object id")
        return None
    request = b"".join(object_id.encode("ascii") + b"\n" for object_id in ordered)
    result = _git(repository, ["cat-file", "--batch"], input_bytes=request)
    if result is None or result.returncode != 0:
        detail = "git unavailable" if result is None else result.stderr.decode(
            "utf-8", "replace",
        ).strip()
        errors.append(f"{label}: {detail or 'Git cat-file batch failed'}")
        return None
    output = result.stdout
    objects: dict[str, tuple[str, bytes]] = {}
    offset = 0
    aggregate = 0
    for expected_object_id in ordered:
        newline = output.find(b"\n", offset)
        if newline < 0:
            errors.append(f"{label}: truncated Git cat-file header")
            return None
        try:
            returned_object_id, kind, raw_size = output[offset:newline].decode(
                "ascii",
            ).split(" ")
            size = int(raw_size, 10)
        except (UnicodeDecodeError, ValueError):
            errors.append(f"{label}: malformed Git cat-file header")
            return None
        if (
            returned_object_id != expected_object_id
            or kind not in {"blob", "tree", "commit"} or size < 0
        ):
            errors.append(f"{label}: unexpected Git cat-file binding")
            return None
        aggregate += size
        if aggregate > PROTOCOL_TOPOLOGY_AGGREGATE_BLOB_BYTES_CAP:
            errors.append(f"{label}: aggregate Git object bytes exceed frozen cap")
            return None
        start = newline + 1
        end = start + size
        if end >= len(output) or output[end:end + 1] != b"\n":
            errors.append(f"{label}: truncated Git cat-file object")
            return None
        raw = output[start:end]
        if _git_object_id(kind, raw) != expected_object_id:
            errors.append(
                f"{label}: Git {kind} bytes do not self-hash to advertised object id "
                f"{expected_object_id}"
            )
            return None
        objects[expected_object_id] = (kind, raw)
        offset = end + 1
    if offset != len(output):
        errors.append(f"{label}: trailing Git cat-file output")
        return None
    return objects


def _git_blob(repository: Path, object_id: str, label: str, errors: list[str]) -> bytes | None:
    objects = _git_objects(repository, [object_id], label, errors)
    if objects is None or object_id not in objects:
        return None
    kind, raw = objects[object_id]
    _exact(kind, "blob", f"{label} Git object type", errors)
    return raw if kind == "blob" else None


def _git_blobs(
    repository: Path, object_ids: Iterable[str], label: str, errors: list[str],
) -> dict[str, bytes] | None:
    objects = _git_objects(repository, object_ids, label, errors)
    if objects is None:
        return None
    blobs: dict[str, bytes] = {}
    for object_id, (kind, raw) in objects.items():
        if kind != "blob":
            errors.append(f"{label}: object {object_id} is not a blob")
            return None
        blobs[object_id] = raw
    return blobs


def _git_blob_payload_custody_map(
    repository: Path, object_ids: Iterable[str], label: str,
    errors: list[str],
) -> list[dict[str, Any]] | None:
    """Stream a collision-resistant map without the structural 256 MiB buffer."""
    sizes = _git_blob_sizes(repository, object_ids, f"{label} size preflight", errors)
    if sizes is None:
        return None
    size_errors = _distinct_blob_payload_size_errors(sizes, label)
    errors.extend(size_errors)
    if size_errors:
        return None
    streamed = _stream_git_blob_batch_file_equality(
        repository, sizes, {object_id: [] for object_id in sizes}, label, errors,
        object_kinds={object_id: "blob" for object_id in sizes},
    )
    if streamed is None:
        return None
    return [
        {
            "object_id": object_id,
            "kind": "blob",
            "byte_length": sizes[object_id],
            "sha256": streamed[object_id],
        }
        for object_id in sorted(streamed)
    ]


def _git_blob_sizes(
    repository: Path, object_ids: Iterable[str], label: str,
    errors: list[str],
) -> dict[str, int] | None:
    ordered = sorted(set(object_ids))
    if not ordered:
        return {}
    request = b"".join(item.encode("ascii") + b"\n" for item in ordered)
    result = _git(
        repository,
        ["cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize)"],
        input_bytes=request,
    )
    if result is None or result.returncode != 0:
        detail = "git unavailable" if result is None else result.stderr.decode(
            "utf-8", "replace",
        ).strip()
        errors.append(f"{label}: {detail or 'Git size preflight failed'}")
        return None
    records = result.stdout.splitlines()
    if len(records) != len(ordered):
        errors.append(f"{label}: Git size preflight record count differs")
        return None
    sizes: dict[str, int] = {}
    for expected, record in zip(ordered, records):
        try:
            object_id, kind, raw_size = record.decode("ascii").split(" ")
            size = int(raw_size, 10)
        except (UnicodeDecodeError, ValueError):
            errors.append(f"{label}: malformed Git size preflight record")
            return None
        if object_id != expected or kind != "blob" or size < 0:
            errors.append(f"{label}: unexpected Git size/type binding")
            return None
        sizes[object_id] = size
    return sizes


def _distinct_blob_payload_size_errors(
    sizes: dict[str, int], label: str,
) -> list[str]:
    """Apply the per-object and deduplicated committed-payload caps."""
    errors: list[str] = []
    oversized = sorted(
        object_id for object_id, size in sizes.items()
        if size > EVIDENCE_ARTIFACT_BYTE_CAP
    )
    if oversized:
        errors.append(f"{label}: blob exceeds 512 MiB cap: {oversized}")
    if sum(sizes.values()) > COMMITTED_DISTINCT_BLOB_BYTE_CAP:
        errors.append(f"{label}: distinct blob payload exceeds 1 GiB cap")
    return errors


def _stream_git_blob_file_equality(
    repository: Path, object_id: str, expected_size: int, path: Path,
    label: str, errors: list[str],
) -> None:
    """Stream one large committed blob against a retained nofollow file."""
    try:
        descriptor = os.open(
            path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK,
        )
        opened = os.fstat(descriptor)
    except OSError as exc:
        errors.append(f"{label}: cannot open evidence file: {exc}")
        return
    if (
        not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1
        or opened.st_size != expected_size
    ):
        errors.append(f"{label}: evidence file identity/size differs")
        os.close(descriptor)
        return
    command = [
        "/usr/bin/git", "--no-pager", "--no-replace-objects",
        "-c", "core.fsmonitor=false", "-c", "core.hooksPath=/dev/null",
        "-c", "core.attributesFile=/dev/null", "-c", "core.commitGraph=false",
        "-c", "protocol.ext.allow=never", "-c", "diff.external=",
        "-C", str(repository), "cat-file", "blob", object_id,
    ]
    environment = {
        "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_NO_REPLACE_OBJECTS": "1",
        "GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0",
        "GIT_PAGER": "cat", "GIT_ATTR_NOSYSTEM": "1",
        "GIT_GRAFT_FILE": "/dev/null", "GIT_NO_LAZY_FETCH": "1",
        "GIT_LITERAL_PATHSPECS": "1",
    }
    process: subprocess.Popen[bytes] | None = None
    selector = selectors.DefaultSelector()
    total = 0
    stderr = bytearray()
    git_hash = hashlib.sha1(
        b"blob " + str(expected_size).encode("ascii") + b"\0"
    )
    failed = False
    try:
        process = subprocess.Popen(
            command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, env=environment, start_new_session=True,
        )
        assert process.stdout is not None and process.stderr is not None
        for name, stream in (("stdout", process.stdout), ("stderr", process.stderr)):
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ, name)
        deadline = time.monotonic() + GIT_COMMAND_TIMEOUT_SECONDS
        while selector.get_map() and not failed:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                errors.append(f"{label}: streaming Git blob comparison timed out")
                failed = True
                break
            for key, _mask in selector.select(min(remaining, 0.1)):
                stream = key.fileobj
                try:
                    chunk = os.read(stream.fileno(), 1024 * 1024)
                except BlockingIOError:
                    continue
                if not chunk:
                    selector.unregister(stream)
                    stream.close()
                    continue
                if key.data == "stderr":
                    stderr.extend(chunk)
                    if len(stderr) > 1048576:
                        errors.append(f"{label}: Git stderr exceeds 1 MiB cap")
                        failed = True
                    continue
                total += len(chunk)
                if total > expected_size:
                    errors.append(f"{label}: Git blob exceeds advertised size")
                    failed = True
                    break
                file_chunk = bytearray()
                while len(file_chunk) < len(chunk):
                    part = os.read(descriptor, len(chunk) - len(file_chunk))
                    if not part:
                        break
                    file_chunk.extend(part)
                if bytes(file_chunk) != chunk:
                    errors.append(f"{label}: committed blob/file bytes differ")
                    failed = True
                    break
                git_hash.update(chunk)
        if failed:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            return
        return_code = process.wait(timeout=max(0.0, deadline - time.monotonic()))
        if return_code != 0:
            errors.append(
                f"{label}: Git blob stream failed: "
                f"{stderr.decode('utf-8', 'replace').strip()}"
            )
        if total != expected_size or os.read(descriptor, 1) != b"":
            errors.append(f"{label}: streamed blob/file length differs")
        if git_hash.hexdigest() != object_id:
            errors.append(f"{label}: streamed blob fails advertised object self-hash")
        terminal = os.fstat(descriptor)
        path_terminal = os.stat(path, follow_symlinks=False)
        stable_fields = (
            "st_dev", "st_ino", "st_mode", "st_nlink", "st_size",
            "st_mtime_ns", "st_ctime_ns",
        )
        if any(
            getattr(terminal, field) != getattr(opened, field)
            or getattr(path_terminal, field) != getattr(opened, field)
            for field in stable_fields
        ):
            errors.append(f"{label}: evidence file changed during streaming comparison")
    except (OSError, subprocess.TimeoutExpired) as exc:
        errors.append(f"{label}: streaming Git blob comparison failed: {exc}")
        if process is not None and process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except OSError:
                pass
            process.wait()
    finally:
        selector.close()
        os.close(descriptor)


def _stream_git_blob_batch_file_equality(
    repository: Path, sizes: dict[str, int],
    file_bindings: dict[str, list[tuple[Path, str]]],
    label: str, errors: list[str], *,
    object_kinds: dict[str, str] | None = None,
    expected_payload_sha256: dict[str, str] | None = None,
) -> dict[str, str] | None:
    """Make one terminal Git process stream/self-hash admitted objects.

    A single batch process is important: a later Git process must not be able
    to mutate an object already verified by an earlier per-path process.  Some
    policy blobs intentionally have no worktree binding because they are
    omitted `S` entries; those bytes are still streamed and self-hashed.
    """
    object_kinds = object_kinds or {object_id: "blob" for object_id in sizes}
    expected_payload_sha256 = expected_payload_sha256 or {}
    ordered = sorted(sizes)
    if not ordered:
        return {}
    descriptors: dict[str, list[tuple[int, Path, str, os.stat_result]]] = {}
    for object_id in ordered:
        if re.fullmatch(r"[0-9a-f]{40}", object_id) is None:
            errors.append(f"{label}: invalid Git object id")
            return
        expected_size = sizes[object_id]
        expected_kind = object_kinds.get(object_id)
        if expected_kind not in {"blob", "tree", "commit"}:
            errors.append(f"{label}: invalid Git object kind {object_id}")
            return None
        if expected_kind != "blob" and file_bindings.get(object_id):
            errors.append(f"{label}: non-blob object has a worktree file binding")
            return None
        if expected_size < 0 or expected_size > EVIDENCE_ARTIFACT_BYTE_CAP:
            errors.append(f"{label}: invalid or oversized Git blob {object_id}")
            return
        opened_rows: list[tuple[int, Path, str, os.stat_result]] = []
        for path, binding_label in file_bindings.get(object_id, []):
            try:
                descriptor = os.open(
                    path,
                    os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK,
                )
                opened = os.fstat(descriptor)
            except OSError as exc:
                errors.append(
                    f"{binding_label}: cannot open terminal evidence file: {exc}"
                )
                for prior, _path, _label, _opened in opened_rows:
                    os.close(prior)
                for rows in descriptors.values():
                    for prior, _path, _label, _opened in rows:
                        os.close(prior)
                return
            if (
                not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1
                or opened.st_size != expected_size
            ):
                errors.append(f"{binding_label}: terminal file identity/size differs")
                os.close(descriptor)
                for prior, _path, _label, _opened in opened_rows:
                    os.close(prior)
                for rows in descriptors.values():
                    for prior, _path, _label, _opened in rows:
                        os.close(prior)
                return
            opened_rows.append((descriptor, path, binding_label, opened))
        descriptors[object_id] = opened_rows

    command = [
        "/usr/bin/git", "--no-pager", "--no-replace-objects",
        "-c", "core.fsmonitor=false", "-c", "core.hooksPath=/dev/null",
        "-c", "core.attributesFile=/dev/null", "-c", "core.commitGraph=false",
        "-c", "protocol.ext.allow=never", "-c", "diff.external=",
        "-C", str(repository), "cat-file", "--batch",
    ]
    environment = {
        "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_NO_REPLACE_OBJECTS": "1",
        "GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0",
        "GIT_PAGER": "cat", "GIT_ATTR_NOSYSTEM": "1",
        "GIT_GRAFT_FILE": "/dev/null", "GIT_NO_LAZY_FETCH": "1",
        "GIT_LITERAL_PATHSPECS": "1",
    }
    process: subprocess.Popen[bytes] | None = None
    selector = selectors.DefaultSelector()
    stderr = bytearray()
    buffer = bytearray()
    index = 0
    current_id: str | None = None
    current_remaining = 0
    current_hash: Any = None
    current_sha256: Any = None
    payload_sha256: dict[str, str] = {}
    expect_delimiter = False
    request_index = 0
    request_offset = 0
    failed = False

    def fail(message: str) -> None:
        nonlocal failed
        if not failed:
            errors.append(f"{label}: {message}")
        failed = True

    try:
        process = subprocess.Popen(
            command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, env=environment, start_new_session=True,
        )
        assert process.stdin is not None and process.stdout is not None
        assert process.stderr is not None
        deadline = time.monotonic() + GIT_COMMAND_TIMEOUT_SECONDS
        os.set_blocking(process.stdin.fileno(), False)
        selector.register(process.stdin, selectors.EVENT_WRITE, "stdin")
        for name, stream in (("stdout", process.stdout), ("stderr", process.stderr)):
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ, name)
        while selector.get_map() and not failed:
            remaining_time = deadline - time.monotonic()
            if remaining_time <= 0:
                fail("terminal Git blob batch timed out")
                break
            for key, _mask in selector.select(min(remaining_time, 0.1)):
                stream = key.fileobj
                if key.data == "stdin":
                    request_line = ordered[request_index].encode("ascii") + b"\n"
                    try:
                        written = os.write(
                            stream.fileno(), request_line[request_offset:],
                        )
                    except BlockingIOError:
                        continue
                    if written <= 0:
                        fail("terminal Git blob batch request write failed")
                        break
                    request_offset += written
                    if request_offset == len(request_line):
                        selector.unregister(stream)
                        request_offset = 0
                    continue
                try:
                    chunk = os.read(stream.fileno(), 1024 * 1024)
                except BlockingIOError:
                    continue
                if not chunk:
                    selector.unregister(stream)
                    stream.close()
                    continue
                if key.data == "stderr":
                    stderr.extend(chunk)
                    if len(stderr) > 1048576:
                        fail("terminal Git blob batch stderr exceeds 1 MiB")
                    continue
                buffer.extend(chunk)
                while buffer and not failed:
                    if current_id is None:
                        newline = buffer.find(b"\n")
                        if newline < 0:
                            if len(buffer) > 256:
                                fail("terminal Git blob batch header exceeds cap")
                            break
                        header = bytes(buffer[:newline])
                        del buffer[:newline + 1]
                        if index >= len(ordered):
                            fail("terminal Git blob batch returned extra object")
                            break
                        try:
                            returned_id, kind, raw_size = header.decode("ascii").split(" ")
                            size = int(raw_size, 10)
                        except (UnicodeDecodeError, ValueError):
                            fail("terminal Git blob batch header is malformed")
                            break
                        expected_id = ordered[index]
                        if (
                            returned_id != expected_id
                            or kind != object_kinds[expected_id]
                            or size != sizes[expected_id]
                        ):
                            fail("terminal Git blob batch binding differs")
                            break
                        current_id = expected_id
                        current_remaining = size
                        current_hash = hashlib.sha1(
                            kind.encode("ascii") + b" "
                            + str(size).encode("ascii") + b"\0"
                        )
                        current_sha256 = hashlib.sha256()
                        expect_delimiter = size == 0
                    elif current_remaining:
                        take = min(current_remaining, len(buffer))
                        if take == 0:
                            break
                        body = bytes(buffer[:take])
                        del buffer[:take]
                        current_hash.update(body)
                        current_sha256.update(body)
                        for descriptor, _path, binding_label, _opened in descriptors[current_id]:
                            file_chunk = bytearray()
                            while len(file_chunk) < take:
                                part = os.read(descriptor, take - len(file_chunk))
                                if not part:
                                    break
                                file_chunk.extend(part)
                            if bytes(file_chunk) != body:
                                fail(f"{binding_label}: committed blob/file bytes differ")
                                break
                        current_remaining -= take
                        expect_delimiter = current_remaining == 0
                    elif expect_delimiter:
                        if buffer[:1] != b"\n":
                            fail("terminal Git blob batch object delimiter differs")
                            break
                        del buffer[:1]
                        assert current_id is not None
                        if current_hash.hexdigest() != current_id:
                            fail(
                                "terminal Git blob bytes do not self-hash to "
                                f"advertised object id {current_id}"
                            )
                            break
                        observed_sha256 = current_sha256.hexdigest()
                        payload_sha256[current_id] = observed_sha256
                        expected_sha256 = expected_payload_sha256.get(current_id)
                        if (
                            expected_sha256 is not None
                            and observed_sha256 != expected_sha256
                        ):
                            fail(
                                "terminal Git object SHA-256 differs from initial "
                                f"custody map: {current_id}"
                            )
                            break
                        for descriptor, _path, binding_label, _opened in descriptors[current_id]:
                            if os.read(descriptor, 1) != b"":
                                fail(f"{binding_label}: terminal file has trailing bytes")
                                break
                        index += 1
                        current_id = None
                        current_hash = None
                        current_sha256 = None
                        expect_delimiter = False
                        if index < len(ordered):
                            request_index = index
                            selector.register(
                                process.stdin, selectors.EVENT_WRITE, "stdin",
                            )
                        else:
                            process.stdin.close()
        if failed:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
            process.wait()
        else:
            return_code = process.wait(timeout=max(0.0, deadline - time.monotonic()))
            if return_code != 0:
                fail(
                    "terminal Git blob batch failed: "
                    + stderr.decode("utf-8", "replace").strip()
                )
            if index != len(ordered) or current_id is not None or buffer:
                fail("terminal Git blob batch output is truncated or has trailing bytes")
        for rows in descriptors.values():
            for descriptor, path, binding_label, opened in rows:
                terminal = os.fstat(descriptor)
                path_terminal = os.stat(path, follow_symlinks=False)
                stable_fields = (
                    "st_dev", "st_ino", "st_mode", "st_nlink", "st_size",
                    "st_mtime_ns", "st_ctime_ns",
                )
                if any(
                    getattr(terminal, field) != getattr(opened, field)
                    or getattr(path_terminal, field) != getattr(opened, field)
                    for field in stable_fields
                ):
                    errors.append(
                        f"{binding_label}: terminal evidence file changed during batch"
                    )
    except (OSError, subprocess.TimeoutExpired) as exc:
        fail(f"terminal Git blob batch failed: {exc}")
        if process is not None and process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except OSError:
                pass
            process.wait()
    finally:
        selector.close()
        for rows in descriptors.values():
            for descriptor, _path, _binding_label, _opened in rows:
                try:
                    os.close(descriptor)
                except OSError:
                    pass
    if failed or index != len(ordered):
        return None
    return payload_sha256


def _git_tree_entries(
    repository: Path, commit: str, relative: str, label: str, errors: list[str],
) -> dict[str, tuple[str, str, str]] | None:
    output = _git_stdout(
        repository, ["ls-tree", "-r", "-z", commit, "--", relative], label, errors,
    )
    if output is None:
        return None
    result: dict[str, tuple[str, str, str]] = {}
    for record in (item for item in output.split(b"\0") if item):
        try:
            header, encoded_path = record.split(b"\t", 1)
            mode, kind, object_id = header.decode("ascii").split(" ")
            path = encoded_path.decode("utf-8")
        except (ValueError, UnicodeDecodeError):
            errors.append(f"{label}: malformed Git tree record")
            return None
        if path in result:
            errors.append(f"{label}: duplicate Git tree path {path}")
            return None
        result[path] = (mode, kind, object_id)
    return result


def _tracked_index_flag_errors(
    repository: Path, relative_paths: list[str], label: str,
) -> list[str]:
    errors: list[str] = []
    if not relative_paths:
        return errors
    output = _git_stdout(
        repository, ["ls-files", "-v", "-z", "--", *relative_paths],
        f"{label} index flags", errors,
    )
    if output is None:
        return errors
    observed: set[str] = set()
    for record in (item for item in output.split(b"\0") if item):
        if len(record) < 3 or record[1:2] != b" ":
            errors.append(f"{label}: malformed ls-files -v record")
            continue
        tag = chr(record[0])
        try:
            path = record[2:].decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"{label}: non-UTF-8 tracked path")
            continue
        observed.add(path)
        if tag != "H":
            errors.append(
                f"{label}: tracked path has forbidden index flag {tag}: {path}"
            )
    missing = sorted(set(relative_paths) - observed)
    if missing:
        errors.append(f"{label}: tracked input absent from index flag inventory: {missing}")
    return errors


def _repository_index_flag_errors(repository: Path, label: str) -> list[str]:
    errors: list[str] = []
    output = _git_stdout(
        repository, ["ls-files", "-v", "-z"], f"{label} repository index flags", errors,
    )
    if output is None:
        return errors
    for record in (item for item in output.split(b"\0") if item):
        if len(record) < 3 or record[1:2] != b" ":
            errors.append(f"{label}: malformed repository ls-files -v record")
            continue
        tag = chr(record[0])
        if tag != "H":
            path = record[2:].decode("utf-8", "replace")
            errors.append(f"{label}: repository path has forbidden index flag {tag}: {path}")
    return errors


def _raw_protocol_head_tree(
    repository: Path, head: str, errors: list[str], *,
    object_custody: list[dict[str, Any]] | None = None,
) -> dict[str, tuple[str, str]] | None:
    """Return the self-hashed raw HEAD leaf map without consulting attributes."""
    topology = _raw_commit_tree_topology(
        repository, head, "protocol topology raw HEAD", errors,
        object_custody=object_custody,
    )
    if topology is None:
        return None
    result: dict[str, tuple[str, str]] = {}
    tree_paths: set[str] = set()
    namespace_keys: dict[str, str] = {}
    for relative, (mode, kind, object_id) in topology.items():
        normalized_parts = tuple(
            unicodedata.normalize("NFC", part).casefold()
            for part in Path(relative).parts
        )
        namespace_key = "/".join(normalized_parts)
        prior = namespace_keys.get(namespace_key)
        if prior is not None and prior != relative:
            errors.append(
                "protocol topology raw HEAD has case/Unicode namespace alias: "
                f"{prior} and {relative}"
            )
        else:
            namespace_keys[namespace_key] = relative
        if any(part == ".git" for part in normalized_parts):
            errors.append(
                f"protocol topology raw HEAD path aliases Git administration: {relative}"
            )
        if kind == "tree" and mode == "040000":
            tree_paths.add(relative)
            continue
        admitted = (
            (kind == "blob" and mode in {"100644", "100755", "120000"})
            or (kind == "commit" and mode == "160000")
        )
        if not admitted:
            errors.append(
                "protocol topology raw HEAD entry has an unsupported mode/type: "
                f"{relative} ({mode} {kind})"
            )
        if Path(relative).name == ".gitmodules":
            errors.append(
                f"protocol topology raw HEAD contains forbidden .gitmodules: {relative}"
            )
        result[relative] = (mode, object_id)
    implied_directories: set[str] = set()
    for relative in result:
        parent = Path(relative).parent
        while parent != Path("."):
            implied_directories.add(parent.as_posix())
            parent = parent.parent
    _exact(
        tree_paths, implied_directories,
        "protocol topology raw HEAD directory tree inventory", errors,
    )
    return result


def _raw_protocol_stage_zero_index(
    repository: Path, errors: list[str],
) -> dict[str, tuple[str, str]] | None:
    """Return the raw index blob map and reject every non-stage-zero entry."""
    output = _git_stdout(
        repository, ["ls-files", "--sparse", "--stage", "-z"],
        "protocol topology raw index", errors,
    )
    if output is None:
        return None
    result: dict[str, tuple[str, str]] = {}
    record_count = 0
    for record in (item for item in output.split(b"\0") if item):
        record_count += 1
        if record_count > PROTOCOL_TOPOLOGY_ENTRY_CAP:
            errors.append("protocol topology raw index exceeds entry cap")
            return None
        try:
            header, encoded_path = record.split(b"\t", 1)
            mode, object_id, stage = header.decode("ascii").split(" ")
            relative = encoded_path.decode("utf-8")
        except (ValueError, UnicodeDecodeError):
            errors.append("protocol topology raw index has a malformed record")
            return None
        candidate = Path(relative)
        if (
            not relative or candidate.is_absolute()
            or candidate.as_posix() != relative
            or any(part in {"", ".", ".."} for part in candidate.parts)
        ):
            errors.append(f"protocol topology raw index path is not normalized: {relative!r}")
            continue
        if len(encoded_path) > PROTOCOL_TOPOLOGY_PATH_BYTES_CAP:
            errors.append(f"protocol topology raw index path exceeds byte cap: {relative}")
        if len(candidate.parts) > PROTOCOL_TOPOLOGY_DEPTH_CAP:
            errors.append(f"protocol topology raw index path exceeds depth cap: {relative}")
        if stage != "0":
            errors.append(
                f"protocol topology raw index has forbidden non-stage-zero entry: "
                f"stage {stage} {relative}"
            )
            continue
        if relative in result:
            errors.append(f"protocol topology raw index has duplicate stage-zero path: {relative}")
            continue
        if mode not in {"100644", "100755", "120000", "160000"}:
            errors.append(
                f"protocol topology raw index entry has forbidden mode {mode}: {relative}"
            )
        if re.fullmatch(r"[0-9a-f]{40}", object_id) is None:
            errors.append(f"protocol topology raw index blob ID is invalid: {relative}")
        result[relative] = (mode, object_id)
    return result


def _selective_profile_parts(
    profile: dict[str, Any], errors: list[str],
) -> tuple[
    set[str], tuple[str, ...], tuple[str, ...], tuple[str, ...], set[str]
] | None:
    exact = profile.get("materialized_exact_paths")
    prefixes = profile.get("materialized_subtree_prefixes")
    required_prefixes = profile.get("required_existing_subtree_prefixes")
    mutable_prefixes = profile.get("mutable_output_subtree_prefixes")
    mutable_exact = profile.get("mutable_output_exact_paths")
    if (
        not isinstance(exact, list) or not all(isinstance(item, str) for item in exact)
        or not isinstance(prefixes, list)
        or not all(isinstance(item, str) for item in prefixes)
        or not isinstance(required_prefixes, list)
        or not all(isinstance(item, str) for item in required_prefixes)
        or not isinstance(mutable_prefixes, list)
        or not all(isinstance(item, str) for item in mutable_prefixes)
        or not isinstance(mutable_exact, list)
        or not all(isinstance(item, str) for item in mutable_exact)
    ):
        errors.append("exact sparse profile path lists are invalid")
        return None
    normalized_exact: set[str] = set()
    normalized_mutable_exact: set[str] = set()
    normalized_prefixes: list[str] = []
    for label, values, destination in (
        ("exact path", exact, normalized_exact),
        ("mutable exact path", mutable_exact, normalized_mutable_exact),
        ("subtree prefix", prefixes, normalized_prefixes),
    ):
        for value in values:
            candidate = Path(value)
            if (
                not value or candidate.is_absolute()
                or candidate.as_posix() != value
                or any(part in {"", ".", ".."} for part in candidate.parts)
            ):
                errors.append(f"exact sparse profile {label} is not normalized: {value!r}")
                continue
            destination.add(value) if isinstance(destination, set) else destination.append(value)
    if errors:
        return None
    prefix_tuple = tuple(sorted(set(normalized_prefixes)))
    required_tuple = tuple(sorted(set(required_prefixes)))
    mutable_tuple = tuple(sorted(set(mutable_prefixes)))
    _require(
        set(required_tuple).issubset(prefix_tuple),
        "sealed selective required prefixes are outside materialized prefixes", errors,
    )
    _require(
        set(mutable_tuple).issubset(prefix_tuple),
        "sealed selective mutable prefixes are outside materialized prefixes", errors,
    )
    _require(
        set(required_tuple).isdisjoint(mutable_tuple),
        "sealed selective required and mutable prefixes overlap", errors,
    )
    _require(
        normalized_exact.isdisjoint(normalized_mutable_exact),
        "sealed selective required and mutable exact paths overlap", errors,
    )
    return (
        normalized_exact, prefix_tuple, required_tuple, mutable_tuple,
        normalized_mutable_exact,
    )


def _sparse_selected_paths(
    head_tree: dict[str, tuple[str, str]], profile: dict[str, Any],
    errors: list[str],
) -> set[str] | None:
    parts = _selective_profile_parts(profile, errors)
    if parts is None:
        return None
    exact, prefixes, required_prefixes, _mutable_prefixes, mutable_exact = parts
    selected: set[str] = set()
    for relative, (mode, _object_id) in head_tree.items():
        admitted = relative in exact or relative in mutable_exact or any(
            relative == prefix or relative.startswith(prefix + "/")
            for prefix in prefixes
        )
        if not admitted:
            continue
        if mode not in {"100644", "100755"}:
            errors.append(
                f"exact sparse materialized path is not a regular blob: {relative} ({mode})"
            )
            continue
        selected.add(relative)
    missing_exact = sorted(
        path for path in exact if path not in head_tree
        and path not in SOURCE_SPARSE_EXACT_PATHS
    )
    if missing_exact:
        errors.append(f"exact sparse required tracked paths are absent from HEAD: {missing_exact}")
    missing_required_prefixes = sorted(
        prefix for prefix in required_prefixes
        if not any(
            relative == prefix or relative.startswith(prefix + "/")
            for relative in head_tree
        )
    )
    if missing_required_prefixes:
        errors.append(
            "sealed selective required subtrees are absent from HEAD: "
            f"{missing_required_prefixes}"
        )
    return selected


def _raw_index_v3_flag_errors(
    repository: Path, head_tree: dict[str, tuple[str, str]],
    selected: set[str], label: str,
) -> list[str]:
    """Parse the sealed v3 index and require the exact H/S flag state.

    Porcelain H/S tags intentionally collapse CE_INTENT_TO_ADD and other
    extended states.  The execution checkout therefore admits only a v3
    index with no extensions: ordinary selected entries have no flags beyond
    the pathname length, while omitted entries have exactly CE_EXTENDED plus
    CE_SKIP_WORKTREE.  The trailing index checksum is independently verified.
    """
    errors: list[str] = []
    try:
        raw = _read_regular_file_bytes(
            repository / ".git/index", f"{label} raw v3 index",
            byte_cap=PROTOCOL_INDEX_BYTES_CAP,
        )
    except (OSError, ValueError) as exc:
        return [f"{label}: raw v3 index cannot be read: {exc}"]
    if len(raw) < 32:
        return [f"{label}: raw v3 index is truncated"]
    body, recorded_checksum = raw[:-20], raw[-20:]
    _exact(
        recorded_checksum, hashlib.sha1(body).digest(),
        f"{label} raw v3 index checksum", errors,
    )
    if body[:4] != b"DIRC":
        errors.append(f"{label}: raw index signature is not DIRC")
        return errors
    version = int.from_bytes(body[4:8], "big")
    count = int.from_bytes(body[8:12], "big")
    _exact(version, 3, f"{label} raw index version", errors)
    if count > PROTOCOL_TOPOLOGY_ENTRY_CAP:
        errors.append(f"{label}: raw index entry count exceeds cap")
        return errors
    offset = 12
    observed: dict[str, tuple[str, str, bool]] = {}
    previous_encoded_path: bytes | None = None
    for entry_number in range(count):
        entry_start = offset
        # Ten 32-bit stat/mode words, a 20-byte object id, and 16-bit flags.
        if offset + 62 > len(body):
            errors.append(f"{label}: raw index entry {entry_number} is truncated")
            return errors
        mode_value = int.from_bytes(body[offset + 24:offset + 28], "big")
        object_id = body[offset + 40:offset + 60].hex()
        flags = int.from_bytes(body[offset + 60:offset + 62], "big")
        offset += 62
        extended = bool(flags & 0x4000)
        extended_flags = 0
        if extended:
            if offset + 2 > len(body):
                errors.append(f"{label}: raw extended index entry is truncated")
                return errors
            extended_flags = int.from_bytes(body[offset:offset + 2], "big")
            offset += 2
        nul = body.find(b"\0", offset)
        if nul < 0:
            errors.append(f"{label}: raw index pathname is not NUL terminated")
            return errors
        encoded_path = body[offset:nul]
        if len(encoded_path) > PROTOCOL_TOPOLOGY_PATH_BYTES_CAP:
            errors.append(f"{label}: raw index pathname exceeds byte cap")
            return errors
        try:
            relative = encoded_path.decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"{label}: raw index pathname is not UTF-8")
            return errors
        if relative in observed:
            errors.append(f"{label}: raw index has duplicate path {relative}")
            return errors
        if (
            previous_encoded_path is not None
            and previous_encoded_path >= encoded_path
        ):
            errors.append(
                f"{label}: raw index path order is not strictly canonical: {relative}"
            )
            return errors
        previous_encoded_path = encoded_path
        name_length = flags & 0x0fff
        _exact(
            name_length, min(len(encoded_path), 0x0fff),
            f"{label} raw index pathname length {relative}", errors,
        )
        stage = (flags >> 12) & 0x3
        assume_valid = bool(flags & 0x8000)
        _exact(stage, 0, f"{label} raw index stage {relative}", errors)
        _exact(
            assume_valid, False,
            f"{label} raw index assume-valid flag {relative}", errors,
        )
        selected_entry = relative in selected
        expected_primary = name_length | (0 if selected_entry else 0x4000)
        expected_extended = 0 if selected_entry else 0x4000
        _exact(
            flags, expected_primary,
            f"{label} raw index primary flags {relative}", errors,
        )
        _exact(
            extended_flags, expected_extended,
            f"{label} raw index extended flags {relative}", errors,
        )
        mode = f"{mode_value:06o}"
        observed[relative] = (mode, object_id, selected_entry)
        # v3 entries are padded to an eight-byte boundary from entry start.
        entry_length = nul + 1 - entry_start
        next_offset = entry_start + ((entry_length + 7) & ~7)
        if any(body[nul + 1:next_offset]):
            errors.append(
                f"{label}: raw index alignment padding is nonzero: {relative}"
            )
            return errors
        offset = next_offset
        if offset > len(body):
            errors.append(f"{label}: raw index entry padding is truncated")
            return errors
    # A canonical execution index has no cache or state extensions.  Trusted
    # preparation strips TREE/EOIE/IEOT as well as REUC/FSMN/UNTR/link/sdir
    # and recomputes the checksum, then performs no index-mutating operation.
    _exact(offset, len(body), f"{label} raw index extension absence", errors)
    _exact(set(observed), set(head_tree), f"{label} raw index path set", errors)
    for relative in sorted(set(observed) & set(head_tree)):
        mode, object_id, selected_entry = observed[relative]
        _exact(
            (mode, object_id), head_tree[relative],
            f"{label} raw index HEAD binding {relative}", errors,
        )
        _exact(
            selected_entry, relative in selected,
            f"{label} raw index selected state {relative}", errors,
        )
    return errors


def _sparse_index_flag_errors(
    repository: Path, head_tree: dict[str, tuple[str, str]],
    selected: set[str], label: str,
) -> list[str]:
    errors: list[str] = []
    errors.extend(_raw_index_v3_flag_errors(
        repository, head_tree, selected, label,
    ))
    expected_tags = {
        relative: ("H" if relative in selected else "S")
        for relative in head_tree
    }
    raw = _git_stdout(
        repository, ["ls-files", "--sparse", "--stage", "-v", "-z"],
        f"{label} exact sparse index", errors,
    )
    observed: dict[str, tuple[str, str, str, str]] = {}
    if raw is not None:
        for record in (item for item in raw.split(b"\0") if item):
            try:
                tag_raw, remainder = record[:1], record[2:]
                if record[1:2] != b" ":
                    raise ValueError
                header, encoded_path = remainder.split(b"\t", 1)
                mode, object_id, stage = header.decode("ascii").split(" ")
                relative = encoded_path.decode("utf-8")
                tag = tag_raw.decode("ascii")
            except (UnicodeDecodeError, ValueError):
                errors.append(f"{label}: malformed exact sparse index record")
                continue
            if relative in observed:
                errors.append(f"{label}: duplicate exact sparse index path {relative}")
                continue
            observed[relative] = (tag, mode, object_id, stage)
        _exact(set(observed), set(head_tree), f"{label} exact sparse full-index path set", errors)
        for relative in sorted(set(observed) & set(head_tree)):
            tag, mode, object_id, stage = observed[relative]
            _exact(stage, "0", f"{label} exact sparse stage {relative}", errors)
            _exact(
                (mode, object_id), head_tree[relative],
                f"{label} exact sparse HEAD/index binding {relative}", errors,
            )
            _exact(tag, expected_tags[relative], f"{label} exact sparse H/S tag {relative}", errors)
            if mode == "040000":
                errors.append(f"{label}: sparse-index directory entry is forbidden: {relative}")
    fsmonitor_raw = _git_stdout(
        repository, ["ls-files", "-f", "-v", "-z"],
        f"{label} fsmonitor/index flags", errors,
    )
    if fsmonitor_raw is not None:
        fsmonitor_tags: dict[str, str] = {}
        for record in (item for item in fsmonitor_raw.split(b"\0") if item):
            if len(record) < 3 or record[1:2] != b" ":
                errors.append(f"{label}: malformed fsmonitor/index flag record")
                continue
            try:
                relative = record[2:].decode("utf-8")
                tag = record[:1].decode("ascii")
            except UnicodeDecodeError:
                errors.append(f"{label}: non-UTF-8 fsmonitor/index path")
                continue
            fsmonitor_tags[relative] = tag
        _exact(set(fsmonitor_tags), set(head_tree), f"{label} fsmonitor full-index path set", errors)
        for relative in sorted(set(fsmonitor_tags) & set(head_tree)):
            _exact(
                fsmonitor_tags[relative], expected_tags[relative],
                f"{label} fsmonitor/assume-unchanged tag {relative}", errors,
            )
    resolve_undo = _git_stdout(
        repository, ["ls-files", "--resolve-undo", "-z"],
        f"{label} resolve-undo index extension", errors,
    )
    if resolve_undo is not None:
        _exact(
            resolve_undo, b"", f"{label} resolve-undo index extension absence", errors,
        )
    return errors


def _git_admin_topology_errors(git_dir: Path) -> list[str]:
    """Nofollow-walk the entire Git administration tree before invoking Git."""
    errors: list[str] = []
    try:
        metadata = os.lstat(git_dir)
        if not stat.S_ISDIR(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode):
            return ["repository .git is not a real nofollow directory"]
    except OSError as exc:
        return [f"repository .git cannot be lstatted: {exc}"]
    admin_inodes: dict[tuple[int, int], str] = {}
    pending: list[tuple[Path, int]] = [(git_dir, 0)]
    admin_count = 0
    aggregate_path_bytes = 0
    while pending:
        directory, depth = pending.pop()
        if depth > PROTOCOL_TOPOLOGY_DEPTH_CAP:
            errors.append(f"repository Git administration exceeds depth cap: {directory}")
            continue
        try:
            entries = _bounded_sorted_scandir(
                directory, PROTOCOL_TOPOLOGY_ENTRY_CAP - admin_count,
                "repository Git administration",
            )
        except ValueError as exc:
            errors.append(str(exc))
            return errors
        for entry in entries:
            admin_count += 1
            path = Path(entry.path)
            relative = path.relative_to(git_dir).as_posix()
            root_component = relative.split("/", 1)[0]
            if (
                root_component in {
                    "MERGE_HEAD", "MERGE_MSG", "MERGE_MODE", "AUTO_MERGE",
                    "CHERRY_PICK_HEAD", "REVERT_HEAD", "REBASE_HEAD",
                    "SQUASH_MSG", "sequencer", "rebase-apply", "rebase-merge",
                }
                or root_component.startswith("BISECT_")
            ):
                errors.append(
                    f"repository Git in-progress operation state is forbidden: {relative}"
                )
            encoded = relative.encode("utf-8", "surrogateescape")
            if len(encoded) > PROTOCOL_TOPOLOGY_PATH_BYTES_CAP:
                errors.append(f"repository Git administration path exceeds byte cap: {relative}")
                continue
            aggregate_path_bytes += len(encoded)
            if aggregate_path_bytes > FILESYSTEM_WALK_AGGREGATE_PATH_BYTES_CAP:
                errors.append("repository Git administration exceeds aggregate path-byte cap")
                return errors
            try:
                item_metadata = entry.stat(follow_symlinks=False)
            except OSError as exc:
                errors.append(f"repository Git administration cannot lstat {relative}: {exc}")
                continue
            if stat.S_ISLNK(item_metadata.st_mode):
                errors.append(f"repository Git administration symlink is forbidden: {relative}")
            elif stat.S_ISDIR(item_metadata.st_mode):
                pending.append((path, depth + 1))
            elif stat.S_ISREG(item_metadata.st_mode):
                if entry.name.endswith(".promisor"):
                    errors.append(
                        f"repository Git administration promisor marker is forbidden: {relative}"
                    )
                if entry.name.startswith("sharedindex."):
                    errors.append(
                        f"repository Git administration split-index file is forbidden: {relative}"
                    )
                if entry.name.endswith(".lock"):
                    errors.append(
                        f"repository Git administration lock file is forbidden: {relative}"
                    )
                if item_metadata.st_nlink != 1:
                    errors.append(
                        f"repository Git administration file link count is not one: {relative}"
                    )
                inode = (item_metadata.st_dev, item_metadata.st_ino)
                if inode in admin_inodes:
                    errors.append(
                        f"repository Git administration files alias one inode: "
                        f"{admin_inodes[inode]} and {relative}"
                    )
                else:
                    admin_inodes[inode] = relative
            else:
                errors.append(f"repository Git administration special entry is forbidden: {relative}")
    return errors


def _repository_git_storage_and_conversion_errors(
    repository: Path, head_tree: dict[str, tuple[str, str]],
    profile: dict[str, Any],
) -> list[str]:
    """Require a standalone local object store and no conversion code routes."""
    errors: list[str] = []
    git_dir = repository / ".git"
    admin_errors = _git_admin_topology_errors(git_dir)
    errors.extend(admin_errors)
    if admin_errors:
        return errors
    for relative in ("objects", "objects/info", "objects/pack", "refs"):
        candidate = git_dir / relative
        try:
            candidate_metadata = os.lstat(candidate)
            _require(
                stat.S_ISDIR(candidate_metadata.st_mode)
                and not stat.S_ISLNK(candidate_metadata.st_mode),
                f"repository .git/{relative} is not a real nofollow directory", errors,
            )
        except OSError as exc:
            errors.append(f"repository .git/{relative} cannot be lstatted: {exc}")
    for relative in ("commondir", "gitdir", "modules", "worktrees", "shallow"):
        if os.path.lexists(git_dir / relative):
            errors.append(f"repository linked/common Git administration path exists: .git/{relative}")
    for relative in (
        "objects/info/alternates", "objects/info/http-alternates",
        "info/attributes", "info/exclude", "info/sparse-checkout",
        "config.worktree",
    ):
        candidate = git_dir / relative
        if os.path.lexists(candidate):
            errors.append(f"repository forbidden Git storage/config path exists: .git/{relative}")
    config = git_dir / "config"
    try:
        config_raw = _read_regular_file_bytes(
            config, "repository local Git config", byte_cap=1048576,
        )
    except (OSError, ValueError) as exc:
        errors.append(f"repository local Git config cannot be read: {exc}")
        config_raw = b""
    _exact(
        config_raw, MINIMAL_STANDALONE_GIT_CONFIG,
        "repository canonical minimal standalone Git config", errors,
    )
    try:
        config_text = config_raw.decode("utf-8").lower()
    except UnicodeDecodeError:
        errors.append("repository local Git config is not UTF-8")
        config_text = ""
    forbidden_sections = re.compile(
        r"(?m)^\s*\[\s*(?:filter|diff|include|includeif)(?:\s|\"|\.)"
    )
    if forbidden_sections.search(config_text):
        errors.append("repository local Git config contains filter/diff/include execution route")
    for key in (
        "attributesfile", "excludesfile", "partialclone", "promisor",
        "textconv", "smudge", "clean", "process",
    ):
        if re.search(rf"(?m)^\s*{re.escape(key)}\s*=", config_text):
            errors.append(f"repository local Git config contains forbidden key {key}")
    attribute_paths = sorted(
        path for path in head_tree if Path(path).name == ".gitattributes"
    )
    attribute_object_ids = {
        head_tree[relative][1] for relative in attribute_paths
        if head_tree[relative][0] in {"100644", "100755"}
    }
    attribute_blobs = _git_blobs(
        repository, attribute_object_ids,
        "repository committed attribute policy batch", errors,
    )
    if attribute_blobs is None:
        attribute_blobs = {}
    for relative in attribute_paths:
        mode, object_id = head_tree[relative]
        if mode not in {"100644", "100755"}:
            errors.append(f"repository attributes entry is not a regular blob: {relative}")
            continue
        raw = attribute_blobs.get(object_id)
        if raw is None:
            errors.append(
                f"repository committed attributes blob is unavailable: {relative}"
            )
            continue
        if len(raw) > 16777216:
            errors.append(f"repository attributes exceed byte cap: {relative}")
            continue
        try:
            text_value = raw.decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"repository attributes are not UTF-8: {relative}")
            continue
        # Attribute declarations are committed input, not executable drivers.
        # Real protocol/native origins contain inert `filter=lfs`, `diff=lfs`,
        # and `-diff` declarations.  They cannot dispatch a helper because the
        # exact local config contains no driver, global/system attributes and
        # config are disabled, info/attributes is absent, and admission never
        # performs checkout/merge after the sealed H/S index is established.
        # Selected worktree bytes are still compared directly with these
        # self-hashed Git blobs, so built-in conversion cannot substitute an
        # execution input either.
        _ = text_value.splitlines()
    if errors:
        return errors
    for arguments, label in (
        (["rev-parse", "--absolute-git-dir"], "absolute Git dir"),
        (["rev-parse", "--git-common-dir"], "Git common dir"),
        (["rev-parse", "--git-path", "objects"], "Git object dir"),
    ):
        raw = _git_stdout(repository, arguments, f"repository {label}", errors)
        if raw is None:
            continue
        value = raw.rstrip(b"\n").decode("utf-8", "replace")
        candidate = Path(value)
        if not candidate.is_absolute():
            candidate = repository / candidate
        try:
            canonical = candidate.resolve(strict=True)
            expected = git_dir.resolve(strict=True)
        except OSError as exc:
            errors.append(f"repository {label} cannot be resolved: {exc}")
            continue
        expected_value = git_dir / "objects" if label == "Git object dir" else git_dir
        try:
            expected = expected_value.resolve(strict=True)
        except OSError as exc:
            errors.append(f"repository expected {label} cannot be resolved: {exc}")
            continue
        _exact(canonical, expected, f"repository standalone {label}", errors)
    errors.extend(_git_admin_topology_errors(git_dir))
    return errors


def _repository_git_preflight_errors(
    repository: Path, profile: dict[str, Any],
) -> list[str]:
    """Raw nofollow gate run before any repository-config-sensitive Git command."""
    errors: list[str] = []
    linked = _symlink_component(repository)
    if linked is not None:
        return [f"repository Git preflight has a symlink component: {linked}"]
    try:
        repository_metadata = os.lstat(repository)
    except OSError as exc:
        return [f"repository Git preflight cannot lstat repository root: {exc}"]
    if (
        not stat.S_ISDIR(repository_metadata.st_mode)
        or stat.S_ISLNK(repository_metadata.st_mode)
    ):
        return ["repository Git preflight root is not a real nofollow directory"]
    git_dir = repository / ".git"
    admin_errors = _git_admin_topology_errors(git_dir)
    errors.extend(admin_errors)
    if admin_errors:
        return errors
    for relative in ("", "objects", "objects/info", "objects/pack", "refs"):
        path = git_dir / relative if relative else git_dir
        try:
            metadata = os.lstat(path)
        except OSError as exc:
            errors.append(f"repository Git preflight cannot lstat .git/{relative}: {exc}")
            continue
        _require(
            stat.S_ISDIR(metadata.st_mode) and not stat.S_ISLNK(metadata.st_mode),
            f"repository Git preflight .git/{relative} is not a real nofollow directory",
            errors,
        )
    config = git_dir / "config"
    try:
        raw = _read_regular_file_bytes(
            config, "repository Git preflight config",
            byte_cap=1048576,
        )
        _exact(
            raw, MINIMAL_STANDALONE_GIT_CONFIG,
            "repository canonical minimal standalone Git config", errors,
        )
    except (OSError, ValueError) as exc:
        errors.append(f"repository Git preflight config cannot be opened: {exc}")
    _selective_profile_parts(profile, errors)
    for relative in (
        "commondir", "gitdir", "modules", "worktrees", "shallow",
        "config.worktree",
        "objects/info/alternates", "objects/info/http-alternates",
        "info/attributes", "info/exclude", "info/sparse-checkout",
    ):
        if os.path.lexists(git_dir / relative):
            errors.append(f"repository Git preflight forbidden path exists: .git/{relative}")
    return errors


def _git_head_index_storage_identities(repository: Path) -> list[dict[str, Any]]:
    """Snapshot Git control files without invoking Git or following symlinks."""
    git_dir = repository / ".git"
    head_path = git_dir / "HEAD"
    head_raw = _read_regular_file_bytes(
        head_path, "repository Git HEAD", byte_cap=1048576,
    )
    paths = [head_path, git_dir / "index", git_dir / "config"]
    if head_raw.startswith(b"ref: "):
        match = re.fullmatch(rb"ref: (refs/heads/[^\x00-\x20]+)\n", head_raw)
        if match is None:
            raise ValueError("repository Git HEAD reference bytes are not canonical")
        try:
            reference = match.group(1).decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("repository Git HEAD reference is not UTF-8") from exc
        reference_path = Path(reference)
        if (
            reference_path.is_absolute()
            or reference_path.as_posix() != reference
            or not reference.startswith("refs/")
            or any(part in {"", ".", ".."} for part in reference_path.parts)
        ):
            raise ValueError("repository Git HEAD reference is not canonical")
        loose_ref = git_dir / reference_path
        if os.path.lexists(loose_ref):
            loose_raw = _read_regular_file_bytes(
                loose_ref, "repository Git HEAD loose reference",
                byte_cap=1048576,
            )
            if re.fullmatch(rb"[0-9a-f]{40}\n", loose_raw) is None:
                raise ValueError(
                    "repository Git HEAD loose reference is not a direct 40-hex ID"
                )
            paths.append(loose_ref)
        else:
            raise ValueError(
                "repository Git HEAD must resolve through one direct loose reference"
            )
    elif re.fullmatch(rb"[0-9a-f]{40}\n", head_raw) is None:
        raise ValueError("repository Git HEAD is neither canonical ref nor detached ID")
    packed_refs = git_dir / "packed-refs"
    if os.path.lexists(packed_refs) and packed_refs not in paths:
        paths.append(packed_refs)
    return [_file_identity(path) for path in paths]


def _git_head_commit_no_git(repository: Path) -> str:
    """Resolve the frozen detached/direct-loose HEAD without invoking Git."""
    git_dir = repository / ".git"
    head_raw = _read_regular_file_bytes(
        git_dir / "HEAD", "repository Git HEAD", byte_cap=1048576,
    )
    detached = re.fullmatch(rb"([0-9a-f]{40})\n", head_raw)
    if detached is not None:
        return detached.group(1).decode("ascii")
    symbolic = re.fullmatch(rb"ref: (refs/heads/[^\x00-\x20]+)\n", head_raw)
    if symbolic is None:
        raise ValueError("repository Git HEAD bytes are not canonical")
    reference = symbolic.group(1).decode("utf-8")
    reference_path = Path(reference)
    if (
        reference_path.is_absolute()
        or reference_path.as_posix() != reference
        or any(part in {"", ".", ".."} for part in reference_path.parts)
    ):
        raise ValueError("repository Git HEAD reference is not canonical")
    raw = _read_regular_file_bytes(
        git_dir / reference_path, "repository Git HEAD loose reference",
        byte_cap=1048576,
    )
    match = re.fullmatch(rb"([0-9a-f]{40})\n", raw)
    if match is None:
        raise ValueError("repository Git HEAD loose reference is not a direct ID")
    return match.group(1).decode("ascii")


def _protocol_repository_topology_errors(
    repository: Path, head: str, excluded_output_roots: tuple[Path, ...],
    profile: dict[str, Any], *, forbid_tracked_excluded: bool = False,
    additional_object_custody: Iterable[dict[str, Any]] = (),
) -> list[str]:
    """Bind raw HEAD, index, and nofollow worktree topology outside output roots."""
    errors = _repository_git_preflight_errors(repository, profile)
    if errors:
        return errors
    try:
        entry_git_storage = _git_head_index_storage_identities(repository)
        _exact(
            _git_head_commit_no_git(repository), head,
            "repository topology HEAD argument/storage binding", errors,
        )
    except (OSError, ValueError) as exc:
        return [f"repository Git control identity unavailable: {exc}"]

    def finish() -> list[str]:
        # This no-Git admin/config scan is deliberately the final repository
        # operation.  It catches a helper that mutates .git during any of the
        # raw-object/index queries above, including creation of a late lock.
        terminal = _repository_git_preflight_errors(repository, profile)
        errors.extend(
            f"terminal repository administration: {item}" for item in terminal
        )
        try:
            _exact(
                _git_head_index_storage_identities(repository),
                entry_git_storage,
                "terminal repository HEAD/index/config/ref identities", errors,
            )
            _exact(
                _git_head_commit_no_git(repository), head,
                "terminal repository HEAD argument/storage binding", errors,
            )
        except (OSError, ValueError) as exc:
            errors.append(
                f"terminal repository Git control identity unavailable: {exc}"
            )
        return errors

    head_object_rows: list[dict[str, Any]] = []
    head_tree = _raw_protocol_head_tree(
        repository, head, errors, object_custody=head_object_rows,
    )
    index_tree = _raw_protocol_stage_zero_index(repository, errors)
    if head_tree is None or index_tree is None:
        return finish()
    attribute_object_ids = {
        object_id for relative, (mode, object_id) in head_tree.items()
        if Path(relative).name == ".gitattributes"
        and mode in {"100644", "100755"}
    }
    initial_attribute_blobs = _git_blobs(
        repository, attribute_object_ids,
        "repository topology initial attribute policy blobs", errors,
    )
    if initial_attribute_blobs is None:
        return finish()
    errors.extend(_repository_git_storage_and_conversion_errors(
        repository, head_tree, profile,
    ))

    missing_index = sorted(set(head_tree) - set(index_tree))
    unexpected_index = sorted(set(index_tree) - set(head_tree))
    if missing_index:
        errors.append(f"protocol topology raw index is missing HEAD paths: {missing_index}")
    if unexpected_index:
        errors.append(f"protocol topology raw index has paths absent from HEAD: {unexpected_index}")
    for relative in sorted(set(head_tree) & set(index_tree)):
        _exact(
            index_tree[relative], head_tree[relative],
            f"protocol topology raw HEAD/index blob and mode {relative}", errors,
        )

    excluded_relatives: set[str] = set()
    for output_root in excluded_output_roots:
        try:
            relative = output_root.relative_to(repository).as_posix()
        except ValueError:
            errors.append(f"protocol topology output root is outside repository: {output_root}")
            continue
        if not relative or relative == "." or relative.startswith("../"):
            errors.append(f"protocol topology output root is not a strict child: {output_root}")
            continue
        excluded_relatives.add(relative)

    def excluded(relative: str) -> bool:
        return any(
            relative == root or relative.startswith(root + "/")
            for root in excluded_relatives
        )

    if forbid_tracked_excluded:
        tracked_beneath_excluded = sorted(
            relative for relative in set(head_tree) | set(index_tree)
            if excluded(relative)
        )
        if tracked_beneath_excluded:
            errors.append(
                "repository topology has tracked paths beneath a mutable output root: "
                f"{tracked_beneath_excluded}"
            )

    selected = _sparse_selected_paths(head_tree, profile, errors)
    if selected is None:
        return finish()
    tracked_unselected_under_excluded = sorted(
        relative for relative in head_tree
        if excluded(relative) and relative not in selected
    )
    if tracked_unselected_under_excluded:
        errors.append(
            "repository topology has tracked omitted paths beneath an excluded root: "
            f"{tracked_unselected_under_excluded}"
        )
    errors.extend(_sparse_index_flag_errors(
        repository, head_tree, selected, "repository topology",
    ))
    worktree_head = {
        relative: head_tree[relative] for relative in selected
        if not excluded(relative)
    }
    # Only execution-relevant sparse leaves are required locally.  Stream
    # selected payloads so a valid 512 MiB leaf cannot hit the structural
    # 256 MiB command-output cap.  Attribute policy blobs remain a separately
    # bounded small raw-byte set because their text is parsed above.
    selected_object_ids = {
        object_id for _mode, object_id in worktree_head.values()
    }
    selected_sizes = _git_blob_sizes(
        repository, selected_object_ids,
        "protocol topology selected blob size preflight", errors,
    )
    if selected_sizes is None:
        return finish()
    if any(size > EVIDENCE_ARTIFACT_BYTE_CAP for size in selected_sizes.values()):
        errors.append("protocol topology selected blob exceeds 512 MiB cap")
        return finish()
    if sum(selected_sizes.values()) > COMMITTED_DISTINCT_BLOB_BYTE_CAP:
        errors.append("protocol topology selected blob payload exceeds 1 GiB cap")
        return finish()
    selected_bindings: dict[str, list[tuple[Path, str]]] = {
        object_id: [] for object_id in selected_sizes
    }
    for relative, (_mode, object_id) in worktree_head.items():
        selected_bindings.setdefault(object_id, []).append((
            repository / relative,
            f"protocol topology initial selected file {relative}",
        ))
    selected_sha256 = _stream_git_blob_batch_file_equality(
        repository, selected_sizes, selected_bindings,
        "protocol topology initial selected blob stream", errors,
        object_kinds={object_id: "blob" for object_id in selected_sizes},
    )
    if selected_sha256 is None:
        return finish()
    combined_closure_rows = [*additional_object_custody, *head_object_rows]
    for object_id, digest in selected_sha256.items():
        combined_closure_rows.append({
            "object_id": object_id, "kind": "blob",
            "byte_length": selected_sizes[object_id], "sha256": digest,
        })
    for object_id, raw in initial_attribute_blobs.items():
        combined_closure_rows.append({
            "object_id": object_id, "kind": "blob",
            "byte_length": len(raw), "sha256": sha256_bytes(raw),
        })
    closure_rows = _object_custody_by_oid(
        combined_closure_rows, "protocol topology admitted closure", errors,
    )
    if closure_rows is None:
        return finish()
    closure_size_errors = _distinct_blob_payload_size_errors(
        {
            object_id: int(row["byte_length"])
            for object_id, row in closure_rows.items()
            if row.get("kind") == "blob"
        },
        "protocol topology admitted closure",
    )
    errors.extend(closure_size_errors)
    if closure_size_errors:
        return finish()
    closure_file_bindings: dict[str, list[tuple[Path, str]]] = {
        object_id: [] for object_id in closure_rows
    }
    for relative, (_mode, object_id) in worktree_head.items():
        closure_file_bindings.setdefault(object_id, []).append((
            repository / relative,
            f"protocol topology terminal selected file {relative}",
        ))
    terminal_closure = _stream_git_blob_batch_file_equality(
        repository,
        {
            object_id: int(row["byte_length"])
            for object_id, row in closure_rows.items()
        },
        closure_file_bindings,
        "protocol topology terminal admitted-object closure", errors,
        object_kinds={
            object_id: str(row["kind"])
            for object_id, row in closure_rows.items()
        },
        expected_payload_sha256={
            object_id: str(row["sha256"])
            for object_id, row in closure_rows.items()
        },
    )
    if terminal_closure is None:
        return finish()
    expected_directories: set[str] = set()
    for relative in worktree_head:
        parent = Path(relative).parent
        while parent != Path("."):
            expected_directories.add(parent.as_posix())
            parent = parent.parent

    observed_files: set[str] = set()
    observed_directories: set[str] = set()
    observed_inodes: dict[tuple[int, int], str] = {}
    pending: list[tuple[Path, str]] = [(repository, "")]
    entry_count = 0
    aggregate_path_bytes = 0
    while pending:
        directory, prefix = pending.pop()
        try:
            entries = _bounded_sorted_scandir(
                directory, PROTOCOL_TOPOLOGY_ENTRY_CAP - entry_count,
                "protocol topology worktree",
            )
        except ValueError as exc:
            errors.append(str(exc))
            return finish()
        for entry in entries:
            if not prefix and entry.name == ".git":
                continue
            entry_count += 1
            if entry_count > PROTOCOL_TOPOLOGY_ENTRY_CAP:
                errors.append("protocol topology worktree exceeds entry cap")
                return finish()
            relative = f"{prefix}/{entry.name}" if prefix else entry.name
            try:
                encoded_relative = relative.encode("utf-8")
            except UnicodeEncodeError:
                errors.append(f"protocol topology worktree has non-UTF-8 path: {relative!r}")
                continue
            if len(encoded_relative) > PROTOCOL_TOPOLOGY_PATH_BYTES_CAP:
                errors.append(f"protocol topology worktree path exceeds byte cap: {relative}")
                continue
            aggregate_path_bytes += len(encoded_relative)
            if aggregate_path_bytes > FILESYSTEM_WALK_AGGREGATE_PATH_BYTES_CAP:
                errors.append("protocol topology worktree exceeds aggregate path-byte cap")
                return finish()
            if len(Path(relative).parts) > PROTOCOL_TOPOLOGY_DEPTH_CAP:
                errors.append(f"protocol topology worktree path exceeds depth cap: {relative}")
                continue
            try:
                metadata = entry.stat(follow_symlinks=False)
            except OSError as exc:
                errors.append(f"protocol topology cannot lstat {relative}: {exc}")
                continue
            if stat.S_ISLNK(metadata.st_mode):
                errors.append(f"protocol topology worktree symlink is forbidden: {relative}")
                continue
            if relative in excluded_relatives:
                if not stat.S_ISDIR(metadata.st_mode):
                    errors.append(
                        f"protocol topology authorized output root is not a directory: {relative}"
                    )
                else:
                    observed_directories.add(relative)
                    pending.append((Path(entry.path), relative))
                continue
            if stat.S_ISDIR(metadata.st_mode):
                observed_directories.add(relative)
                pending.append((Path(entry.path), relative))
                continue
            if not stat.S_ISREG(metadata.st_mode):
                errors.append(f"protocol topology worktree special file is forbidden: {relative}")
                continue
            observed_files.add(relative)
            if metadata.st_nlink != 1:
                errors.append(
                    f"protocol topology worktree file link count is not one: "
                    f"{relative} ({metadata.st_nlink})"
                )
            inode = (metadata.st_dev, metadata.st_ino)
            if inode in observed_inodes:
                errors.append(
                    f"protocol topology worktree files alias one inode: "
                    f"{observed_inodes[inode]} and {relative}"
                )
            else:
                observed_inodes[inode] = relative
            expected = worktree_head.get(relative)
            if expected is None:
                continue
            file_cap = (
                EVIDENCE_ARTIFACT_BYTE_CAP
                if excluded(relative) else REGULAR_FILE_BYTE_CAP
            )
            if metadata.st_size > file_cap:
                errors.append(
                    f"protocol topology worktree file exceeds byte cap: {relative}"
                )
                continue
            flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK
            try:
                descriptor = os.open(entry.path, flags)
            except OSError as exc:
                errors.append(f"protocol topology cannot open nofollow file {relative}: {exc}")
                continue
            opened: os.stat_result | None = None
            worktree_digest: str | None = None
            try:
                opened = os.fstat(descriptor)
                if (
                    not stat.S_ISREG(opened.st_mode)
                    or (opened.st_dev, opened.st_ino) != inode
                    or opened.st_nlink != 1
                ):
                    errors.append(
                        f"protocol topology opened file identity changed: {relative}"
                    )
                else:
                    digest = hashlib.sha256()
                    byte_length = 0
                    while True:
                        chunk = os.read(descriptor, 1024 * 1024)
                        if not chunk:
                            break
                        byte_length += len(chunk)
                        digest.update(chunk)
                    terminal = os.fstat(descriptor)
                    if (
                        terminal.st_dev, terminal.st_ino, terminal.st_mode,
                        terminal.st_nlink, terminal.st_size, terminal.st_mtime_ns,
                        terminal.st_ctime_ns,
                    ) != (
                        opened.st_dev, opened.st_ino, opened.st_mode,
                        opened.st_nlink, opened.st_size, opened.st_mtime_ns,
                        opened.st_ctime_ns,
                    ) or byte_length != opened.st_size:
                        errors.append(
                            f"protocol topology opened file changed during read: {relative}"
                        )
                    else:
                        worktree_digest = digest.hexdigest()
            except OSError as exc:
                errors.append(f"protocol topology cannot read opened file {relative}: {exc}")
            finally:
                os.close(descriptor)
            if opened is None or worktree_digest is None:
                continue
            try:
                path_terminal = os.stat(entry.path, follow_symlinks=False)
            except OSError as exc:
                errors.append(
                    f"protocol topology cannot terminal-lstat file {relative}: {exc}"
                )
                continue
            if (
                path_terminal.st_dev, path_terminal.st_ino, path_terminal.st_mode,
                path_terminal.st_nlink, path_terminal.st_size,
                path_terminal.st_mtime_ns, path_terminal.st_ctime_ns,
            ) != (
                opened.st_dev, opened.st_ino, opened.st_mode, opened.st_nlink,
                opened.st_size, opened.st_mtime_ns, opened.st_ctime_ns,
            ):
                errors.append(
                    f"protocol topology worktree path changed during read: {relative}"
                )
                continue
            expected_mode, expected_object_id = expected
            _exact(
                _mode_string(opened), expected_mode,
                f"protocol topology worktree mode {relative}", errors,
            )
            expected_row = closure_rows.get(expected_object_id)
            if expected_row is None or expected_row.get("kind") != "blob":
                errors.append(
                    f"protocol topology committed blob is unavailable for {relative}"
                )
            else:
                _exact(
                    worktree_digest, expected_row.get("sha256"),
                    f"protocol topology worktree SHA-256 {relative}", errors,
                )

    missing_files = sorted(set(worktree_head) - observed_files)
    unexpected_files = sorted(
        relative for relative in observed_files - set(worktree_head)
        if not excluded(relative)
    )
    missing_directories = sorted(expected_directories - observed_directories)
    unexpected_directories = sorted(
        relative for relative in observed_directories - expected_directories
        if not excluded(relative)
    )
    if missing_files:
        errors.append(f"protocol topology worktree is missing files: {missing_files}")
    if unexpected_files:
        errors.append(f"protocol topology worktree has unexpected files: {unexpected_files}")
    if missing_directories:
        errors.append(
            f"protocol topology worktree is missing directories: {missing_directories}"
        )
    if unexpected_directories:
        errors.append(
            "protocol topology worktree has unexpected or empty directories: "
            f"{unexpected_directories}"
        )
    return finish()


def _no_git_selected_worktree_topology_errors(
    repository: Path, selected: set[str], label: str,
) -> list[str]:
    """Re-enumerate a sealed selected worktree without running a process."""
    errors: list[str] = []
    expected_directories: set[str] = set()
    for relative in selected:
        parent = Path(relative).parent
        while parent != Path("."):
            expected_directories.add(parent.as_posix())
            parent = parent.parent
    observed_files: set[str] = set()
    observed_directories: set[str] = set()
    observed_inodes: dict[tuple[int, int], str] = {}
    pending: list[tuple[Path, str, int]] = [(repository, "", 0)]
    entry_count = 0
    aggregate_path_bytes = 0
    while pending:
        directory, prefix, depth = pending.pop()
        if depth > PROTOCOL_TOPOLOGY_DEPTH_CAP:
            errors.append(f"{label}: worktree exceeds depth cap")
            return errors
        try:
            entries = _bounded_sorted_scandir(
                directory, PROTOCOL_TOPOLOGY_ENTRY_CAP - entry_count, label,
            )
        except (OSError, ValueError) as exc:
            errors.append(f"{label}: worktree enumeration failed: {exc}")
            return errors
        for entry in entries:
            if not prefix and entry.name == ".git":
                continue
            entry_count += 1
            if entry_count > PROTOCOL_TOPOLOGY_ENTRY_CAP:
                errors.append(f"{label}: worktree exceeds entry cap")
                return errors
            relative = f"{prefix}/{entry.name}" if prefix else entry.name
            encoded = relative.encode("utf-8")
            if len(encoded) > PROTOCOL_TOPOLOGY_PATH_BYTES_CAP:
                errors.append(f"{label}: path exceeds byte cap: {relative}")
                continue
            aggregate_path_bytes += len(encoded)
            if aggregate_path_bytes > FILESYSTEM_WALK_AGGREGATE_PATH_BYTES_CAP:
                errors.append(f"{label}: worktree exceeds aggregate path-byte cap")
                return errors
            try:
                metadata = entry.stat(follow_symlinks=False)
            except OSError as exc:
                errors.append(f"{label}: cannot lstat {relative}: {exc}")
                continue
            inode = (metadata.st_dev, metadata.st_ino)
            prior = observed_inodes.get(inode)
            if prior is not None:
                errors.append(f"{label}: {relative} aliases {prior}")
            else:
                observed_inodes[inode] = relative
            if stat.S_ISDIR(metadata.st_mode) and not stat.S_ISLNK(metadata.st_mode):
                observed_directories.add(relative)
                pending.append((Path(entry.path), relative, depth + 1))
            elif stat.S_ISREG(metadata.st_mode) and not stat.S_ISLNK(metadata.st_mode):
                observed_files.add(relative)
                if metadata.st_nlink != 1:
                    errors.append(f"{label}: file link count is not one: {relative}")
            else:
                errors.append(f"{label}: special/symlink path is forbidden: {relative}")
    _exact(observed_files, selected, f"{label} exact selected file set", errors)
    _exact(
        observed_directories, expected_directories,
        f"{label} exact selected directory topology", errors,
    )
    return errors


def _verifier_rust_channel_errors(package: Path) -> list[str]:
    """Reject local Rust source-loading channels outside Cargo's bound target set."""
    errors: list[str] = []
    try:
        records = _collect_rust_sources(package, exclude_root_target=True)
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        return [f"verifier Rust compiler-input scan failed: {exc}"]
    forbidden_macros = {"include", "include_bytes", "include_str"}
    for relative, raw, _normalized in records:
        try:
            tokens = _rust_structural_tokens(raw, preserve_identifiers=True)
        except (UnicodeDecodeError, ValueError) as exc:
            errors.append(f"verifier Rust compiler-input scan {relative}: {exc}")
            continue
        for token in tokens:
            # The verifier contract has no local inclusion channel.  Rejecting
            # every reference to these builtin names also closes imports,
            # reexports, grouped aliases, raw identifiers, and macro_rules!
            # forwarding that a direct `name !` scan would miss.
            if token in forbidden_macros:
                errors.append(
                    f"verifier Rust source {relative} mentions forbidden local-input macro identifier {token}"
                )
        if "OUT_DIR" in tokens or b"OUT_DIR" in raw:
            errors.append(
                f"verifier Rust source {relative} references forbidden generated-input OUT_DIR"
            )
        # Comments and whitespace have already been removed.  Reject path in
        # any attribute, including cfg_attr(..., path = ...), rather than try
        # to predict macro expansion.
        depth = 0
        in_attribute = False
        for index, token in enumerate(tokens):
            if token == "#" and index + 1 < len(tokens) and tokens[index + 1] == "[":
                in_attribute = True
                depth = 0
                continue
            if not in_attribute:
                continue
            if token == "[":
                depth += 1
            elif token == "]":
                depth -= 1
                if depth <= 0:
                    in_attribute = False
            elif token == "path":
                tail = tokens[index + 1:index + 3]
                if "=" in tail or "path" in tokens[max(0, index - 3):index + 1]:
                    errors.append(
                        f"verifier Rust source {relative} uses forbidden #[path]/cfg_attr(path)"
                    )
                    break
    return errors


def _verifier_compiler_input_errors(
    manifest_bytes: bytes, package: Path,
) -> list[str]:
    """Close Cargo root-target and build-script paths over the package tree."""
    errors: list[str] = []
    try:
        manifest = tomllib.loads(manifest_bytes.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        return [f"verifier Cargo target manifest is invalid: {exc}"]
    try:
        canonical_package = package.resolve(strict=True)
    except OSError as exc:
        return [f"verifier package cannot be resolved for compiler-input scan: {exc}"]
    if canonical_package != package or _symlink_component(package) is not None:
        errors.append("verifier package is not a canonical no-symlink path")

    def validate_target_path(raw_path: Any, label: str) -> None:
        if not isinstance(raw_path, str) or not raw_path:
            errors.append(f"{label} is not a nonempty relative path")
            return
        candidate_value = Path(raw_path)
        normalized_value = Path(os.path.normpath(raw_path))
        if (
            candidate_value.is_absolute()
            or candidate_value != normalized_value
            or any(part in {"", ".", ".."} for part in candidate_value.parts)
        ):
            errors.append(f"{label} is not a normalized package-relative path")
            return
        lexical = package / candidate_value
        linked = _symlink_component(lexical)
        try:
            resolved = lexical.resolve(strict=True)
            metadata = os.lstat(lexical)
        except OSError as exc:
            errors.append(f"{label} cannot be resolved: {exc}")
            return
        if linked is not None or resolved != lexical:
            errors.append(f"{label} contains a symlink component")
        if resolved != canonical_package and canonical_package not in resolved.parents:
            errors.append(f"{label} escapes the verifier package")
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            errors.append(f"{label} is not a regular single-link compiler input")

    package_table = manifest.get("package")
    if not isinstance(package_table, dict):
        errors.append("verifier Cargo manifest lacks [package]")
        return errors
    build_value = package_table.get("build")
    if build_value is False:
        if os.path.lexists(package / "build.rs"):
            errors.append("verifier disables build.rs but a root build.rs input is present")
    elif build_value is None:
        if os.path.lexists(package / "build.rs"):
            validate_target_path("build.rs", "verifier implicit [package].build")
    elif isinstance(build_value, str):
        validate_target_path(build_value, "verifier [package].build")
    else:
        errors.append("verifier [package].build must be false, absent, or a relative path")
    if "workspace" in package_table:
        errors.append("verifier [package].workspace is forbidden")
    workspace_table = manifest.get("workspace")
    if workspace_table != {}:
        errors.append("verifier must contain a literal empty standalone [workspace] table")
    for forbidden_table in ("patch", "replace", "source", "registries", "registry"):
        if forbidden_table in manifest:
            errors.append(f"verifier Cargo [{forbidden_table}] source override is forbidden")

    lib_table = manifest.get("lib")
    if lib_table is not None:
        if not isinstance(lib_table, dict):
            errors.append("verifier Cargo [lib] is not a table")
        else:
            if lib_table.get("proc-macro") is True:
                errors.append("verifier local proc-macro target is forbidden")
            if "path" in lib_table:
                validate_target_path(lib_table["path"], "verifier [lib].path")
    for target_kind in ("bin", "example", "test", "bench"):
        targets = manifest.get(target_kind, [])
        if not isinstance(targets, list):
            errors.append(f"verifier Cargo [[{target_kind}]] target inventory is invalid")
            continue
        for index, target in enumerate(targets):
            if not isinstance(target, dict):
                errors.append(f"verifier Cargo [[{target_kind}]] target {index} is invalid")
            elif "path" in target:
                validate_target_path(
                    target["path"], f"verifier [[{target_kind}]] target {index} path",
                )
    errors.extend(_verifier_rust_channel_errors(package))
    return errors


def _source_build_input_rows(
    repository: Path, package: Path, commit: str, label: str, errors: list[str],
) -> list[dict[str, Any]] | None:
    """Bind all package Rust and relevant Cargo/toolchain inputs to raw commit blobs."""
    try:
        package_relative = package.relative_to(repository).as_posix()
    except ValueError:
        errors.append(f"{label}: package is outside repository")
        return None
    package_entries = _git_tree_entries(
        repository, commit, package_relative, f"{label} package tree", errors,
    )
    if package_entries is None:
        return None
    expected: dict[str, tuple[str, str, str]] = {}
    expected_directories: set[str] = set()
    prefix = package_relative + "/"
    for path, entry in package_entries.items():
        if not path.startswith(prefix):
            continue
        within = path[len(prefix):]
        if within == "target" or within.startswith("target/"):
            continue
        if entry[1] == "blob":
            expected[path] = entry
            within_path = Path(within)
            for parent in within_path.parents:
                if str(parent) != ".":
                    expected_directories.add(parent.as_posix())
    for relative in ("Cargo.lock", *SOURCE_BUILD_OPTIONAL_ROOT_PATHS):
        entry = _git_tree_entry(
            repository, commit, relative, f"{label} build input {relative}", [],
        )
        # Optional inputs legitimately have no entry; Cargo.lock is mandatory.
        if entry is not None:
            expected[relative] = entry
        elif relative == "Cargo.lock":
            errors.append(f"{label}: committed Cargo.lock is missing")

    actual_paths: set[str] = set()
    actual_directories: set[str] = set()
    visited_entries = 0
    aggregate_path_bytes = 0

    def visit_package(directory: Path, depth: int = 0) -> None:
        nonlocal visited_entries, aggregate_path_bytes
        if depth > 64:
            errors.append(f"{label}: package input directory depth exceeds 64 at {directory}")
            return
        try:
            entries = _bounded_sorted_scandir(
                directory, 100000 - visited_entries,
                f"{label} package input inventory",
            )
        except ValueError as exc:
            errors.append(str(exc))
            return
        names = [entry.name for entry in entries]
        if len(names) != len(set(names)):
            errors.append(f"{label}: package directory has duplicate names: {directory}")
        for item in entries:
            visited_entries += 1
            if visited_entries > 100000:
                errors.append(f"{label}: package input inventory exceeds 100000 entries")
                return
            path = Path(item.path)
            relative_within = path.relative_to(package).as_posix()
            encoded_relative = relative_within.encode("utf-8")
            if len(encoded_relative) > 4096:
                errors.append(f"{label}: package input path exceeds 4096 UTF-8 bytes: {relative_within}")
                continue
            aggregate_path_bytes += len(encoded_relative)
            if aggregate_path_bytes > FILESYSTEM_WALK_AGGREGATE_PATH_BYTES_CAP:
                errors.append(f"{label}: package input inventory exceeds aggregate path-byte cap")
                return
            try:
                metadata = item.stat(follow_symlinks=False)
            except OSError as exc:
                errors.append(f"{label}: cannot stat package input {path}: {exc}")
                continue
            if directory == package and item.name == "target":
                if not stat.S_ISDIR(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode):
                    errors.append(f"{label}: root target exclusion is not a real directory: {path}")
                continue
            if stat.S_ISLNK(metadata.st_mode):
                errors.append(f"{label}: package input symlink is forbidden: {path}")
            elif stat.S_ISDIR(metadata.st_mode):
                actual_directories.add(relative_within)
                visit_package(path, depth + 1)
            elif stat.S_ISREG(metadata.st_mode):
                actual_paths.add(path.relative_to(repository).as_posix())
            else:
                errors.append(f"{label}: non-regular package input is forbidden: {path}")

    visit_package(package)
    for relative in ("Cargo.lock", *SOURCE_BUILD_OPTIONAL_ROOT_PATHS):
        candidate = repository / relative
        if os.path.lexists(candidate):
            actual_paths.add(relative)

    _exact(sorted(actual_paths), sorted(expected), f"{label} source/build path inventory", errors)
    _exact(
        sorted(actual_directories), sorted(expected_directories),
        f"{label} package directory inventory", errors,
    )
    rows: list[dict[str, Any]] = []
    for relative in sorted(actual_paths | set(expected)):
        entry = expected.get(relative)
        path = repository / relative
        linked = _symlink_component(path)
        if linked is not None:
            errors.append(f"{label}: source/build input has symlink component: {linked}")
            continue
        try:
            metadata = os.lstat(path)
        except OSError as exc:
            errors.append(f"{label}: cannot stat source/build input {relative}: {exc}")
            continue
        if not stat.S_ISREG(metadata.st_mode):
            errors.append(f"{label}: source/build input is not regular: {relative}")
            continue
        _require(
            metadata.st_nlink == 1,
            f"{label}: source/build input link count is not one: {relative}", errors,
        )
        try:
            raw, opened = _regular_file_snapshot(
                path, f"{label} source/build input {relative}",
            )
        except (OSError, ValueError) as exc:
            errors.append(f"{label}: cannot read source/build input {relative}: {exc}")
            continue
        mode = _mode_string(opened)
        if entry is None:
            continue
        git_mode, kind, object_id = entry
        _exact(kind, "blob", f"{label} Git object type {relative}", errors)
        _exact(mode, git_mode, f"{label} Git/working mode {relative}", errors)
        blob = _git_blob(repository, object_id, f"{label} committed bytes {relative}", errors)
        if blob is not None:
            _exact(raw, blob, f"{label} Git/working bytes {relative}", errors)
        rows.append({
            "path": relative,
            "mode": mode,
            "device": str(opened.st_dev),
            "inode": str(opened.st_ino),
            "link_count": opened.st_nlink,
            "byte_length": len(raw),
            "sha256": sha256_bytes(raw),
        })
    errors.extend(_tracked_index_flag_errors(repository, sorted(expected), label))
    if "verifier" in label:
        manifest_path = package / "Cargo.toml"
        try:
            errors.extend(_verifier_compiler_input_errors(
                _read_regular_file_bytes(
                    manifest_path, f"{label} verifier Cargo.toml compiler-input scan",
                ),
                package,
            ))
        except (OSError, ValueError) as exc:
            errors.append(f"{label}: cannot read verifier Cargo.toml for compiler-input scan: {exc}")
    return rows


def _evidence_size_errors(run_dir: Path, control_dir: Path) -> list[str]:
    """Preflight all evidence lengths before any whole-artifact read."""
    errors: list[str] = []

    def inventory(root: Path, label: str) -> dict[str, int]:
        sizes: dict[str, int] = {}
        try:
            metadata = os.lstat(root)
        except OSError as exc:
            errors.append(f"{label} size preflight cannot lstat root: {exc}")
            return sizes
        if not stat.S_ISDIR(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode):
            errors.append(f"{label} size preflight root is not a nofollow directory")
            return sizes
        try:
            entries = _bounded_sorted_scandir(
                root, PROTOCOL_TOPOLOGY_ENTRY_CAP, f"{label} size preflight",
            )
        except (OSError, ValueError) as exc:
            errors.append(f"{label} size preflight cannot enumerate: {exc}")
            return sizes
        for entry in entries:
            try:
                item = entry.stat(follow_symlinks=False)
            except OSError as exc:
                errors.append(
                    f"{label} size preflight cannot lstat {entry.name}: {exc}"
                )
                continue
            if not stat.S_ISREG(item.st_mode) or stat.S_ISLNK(item.st_mode):
                errors.append(
                    f"{label} size preflight forbids nonregular leaf {entry.name}"
                )
                continue
            if item.st_nlink != 1:
                errors.append(
                    f"{label} size preflight link count is not one: {entry.name}"
                )
            sizes[entry.name] = item.st_size
            if item.st_size > EVIDENCE_ARTIFACT_BYTE_CAP:
                errors.append(
                    f"{label} artifact exceeds 512 MiB cap: {entry.name}"
                )
            if (
                entry.name in SMALL_PRODUCER_PATHS
                and item.st_size > SMALL_PRODUCER_ARTIFACT_BYTE_CAP
            ):
                errors.append(
                    f"{label} small producer artifact exceeds 64 KiB cap: "
                    f"{entry.name}"
                )
        return sizes

    run_sizes = inventory(run_dir, "RUN_DIR")
    control_sizes = inventory(control_dir, "CONTROL_DIR")
    for label, sizes in (("RUN_DIR", run_sizes), ("CONTROL_DIR", control_sizes)):
        producer_total = sum(
            size for name, size in sizes.items() if name in PRODUCER_PATHS
        )
        if producer_total > PRODUCER_TREE_BYTE_CAP:
            errors.append(f"{label} producer tree exceeds 844 MiB cap")
        tree_total = sum(sizes.values())
        if tree_total > EVIDENCE_TREE_BYTE_CAP:
            errors.append(f"{label} tree exceeds 896 MiB cap")
    run_metadata_total = sum(
        size for name, size in run_sizes.items() if name not in PRODUCER_PATHS
    )
    if run_metadata_total > RUN_METADATA_BYTE_CAP:
        errors.append("RUN_DIR nonproducer metadata exceeds 64 MiB cap")
    if sum(run_sizes.values()) + sum(control_sizes.values()) > EVIDENCE_COMBINED_BYTE_CAP:
        errors.append("combined RUN_DIR/CONTROL_DIR evidence exceeds 1792 MiB cap")
    return errors


def _output_leaf_paths(
    repository: Path, roots: tuple[Path, Path], errors: list[str],
) -> set[str]:
    leaves: set[str] = set()
    entry_count = 0
    aggregate_path_bytes = 0
    for root in roots:
        try:
            root_metadata = os.lstat(root)
        except OSError as exc:
            errors.append(f"protocol output root cannot be lstatted {root}: {exc}")
            continue
        if not stat.S_ISDIR(root_metadata.st_mode) or stat.S_ISLNK(root_metadata.st_mode):
            errors.append(f"protocol output root is not a nofollow directory: {root}")
            continue
        try:
            entries = _bounded_sorted_scandir(
                root, PROTOCOL_TOPOLOGY_ENTRY_CAP - entry_count,
                "protocol output inventory",
            )
        except ValueError as exc:
            errors.append(str(exc))
            continue
        for entry in entries:
            entry_count += 1
            path = Path(entry.path)
            try:
                relative = path.relative_to(repository).as_posix()
                encoded = relative.encode("utf-8")
            except (ValueError, UnicodeEncodeError) as exc:
                errors.append(f"protocol output path is invalid {path}: {exc}")
                continue
            if len(encoded) > PROTOCOL_TOPOLOGY_PATH_BYTES_CAP:
                errors.append(f"protocol output path exceeds byte cap: {relative}")
                continue
            aggregate_path_bytes += len(encoded)
            if aggregate_path_bytes > FILESYSTEM_WALK_AGGREGATE_PATH_BYTES_CAP:
                errors.append("protocol output inventory exceeds aggregate path-byte cap")
                return leaves
            try:
                metadata = entry.stat(follow_symlinks=False)
            except OSError as exc:
                errors.append(f"protocol output cannot lstat {relative}: {exc}")
                continue
            leaves.add(relative)
            if stat.S_ISDIR(metadata.st_mode):
                errors.append(f"protocol output nested directory is forbidden: {relative}")
            elif stat.S_ISLNK(metadata.st_mode):
                errors.append(f"protocol output symlink is forbidden: {relative}")
            elif not stat.S_ISREG(metadata.st_mode):
                errors.append(f"protocol output special leaf is forbidden: {relative}")
    return leaves


def _archive_chain_errors(
    repository: Path, decision_commit: str, head: str,
    allowed_roots: tuple[str, str],
) -> list[str]:
    """Audit every single-parent archive commit; endpoint reverts cannot launder paths."""
    errors: list[str] = []
    current = head
    seen: set[str] = set()
    commit_count = 0
    while current != decision_commit:
        commit_count += 1
        if commit_count > GIT_EXECUTION_POLICY["raw_parent_walk_commit_cap"]:
            errors.append("committed evidence archive chain exceeds commit cap")
            return errors
        if current in seen:
            errors.append("committed evidence archive chain contains a parent cycle")
            return errors
        seen.add(current)
        parents = _raw_commit_parents(
            repository, current, "committed evidence archive", errors,
        )
        if parents is None:
            return errors
        if len(parents) != 1:
            errors.append(
                f"committed evidence archive commit is not single-parent: {current}"
            )
            return errors
        parent = parents[0]
        if commit_count == 1 and parent != decision_commit:
            errors.append(
                "committed evidence must be one direct archive commit over the decision commit"
            )
            return errors
        parent_topology = _raw_commit_tree_topology(
            repository, parent, "archive parent", errors,
        )
        child_topology = _raw_commit_tree_topology(
            repository, current, "archive child", errors,
        )
        if parent_topology is None or child_topology is None:
            return errors
        changed = {
            relative
            for relative in set(parent_topology) | set(child_topology)
            if parent_topology.get(relative) != child_topology.get(relative)
        }
        if not changed:
            errors.append(f"committed evidence archive commit has no output change: {current}")
        for relative in sorted(changed):
            authorized = any(
                relative == root
                or relative.startswith(root + "/")
                or root.startswith(relative + "/")
                for root in allowed_roots
            )
            if not authorized:
                errors.append(
                    f"committed evidence archive commit changes unrelated tree/blob path "
                    f"{current}:{relative}"
                )
        current = parent
    if commit_count == 0:
        errors.append("committed evidence archive chain is empty")
    elif commit_count != 1:
        errors.append("committed evidence archive chain is not exactly one commit")
    return errors


def _git_base_name_compare(
    left_name: bytes, left_is_tree: bool,
    right_name: bytes, right_is_tree: bool,
) -> int:
    """Git tree base_name_compare over raw entry names."""
    common = min(len(left_name), len(right_name))
    if left_name[:common] != right_name[:common]:
        for left, right in zip(left_name[:common], right_name[:common]):
            if left != right:
                return -1 if left < right else 1
    left_next = (
        left_name[common] if common < len(left_name)
        else (ord("/") if left_is_tree else 0)
    )
    right_next = (
        right_name[common] if common < len(right_name)
        else (ord("/") if right_is_tree else 0)
    )
    if left_next == right_next:
        return 0
    return -1 if left_next < right_next else 1


def _raw_commit_tree_topology(
    repository: Path, commit: str, label: str, errors: list[str], *,
    object_custody: list[dict[str, Any]] | None = None,
) -> dict[str, tuple[str, str, str]] | None:
    """Self-hash and parse a commit plus every recursively traversed tree."""
    commit_objects = _git_objects(
        repository, [commit], f"{label} commit object", errors,
    )
    if commit_objects is None or commit not in commit_objects:
        return None
    commit_kind, commit_raw = commit_objects[commit]
    if commit_kind != "commit" or b"\n\n" not in commit_raw:
        errors.append(f"{label} is not a canonical raw commit object")
        return None
    header = commit_raw.split(b"\n\n", 1)[0]
    trees = [line[5:] for line in header.splitlines() if line.startswith(b"tree ")]
    if len(trees) != 1:
        errors.append(f"{label} commit does not name exactly one root tree")
        return None
    try:
        root_tree = trees[0].decode("ascii")
    except UnicodeDecodeError:
        errors.append(f"{label} commit root tree is not ASCII")
        return None
    if re.fullmatch(r"[0-9a-f]{40}", root_tree) is None:
        errors.append(f"{label} commit root tree object ID is invalid")
        return None
    if object_custody is not None:
        object_custody.append({
            "object_id": commit,
            "kind": "commit",
            "byte_length": len(commit_raw),
            "sha256": sha256_bytes(commit_raw),
        })

    result: dict[str, tuple[str, str, str]] = {}
    pending: list[tuple[str, str, int]] = [(root_tree, "", 0)]
    parsed_cache: dict[str, list[tuple[str, str, str, str]]] = {}
    aggregate_tree_bytes = 0
    entry_count = 0
    aggregate_path_bytes = 0
    while pending:
        level = pending
        pending = []
        missing_oids = {oid for oid, _prefix, _depth in level if oid not in parsed_cache}
        objects = _git_objects(
            repository, missing_oids, f"{label} traversed tree objects", errors,
        )
        if objects is None:
            return None
        for object_id, (kind, raw_tree) in objects.items():
            if kind != "tree":
                errors.append(f"{label} traversed object is not a tree: {object_id}")
                return None
            aggregate_tree_bytes += len(raw_tree)
            if aggregate_tree_bytes > PROTOCOL_TOPOLOGY_AGGREGATE_BLOB_BYTES_CAP:
                errors.append(f"{label} traversed tree bytes exceed aggregate cap")
                return None
            if object_custody is not None:
                object_custody.append({
                    "object_id": object_id,
                    "kind": "tree",
                    "byte_length": len(raw_tree),
                    "sha256": sha256_bytes(raw_tree),
                })
            parsed: list[tuple[str, str, str, str]] = []
            offset = 0
            names: set[str] = set()
            previous_entry: tuple[bytes, bool] | None = None
            while offset < len(raw_tree):
                space = raw_tree.find(b" ", offset)
                nul = raw_tree.find(b"\0", space + 1) if space >= 0 else -1
                if space <= offset or nul < 0 or nul + 21 > len(raw_tree):
                    errors.append(f"{label} tree object has a malformed entry: {object_id}")
                    return None
                try:
                    raw_mode_bytes = raw_tree[offset:space]
                    raw_name = raw_tree[space + 1:nul]
                    raw_mode = raw_mode_bytes.decode("ascii")
                    name = raw_name.decode("utf-8")
                except UnicodeDecodeError:
                    errors.append(f"{label} tree object has non-UTF-8 mode/name: {object_id}")
                    return None
                canonical_modes = {
                    "40000": ("040000", "tree"),
                    "100644": ("100644", "blob"),
                    "100755": ("100755", "blob"),
                    "120000": ("120000", "blob"),
                    "160000": ("160000", "commit"),
                }
                mode_binding = canonical_modes.get(raw_mode)
                if mode_binding is None:
                    errors.append(
                        f"{label} tree object has noncanonical/forbidden raw mode "
                        f"{raw_mode}: {name}"
                    )
                    return None
                mode, child_kind = mode_binding
                child_oid = raw_tree[nul + 1:nul + 21].hex()
                offset = nul + 21
                if (
                    not name or "/" in name or name in {".", ".."}
                    or any(ord(character) < 32 for character in name)
                ):
                    errors.append(f"{label} tree object has invalid entry name: {name!r}")
                    return None
                if name in names:
                    errors.append(f"{label} tree object has duplicate entry name: {name}")
                    return None
                names.add(name)
                current_entry = (raw_name, child_kind == "tree")
                if (
                    previous_entry is not None
                    and _git_base_name_compare(
                        previous_entry[0], previous_entry[1],
                        current_entry[0], current_entry[1],
                    ) >= 0
                ):
                    errors.append(
                        f"{label} tree object entries are not in canonical Git order: "
                        f"{object_id}:{name}"
                    )
                    return None
                previous_entry = current_entry
                parsed.append((mode, child_kind, child_oid, name))
            parsed_cache[object_id] = parsed
        for object_id, prefix, depth in level:
            if depth > PROTOCOL_TOPOLOGY_DEPTH_CAP:
                errors.append(f"{label} full tree topology exceeds depth cap")
                return None
            for mode, child_kind, child_oid, name in parsed_cache[object_id]:
                relative = f"{prefix}/{name}" if prefix else name
                entry_count += 1
                if entry_count > PROTOCOL_TOPOLOGY_ENTRY_CAP:
                    errors.append(f"{label} full tree topology exceeds entry cap")
                    return None
                encoded_path = relative.encode("utf-8")
                aggregate_path_bytes += len(encoded_path)
                if (
                    len(encoded_path) > PROTOCOL_TOPOLOGY_PATH_BYTES_CAP
                    or aggregate_path_bytes > FILESYSTEM_WALK_AGGREGATE_PATH_BYTES_CAP
                ):
                    errors.append(f"{label} full tree topology exceeds path-byte cap")
                    return None
                if relative in result:
                    errors.append(f"{label} full tree topology has duplicate path: {relative}")
                    return None
                result[relative] = (mode, child_kind, child_oid)
                if child_kind == "tree":
                    pending.append((child_oid, relative, depth + 1))
    return result


def _custody_digest(domain: bytes, value: Any) -> str:
    return sha256_bytes(domain + canonical_json_bytes(value))


def _topology_rows(
    topology: dict[str, tuple[str, str, str]],
) -> list[dict[str, str]]:
    return [
        {
            "path": relative, "mode": mode, "kind": kind,
            "object_id": object_id,
        }
        for relative, (mode, kind, object_id) in sorted(topology.items())
    ]


def _leaf_tree(
    topology: dict[str, tuple[str, str, str]],
) -> dict[str, tuple[str, str]]:
    return {
        relative: (mode, object_id)
        for relative, (mode, kind, object_id) in topology.items()
        if kind != "tree"
    }


def _sealed_repository_custody_receipt(
    repository: Path, head: str, profile: dict[str, Any], phase: str,
    errors: list[str],
) -> dict[str, Any] | None:
    """Admit one sealed repository and return its exact custody receipt.

    The pre-execution receipt is generated while HEAD/index/worktree are still
    sealed at D1.  Its historical raw-index identity cannot be reconstructed
    after A1 rewrites the index, so the archived receipt binds that identity;
    every deterministic D1 commit/tree/selected-blob digest is independently
    replayed from the later archive before Role-2 admission.
    """
    initial_error_count = len(errors)
    if phase not in {"pre_role1_execution", "terminal_role1_archive"}:
        errors.append("sealed repository custody phase is invalid")
        return None
    preflight = _repository_git_preflight_errors(repository, profile)
    errors.extend(f"sealed repository custody: {item}" for item in preflight)
    if preflight:
        return None
    try:
        entry_git_storage = _git_head_index_storage_identities(repository)
    except (OSError, ValueError) as exc:
        errors.append(f"sealed repository Git control identity unavailable: {exc}")
        return None
    actual_head_raw = _git_stdout(
        repository, ["rev-parse", "HEAD"],
        "sealed repository custody HEAD", errors,
    )
    if actual_head_raw is None:
        return None
    actual_head = actual_head_raw.rstrip(b"\n").decode("ascii", "replace")
    _exact(actual_head, head, "sealed repository custody exact HEAD", errors)
    errors.extend(_protocol_repository_topology_errors(
        repository, head, (), profile,
    ))
    object_rows: list[dict[str, Any]] = []
    topology = _raw_commit_tree_topology(
        repository, head, "sealed repository custody", errors,
        object_custody=object_rows,
    )
    if topology is None:
        return None
    head_tree = _leaf_tree(topology)
    selected = _sparse_selected_paths(head_tree, profile, errors)
    index_tree = _raw_protocol_stage_zero_index(repository, errors)
    if selected is None or index_tree is None:
        return None
    custody_checker_relative = PROTECTED_PROTOCOL_RELATIVE_PATHS[
        "check_role2_box0_interface.py"
    ]
    custody_checker_entry = head_tree.get(custody_checker_relative)
    if custody_checker_entry is None or custody_checker_entry[0] != "100644":
        errors.append(
            "sealed repository custody checker is absent/nonregular in HEAD"
        )
        return None
    _exact(
        index_tree, head_tree,
        "sealed repository custody full HEAD/index entry map", errors,
    )
    selected_rows: list[dict[str, Any]] = []
    for relative in sorted(selected):
        path = repository / relative
        try:
            selected_rows.append(_file_identity(path, relative))
        except (OSError, ValueError) as exc:
            errors.append(
                f"sealed repository custody selected path unavailable "
                f"{relative}: {exc}"
            )
    policy_blob_ids = {
        object_id for relative, (mode, object_id) in head_tree.items()
        if relative in selected or Path(relative).name == ".gitattributes"
        if mode in {"100644", "100755"}
    }
    policy_rows = _git_blob_payload_custody_map(
        repository, policy_blob_ids,
        "sealed repository custody selected/policy blobs", errors,
    )
    if policy_rows is None:
        return None
    custody_checker_raw = _git_blob(
        repository, custody_checker_entry[1],
        "sealed repository custody checker blob", errors,
    )
    if custody_checker_raw is None:
        errors.append("sealed repository custody checker blob is unavailable")
        return None
    object_rows.extend(policy_rows)
    admitted_by_oid = _object_custody_by_oid(
        object_rows, "sealed repository admitted object closure", errors,
    )
    if admitted_by_oid is None:
        return None
    admitted_size_errors = _distinct_blob_payload_size_errors(
        {
            object_id: int(row["byte_length"])
            for object_id, row in admitted_by_oid.items()
            if row.get("kind") == "blob"
        },
        "sealed repository admitted object closure",
    )
    errors.extend(admitted_size_errors)
    if admitted_size_errors:
        return None
    admitted_objects = [
        admitted_by_oid[object_id] for object_id in sorted(admitted_by_oid)
    ]
    topology_rows = _topology_rows(topology)
    index_rows = [
        {
            "path": relative, "mode": mode, "object_id": object_id,
            "stage": 0, "tag": "H" if relative in selected else "S",
            "flag_policy": (
                "selected_normal" if relative in selected
                else "omitted_CE_EXTENDED_CE_SKIP_WORKTREE"
            ),
        }
        for relative, (mode, object_id) in sorted(index_tree.items())
    ]
    try:
        receipt = {
            "schema": "p192-wcm-sealed-repository-custody-v1",
            "phase": phase,
            "repository_path": str(repository),
            "repository_identity": _directory_identity(repository),
            "head_commit": head,
            "profile": profile,
            "profile_sha256": _custody_digest(
                b"P192-WCM-SEALED-PROFILE-v1\0", profile,
            ),
            "custody_checker_relative_path": custody_checker_relative,
            "custody_checker_object_id": custody_checker_entry[1],
            "custody_checker_sha256": sha256_bytes(custody_checker_raw),
            "git_index_identity": _file_identity(repository / ".git/index"),
            "git_config_identity": _file_identity(repository / ".git/config"),
            "git_objects_directory_identity": _directory_identity(
                repository / ".git/objects"
            ),
            "head_entry_map_sha256": _custody_digest(
                b"P192-WCM-SEALED-HEAD-ENTRY-MAP-v1\0", topology_rows,
            ),
            "index_entry_map_sha256": _custody_digest(
                b"P192-WCM-SEALED-INDEX-ENTRY-MAP-v1\0", index_rows,
            ),
            "selected_worktree_identities": selected_rows,
            "selected_worktree_sha256": _custody_digest(
                b"P192-WCM-SEALED-SELECTED-WORKTREE-v1\0", selected_rows,
            ),
            "admitted_git_objects": admitted_objects,
            "admitted_git_objects_sha256": _custody_digest(
                b"P192-WCM-SEALED-ADMITTED-GIT-OBJECTS-v1\0",
                admitted_objects,
            ),
            "omitted_leaf_payload_scope": (
                "ordinary_omitted_blobs_and_gitlink_targets_not_consulted"
            ),
            "inode_custody_scope": "original_supervised_workspace_only",
            "exclusive_workspace_boundary": (
                "trusted_local_host_exclusive_workspace_no_concurrent_mutator"
            ),
            "role1_launch_performed": phase == "terminal_role1_archive",
            "overall_status": "PASS",
        }
    except (OSError, ValueError) as exc:
        errors.append(f"sealed repository custody identity unavailable: {exc}")
        return None
    # Replay the complete selected/omitted worktree and Git-admin topology so
    # a helper cannot add a rogue leaf or mutate a selected input after the
    # first admission pass.  Then make one final raw-object batch the last
    # process: a later per-object process must not be able to corrupt an object
    # already admitted by an earlier query.  Only no-process identity reads
    # follow that terminal batch.
    errors.extend(_protocol_repository_topology_errors(
        repository, head, (), profile,
    ))
    terminal_file_bindings: dict[str, list[tuple[Path, str]]] = {
        object_id: [] for object_id in admitted_by_oid
    }
    for relative in sorted(selected):
        entry = head_tree.get(relative)
        if entry is None or entry[0] not in {"100644", "100755"}:
            continue
        terminal_file_bindings.setdefault(entry[1], []).append((
            repository / relative,
            f"sealed repository terminal selected file {relative}",
        ))
    terminal_objects = _stream_git_blob_batch_file_equality(
        repository,
        {
            object_id: int(row["byte_length"])
            for object_id, row in admitted_by_oid.items()
        },
        terminal_file_bindings,
        "sealed repository terminal admitted-object closure", errors,
        object_kinds={
            object_id: str(row["kind"])
            for object_id, row in admitted_by_oid.items()
        },
        expected_payload_sha256={
            object_id: str(row["sha256"])
            for object_id, row in admitted_by_oid.items()
        },
    )
    if terminal_objects is None:
        errors.append("sealed repository terminal admitted-object closure failed")
    errors.extend(_no_git_selected_worktree_topology_errors(
        repository, selected, "sealed repository terminal no-Git worktree",
    ))
    terminal_preflight = _repository_git_preflight_errors(repository, profile)
    errors.extend(
        f"sealed repository custody terminal administration: {item}"
        for item in terminal_preflight
    )
    try:
        terminal_selected_rows = [
            _file_identity(repository / relative, relative)
            for relative in sorted(selected)
        ]
        _exact(
            terminal_selected_rows, selected_rows,
            "sealed repository terminal selected-worktree identities", errors,
        )
        _exact(
            _git_head_index_storage_identities(repository), entry_git_storage,
            "sealed repository terminal HEAD/index/config/ref identities", errors,
        )
        _exact(
            _git_head_commit_no_git(repository), head,
            "sealed repository terminal HEAD argument/storage binding", errors,
        )
    except (OSError, ValueError) as exc:
        errors.append(
            f"sealed repository terminal identity unavailable: {exc}"
        )
    if len(errors) != initial_error_count:
        return None
    return receipt


def _replay_historical_sealed_repository_receipt(
    receipt: dict[str, Any], repository: Path, head: str,
    profile: dict[str, Any], errors: list[str],
) -> None:
    """Replay deterministic D1 custody from the archived pre-launch receipt."""
    initial_error_count = len(errors)
    _exact(
        receipt.get("schema"), "p192-wcm-sealed-repository-custody-v1",
        "Role-1 pre-execution custody schema", errors,
    )
    _exact(
        receipt.get("phase"), "pre_role1_execution",
        "Role-1 pre-execution custody phase", errors,
    )
    _exact(
        receipt.get("repository_path"), str(repository),
        "Role-1 pre-execution custody repository", errors,
    )
    _exact(
        receipt.get("head_commit"), head,
        "Role-1 pre-execution custody HEAD", errors,
    )
    _exact(
        receipt.get("profile"), profile,
        "Role-1 pre-execution custody profile", errors,
    )
    _exact(
        receipt.get("profile_sha256"),
        _custody_digest(b"P192-WCM-SEALED-PROFILE-v1\0", profile),
        "Role-1 pre-execution custody profile hash", errors,
    )
    object_rows: list[dict[str, Any]] = []
    topology = _raw_commit_tree_topology(
        repository, head, "Role-1 pre-execution custody replay", errors,
        object_custody=object_rows,
    )
    if topology is None:
        return
    head_tree = _leaf_tree(topology)
    selected = _sparse_selected_paths(head_tree, profile, errors)
    if selected is None:
        return
    custody_checker_relative = PROTECTED_PROTOCOL_RELATIVE_PATHS[
        "check_role2_box0_interface.py"
    ]
    custody_checker_entry = head_tree.get(custody_checker_relative)
    if custody_checker_entry is None or custody_checker_entry[0] != "100644":
        errors.append(
            "Role-1 pre-execution custody checker is absent/nonregular"
        )
        return
    selected_rows: list[dict[str, Any]] = []
    for relative in sorted(selected):
        try:
            selected_rows.append(_file_identity(repository / relative, relative))
        except (OSError, ValueError) as exc:
            errors.append(
                f"Role-1 pre-execution selected path unavailable {relative}: {exc}"
            )
    policy_blob_ids = {
        object_id for relative, (mode, object_id) in head_tree.items()
        if relative in selected or Path(relative).name == ".gitattributes"
        if mode in {"100644", "100755"}
    }
    policy_rows = _git_blob_payload_custody_map(
        repository, policy_blob_ids,
        "Role-1 pre-execution custody selected/policy blobs", errors,
    )
    if policy_rows is None:
        return
    custody_checker_raw = _git_blob(
        repository, custody_checker_entry[1],
        "Role-1 pre-execution custody checker blob", errors,
    )
    if custody_checker_raw is None:
        errors.append("Role-1 pre-execution custody checker blob is unavailable")
        return
    object_rows.extend(policy_rows)
    admitted_by_oid = _object_custody_by_oid(
        object_rows, "Role-1 pre-execution admitted object closure", errors,
    )
    if admitted_by_oid is None:
        return
    admitted_size_errors = _distinct_blob_payload_size_errors(
        {
            object_id: int(row["byte_length"])
            for object_id, row in admitted_by_oid.items()
            if row.get("kind") == "blob"
        },
        "Role-1 pre-execution admitted object closure",
    )
    errors.extend(admitted_size_errors)
    if admitted_size_errors:
        return
    admitted_objects = [
        admitted_by_oid[object_id] for object_id in sorted(admitted_by_oid)
    ]
    topology_rows = _topology_rows(topology)
    index_rows = [
        {
            "path": relative, "mode": mode, "object_id": object_id,
            "stage": 0, "tag": "H" if relative in selected else "S",
            "flag_policy": (
                "selected_normal" if relative in selected
                else "omitted_CE_EXTENDED_CE_SKIP_WORKTREE"
            ),
        }
        for relative, (mode, object_id) in sorted(head_tree.items())
    ]
    _exact(
        receipt.get("head_entry_map_sha256"),
        _custody_digest(
            b"P192-WCM-SEALED-HEAD-ENTRY-MAP-v1\0", topology_rows,
        ),
        "Role-1 pre-execution custody HEAD-entry digest", errors,
    )
    _exact(
        receipt.get("custody_checker_relative_path"), custody_checker_relative,
        "Role-1 pre-execution custody checker path", errors,
    )
    _exact(
        receipt.get("custody_checker_object_id"), custody_checker_entry[1],
        "Role-1 pre-execution custody checker object", errors,
    )
    _exact(
        receipt.get("custody_checker_sha256"),
        sha256_bytes(custody_checker_raw),
        "Role-1 pre-execution custody checker SHA-256", errors,
    )
    _exact(
        receipt.get("index_entry_map_sha256"),
        _custody_digest(
            b"P192-WCM-SEALED-INDEX-ENTRY-MAP-v1\0", index_rows,
        ),
        "Role-1 pre-execution custody historical index-entry digest", errors,
    )
    _exact(
        receipt.get("selected_worktree_identities"), selected_rows,
        "Role-1 pre-execution selected-worktree identities", errors,
    )
    _exact(
        receipt.get("selected_worktree_sha256"),
        _custody_digest(
            b"P192-WCM-SEALED-SELECTED-WORKTREE-v1\0", selected_rows,
        ),
        "Role-1 pre-execution selected-worktree digest", errors,
    )
    _exact(
        receipt.get("admitted_git_objects"), admitted_objects,
        "Role-1 pre-execution admitted object identities", errors,
    )
    _exact(
        receipt.get("admitted_git_objects_sha256"),
        _custody_digest(
            b"P192-WCM-SEALED-ADMITTED-GIT-OBJECTS-v1\0",
            admitted_objects,
        ),
        "Role-1 pre-execution admitted object digest", errors,
    )
    _exact(
        receipt.get("repository_identity"), _directory_identity(repository),
        "Role-1 pre-execution repository identity", errors,
    )
    _exact(
        receipt.get("git_config_identity"),
        _file_identity(repository / ".git/config"),
        "Role-1 pre-execution Git config identity", errors,
    )
    _exact(
        receipt.get("git_objects_directory_identity"),
        _directory_identity(repository / ".git/objects"),
        "Role-1 pre-execution object-directory identity", errors,
    )
    index_identity = receipt.get("git_index_identity")
    _require(
        isinstance(index_identity, dict)
        and index_identity.get("path") == str(repository / ".git/index")
        and index_identity.get("mode") == "100644"
        and index_identity.get("link_count") == 1
        and isinstance(index_identity.get("byte_length"), int)
        and index_identity.get("byte_length", 0) > 0
        and isinstance(index_identity.get("sha256"), str)
        and re.fullmatch(r"[0-9a-f]{64}", index_identity["sha256"]) is not None,
        "Role-1 pre-execution historical raw-index identity is malformed", errors,
    )
    _exact(
        receipt.get("omitted_leaf_payload_scope"),
        "ordinary_omitted_blobs_and_gitlink_targets_not_consulted",
        "Role-1 pre-execution omitted object scope", errors,
    )
    _exact(
        receipt.get("inode_custody_scope"),
        "original_supervised_workspace_only",
        "Role-1 pre-execution inode custody scope", errors,
    )
    _exact(
        receipt.get("exclusive_workspace_boundary"),
        "trusted_local_host_exclusive_workspace_no_concurrent_mutator",
        "Role-1 pre-execution exclusive workspace boundary", errors,
    )
    _exact(
        receipt.get("role1_launch_performed"), False,
        "Role-1 pre-execution launch state", errors,
    )
    _exact(
        receipt.get("overall_status"), "PASS",
        "Role-1 pre-execution custody status", errors,
    )
    if len(errors) != initial_error_count:
        return


def _predecessor_repository_custody_errors(
    decision: dict[str, Any], repository: Path, decision_commit: str,
    archive_commit: str,
) -> list[str]:
    """Replay D1 pre-launch custody and exact live A1 terminal custody."""
    errors: list[str] = []
    binding = decision.get("predecessor_repository_custody")
    if not isinstance(binding, dict):
        return ["Role-1 predecessor repository custody binding is absent"]
    expected_relative = _role1_pre_execution_custody_relative(
        decision["predecessor_run_id"],
    )
    expected_path = repository / expected_relative
    retained_path = _role1_pre_execution_retained_path(
        repository, decision["predecessor_run_id"],
    )
    _exact(
        binding.get("schema"),
        "p192-wcm-role1-predecessor-repository-custody-v1",
        "Role-1 repository custody binding schema", errors,
    )
    _exact(
        binding.get("pre_execution_receipt_path"), str(expected_path),
        "Role-1 pre-execution custody canonical path", errors,
    )
    _exact(
        binding.get("pre_execution_retained_path"), str(retained_path),
        "Role-1 pre-execution custody retained path", errors,
    )
    try:
        staging_parent_identity = _owned_private_directory_identity(
            retained_path.parent,
        )
    except (OSError, ValueError) as exc:
        errors.append(f"Role-1 custody staging-parent identity is invalid: {exc}")
        return errors
    _exact(
        binding.get("pre_execution_staging_parent_identity"),
        staging_parent_identity,
        "Role-1 pre-execution custody staging-parent identity", errors,
    )
    _validate_regular_file(
        expected_path, "Role-1 pre-execution repository custody receipt", errors,
    )
    _validate_regular_file(
        retained_path, "retained Role-1 pre-execution custody receipt", errors,
    )
    if errors:
        return errors
    try:
        receipt_raw = _read_regular_file_bytes(
            expected_path, "Role-1 pre-execution repository custody receipt",
            byte_cap=16777216,
        )
        receipt = decode_canonical_json(receipt_raw)
        retained_raw = _read_regular_file_bytes(
            retained_path, "retained Role-1 pre-execution custody receipt",
            byte_cap=16777216,
        )
        archived_identity = _file_identity(expected_path)
        retained_identity = _file_identity(retained_path)
    except (OSError, ValueError) as exc:
        return [f"Role-1 pre-execution custody receipt is invalid: {exc}"]
    if not isinstance(receipt, dict):
        return ["Role-1 pre-execution custody receipt root is not an object"]
    _exact(
        binding.get("pre_execution_receipt_sha256"),
        sha256_bytes(receipt_raw),
        "Role-1 pre-execution custody receipt hash", errors,
    )
    _exact(
        binding.get("pre_execution_receipt"), receipt,
        "Role-1 pre-execution custody receipt bytes/inline binding", errors,
    )
    _exact(
        retained_raw, receipt_raw,
        "Role-1 retained/archive pre-execution custody bytes", errors,
    )
    _exact(
        binding.get("pre_execution_retained_identity"), retained_identity,
        "Role-1 retained pre-execution custody identity", errors,
    )
    _require(
        (archived_identity["device"], archived_identity["inode"])
        != (retained_identity["device"], retained_identity["inode"]),
        "Role-1 retained and archived custody receipts alias one inode", errors,
    )
    archive_topology = _raw_commit_tree_topology(
        repository, archive_commit,
        "Role-1 custody archive commit", errors,
    )
    decision_topology = _raw_commit_tree_topology(
        repository, decision_commit,
        "Role-1 custody decision commit", errors,
    )
    if archive_topology is not None:
        entry = archive_topology.get(expected_relative)
        if entry is None:
            errors.append(
                "Role-1 pre-execution custody receipt is absent from archive commit"
            )
        else:
            _exact(
                entry[:2], ("100644", "blob"),
                "Role-1 pre-execution custody archived mode/type", errors,
            )
            blob = _git_blob(
                repository, entry[2],
                "Role-1 pre-execution custody archived blob", errors,
            )
            if blob is not None:
                _exact(
                    blob, receipt_raw,
                    "Role-1 pre-execution custody archive/current bytes", errors,
                )
    if decision_topology is not None:
        _exact(
            decision_topology.get(expected_relative), None,
            "Role-1 pre-execution custody absence at decision commit", errors,
        )
    profiles = decision["selective_worktree_profiles"]
    _replay_historical_sealed_repository_receipt(
        receipt, repository, decision_commit,
        profiles["predecessor_pre_execution"], errors,
    )
    terminal_errors: list[str] = []
    terminal = _sealed_repository_custody_receipt(
        repository, archive_commit, profiles["predecessor"],
        "terminal_role1_archive", terminal_errors,
    )
    errors.extend(
        f"Role-1 terminal archive custody: {item}" for item in terminal_errors
    )
    if terminal is not None:
        _exact(
            binding.get("terminal_archive_receipt"), terminal,
            "Role-1 terminal archive custody receipt", errors,
        )
        _exact(
            binding.get("terminal_archive_receipt_sha256"),
            sha256_bytes(canonical_json_bytes(terminal)),
            "Role-1 terminal archive custody receipt hash", errors,
        )
    _exact(
        binding.get("chronology"),
        "sealed_D1_then_pre_receipt_then_Role1_then_direct_A1_then_terminal_receipt_then_D2",
        "Role-1 repository custody chronology", errors,
    )
    _exact(
        binding.get("launch_handoff_trust_boundary"),
        "trusted_local_host_exclusive_workspace_between_pre_receipt_and_Role1_launch",
        "Role-1 repository custody launch handoff", errors,
    )
    _exact(
        binding.get("overall_status"), "PASS",
        "Role-1 repository custody binding status", errors,
    )
    return errors


def _protocol_output_state(
    repository: Path, run_dir: Path, control_dir: Path,
    decision_commit: str, profile: dict[str, Any], errors: list[str],
    additional_object_custody: Iterable[dict[str, Any]] = (),
) -> dict[str, Any]:
    roots = (run_dir, control_dir)
    actual = _output_leaf_paths(repository, roots, errors)
    head_raw = _git_stdout(
        repository, ["rev-parse", "HEAD"], "protocol output HEAD", errors,
    )
    if head_raw is None:
        return {"mode": "unavailable", "unexpected_paths": []}
    head = head_raw.rstrip(b"\n").decode("ascii", "replace")
    head_object_rows: list[dict[str, Any]] = []
    head_tree = _raw_protocol_head_tree(
        repository, head, errors, object_custody=head_object_rows,
    )
    index_tree = _raw_protocol_stage_zero_index(repository, errors)
    if head_tree is None or index_tree is None:
        return {"mode": "unavailable", "unexpected_paths": []}
    relative_roots = tuple(root.relative_to(repository).as_posix() for root in roots)
    selected_paths = _sparse_selected_paths(head_tree, profile, errors)
    if selected_paths is None:
        selected_paths = set()
    policy_object_ids = {
        object_id for relative, (mode_value, object_id) in head_tree.items()
        if mode_value in {"100644", "100755"}
        and (relative in selected_paths or Path(relative).name == ".gitattributes")
    }
    tracked = {
        relative for relative in index_tree
        if any(relative == root or relative.startswith(root + "/") for root in relative_roots)
    }
    unexpected: list[str] = []
    terminal_object_custody: list[dict[str, Any]] = []
    head_closure = _object_custody_by_oid(
        [*additional_object_custody, *head_object_rows],
        "protocol output structural/historical closure", errors,
    )
    if head_closure is None:
        return {"mode": "unavailable", "unexpected_paths": []}
    if not tracked:
        mode = "exact_untracked_output_trees"
        _exact(
            head, decision_commit,
            "untracked evidence protocol HEAD/decision commit", errors,
        )
        policy_sizes = _git_blob_sizes(
            repository, policy_object_ids,
            "untracked evidence policy blob size preflight", errors,
        )
        if policy_sizes is not None:
            conflicting_object_id = False
            for object_id, size in policy_sizes.items():
                prior = head_closure.get(object_id)
                if prior is not None and (
                    prior.get("kind") != "blob"
                    or prior.get("byte_length") != size
                ):
                    errors.append(
                        "untracked evidence object ID has conflicting structural/"
                        f"blob custody: {object_id}"
                    )
                    conflicting_object_id = True
            if conflicting_object_id:
                return {
                    "mode": mode, "unexpected_paths": unexpected,
                    "terminal_object_custody": [],
                }
            combined_sizes = {
                **{
                    object_id: int(row["byte_length"])
                    for object_id, row in head_closure.items()
                },
                **policy_sizes,
            }
            combined_kinds = {
                **{
                    object_id: str(row["kind"])
                    for object_id, row in head_closure.items()
                },
                **{object_id: "blob" for object_id in policy_sizes},
            }
            combined_size_errors = _distinct_blob_payload_size_errors(
                {
                    object_id: size for object_id, size in combined_sizes.items()
                    if combined_kinds[object_id] == "blob"
                },
                "untracked evidence admitted closure",
            )
            errors.extend(combined_size_errors)
            if combined_size_errors:
                return {
                    "mode": mode, "unexpected_paths": unexpected,
                    "terminal_object_custody": [],
                }
            selected_bindings: dict[str, list[tuple[Path, str]]] = {
                object_id: [] for object_id in combined_sizes
            }
            for relative in sorted(selected_paths):
                entry = head_tree.get(relative)
                if entry is None or entry[0] not in {"100644", "100755"}:
                    continue
                selected_bindings.setdefault(entry[1], []).append((
                    repository / relative,
                    f"untracked evidence selected file {relative}",
                ))
            streamed = _stream_git_blob_batch_file_equality(
                repository, combined_sizes, selected_bindings,
                "untracked evidence terminal admitted-object batch", errors,
                object_kinds=combined_kinds,
                expected_payload_sha256={
                    object_id: str(row["sha256"])
                    for object_id, row in head_closure.items()
                },
            )
            if streamed is not None:
                terminal_object_custody = [
                    {
                        "object_id": object_id,
                        "kind": combined_kinds[object_id],
                        "byte_length": combined_sizes[object_id],
                        "sha256": streamed[object_id],
                    }
                    for object_id in sorted(streamed)
                ]
    elif tracked == actual:
        mode = "exact_committed_evidence"
        _exact(
            {relative: index_tree[relative] for relative in tracked},
            {relative: head_tree.get(relative) for relative in tracked},
            "committed evidence output HEAD/index bindings", errors,
        )
        delta_raw = _git_stdout(
            repository,
            [
                "diff-tree", "--no-ext-diff", "--no-textconv", "-r",
                "--name-only", "-z", decision_commit, head,
            ],
            "committed evidence decision-to-archive delta", errors,
        )
        if delta_raw is not None:
            delta = {
                item.decode("utf-8", "replace")
                for item in delta_raw.split(b"\0") if item
            }
            _exact(delta, actual, "committed evidence exact decision-to-archive delta", errors)
        errors.extend(_archive_chain_errors(
            repository, decision_commit, head, relative_roots,
        ))
        output_bindings: dict[str, tuple[str, str, str]] = {}
        for root, label in zip(roots, ("RUN_DIR", "CONTROL_DIR")):
            relative_root = root.relative_to(repository).as_posix()
            root_actual = {
                path for path in actual if path.startswith(relative_root + "/")
            }
            root_tree = {
                path for path in head_tree if path.startswith(relative_root + "/")
            }
            _exact(
                root_tree, root_actual,
                f"committed evidence {label} verified raw-tree inventory", errors,
            )
            for relative in sorted(root_actual):
                entry = head_tree.get(relative)
                if entry is None:
                    continue
                mode_value, object_id = entry
                if mode_value not in {"100644", "100755"}:
                    errors.append(
                        f"committed evidence {label} is not a regular blob: "
                        f"{relative} ({mode_value})"
                    )
                    continue
                output_bindings[relative] = (label, mode_value, object_id)

        blob_sizes = _git_blob_sizes(
            repository,
            [
                *(binding[2] for binding in output_bindings.values()),
                *policy_object_ids,
            ],
            "committed evidence distinct blob size preflight", errors,
        )
        if blob_sizes is not None:
            conflicting_object_id = False
            for object_id, size in blob_sizes.items():
                prior = head_closure.get(object_id)
                if prior is not None and (
                    prior.get("kind") != "blob"
                    or prior.get("byte_length") != size
                ):
                    errors.append(
                        "committed evidence object ID has conflicting structural/"
                        f"blob custody: {object_id}"
                    )
                    conflicting_object_id = True
            if conflicting_object_id:
                return {
                    "mode": mode, "unexpected_paths": unexpected,
                    "terminal_object_custody": [],
                }
            distinct_total = sum(blob_sizes.values())
            if distinct_total > COMMITTED_DISTINCT_BLOB_BYTE_CAP:
                errors.append(
                    "committed evidence distinct blob payload exceeds 1 GiB cap"
                )
            for object_id, size in blob_sizes.items():
                if size > EVIDENCE_ARTIFACT_BYTE_CAP:
                    errors.append(
                        "committed evidence blob exceeds 512 MiB artifact cap: "
                        f"{object_id}"
                    )
            if (
                distinct_total <= COMMITTED_DISTINCT_BLOB_BYTE_CAP
                and all(
                    size <= EVIDENCE_ARTIFACT_BYTE_CAP
                    for size in blob_sizes.values()
                )
            ):
                combined_sizes = {
                    **{
                        object_id: int(row["byte_length"])
                        for object_id, row in head_closure.items()
                    },
                    **blob_sizes,
                }
                combined_kinds = {
                    **{
                        object_id: str(row["kind"])
                        for object_id, row in head_closure.items()
                    },
                    **{object_id: "blob" for object_id in blob_sizes},
                }
                combined_size_errors = _distinct_blob_payload_size_errors(
                    {
                        object_id: size
                        for object_id, size in combined_sizes.items()
                        if combined_kinds[object_id] == "blob"
                    },
                    "committed evidence admitted closure",
                )
                errors.extend(combined_size_errors)
                if combined_size_errors:
                    return {
                        "mode": mode, "unexpected_paths": unexpected,
                        "terminal_object_custody": [],
                    }
                file_bindings: dict[str, list[tuple[Path, str]]] = {
                    object_id: [] for object_id in combined_sizes
                }
                for relative, (root_label, mode_value, object_id) in sorted(
                    output_bindings.items()
                ):
                    path = repository / relative
                    binding_label = (
                        f"committed evidence {root_label} blob {relative}"
                    )
                    try:
                        metadata = os.lstat(path)
                    except OSError as exc:
                        errors.append(
                            f"committed evidence {root_label} cannot stat "
                            f"{relative}: {exc}"
                        )
                        continue
                    _exact(
                        _mode_string(metadata), mode_value,
                        f"committed evidence {root_label} mode {relative}", errors,
                    )
                    expected_size = blob_sizes.get(object_id)
                    if expected_size is None:
                        errors.append(
                            f"committed evidence {root_label} blob size is absent: "
                            f"{relative}"
                        )
                        continue
                    file_bindings.setdefault(object_id, []).append(
                        (path, binding_label)
                    )
                for relative in sorted(selected_paths):
                    if any(
                        relative == root or relative.startswith(root + "/")
                        for root in relative_roots
                    ):
                        continue
                    entry = head_tree.get(relative)
                    if entry is None or entry[0] not in {"100644", "100755"}:
                        continue
                    file_bindings.setdefault(entry[1], []).append((
                        repository / relative,
                        f"committed evidence selected file {relative}",
                    ))
                streamed = _stream_git_blob_batch_file_equality(
                    repository, combined_sizes, file_bindings,
                    "committed evidence terminal admitted-object batch", errors,
                    object_kinds=combined_kinds,
                    expected_payload_sha256={
                        object_id: str(row["sha256"])
                        for object_id, row in head_closure.items()
                    },
                )
                if streamed is not None:
                    terminal_object_custody = [
                        {
                            "object_id": object_id,
                            "kind": combined_kinds[object_id],
                            "byte_length": combined_sizes[object_id],
                            "sha256": streamed[object_id],
                        }
                        for object_id in sorted(streamed)
                    ]
    else:
        mode = "hybrid_or_incomplete_output_custody"
        unexpected.append(
            f"tracked output inventory differs: tracked={sorted(tracked)} actual={sorted(actual)}"
        )
    return {
        "mode": mode,
        "unexpected_paths": unexpected,
        "terminal_object_custody": terminal_object_custody,
    }


def _post_run_protocol_status_errors(
    repository: Path, run_dir: Path, control_dir: Path, decision_commit: str,
    profile: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    state = _protocol_output_state(
        repository, run_dir, control_dir, decision_commit, profile, errors,
    )
    _require(
        state["mode"] in {"exact_untracked_output_trees", "exact_committed_evidence"},
        "protocol post-run output custody is hybrid or incomplete", errors,
    )
    errors.extend(
        f"protocol post-run unexpected path: {item}"
        for item in state["unexpected_paths"]
    )
    return errors


def _protocol_terminal_state(
    repository: Path, run_dir: Path, control_dir: Path,
    decision_commit: str, profile: dict[str, Any], errors: list[str],
    additional_object_custody: Iterable[dict[str, Any]] = (),
) -> dict[str, Any]:
    return _protocol_output_state(
        repository, run_dir, control_dir, decision_commit, profile, errors,
        additional_object_custody,
    )


def _raw_commit_parents(
    repository: Path, commit: str, label: str, errors: list[str],
) -> list[str] | None:
    objects = _git_objects(repository, [commit], f"raw {label} commit", errors)
    if objects is None or commit not in objects:
        return None
    kind, raw = objects[commit]
    if kind != "commit":
        errors.append(f"raw {label} object is not a commit")
        return None
    if b"\n\n" not in raw:
        errors.append(f"raw {label} commit lacks a header terminator")
        return None
    header = raw.split(b"\n\n", 1)[0]
    trees: list[str] = []
    parents: list[str] = []
    for line in header.splitlines():
        if line.startswith(b"tree "):
            trees.append(line[5:].decode("ascii", "replace"))
        elif line.startswith(b"parent "):
            parents.append(line[7:].decode("ascii", "replace"))
    if len(trees) != 1 or re.fullmatch(r"[0-9a-f]{40}", trees[0]) is None:
        errors.append(f"raw {label} commit must contain exactly one valid tree")
        return None
    if any(re.fullmatch(r"[0-9a-f]{40}", parent) is None for parent in parents):
        errors.append(f"raw {label} commit contains an invalid parent")
        return None
    if len(set(parents)) != len(parents):
        errors.append(f"raw {label} commit contains duplicate parents")
        return None
    return parents


def _raw_commit_is_strict_ancestor(
    repository: Path, ancestor: str, descendant: str, errors: list[str],
) -> bool | None:
    if ancestor == descendant:
        return False
    pending = _raw_commit_parents(repository, descendant, "descendant", errors)
    if pending is None:
        return None
    visited: set[str] = set()
    while pending:
        commit = pending.pop()
        if commit == ancestor:
            return True
        if commit in visited:
            continue
        visited.add(commit)
        if len(visited) > 1_000_000:
            errors.append("raw commit ancestry exceeds the one-million-commit safety cap")
            return None
        parents = _raw_commit_parents(repository, commit, "ancestor traversal", errors)
        if parents is None:
            return None
        pending.extend(parents)
    return False


def _decision_commit_at_head(
    repository: Path, relative_decision: str, head: str, errors: list[str],
) -> str | None:
    """Locate the decision by raw trees on the only two admitted HEAD shapes."""
    current = head
    for depth in range(2):
        entry = _git_tree_entry(
            repository, current, relative_decision,
            f"raw decision-path entry at depth {depth}", errors,
        )
        if entry is None:
            errors.append("decision path is absent from admitted HEAD ancestry")
            return None
        parents = _raw_commit_parents(
            repository, current, f"raw decision ancestry depth {depth}", errors,
        )
        if parents is None or len(parents) != 1:
            errors.append("decision/archive ancestry is not a single-parent chain")
            return None
        parent = parents[0]
        parent_entry = _git_tree_entry(
            repository, parent, relative_decision,
            f"raw decision-path parent entry at depth {depth}", [],
        )
        if parent_entry is None:
            return current
        if parent_entry != entry:
            errors.append("decision path changed after its introduction")
            return None
        current = parent
    errors.append("decision introduction is more than one archive commit behind HEAD")
    return None


def _validate_regular_file(path: Path, label: str, errors: list[str], executable: bool = False) -> None:
    linked = _symlink_component(path)
    _require(linked is None, f"{label}: symlink path component forbidden: {linked}", errors)
    try:
        metadata = os.lstat(path)
    except OSError as exc:
        errors.append(f"{label}: cannot stat: {exc}")
        return
    _require(stat.S_ISREG(metadata.st_mode), f"{label}: not a regular file", errors)
    _require(metadata.st_nlink == 1, f"{label}: link count is not one", errors)
    if executable:
        _require(metadata.st_mode & 0o111 != 0, f"{label}: executable bit is missing", errors)


def _validate_git_checkout(
    repository: Path, package: Path, expected_commit: str, package_suffix: tuple[str, ...],
    profile: dict[str, Any], label: str, errors: list[str],
) -> None:
    _require(_symlink_component(repository) is None, f"{label}: repository has a symlink component", errors)
    _require(_symlink_component(package) is None, f"{label}: package has a symlink component", errors)
    _require(repository.is_dir(), f"{label}: repository is not a directory", errors)
    _require(package.is_dir(), f"{label}: package is not a directory", errors)
    _require(repository in package.parents, f"{label}: package is not a strict repository descendant", errors)
    _require(package.parts[-len(package_suffix):] == package_suffix, f"{label}: package suffix differs", errors)
    preflight_errors = _repository_git_preflight_errors(repository, profile)
    errors.extend(f"{label}: {item}" for item in preflight_errors)
    if preflight_errors:
        return
    top = _git_stdout(repository, ["rev-parse", "--show-toplevel"], f"{label} Git top level", errors)
    if top is not None:
        _exact(top.rstrip(b"\n").decode("utf-8", "replace"), str(repository), f"{label} Git top level", errors)
    head = _git_stdout(repository, ["rev-parse", "HEAD"], f"{label} Git HEAD", errors)
    if head is not None:
        _exact(head.rstrip(b"\n").decode("ascii", "replace"), expected_commit, f"{label} Git HEAD", errors)
    errors.extend(_protocol_repository_topology_errors(
        repository, expected_commit, (package / "target",), profile,
        forbid_tracked_excluded=True,
    ))


def _decision_custody(
    decision: dict[str, Any], decision_path: Path, decision_bytes: bytes, decision_commit: str,
) -> dict[str, Any]:
    paths = decision["paths"]
    return {
        "decision_id": decision["decision_id"],
        "decision_path": str(decision_path),
        "decision_commit": decision_commit,
        "decision_sha256": sha256_bytes(decision_bytes),
        "protocol_checkout": {
            "repository": decision["protocol_repository"],
            "repository_path": paths["protocol_repository_path"],
            "package_path": paths["protocol_package_path"],
            "protocol_commit": decision["protocol_commit"],
            "decision_commit": decision_commit,
            "prelaunch_worktree_clean": True,
        },
    }


def validate_decision(value: dict[str, Any], schema: dict[str, Any] | None = None) -> list[str]:
    schema = schema or load_json(DECISION_SCHEMA)
    errors = _schema_errors(schema, value)
    if errors:
        return errors
    paths = value["paths"]
    normalized: dict[str, Path] = {}
    for field, raw_path in paths.items():
        parsed = _normalized_absolute_path(raw_path, f"decision paths.{field}", errors)
        if parsed is not None:
            normalized[field] = parsed
    if len(normalized) != len(paths):
        return errors
    protocol_repository = normalized["protocol_repository_path"]
    _exact(
        normalized["protocol_package_path"], protocol_repository,
        "protocol package/repository identity", errors,
    )
    expected_decision = protocol_repository / DECISION_RELATIVE_DIRECTORY / f'{value["decision_id"]}.json'
    _exact(normalized["decision_json"], expected_decision, "exact decision path", errors)
    expected_run = protocol_repository / RUNS_RELATIVE_DIRECTORY / value["run_id"]
    expected_control = (
        protocol_repository / CONTROLS_RELATIVE_DIRECTORY
        / f'{value["run_id"]}-restart'
    )
    _exact(normalized["run_dir"], expected_run, "canonical RUN_DIR", errors)
    _exact(normalized["control_dir"], expected_control, "canonical CONTROL_DIR", errors)
    _exact(
        normalized["audit_file"], expected_run / "dependency-audit.json",
        "canonical AUDIT_FILE", errors,
    )
    predecessor_repository = normalized["predecessor_repository_path"]
    repository_fields = (
        "protocol_repository_path", "predecessor_repository_path",
        "producer_repository_path", "verifier_repository_path",
        "supervisor_repository_path",
    )
    for index, first_field in enumerate(repository_fields):
        for second_field in repository_fields[index + 1:]:
            _require(
                not _paths_overlap(
                    normalized[first_field], normalized[second_field],
                ),
                f"execution repositories overlap: {first_field}/{second_field}",
                errors,
            )
    _require(
        predecessor_repository in normalized["predecessor_dir"].parents,
        "predecessor_dir is not a strict predecessor-repository descendant", errors,
    )
    try:
        predecessor_decision = Path(value["predecessor_role1"]["decision_path"])
        _exact(
            predecessor_decision.parent,
            predecessor_repository / DECISION_RELATIVE_DIRECTORY,
            "Role-1 decision/predecessor repository binding", errors,
        )
    except (KeyError, TypeError):
        errors.append("Role-1 predecessor decision path binding is missing")
    if paths["factor_base_json"] != str(Path(paths["predecessor_dir"]) / "factor-base.json"):
        errors.append("factor_base_json is not predecessor_dir/factor-base.json")
    if paths["audit_file"] != str(Path(paths["run_dir"]) / "dependency-audit.json"):
        errors.append("audit_file is not run_dir/dependency-audit.json")
    if Path(paths["run_dir"]).name != value["run_id"]:
        errors.append("run_dir basename does not equal run_id")
    if Path(paths["predecessor_dir"]).name != value["predecessor_run_id"]:
        errors.append("predecessor_dir basename does not equal predecessor_run_id")
    created_date = value["created_at_utc"][:10].replace("-", "")
    _exact(value["decision_id"][4:12], created_date, "decision id/date binding", errors)
    if value["factor_base_source_commit"] != value["producer_commit"]:
        errors.append(
            "producer_commit does not equal predecessor factor_base_source_commit"
        )
    _exact(
        value["predecessor_role1"]["protocol_commit"],
        value["protocol_commit"],
        "Role-1/Role-2 shared protocol base commit", errors,
    )
    _exact(value.get("execution_controls"), EXECUTION_CONTROLS, "execution controls", errors)
    try:
        _exact(
            value.get("selective_worktree_profiles"), selective_worktree_profiles(value),
            "sealed selective worktree profiles", errors,
        )
    except ValueError as exc:
        errors.append(f"sealed selective worktree profile paths are invalid: {exc}")
    predecessor_custody = value.get("predecessor_repository_custody", {})
    expected_pre_receipt = (
        predecessor_repository
        / _role1_pre_execution_custody_relative(value["predecessor_run_id"])
    )
    expected_retained_receipt = _role1_pre_execution_retained_path(
        predecessor_repository, value["predecessor_run_id"],
    )
    _exact(
        predecessor_custody.get("pre_execution_receipt_path"),
        str(expected_pre_receipt),
        "canonical Role-1 pre-execution custody receipt path", errors,
    )
    _exact(
        predecessor_custody.get("pre_execution_retained_path"),
        str(expected_retained_receipt),
        "canonical retained Role-1 pre-execution custody path", errors,
    )
    retained_identity = predecessor_custody.get(
        "pre_execution_retained_identity", {},
    )
    _exact(
        retained_identity.get("path"), str(expected_retained_receipt),
        "retained Role-1 pre-execution custody identity path", errors,
    )
    staging_identity = predecessor_custody.get(
        "pre_execution_staging_parent_identity", {},
    )
    _exact(
        staging_identity.get("path"), str(expected_retained_receipt.parent),
        "retained Role-1 custody staging-parent identity path", errors,
    )
    for field, path in normalized.items():
        _require(
            not _paths_overlap(expected_retained_receipt, path),
            f"retained Role-1 pre-execution custody path overlaps paths.{field}",
            errors,
        )
        _require(
            not _paths_overlap(expected_retained_receipt.parent, path),
            f"retained Role-1 custody staging directory overlaps paths.{field}",
            errors,
        )
    pre_receipt = predecessor_custody.get("pre_execution_receipt", {})
    terminal_receipt = predecessor_custody.get("terminal_archive_receipt", {})
    _exact(
        pre_receipt.get("repository_path"), str(predecessor_repository),
        "Role-1 pre-execution custody repository path", errors,
    )
    _exact(
        pre_receipt.get("head_commit"),
        value["predecessor_role1"]["decision_commit"],
        "Role-1 pre-execution custody decision commit", errors,
    )
    _exact(
        pre_receipt.get("profile"),
        value["selective_worktree_profiles"]["predecessor_pre_execution"],
        "Role-1 pre-execution custody profile binding", errors,
    )
    _exact(
        pre_receipt.get("role1_launch_performed"), False,
        "Role-1 pre-execution custody launch state", errors,
    )
    _exact(
        terminal_receipt.get("repository_path"), str(predecessor_repository),
        "Role-1 terminal custody repository path", errors,
    )
    _exact(
        terminal_receipt.get("head_commit"),
        value["predecessor_role1"]["archive_commit"],
        "Role-1 terminal custody archive commit", errors,
    )
    _exact(
        terminal_receipt.get("profile"),
        value["selective_worktree_profiles"]["predecessor"],
        "Role-1 terminal custody profile binding", errors,
    )
    _exact(
        terminal_receipt.get("role1_launch_performed"), True,
        "Role-1 terminal custody launch state", errors,
    )
    if isinstance(predecessor_custody.get("pre_execution_receipt"), dict):
        _exact(
            predecessor_custody.get("pre_execution_receipt_sha256"),
            sha256_bytes(canonical_json_bytes(pre_receipt)),
            "Role-1 pre-execution custody inline hash", errors,
        )
    if isinstance(predecessor_custody.get("terminal_archive_receipt"), dict):
        _exact(
            predecessor_custody.get("terminal_archive_receipt_sha256"),
            sha256_bytes(canonical_json_bytes(terminal_receipt)),
            "Role-1 terminal custody inline hash", errors,
        )
    errors.extend(_verifier_build_admission_errors(value, runtime=False))
    binary_paths = [normalized[f"{role}_bin"] for role in ("producer", "verifier", "supervisor")]
    if len(set(binary_paths)) != 3:
        errors.append("producer, verifier, and supervisor binary paths are not pairwise distinct")
    binary_hashes = [value[f"{role}_binary_sha256"] for role in ("producer", "verifier", "supervisor")]
    if len(set(binary_hashes)) != 3:
        errors.append("producer, verifier, and supervisor binary hashes are not pairwise distinct")
    role_paths = {
        "producer": (
            normalized["producer_repository_path"], normalized["producer_package_path"],
            ("tools", "p192-weighted-cm"),
        ),
        "verifier": (
            normalized["verifier_repository_path"], normalized["verifier_package_path"],
            ("tools", "p192-weighted-cm-verify"),
        ),
        "supervisor": (
            normalized["supervisor_repository_path"], normalized["supervisor_package_path"],
            ("tools", "p192-weighted-cm-supervisor"),
        ),
    }
    for role, (repository, package, suffix) in role_paths.items():
        _require(repository in package.parents, f"{role} package is not a strict repository descendant", errors)
        _require(package.parts[-len(suffix):] == suffix, f"{role} package suffix differs", errors)
    run = normalized["run_dir"]
    control = normalized["control_dir"]
    if run == control or run in control.parents or control in run.parents:
        errors.append("run_dir and control_dir overlap")
    output_paths = {
        "run_dir": run,
        "control_dir": control,
        "audit_file": normalized["audit_file"],
    }
    immutable_inputs = {
        key: normalized[key] for key in (
            "protocol_repository_path", "protocol_package_path", "decision_json",
            "producer_bin", "verifier_bin", "supervisor_bin",
            "producer_repository_path", "producer_package_path",
            "verifier_repository_path", "verifier_package_path",
            "supervisor_repository_path", "supervisor_package_path",
            "predecessor_repository_path", "predecessor_dir", "factor_base_json",
        )
    }
    for output_name, output_path in output_paths.items():
        for input_name, input_path in immutable_inputs.items():
            if output_name == "audit_file" and input_name in {
                "protocol_repository_path", "protocol_package_path",
            }:
                # This is the only overlap exemption: the exact canonical audit
                # leaf is necessarily below the canonical protocol output tree.
                continue
            if output_name in {"run_dir", "control_dir"} and input_name in {
                "protocol_repository_path", "protocol_package_path",
            }:
                # Canonical experiment outputs are deliberately repository children.
                continue
            if _paths_overlap(output_path, input_path):
                errors.append(f"{output_name} overlaps immutable input {input_name}")
    for field, expected in resolved_argv(value).items():
        _exact(value[field], expected, field, errors)
    protected = {
        name: sha256_path(path) for name, path in PROTECTED_PROTOCOL_PATHS.items()
    }
    _exact(value.get("protected_protocol_blobs"), protected, "protected protocol blobs", errors)
    return errors


def _validate_dispatch_decision_impl(
    decision_path: Path, phase: str, run_dir: Path | None = None,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, list[str]]:
    """Validate exact committed decision and all pre/post-dispatch filesystem custody."""
    errors: list[str] = []
    _require(phase in {"pre-dispatch", "post-run"}, "decision phase is invalid", errors)
    supplied = _normalized_absolute_path(str(decision_path), "supplied decision path", errors)
    if supplied is None:
        return None, None, errors
    _validate_regular_file(supplied, "decision", errors)
    try:
        _require(
            os.lstat(supplied).st_mode & 0o111 == 0,
            "decision working-tree mode is not non-executable 100644", errors,
        )
    except OSError:
        pass
    try:
        raw = _read_regular_file_bytes(supplied, "decision")
        decision_identity_before = _file_identity(supplied)
        decision = decode_canonical_json(raw)
    except Exception as exc:
        errors.append(f"decision bytes invalid: {exc}")
        return None, None, errors
    if not isinstance(decision, dict):
        return None, None, errors + ["decision root is not an object"]
    errors.extend(validate_decision(decision))
    if errors:
        return decision, None, errors
    paths = decision["paths"]
    _exact(paths["decision_json"], str(supplied), "supplied/exact decision path", errors)
    protocol_repository = Path(paths["protocol_repository_path"])
    protocol_package = Path(paths["protocol_package_path"])
    selective_profiles = decision["selective_worktree_profiles"]
    protocol_sparse_profile = selective_profiles["protocol"]
    source_sparse_profile = selective_profiles["source"]
    predecessor_sparse_profile = selective_profiles["predecessor"]
    _exact(protocol_package, protocol_repository, "protocol package/repository path", errors)
    _require(_symlink_component(protocol_repository) is None, "protocol repository has a symlink component", errors)
    _require(protocol_repository.is_dir(), "protocol repository is not a directory", errors)
    repository_identity_paths = {
        "protocol": protocol_repository,
        "predecessor": Path(paths["predecessor_repository_path"]),
        **{
            role: Path(paths[f"{role}_repository_path"])
            for role in ("producer", "verifier", "supervisor")
        },
    }
    repository_identities: dict[str, dict[str, Any]] = {}
    for name, repository_path in repository_identity_paths.items():
        linked = _symlink_component(repository_path)
        _require(
            linked is None,
            f"{name} repository has a symlink component: {linked}", errors,
        )
        try:
            repository_identities[name] = _directory_identity(repository_path)
        except (OSError, ValueError) as exc:
            errors.append(f"{name} repository identity unavailable: {exc}")
    preflight_errors = _repository_git_preflight_errors(
        protocol_repository, protocol_sparse_profile,
    )
    errors.extend(preflight_errors)
    if preflight_errors:
        return decision, None, errors
    top = _git_stdout(protocol_repository, ["rev-parse", "--show-toplevel"], "protocol Git top level", errors)
    if top is not None:
        _exact(top.rstrip(b"\n").decode("utf-8", "replace"), str(protocol_repository), "protocol Git top level", errors)
    head = _git_stdout(protocol_repository, ["rev-parse", "HEAD"], "protocol HEAD", errors)
    protocol_head = ""
    if head is not None:
        protocol_head = head.rstrip(b"\n").decode("ascii", "replace")
        _require(re.fullmatch(r"[0-9a-f]{40}", protocol_head) is not None, "protocol HEAD is not lowercase 40-hex", errors)
    protocol_commit = decision["protocol_commit"]
    protocol_topology: dict[str, tuple[str, str, str]] | None = None
    shared_base_payload_object_ids: tuple[str, ...] = ()
    initial_shared_base_payload_map: list[dict[str, Any]] | None = None
    relative_decision = str(DECISION_RELATIVE_DIRECTORY / f'{decision["decision_id"]}.json')
    decision_commit = ""
    if protocol_head:
        located = _decision_commit_at_head(
            protocol_repository, relative_decision, protocol_head, errors,
        )
        decision_commit = located or ""
    expected_run = Path(paths["run_dir"])
    expected_control = Path(paths["control_dir"])
    if phase == "post-run":
        size_errors = _evidence_size_errors(expected_run, expected_control)
        errors.extend(size_errors)
        if size_errors:
            return decision, None, errors
    if protocol_head:
        errors.extend(_protocol_repository_topology_errors(
            protocol_repository, protocol_head, (expected_run, expected_control),
            protocol_sparse_profile,
        ))
    if phase == "pre-dispatch":
        _exact(protocol_head, decision_commit, "pre-dispatch protocol HEAD/decision commit", errors)
    else:
        if not decision_commit:
            errors.append(
                "protocol post-run output custody cannot be audited without an admitted decision commit"
            )
        else:
            try:
                errors.extend(_post_run_protocol_status_errors(
                    protocol_repository, expected_run, expected_control,
                    decision_commit, protocol_sparse_profile,
                ))
            except ValueError as exc:
                errors.append(f"protocol post-run output path is outside repository: {exc}")
    for commit, label in ((protocol_commit, "protocol commit"), (decision_commit, "decision commit"), (protocol_head, "protocol HEAD")):
        if commit:
            result = _git(protocol_repository, ["cat-file", "-e", f"{commit}^{{commit}}"])
            _require(result is not None and result.returncode == 0, f"{label} is not a Git commit", errors)
    _require(protocol_commit != decision_commit, "protocol commit must be a strict decision-commit ancestor", errors)
    if decision_commit:
        decision_parents = _raw_commit_parents(
            protocol_repository, decision_commit, "decision commit", errors,
        )
        if decision_parents is not None:
            _exact(
                decision_parents, [protocol_commit],
                "decision commit single direct protocol parent", errors,
            )
        decision_delta_raw = _git_stdout(
            protocol_repository,
            [
                "diff-tree", "--no-ext-diff", "--no-textconv", "-r",
                "--name-only", "-z", protocol_commit, decision_commit,
            ],
            "protocol-to-decision exact delta", errors,
        )
        if decision_delta_raw is not None:
            decision_delta = {
                item.decode("utf-8", "replace")
                for item in decision_delta_raw.split(b"\0") if item
            }
            _exact(
                decision_delta, {relative_decision},
                "protocol-to-decision changed path set", errors,
            )
        protocol_topology = _raw_commit_tree_topology(
            protocol_repository, protocol_commit, "protocol commit", errors,
        )
        decision_topology = _raw_commit_tree_topology(
            protocol_repository, decision_commit, "decision commit", errors,
        )
        if protocol_topology is not None and decision_topology is not None:
            changed_topology = {
                relative
                for relative in set(protocol_topology) | set(decision_topology)
                if protocol_topology.get(relative) != decision_topology.get(relative)
            }
            permitted_topology = {
                relative for relative in changed_topology
                if relative == relative_decision
                or relative_decision.startswith(relative + "/")
            }
            _exact(
                changed_topology, permitted_topology,
                "protocol-to-decision full tree topology delta", errors,
            )
            _require(
                bool(changed_topology),
                "protocol-to-decision raw topology delta is empty", errors,
            )
            _exact(
                protocol_topology.get(relative_decision), None,
                "fresh decision absence in raw protocol tree", errors,
            )
            raw_decision_entry = decision_topology.get(relative_decision)
            if raw_decision_entry is None:
                errors.append("decision is absent from raw decision-commit tree")
            else:
                _exact(
                    raw_decision_entry[:2], ("100644", "blob"),
                    "decision raw committed mode/type", errors,
                )
    at_protocol = _git_stdout(
        protocol_repository, ["ls-tree", "-z", protocol_commit, "--", relative_decision],
        "decision absence at protocol commit", errors,
    )
    if at_protocol is not None:
        _exact(at_protocol, b"", "fresh decision absence at protocol commit", errors)
    if decision_commit:
        entry = _git_tree_entry(
            protocol_repository, decision_commit, relative_decision,
            "decision at decision commit", errors,
        )
        if entry is not None:
            mode, kind, object_id = entry
            _exact((mode, kind), ("100644", "blob"), "decision Git mode/type", errors)
            committed = _git_blob(protocol_repository, object_id, "committed decision blob", errors)
            if committed is not None:
                _exact(committed, raw, "decision working bytes", errors)
    protected_identities: dict[str, dict[str, Any]] = {}
    for name, relative in PROTECTED_PROTOCOL_RELATIVE_PATHS.items():
        expected_hash = decision["protected_protocol_blobs"][name]
        current = protocol_repository / relative
        _validate_regular_file(current, f"protected current {relative}", errors)
        try:
            current_bytes, metadata = _regular_file_snapshot(
                current, f"protected current {relative}",
            )
            current_mode = "100755" if metadata.st_mode & 0o111 else "100644"
        except (OSError, ValueError):
            continue
        _exact(current_mode, "100644", f"protected current mode {relative}", errors)
        _exact(sha256_bytes(current_bytes), expected_hash, f"protected current hash {relative}", errors)
        try:
            protected_identities[name] = _file_identity(current)
        except (OSError, ValueError) as exc:
            errors.append(f"protected current identity unavailable {relative}: {exc}")
        entries: list[tuple[str, str, str] | None] = []
        commit_labels = [(protocol_commit, "protocol"), (decision_commit, "decision")]
        if protocol_head and protocol_head not in {protocol_commit, decision_commit}:
            commit_labels.append((protocol_head, "current-head"))
        for commit, label in commit_labels:
            if not commit:
                entries.append(None)
                continue
            tree_entry = _git_tree_entry(
                protocol_repository, commit, relative,
                f"protected {label} entry {relative}", errors,
            )
            entries.append(tree_entry)
            if tree_entry is not None:
                mode, kind, object_id = tree_entry
                _exact((mode, kind), ("100644", "blob"), f"protected {label} mode/type {relative}", errors)
                blob = _git_blob(protocol_repository, object_id, f"protected {label} blob {relative}", errors)
                if blob is not None:
                    _exact(blob, current_bytes, f"protected {label}/current bytes {relative}", errors)
                    _exact(sha256_bytes(blob), expected_hash, f"protected {label} hash {relative}", errors)
        if entries and all(entry is not None for entry in entries):
            _require(
                len(set(entries)) == 1,
                f"protected Git entry stability differs for {relative}", errors,
            )
    role_specs = (
        ("producer", decision["producer_commit"], ("tools", "p192-weighted-cm")),
        ("verifier", decision["verifier_commit"], ("tools", "p192-weighted-cm-verify")),
        ("supervisor", decision["supervisor_commit"], ("tools", "p192-weighted-cm-supervisor")),
    )
    binary_identities: dict[str, dict[str, Any]] = {}
    source_build_rows: dict[str, list[dict[str, Any]]] = {}
    for role, commit, suffix in role_specs:
        repository = Path(paths[f"{role}_repository_path"])
        package = Path(paths[f"{role}_package_path"])
        _validate_git_checkout(
            repository, package, commit, suffix, source_sparse_profile, role, errors,
        )
        binary = Path(paths[f"{role}_bin"])
        _validate_regular_file(binary, f"{role} binary", errors, executable=True)
        try:
            identity = _file_identity(binary)
            binary_identities[role] = identity
            _exact(identity["link_count"], 1, f"{role} binary link count", errors)
            _exact(identity["sha256"], decision[f"{role}_binary_sha256"], f"{role} binary hash", errors)
            _exact(identity["byte_length"], decision[f"{role}_binary_byte_length"], f"{role} binary length", errors)
        except (OSError, ValueError) as exc:
            errors.append(f"{role} binary identity unavailable: {exc}")
        rows = _source_build_input_rows(repository, package, commit, role, errors)
        if rows is not None:
            source_build_rows[role] = rows
    try:
        verifier_package = Path(paths["verifier_package_path"])
        errors.extend(_verifier_dependency_errors(
            _read_regular_file_bytes(
                verifier_package / "Cargo.toml", "verifier Cargo.toml",
            ),
            _read_regular_file_bytes(
                verifier_package / "Cargo.lock", "verifier Cargo.lock",
            ),
            Path(paths["verifier_repository_path"]),
            verifier_package,
            Path(paths["producer_repository_path"]),
            Path(paths["producer_package_path"]),
        ))
    except (OSError, ValueError) as exc:
        errors.append(f"verifier pre-dispatch dependency provenance is unreadable: {exc}")
    if len(binary_identities) == 3:
        inode_keys = {
            (item["device"], item["inode"]) for item in binary_identities.values()
        }
        _require(
            len(inode_keys) == 3,
            "producer, verifier, and supervisor binaries share a device/inode", errors,
        )
        _require(
            len({item["sha256"] for item in binary_identities.values()}) == 3,
            "producer, verifier, and supervisor binary bytes are not distinct", errors,
        )
    predecessor_repository = Path(paths["predecessor_repository_path"])
    predecessor = Path(paths["predecessor_dir"])
    predecessor_preflight = _repository_git_preflight_errors(
        predecessor_repository, predecessor_sparse_profile,
    )
    errors.extend(f"predecessor archive: {item}" for item in predecessor_preflight)
    predecessor_head = ""
    if not predecessor_preflight:
        predecessor_head_raw = _git_stdout(
            predecessor_repository, ["rev-parse", "HEAD"],
            "predecessor archive HEAD", errors,
        )
        if predecessor_head_raw is not None:
            predecessor_head = predecessor_head_raw.rstrip(b"\n").decode("ascii", "replace")
            _exact(
                predecessor_head, decision["predecessor_role1"]["archive_commit"],
                "predecessor archive HEAD binding", errors,
            )
            errors.extend(_protocol_repository_topology_errors(
                predecessor_repository, predecessor_head, (),
                predecessor_sparse_profile,
            ))
            role1_decision_commit = decision["predecessor_role1"]["decision_commit"]
            role1_protocol_commit = decision["predecessor_role1"]["protocol_commit"]
            role1_decision_parents = _raw_commit_parents(
                predecessor_repository, role1_decision_commit,
                "Role-1 decision", errors,
            )
            if role1_decision_parents is not None:
                _exact(
                    role1_decision_parents, [role1_protocol_commit],
                    "Role-1 decision direct protocol parent", errors,
                )
            try:
                role1_decision_relative = Path(
                    decision["predecessor_role1"]["decision_path"]
                ).relative_to(predecessor_repository).as_posix()
            except ValueError:
                errors.append(
                    "Role-1 decision path is outside predecessor repository"
                )
                role1_decision_relative = ""
            role1_protocol_topology = _raw_commit_tree_topology(
                predecessor_repository, role1_protocol_commit,
                "Role-1 protocol commit", errors,
            )
            if protocol_topology is not None and role1_protocol_topology is not None:
                _exact(
                    role1_protocol_topology, protocol_topology,
                    "Role-1/Role-2 shared protocol base raw topology", errors,
                )
            role2_protocol_objects = _git_objects(
                protocol_repository, [protocol_commit],
                "Role-2 shared protocol base raw commit", errors,
            )
            role1_protocol_objects = _git_objects(
                predecessor_repository, [role1_protocol_commit],
                "Role-1 shared protocol base raw commit", errors,
            )
            if (
                role2_protocol_objects is not None
                and role1_protocol_objects is not None
                and protocol_commit in role2_protocol_objects
                and role1_protocol_commit in role1_protocol_objects
            ):
                _exact(
                    role1_protocol_objects[role1_protocol_commit],
                    role2_protocol_objects[protocol_commit],
                    "Role-1/Role-2 shared protocol base raw commit bytes", errors,
                )
            if (
                protocol_topology is not None
                and role1_protocol_topology is not None
                and protocol_topology == role1_protocol_topology
            ):
                protocol_leaf_tree = _leaf_tree(protocol_topology)
                role1_leaf_tree = _leaf_tree(role1_protocol_topology)

                def selected_at_shared_base(profile: dict[str, Any]) -> set[str]:
                    exact = set(profile["materialized_exact_paths"])
                    mutable_exact = set(profile.get("mutable_output_exact_paths", []))
                    prefixes = tuple(profile["materialized_subtree_prefixes"])
                    return {
                        relative for relative, (mode, _object_id) in protocol_leaf_tree.items()
                        if mode in {"100644", "100755"}
                        and (
                            relative in exact or relative in mutable_exact
                            or any(
                                relative == prefix
                                or relative.startswith(prefix + "/")
                                for prefix in prefixes
                            )
                        )
                    }

                shared_payload_paths = (
                    selected_at_shared_base(protocol_sparse_profile)
                    | selected_at_shared_base(
                        selective_profiles["predecessor_pre_execution"]
                    )
                    | {
                        relative for relative, (mode, _object_id)
                        in protocol_leaf_tree.items()
                        if mode in {"100644", "100755"}
                        and Path(relative).name == ".gitattributes"
                    }
                )
                shared_base_payload_object_ids = tuple(sorted({
                    protocol_leaf_tree[relative][1]
                    for relative in shared_payload_paths
                }))
                role2_payload_map = _git_blob_payload_custody_map(
                    protocol_repository,
                    shared_base_payload_object_ids,
                    "Role-2 shared-base execution payloads", errors,
                )
                role1_payload_map = _git_blob_payload_custody_map(
                    predecessor_repository,
                    shared_base_payload_object_ids,
                    "Role-1 shared-base execution payloads", errors,
                )
                if role2_payload_map is not None and role1_payload_map is not None:
                    _exact(
                        role1_payload_map, role2_payload_map,
                        "Role-1/Role-2 shared protocol base selected/policy "
                        "blob SHA-256 custody map", errors,
                    )
                    if role1_payload_map == role2_payload_map:
                        initial_shared_base_payload_map = role2_payload_map
            role1_decision_topology = _raw_commit_tree_topology(
                predecessor_repository, role1_decision_commit,
                "Role-1 decision commit", errors,
            )
            if (
                role1_decision_relative
                and role1_protocol_topology is not None
                and role1_decision_topology is not None
            ):
                role1_changed_topology = {
                    relative
                    for relative in (
                        set(role1_protocol_topology)
                        | set(role1_decision_topology)
                    )
                    if role1_protocol_topology.get(relative)
                    != role1_decision_topology.get(relative)
                }
                role1_permitted_topology = {
                    relative for relative in role1_changed_topology
                    if relative == role1_decision_relative
                    or role1_decision_relative.startswith(relative + "/")
                }
                _exact(
                    role1_changed_topology, role1_permitted_topology,
                    "Role-1 protocol-to-decision full tree topology delta",
                    errors,
                )
                _exact(
                    role1_protocol_topology.get(role1_decision_relative), None,
                    "Role-1 decision absence at protocol commit", errors,
                )
                role1_decision_entry = role1_decision_topology.get(
                    role1_decision_relative,
                )
                if role1_decision_entry is not None:
                    _exact(
                        role1_decision_entry[:2], ("100644", "blob"),
                        "Role-1 decision committed mode/type", errors,
                    )
            role1_archive_parents = _raw_commit_parents(
                predecessor_repository, predecessor_head,
                "Role-1 archive", errors,
            )
            if role1_archive_parents is not None:
                _exact(
                    role1_archive_parents, [role1_decision_commit],
                    "Role-1 archive direct decision parent", errors,
                )
            try:
                predecessor_relative = predecessor.relative_to(
                    predecessor_repository,
                ).as_posix()
                role1_archive_topology = _raw_commit_tree_topology(
                    predecessor_repository, predecessor_head,
                    "Role-1 archive commit", errors,
                )
                if role1_decision_topology is not None:
                    preexisting_predecessor = sorted(
                        relative for relative in role1_decision_topology
                        if relative == predecessor_relative
                        or relative.startswith(predecessor_relative + "/")
                    )
                    _exact(
                        preexisting_predecessor, [],
                        "Role-1 predecessor run absence at decision commit",
                        errors,
                    )
                if role1_archive_topology is not None:
                    expected_leaves = {
                        f"{predecessor_relative}/{relative}"
                        for relative in ROLE1_REQUIRED_PATHS
                    }
                    expected_directories = {predecessor_relative}
                    for leaf in expected_leaves:
                        parent = Path(leaf).parent
                        while parent.as_posix() != predecessor_relative:
                            expected_directories.add(parent.as_posix())
                            parent = parent.parent
                    expected_subtree = expected_directories | expected_leaves
                    actual_subtree = {
                        relative for relative in role1_archive_topology
                        if relative == predecessor_relative
                        or relative.startswith(predecessor_relative + "/")
                    }
                    _exact(
                        actual_subtree, expected_subtree,
                        "Role-1 archive exact predecessor subtree", errors,
                    )
                    for relative in sorted(expected_leaves & actual_subtree):
                        mode, kind, _object_id = role1_archive_topology[relative]
                        _require(
                            mode in {"100644", "100755"} and kind == "blob",
                            f"Role-1 archive predecessor leaf is not regular: {relative}",
                            errors,
                        )
                    custody_relative = _role1_pre_execution_custody_relative(
                        decision["predecessor_run_id"],
                    )
                    custody_entry = role1_archive_topology.get(custody_relative)
                    if custody_entry is None:
                        errors.append(
                            "Role-1 archive omits pre-execution repository custody receipt"
                        )
                    else:
                        _exact(
                            custody_entry[:2], ("100644", "blob"),
                            "Role-1 archived pre-execution custody mode/type", errors,
                        )
                errors.extend(_archive_chain_errors(
                    predecessor_repository, role1_decision_commit,
                    predecessor_head,
                    {
                        predecessor_relative,
                        _role1_pre_execution_custody_relative(
                            decision["predecessor_run_id"],
                        ),
                    },
                ))
            except ValueError:
                errors.append("Role-1 predecessor run is outside predecessor repository")
            errors.extend(_predecessor_repository_custody_errors(
                decision, predecessor_repository, role1_decision_commit,
                predecessor_head,
            ))
    _require(_symlink_component(predecessor) is None, "predecessor has a symlink component", errors)
    _require(predecessor.is_dir(), "predecessor is not a directory", errors)
    predecessor_identities: dict[str, dict[str, Any]] = {}
    for name in PREDECESSOR_PATHS:
        path = predecessor / name
        _validate_regular_file(path, f"predecessor {name}", errors)
        try:
            identity = _file_identity(path)
            predecessor_identities[name] = identity
            _exact(identity["link_count"], 1, f"predecessor {name} link count", errors)
            _exact(identity["sha256"], decision["predecessor_artifacts"][name], f"predecessor hash {name}", errors)
        except (OSError, ValueError) as exc:
            errors.append(f"predecessor {name} identity unavailable: {exc}")
    retained_pre_custody = Path(
        decision["predecessor_repository_custody"][
            "pre_execution_retained_path"
        ]
    )
    try:
        retained_pre_identity = _file_identity(retained_pre_custody)
        predecessor_identities[
            "pre_execution_repository_custody"
        ] = retained_pre_identity
        _exact(
            retained_pre_identity,
            decision["predecessor_repository_custody"][
                "pre_execution_retained_identity"
            ],
            "retained pre-execution repository custody identity", errors,
        )
    except (OSError, ValueError) as exc:
        errors.append(
            f"retained pre-execution repository custody unavailable: {exc}"
        )
    try:
        factor_base_bytes = _read_regular_file_bytes(
            predecessor / "factor-base.json", "pre-dispatch factor base",
        )
        factor_base = decode_canonical_json(factor_base_bytes)
        _exact(factor_base.get("source_commit"), decision["factor_base_source_commit"], "pre-dispatch factor-base source commit", errors)
        expected_sidecar = f'{sha256_bytes(factor_base_bytes)}  factor-base.json\n'.encode("ascii")
        _exact(
            _read_regular_file_bytes(
                predecessor / "factor-base.sha256",
                "pre-dispatch factor-base sidecar",
            ),
            expected_sidecar, "pre-dispatch factor-base sidecar", errors,
        )
    except Exception as exc:
        errors.append(f"pre-dispatch predecessor semantic validation failed: {exc}")
    role1_binding = _role1_predecessor_binding(
        predecessor, predecessor_repository, errors,
    )
    if role1_binding is not None:
        _exact(
            decision.get("predecessor_role1"), role1_binding,
            "complete Role-1 predecessor binding", errors,
        )
        role1_receipt = role1_binding.get("receipt", {})
        role1_decision_binding = role1_receipt.get("decision_binding", {})
        _exact(
            role1_binding.get("run_id"), decision["predecessor_run_id"],
            "Role-1 predecessor run id", errors,
        )
        _exact(
            role1_binding.get("source_commit"), decision["factor_base_source_commit"],
            "Role-1 predecessor source/factor-base commit", errors,
        )
        _exact(
            role1_binding.get("verifier_commit"), decision["verifier_commit"],
            "Role-1/Role-2 verifier commit", errors,
        )
        _exact(
            role1_decision_binding.get("protocol_repository_path"),
            paths["predecessor_repository_path"],
            "Role-1 predecessor archive repository path", errors,
        )
        role1_producer = role1_receipt.get("producer", {})
        role1_verifier = role1_receipt.get("verifier", {})
        role1_dependency = role1_receipt.get("dependency_audit", {})
        _exact(
            role1_producer.get("binary_sha256"), decision["producer_binary_sha256"],
            "Role-1/Role-2 producer binary", errors,
        )
        _exact(
            role1_verifier.get("binary_sha256"), decision["verifier_binary_sha256"],
            "Role-1/Role-2 verifier binary", errors,
        )
        _exact(role1_receipt.get("overall_status"), "PASS", "Role-1 receipt status", errors)
        _exact(
            role1_dependency.get("verifier_crypto_lib_found"), False,
            "Role-1 verifier dependency isolation", errors,
        )
        _exact(
            role1_dependency.get("shared_implementation_components"), [],
            "Role-1 shared implementation components", errors,
        )
        _exact(
            role1_binding.get("archive_commit"), predecessor_head,
            "Role-1 archive checkout HEAD", errors,
        )
    # The bound Cargo executable is the last admitted external tool.  All
    # mutable inputs above were snapshotted first and are rechecked after it.
    errors.extend(_verifier_build_admission_errors(decision, runtime=True))
    for label, path in (
        ("RUN_DIR", expected_run), ("CONTROL_DIR", expected_control),
        ("AUDIT_FILE", Path(paths["audit_file"])),
    ):
        linked = _symlink_component(path)
        _require(linked is None, f"{label} has a symlink component: {linked}", errors)
    if phase == "pre-dispatch":
        _require(not os.path.lexists(expected_run), "pre-dispatch RUN_DIR already exists", errors)
        _require(not os.path.lexists(expected_control), "pre-dispatch CONTROL_DIR already exists", errors)
    else:
        if run_dir is None:
            errors.append("post-run validation requires run_dir")
        else:
            parsed_run = _normalized_absolute_path(str(run_dir), "supplied run_dir", errors)
            if parsed_run is not None:
                _exact(parsed_run, expected_run, "supplied/decision run_dir", errors)
        _require(expected_run.is_dir(), "post-run RUN_DIR is not a directory", errors)
        _require(_symlink_component(expected_run) is None, "post-run RUN_DIR has a symlink component", errors)
        if os.path.lexists(expected_control):
            _require(expected_control.is_dir(), "post-run CONTROL_DIR is not a directory", errors)
            _require(_symlink_component(expected_control) is None, "post-run CONTROL_DIR has a symlink component", errors)
    protocol_historical_rows = _historical_repository_object_custody(
        protocol_repository,
        (
            (
                protocol_commit,
                (
                    protocol_sparse_profile,
                    selective_profiles["predecessor_pre_execution"],
                ),
            ),
            (decision_commit, ()),
        ),
        "Role-2 protocol historical custody", errors,
    ) or []
    predecessor_historical_rows = _historical_repository_object_custody(
        predecessor_repository,
        (
            (
                decision["predecessor_role1"]["protocol_commit"],
                (
                    protocol_sparse_profile,
                    selective_profiles["predecessor_pre_execution"],
                ),
            ),
            (
                decision["predecessor_role1"]["decision_commit"],
                (selective_profiles["predecessor_pre_execution"],),
            ),
        ),
        "Role-1 predecessor historical custody", errors,
    ) or []
    if shared_base_payload_object_ids and initial_shared_base_payload_map is not None:
        terminal_role2_shared_map = _git_blob_payload_custody_map(
            protocol_repository, shared_base_payload_object_ids,
            "terminal Role-2 shared-base execution payloads", errors,
        )
        terminal_role1_shared_map = _git_blob_payload_custody_map(
            predecessor_repository, shared_base_payload_object_ids,
            "terminal Role-1 shared-base execution payloads", errors,
        )
        if terminal_role2_shared_map is not None:
            _exact(
                terminal_role2_shared_map, initial_shared_base_payload_map,
                "terminal Role-2 shared-base payload custody stability", errors,
            )
        if terminal_role1_shared_map is not None:
            _exact(
                terminal_role1_shared_map, initial_shared_base_payload_map,
                "terminal Role-1 shared-base payload custody stability", errors,
            )
        if terminal_role2_shared_map is not None and terminal_role1_shared_map is not None:
            _exact(
                terminal_role1_shared_map, terminal_role2_shared_map,
                "terminal cross-repository shared-base payload custody", errors,
            )
    # Cargo metadata and Role-1 replay run after the first source-repository
    # admission.  Recheck every implementation checkout now, with no later Git
    # call against that checkout, before making the protocol scan absolutely
    # last.
    for role, commit, suffix in role_specs:
        repository = Path(paths[f"{role}_repository_path"])
        package = Path(paths[f"{role}_package_path"])
        preflight = _repository_git_preflight_errors(repository, source_sparse_profile)
        errors.extend(f"terminal {role}: {item}" for item in preflight)
        if preflight:
            continue
        terminal_role_head = _git_stdout(
            repository, ["rev-parse", "HEAD"], f"terminal {role} HEAD", errors,
        )
        if terminal_role_head is not None:
            _exact(
                terminal_role_head.rstrip(b"\n").decode("ascii", "replace"),
                commit, f"terminal {role} HEAD", errors,
            )
        errors.extend(_protocol_repository_topology_errors(
            repository, commit, (package / "target",), source_sparse_profile,
            forbid_tracked_excluded=True,
        ))
    predecessor_terminal_preflight = _repository_git_preflight_errors(
        predecessor_repository, predecessor_sparse_profile,
    )
    errors.extend(
        f"terminal predecessor archive: {item}"
        for item in predecessor_terminal_preflight
    )
    if not predecessor_terminal_preflight:
        terminal_predecessor_head = _git_stdout(
            predecessor_repository, ["rev-parse", "HEAD"],
            "terminal predecessor archive HEAD", errors,
        )
        if terminal_predecessor_head is not None:
            _exact(
                terminal_predecessor_head.rstrip(b"\n").decode("ascii", "replace"),
                predecessor_head, "terminal predecessor archive HEAD stability", errors,
            )
        errors.extend(_protocol_repository_topology_errors(
            predecessor_repository, predecessor_head, (),
            predecessor_sparse_profile,
            additional_object_custody=predecessor_historical_rows,
        ))
    # This is deliberately the last protocol-repository operation.  It proves
    # that no earlier Git/config/Role-1 validation step changed HEAD, index, raw
    # bytes, or topology after the first admission scan.
    terminal_protocol_preflight = _repository_git_preflight_errors(
        protocol_repository, protocol_sparse_profile,
    )
    errors.extend(
        f"terminal protocol: {item}" for item in terminal_protocol_preflight
    )
    if not terminal_protocol_preflight:
        terminal_head_raw = _git_stdout(
            protocol_repository, ["rev-parse", "HEAD"],
            "terminal protocol HEAD", errors,
        )
        if terminal_head_raw is not None:
            terminal_head = terminal_head_raw.rstrip(b"\n").decode(
                "ascii", "replace",
            )
            _exact(
                terminal_head, protocol_head,
                "terminal protocol HEAD stability", errors,
            )
            errors.extend(_protocol_repository_topology_errors(
                protocol_repository, terminal_head,
                (expected_run, expected_control), protocol_sparse_profile,
                additional_object_custody=protocol_historical_rows,
            ))
    # No process or Git command follows this point.  Recheck every originally
    # snapshotted external file/directory identity after Cargo and all replay.
    errors.extend(_terminal_immutable_input_errors(
        decision,
        decision_identity=decision_identity_before,
        protected_identities=protected_identities,
        binary_identities=binary_identities,
        source_build_rows=source_build_rows,
        predecessor_identities=predecessor_identities,
        repository_identities=repository_identities,
    ))
    custody = None if not decision_commit else _decision_custody(decision, supplied, raw, decision_commit)
    return decision, custody, errors


def validate_dispatch_decision(
    decision_path: Path, phase: str, run_dir: Path | None = None,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, list[str]]:
    """Fail closed instead of propagating a raced or special-file read error."""
    try:
        return _validate_dispatch_decision_impl(decision_path, phase, run_dir)
    except (OSError, ValueError) as exc:
        return None, None, [f"dispatch filesystem custody failure: {exc}"]


def _artifact_record(path: Path, relative: str) -> dict[str, Any]:
    data = _read_regular_file_bytes(path, f"artifact {relative}")
    return {"path": relative, "byte_length": len(data), "sha256": sha256_bytes(data)}


def _check_artifact_record(
    record: Any, path: Path, relative: str, label: str, errors: list[str],
) -> None:
    if not isinstance(record, dict):
        errors.append(f"{label}: artifact record is not an object")
        return
    try:
        expected = _artifact_record(path, relative)
    except (OSError, ValueError) as exc:
        errors.append(f"{label}: cannot read artifact: {exc}")
        return
    _exact(record, expected, label, errors)


def _load_json_artifact(path: Path, label: str, errors: list[str]) -> dict[str, Any] | None:
    _validate_regular_file(path, label, errors)
    try:
        value = decode_canonical_json(_read_regular_file_bytes(path, label))
    except Exception as exc:
        errors.append(f"{label}: invalid canonical JSON: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{label}: JSON root is not an object")
        return None
    document_errors = validate_artifact_document(value)
    errors.extend(f"{label}: {error}" for error in document_errors)
    if document_errors:
        return None
    return value


def _load_jsonl_artifact(
    path: Path,
    label: str,
    errors: list[str],
    *,
    index_field: str = "candidate_index",
) -> list[dict[str, Any]] | None:
    _validate_regular_file(path, label, errors)
    try:
        values = decode_canonical_jsonl(_read_regular_file_bytes(path, label))
    except Exception as exc:
        errors.append(f"{label}: invalid canonical JSONL: {exc}")
        return None
    if not all(isinstance(value, dict) for value in values):
        errors.append(f"{label}: JSONL contains a non-object")
        return None
    invalid = False
    for index, value in enumerate(values):
        document_errors = validate_artifact_document(value)
        errors.extend(f"{label}[{index}]: {error}" for error in document_errors)
        invalid = invalid or bool(document_errors)
    indices = [value.get(index_field) for value in values]
    if not all(isinstance(index, int) and not isinstance(index, bool) for index in indices):
        errors.append(f"{label}: {index_field} values are not integers")
        invalid = True
    elif indices != sorted(indices) or len(set(indices)) != len(indices):
        errors.append(f"{label}: {index_field} order is not strictly increasing")
        invalid = True
    return None if invalid else values


def _candidate_roots() -> tuple[str, str, int]:
    shell = b"BOX-0"
    shell_binding = len(shell).to_bytes(4, "big") + shell
    records = b"".join(
        v.to_bytes(8, "big") + x.to_bytes(8, "big") for _, v, x in box0_pairs()
    )
    raw_hash = sha256_bytes(records)
    shard = hashlib.sha256(
        b"P192-WCM-CANDIDATE-SHARD-v1\0" + shell_binding
        + (0).to_bytes(8, "big") + (262148).to_bytes(8, "big") + records
    ).digest()
    shell_root = hashlib.sha256(
        b"P192-WCM-SHELL-ROOT-v1\0" + shell_binding + (1).to_bytes(8, "big")
        + (0).to_bytes(8, "big") + (262148).to_bytes(8, "big") + shard
    ).hexdigest()
    return raw_hash, shard.hex(), shell_root


def _disposition_roots(data: bytes) -> tuple[str, str, str]:
    shell = b"BOX-0"
    shell_binding = len(shell).to_bytes(4, "big") + shell
    raw_hash = sha256_bytes(data)
    shard = hashlib.sha256(
        b"P192-WCM-DISPOSITION-SHARD-v1\0" + shell_binding
        + (0).to_bytes(8, "big") + (0).to_bytes(8, "big")
        + (262148).to_bytes(8, "big") + data
    ).digest()
    shell_root = hashlib.sha256(
        b"P192-WCM-DISPOSITION-SHELL-ROOT-v1\0" + shell_binding
        + (1).to_bytes(8, "big") + (0).to_bytes(8, "big")
        + (0).to_bytes(8, "big") + (262148).to_bytes(8, "big") + shard
    ).hexdigest()
    return raw_hash, shard.hex(), shell_root


def _parse_framed_stream(
    data: bytes, stream_name: str, errors: list[str],
) -> dict[str, str]:
    domain = f"P192-WCM-BOX0-SUPERVISOR-{stream_name.upper()}-v1".encode("ascii") + b"\0"
    if not data.startswith(domain):
        errors.append(f"{stream_name}.log: domain prefix differs")
        return {}
    offset = len(domain)
    if len(data) - offset < 4:
        errors.append(f"{stream_name}.log: missing frame count")
        return {}
    count = int.from_bytes(data[offset:offset + 4], "big")
    offset += 4
    _exact(count, len(SUPERVISOR_CHILDREN), f"{stream_name}.log frame count", errors)
    hashes: dict[str, str] = {}
    for expected in SUPERVISOR_CHILDREN:
        if len(data) - offset < 4:
            errors.append(f"{stream_name}.log: truncated role length")
            return hashes
        role_length = int.from_bytes(data[offset:offset + 4], "big")
        offset += 4
        if len(data) - offset < role_length + 8:
            errors.append(f"{stream_name}.log: truncated role frame")
            return hashes
        try:
            role = data[offset:offset + role_length].decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"{stream_name}.log: role is not UTF-8")
            return hashes
        offset += role_length
        length = int.from_bytes(data[offset:offset + 8], "big")
        offset += 8
        if len(data) - offset < length:
            errors.append(f"{stream_name}.log: truncated stream bytes")
            return hashes
        payload = data[offset:offset + length]
        offset += length
        _exact(role, expected["role"], f"{stream_name}.log role order", errors)
        hashes[role] = sha256_bytes(payload)
    if offset != len(data):
        errors.append(f"{stream_name}.log: trailing bytes")
    return hashes


def _parse_failure_framed_stream(
    data: bytes, stream_name: str, errors: list[str],
) -> list[str]:
    domain = (
        f"P192-WCM-BOX0-SUPERVISOR-FAILURE-{stream_name.upper()}-v1"
        .encode("ascii") + b"\0"
    )
    if not data.startswith(domain):
        errors.append(f"failure {stream_name}.log: domain prefix differs")
        return []
    offset = len(domain)
    if len(data) - offset < 4:
        errors.append(f"failure {stream_name}.log: missing frame count")
        return []
    count = int.from_bytes(data[offset:offset + 4], "big")
    offset += 4
    if count > len(SUPERVISOR_CHILDREN):
        errors.append(f"failure {stream_name}.log: frame count exceeds four")
        return []
    roles: list[str] = []
    for child in SUPERVISOR_CHILDREN[:count]:
        if len(data) - offset < 4:
            errors.append(f"failure {stream_name}.log: truncated role length")
            return roles
        role_length = int.from_bytes(data[offset:offset + 4], "big")
        offset += 4
        if len(data) - offset < role_length + 8:
            errors.append(f"failure {stream_name}.log: truncated role frame")
            return roles
        try:
            role = data[offset:offset + role_length].decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"failure {stream_name}.log: role is not UTF-8")
            return roles
        offset += role_length
        length = int.from_bytes(data[offset:offset + 8], "big")
        offset += 8
        if len(data) - offset < length:
            errors.append(f"failure {stream_name}.log: truncated stream bytes")
            return roles
        offset += length
        _exact(
            role, child["role"],
            f"failure {stream_name}.log role order", errors,
        )
        roles.append(role)
    if offset != len(data):
        errors.append(f"failure {stream_name}.log: trailing bytes")
    return roles


def _failure_frame_count_is_admissible(failed_phase: Any, count: int) -> bool:
    bounds = FAILURE_FRAME_COUNT_BOUNDS.get(failed_phase)
    return bounds is not None and bounds[0] <= count <= bounds[1]


def _binding_values_from_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "protocol_commit": candidate["protocol_commit"],
        "producer_commit": candidate["producer_commit"],
        "producer_binary_sha256": candidate["producer_binary_sha256"],
        "factor_base_source_commit": candidate["factor_base_source_commit"],
        "factor_base_sha256": candidate["factor_base_sha256"],
        "shell_id": candidate["shell_id"],
        "candidate_shell_sha256": candidate["candidate_shell_sha256"],
        "disposition_shell_sha256": candidate["disposition"]["shell_sha256"],
        "disposition_schema_sha256": candidate["disposition_schema"]["sha256"],
        "status_counts_sha256": sha256_bytes(canonical_json_bytes(candidate["status_counts"])),
        "retained_candidates_sha256": candidate["retained_candidates"]["artifact"]["sha256"],
        "complete_relations_sha256": candidate["complete_relations"]["artifact"]["sha256"],
        "partial_relations_sha256": candidate["partial_relations"]["artifact"]["sha256"],
        "checkpoint_chain_sha256": candidate["checkpoint_chain"]["artifact"]["sha256"],
    }


def _failure_count_source(run_dir: Path, errors: list[str]) -> tuple[int, int]:
    sources: list[tuple[str, int, int]] = []
    disposition_path = run_dir / "disposition.bin"
    try:
        metadata = os.lstat(disposition_path)
        if stat.S_ISREG(metadata.st_mode) and not stat.S_ISLNK(metadata.st_mode):
            counts = parse_disposition_bytes(_read_regular_file_bytes(
                disposition_path, "failure disposition",
            ))
            sources.append(("disposition.bin", counts["invalid"], counts["unresolved"]))
    except (OSError, ValueError):
        pass
    candidate_path = run_dir / "candidate-stream.json"
    try:
        metadata = os.lstat(candidate_path)
        if stat.S_ISREG(metadata.st_mode) and not stat.S_ISLNK(metadata.st_mode):
            candidate = decode_canonical_json(_read_regular_file_bytes(
                candidate_path, "failure candidate stream",
            ))
            if isinstance(candidate, dict) and not validate_artifact_document(candidate):
                counts = candidate["status_counts"]
                sources.append(("candidate-stream.json", counts["invalid"], counts["unresolved"]))
    except (KeyError, OSError, TypeError, ValueError):
        pass
    if not sources:
        return 0, 0
    expected = sources[0][1:]
    for name, invalid, unresolved in sources[1:]:
        _exact((invalid, unresolved), expected, f"failure terminal counts from {name}", errors)
    return expected


def _terminal_failure_expectation(
    raw: dict[str, Any], invalid: int, unresolved: int,
    incomplete_artifact: bool = False,
) -> tuple[str, str, str]:
    if invalid > 0:
        return "FAIL", "canonical_producer", "invalid_disposition"
    if unresolved > 0:
        return "INCOMPLETE", "canonical_producer", "unresolved_disposition"
    if incomplete_artifact:
        return "INCOMPLETE", raw.get("failed_phase"), "incomplete_child_artifact"
    reason = raw.get("failure_reason")
    if reason == "incomplete_child_artifact":
        return "INCOMPLETE", raw.get("failed_phase"), reason
    return "FAIL", raw.get("failed_phase"), reason


def _schema_valid_completed_artifact(
    run_dir: Path, relative: str, decision: dict[str, Any],
) -> bool:
    path = run_dir / relative
    try:
        metadata = os.lstat(path)
        if not stat.S_ISREG(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode):
            return False
        data = _read_regular_file_bytes(path, f"completed artifact {relative}")
        if relative == "disposition.bin":
            counts, statuses, _ = parse_disposition_details(data)
            if len(statuses) != 262148 or sum(counts.values()) != 262148:
                return False
            return True
        if relative == "command.txt":
            return decode_canonical_json(data) == decision["supervisor_argv"]
        if relative in {"stdout.log", "stderr.log"}:
            stream_errors: list[str] = []
            _parse_framed_stream(data, relative.removesuffix(".log"), stream_errors)
            return not stream_errors
        if relative.endswith(".jsonl"):
            rows = decode_canonical_jsonl(data)
            expected_schema = EXPECTED_JSONL_SCHEMAS.get(relative)
            if expected_schema is None:
                return False
            if relative == "checkpoint-chain.jsonl" and len(rows) != 1:
                return False
            if not all(
                isinstance(row, dict)
                and row.get("schema") == expected_schema
                and not validate_artifact_document(row)
                for row in rows
            ):
                return False
            indices = [row.get("candidate_index") for row in rows]
            return indices == sorted(indices) and len(set(indices)) == len(indices)
        if relative.endswith(".json"):
            document = decode_canonical_json(data)
            expected_schema = EXPECTED_JSON_SCHEMAS.get(relative)
            return (
                expected_schema is not None
                and isinstance(document, dict)
                and document.get("schema") == expected_schema
                and not validate_artifact_document(document)
            )
        if relative == "manifest.yaml":
            document = decode_canonical_json(data)
            return (
                isinstance(document, dict)
                and set(document) == {"run"}
                and not validate_artifact_document(document)
            )
    except (OSError, TypeError, ValueError):
        return False
    return False


def _validate_terminal_output_custody(
    run_dir: Path, control_dir: Path, decision: dict[str, Any], errors: list[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Validate exact retained RUN/CONTROL file custody and return identities."""
    try:
        control_entries = _bounded_sorted_scandir(
            control_dir, PROTOCOL_TOPOLOGY_ENTRY_CAP,
            "CONTROL_DIR inventory",
        )
    except (OSError, ValueError) as exc:
        errors.append(f"CONTROL_DIR inventory unavailable: {exc}")
        return [], []
    control_names = {entry.name for entry in control_entries}
    _exact(control_names, set(PRODUCER_PATHS), "CONTROL_DIR exact path set", errors)
    run_identities: list[dict[str, Any]] = []
    control_identities: list[dict[str, Any]] = []
    all_inode_keys: set[tuple[str, str]] = set()
    input_inode_keys = {
        (str(device), str(inode))
        for device, inode in _immutable_input_inodes(decision)
    }

    for relative in PRODUCER_PATHS:
        run_path = run_dir / relative
        control_path = control_dir / relative
        for label, path, destination in (
            ("RUN_DIR", run_path, run_identities),
            ("CONTROL_DIR", control_path, control_identities),
        ):
            _validate_regular_file(path, f"{label} producer artifact {relative}", errors)
            try:
                identity = _file_identity(path, relative)
            except (OSError, ValueError) as exc:
                errors.append(f"{label} producer artifact {relative}: {exc}")
                try:
                    failed_metadata = os.lstat(path)
                    failed_inode = (
                        str(failed_metadata.st_dev), str(failed_metadata.st_ino),
                    )
                    if failed_inode in input_inode_keys:
                        errors.append(
                            f"{label} producer artifact {relative} aliases an immutable input"
                        )
                except OSError:
                    pass
                continue
            _require(
                identity["link_count"] == 1,
                f"{label} producer artifact {relative} link count is not one", errors,
            )
            inode_key = (identity["device"], identity["inode"])
            _require(
                inode_key not in all_inode_keys,
                f"{label} producer artifact {relative} aliases another output", errors,
            )
            _require(
                inode_key not in input_inode_keys,
                f"{label} producer artifact {relative} aliases an immutable input", errors,
            )
            all_inode_keys.add(inode_key)
            destination.append(identity)
        try:
            _exact(
                _read_regular_file_bytes(
                    control_path, f"retained CONTROL_DIR {relative}",
                ),
                _read_regular_file_bytes(
                    run_path, f"retained RUN_DIR {relative}",
                ),
                f"retained CONTROL_DIR byte equality {relative}", errors,
            )
        except (OSError, ValueError) as exc:
            errors.append(f"retained CONTROL_DIR comparison {relative}: {exc}")
    return run_identities, control_identities


def _validate_canonical_producer_phase(
    run_dir: Path, decision: dict[str, Any], errors: list[str],
) -> dict[str, Any] | None:
    """Replay the complete canonical-producer PASS gate for any caller."""
    disposition_schema = _load_json_artifact(
        run_dir / "disposition-schema.json", "disposition-schema.json", errors,
    )
    candidate = _load_json_artifact(
        run_dir / "candidate-stream.json", "candidate-stream.json", errors,
    )
    verification = _load_json_artifact(
        run_dir / "verification.json", "verification.json", errors,
    )
    retained = _load_jsonl_artifact(
        run_dir / "retained-candidates.jsonl", "retained-candidates.jsonl", errors,
    )
    complete = _load_jsonl_artifact(
        run_dir / "complete-relations.jsonl", "complete-relations.jsonl", errors,
    )
    partial = _load_jsonl_artifact(
        run_dir / "partial-relations.jsonl", "partial-relations.jsonl", errors,
    )
    checkpoints = _load_jsonl_artifact(
        run_dir / "checkpoint-chain.jsonl", "checkpoint-chain.jsonl", errors,
        index_field="shard_index",
    )
    if any(item is None for item in (
        disposition_schema, candidate, verification, retained, complete,
        partial, checkpoints,
    )):
        return None
    assert disposition_schema is not None and candidate is not None
    assert verification is not None and retained is not None
    assert complete is not None and partial is not None and checkpoints is not None
    try:
        disposition_bytes = _read_regular_file_bytes(
            run_dir / "disposition.bin", "canonical-producer disposition.bin",
        )
        status_counts, statuses, disposition_hashes = parse_disposition_details(
            disposition_bytes
        )
    except Exception as exc:
        errors.append(f"canonical-producer disposition.bin: {exc}")
        return None
    _exact(candidate.get("status_counts"), status_counts, "canonical-producer candidate/disposition status counts", errors)
    _exact(status_counts.get("invalid"), 0, "canonical-producer invalid count", errors)
    _exact(status_counts.get("unresolved"), 0, "canonical-producer unresolved count", errors)
    for index, v, x in box0_pairs():
        primitive = math.gcd(abs((x - TRACE_T * v) // 2), v) == 1
        if (statuses[index] == 0) == primitive:
            errors.append(f"canonical-producer disposition primitivity mismatch at candidate {index}")
            break
    candidate_raw, candidate_shard, candidate_shell = _candidate_roots()
    disposition_raw, disposition_shard, disposition_shell = _disposition_roots(
        disposition_bytes
    )
    shards = candidate.get("candidate_shards", [])
    if len(shards) != 1 or not isinstance(shards[0], dict):
        errors.append("canonical-producer candidate shard inventory is malformed")
        return None
    shard = shards[0]
    _exact(shard.get("records_sha256"), candidate_raw, "canonical-producer candidate raw shard hash", errors)
    _exact(shard.get("candidate_shard_sha256"), candidate_shard, "canonical-producer candidate domain shard hash", errors)
    _exact(candidate.get("candidate_shell_sha256"), candidate_shell, "canonical-producer candidate shell root", errors)
    disposition_entry = candidate.get("disposition", {})
    disposition_shards = disposition_entry.get("shards", []) if isinstance(disposition_entry, dict) else []
    if len(disposition_shards) != 1 or not isinstance(disposition_shards[0], dict):
        errors.append("canonical-producer disposition shard inventory is malformed")
        return None
    _exact(disposition_shards[0].get("records_sha256"), disposition_raw, "canonical-producer disposition raw shard hash", errors)
    _exact(disposition_shards[0].get("disposition_shard_sha256"), disposition_shard, "canonical-producer disposition domain shard hash", errors)
    _exact(disposition_entry.get("shell_sha256"), disposition_shell, "canonical-producer disposition shell root", errors)
    _check_artifact_record(
        candidate.get("disposition_schema", {}),
        run_dir / "disposition-schema.json", "disposition-schema.json",
        "canonical-producer candidate disposition schema", errors,
    )
    _check_artifact_record(
        disposition_entry.get("artifact", {}), run_dir / "disposition.bin",
        "disposition.bin", "canonical-producer disposition artifact", errors,
    )
    for key, relative in (
        ("retained_candidates", "retained-candidates.jsonl"),
        ("complete_relations", "complete-relations.jsonl"),
        ("partial_relations", "partial-relations.jsonl"),
        ("checkpoint_chain", "checkpoint-chain.jsonl"),
    ):
        value = candidate.get(key, {})
        record = value.get("artifact", {}) if isinstance(value, dict) else {}
        _check_artifact_record(
            record, run_dir / relative, relative,
            f"canonical-producer candidate {key}", errors,
        )
    expected_retained = [index for index, status in enumerate(statuses) if status in (1, 2, 3)]
    expected_complete = [index for index, status in enumerate(statuses) if status == 1]
    expected_partial = [index for index, status in enumerate(statuses) if status in (2, 3)]
    _exact([row["candidate_index"] for row in retained], expected_retained, "canonical-producer retained membership", errors)
    _exact([row["candidate_index"] for row in complete], expected_complete, "canonical-producer complete membership", errors)
    _exact([row["candidate_index"] for row in partial], expected_partial, "canonical-producer partial membership", errors)
    retained_by_index = {row["candidate_index"]: row for row in retained}
    for row in retained:
        expected_hashes = disposition_hashes.get(row["candidate_index"])
        _exact(
            (row.get("candidate_certificate_sha256"), row.get("factorization_certificate_sha256")),
            expected_hashes,
            f"canonical-producer retained/disposition hashes {row['candidate_index']}", errors,
        )
        _exact(row.get("status"), statuses[row["candidate_index"]], f"canonical-producer retained status {row['candidate_index']}", errors)
    for label, rows in (("complete", complete), ("partial", partial)):
        for row in rows:
            source = retained_by_index.get(row["candidate_index"], {})
            _exact(row.get("candidate_id"), source.get("candidate_id"), f"canonical-producer {label}/retained candidate id", errors)
            _exact(row.get("candidate_certificate_sha256"), source.get("candidate_certificate_sha256"), f"canonical-producer {label}/retained candidate hash", errors)
            _exact(row.get("factorization_certificate_sha256"), source.get("factorization_certificate_sha256"), f"canonical-producer {label}/retained factorization hash", errors)
    _exact(len(checkpoints), 1, "canonical-producer checkpoint line count", errors)
    if len(checkpoints) == 1:
        checkpoint = checkpoints[0]
        _exact(checkpoint.get("protocol_commit"), decision["protocol_commit"], "canonical-producer checkpoint protocol commit", errors)
        _exact(checkpoint.get("producer_commit"), decision["producer_commit"], "canonical-producer checkpoint producer commit", errors)
        _exact(checkpoint.get("producer_binary_sha256"), decision["producer_binary_sha256"], "canonical-producer checkpoint producer binary", errors)
        _exact(checkpoint.get("factor_base_sha256"), candidate.get("factor_base_sha256"), "canonical-producer checkpoint factor base", errors)
        _exact(checkpoint.get("candidate_shard_sha256"), candidate_shard, "canonical-producer checkpoint candidate shard", errors)
        _exact(checkpoint.get("disposition_shard_sha256"), disposition_shard, "canonical-producer checkpoint disposition shard", errors)
        expected_counters = {
            "seen": "262148", "primitive": "168990", "duplicate": "93158",
            "complete": str(status_counts["complete"]),
            "one_lp": str(status_counts["one_large_prime"]),
            "two_lp": str(status_counts["two_large_prime"]),
            "rejected": str(status_counts["rejected"]),
            "invalid": str(status_counts["invalid"]),
            "unresolved": str(status_counts["unresolved"]),
        }
        _exact(checkpoint.get("phase_counters"), expected_counters, "canonical-producer checkpoint/status counters", errors)
        committed_outputs = checkpoint.get("committed_outputs", {})
        for relative in APPEND_PATHS:
            try:
                data = _read_regular_file_bytes(
                    run_dir / relative,
                    f"canonical-producer checkpoint input {relative}",
                )
            except (OSError, ValueError) as exc:
                errors.append(f"canonical-producer checkpoint input {relative}: {exc}")
                continue
            _exact(
                committed_outputs.get(relative),
                {"byte_length": str(len(data)), "prefix_sha256": sha256_bytes(data)},
                f"canonical-producer checkpoint prefix {relative}", errors,
            )
    predecessor = Path(decision["paths"]["predecessor_dir"])
    predecessor_records = candidate.get("predecessor", {})
    _exact(predecessor_records.get("run_id"), decision["predecessor_run_id"], "canonical-producer predecessor run id", errors)
    for field, relative in (
        ("factor_base", "factor-base.json"),
        ("factor_base_sidecar", "factor-base.sha256"),
        ("producer_verification", "verification.json"),
        ("independent_verification", "independent-verification.json"),
        ("independent_agreement", "independent-agreement.json"),
        ("supervisor_receipt", "independent-verifier-receipt.json"),
    ):
        _check_artifact_record(
            predecessor_records.get(field, {}), predecessor / relative, relative,
            f"canonical-producer predecessor {field}", errors,
        )
    try:
        factor_base = decode_canonical_json(_read_regular_file_bytes(
            predecessor / "factor-base.json",
            "canonical-producer predecessor factor base",
        ))
        _exact(factor_base.get("source_commit"), decision["factor_base_source_commit"], "canonical-producer predecessor source commit", errors)
        expected_sidecar = f'{sha256_path(predecessor / "factor-base.json")}  factor-base.json\n'.encode("ascii")
        _exact(
            _read_regular_file_bytes(
                predecessor / "factor-base.sha256",
                "canonical-producer factor-base sidecar",
            ),
            expected_sidecar, "canonical-producer factor-base sidecar", errors,
        )
        for name in (
            "verification.json", "independent-verification.json",
            "independent-agreement.json", "independent-verifier-receipt.json",
        ):
            predecessor_doc = decode_canonical_json(_read_regular_file_bytes(
                predecessor / name, f"canonical-producer predecessor {name}",
            ))
            _exact(predecessor_doc.get("overall_status"), "PASS", f"canonical-producer predecessor {name} status", errors)
            _exact(predecessor_doc.get("protocol_commit"), decision["protocol_commit"], f"canonical-producer predecessor {name} protocol commit", errors)
            _exact(predecessor_doc.get("source_commit"), decision["factor_base_source_commit"], f"canonical-producer predecessor {name} source commit", errors)
    except Exception as exc:
        errors.append(f"canonical-producer predecessor replay failed: {exc}")
    for field in (
        "protocol_commit", "producer_commit", "producer_binary_sha256",
        "factor_base_source_commit", "factor_base_sha256", "shell_id",
    ):
        _exact(candidate.get(field), disposition_schema.get(field), f"canonical-producer candidate/disposition-schema {field}", errors)
    for field in ("protocol_commit", "producer_commit", "factor_base_source_commit"):
        _exact(candidate.get(field), decision.get(field), f"canonical-producer candidate/decision {field}", errors)
    _exact(candidate.get("producer_binary_sha256"), decision["producer_binary_sha256"], "canonical-producer candidate binary", errors)
    try:
        _exact(candidate.get("factor_base_sha256"), sha256_path(predecessor / "factor-base.json"), "canonical-producer candidate factor-base hash", errors)
    except (OSError, ValueError) as exc:
        errors.append(f"canonical-producer factor-base hash unavailable: {exc}")
    try:
        bindings = _binding_values_from_candidate(candidate)
    except (KeyError, TypeError) as exc:
        errors.append(f"canonical-producer bindings are malformed: {exc}")
        return None
    _exact(verification.get("bindings"), bindings, "canonical-producer verification bindings", errors)
    _exact(verification.get("overall_status"), "PASS", "canonical-producer verification status", errors)
    _require(
        all(item.get("status") == "PASS" for item in verification.get("checks", [])),
        "canonical-producer verification contains a non-PASS check", errors,
    )
    for item in verification.get("artifacts", []):
        if isinstance(item, dict) and isinstance(item.get("path"), str):
            _check_artifact_record(
                item, run_dir / item["path"], item["path"],
                "canonical-producer verification artifact", errors,
            )
    return bindings


def _validate_failure_prior_phase_passes(
    run_dir: Path,
    control_dir: Path,
    decision: dict[str, Any],
    custody: dict[str, Any],
    failed_phase: Any,
    completed_paths: set[str],
    errors: list[str],
) -> None:
    """Require full semantic PASS evidence before admitting a later failure."""
    phase_names = list(FAILURE_PHASE_ARTIFACTS)
    if failed_phase not in phase_names:
        return
    failed_index = phase_names.index(failed_phase)

    def load(relative: str) -> dict[str, Any] | None:
        local_errors: list[str] = []
        document = _load_json_artifact(run_dir / relative, relative, local_errors)
        errors.extend(
            f"failure prior-phase semantic gate: {item}" for item in local_errors
        )
        return document

    candidate: dict[str, Any] | None = None
    bindings: dict[str, Any] | None = None
    if failed_index > 0:
        shared_bindings = _validate_canonical_producer_phase(
            run_dir, decision, errors,
        )
        candidate = load("candidate-stream.json")
        verification = load("verification.json")
        disposition_schema = load("disposition-schema.json")
        if candidate is None or verification is None or disposition_schema is None:
            return
        try:
            bindings = _binding_values_from_candidate(candidate)
        except (KeyError, TypeError) as exc:
            errors.append(f"failure prior canonical-producer bindings are malformed: {exc}")
            return
        _exact(
            bindings, shared_bindings,
            "failure prior canonical-producer shared PASS replay", errors,
        )
        _exact(candidate.get("complete"), True, "failure prior canonical-producer completeness", errors)
        _exact(candidate.get("protocol_commit"), decision["protocol_commit"], "failure prior candidate protocol commit", errors)
        _exact(candidate.get("producer_commit"), decision["producer_commit"], "failure prior candidate producer commit", errors)
        _exact(candidate.get("factor_base_source_commit"), decision["factor_base_source_commit"], "failure prior candidate factor-base commit", errors)
        _exact(candidate.get("producer_binary_sha256"), decision["producer_binary_sha256"], "failure prior candidate producer binary", errors)
        counts = candidate.get("status_counts", {})
        _exact(counts.get("invalid"), 0, "failure prior canonical-producer invalid count", errors)
        _exact(counts.get("unresolved"), 0, "failure prior canonical-producer unresolved count", errors)
        _exact(verification.get("overall_status"), "PASS", "failure prior canonical-producer verification status", errors)
        _require(
            all(item.get("status") == "PASS" for item in verification.get("checks", [])),
            "failure prior canonical-producer contains a non-PASS check", errors,
        )
        _exact(verification.get("bindings"), bindings, "failure prior producer verification bindings", errors)
        for item in verification.get("artifacts", []):
            path_value = item.get("path") if isinstance(item, dict) else None
            if isinstance(path_value, str):
                _check_artifact_record(
                    item, run_dir / path_value, path_value,
                    "failure prior producer verification artifact", errors,
                )
        for key, relative in (
            ("disposition_schema", "disposition-schema.json"),
            ("retained_candidates", "retained-candidates.jsonl"),
            ("complete_relations", "complete-relations.jsonl"),
            ("partial_relations", "partial-relations.jsonl"),
            ("checkpoint_chain", "checkpoint-chain.jsonl"),
        ):
            value = candidate.get(key, {})
            record = value if key == "disposition_schema" else value.get("artifact", {})
            _check_artifact_record(
                record, run_dir / relative, relative,
                f"failure prior candidate {key}", errors,
            )
        disposition_record = candidate.get("disposition", {}).get("artifact", {})
        _check_artifact_record(
            disposition_record, run_dir / "disposition.bin", "disposition.bin",
            "failure prior candidate disposition", errors,
        )
        try:
            disposition_counts, statuses, _ = parse_disposition_details(
                _read_regular_file_bytes(
                    run_dir / "disposition.bin", "failure prior disposition",
                )
            )
            _exact(disposition_counts, counts, "failure prior disposition/candidate counts", errors)
            _exact(len(statuses), 262148, "failure prior disposition record count", errors)
        except (OSError, ValueError) as exc:
            errors.append(f"failure prior disposition replay failed: {exc}")
        for relative in (
            "retained-candidates.jsonl", "complete-relations.jsonl",
            "partial-relations.jsonl", "checkpoint-chain.jsonl",
        ):
            local_errors: list[str] = []
            _load_jsonl_artifact(
                run_dir / relative, relative, local_errors,
                index_field="shard_index" if relative == "checkpoint-chain.jsonl" else "candidate_index",
            )
            errors.extend(
                f"failure prior canonical-producer semantic gate: {item}"
                for item in local_errors
            )
        for field in (
            "protocol_commit", "producer_commit", "producer_binary_sha256",
            "factor_base_source_commit", "factor_base_sha256", "shell_id",
        ):
            _exact(
                candidate.get(field), disposition_schema.get(field),
                f"failure prior candidate/disposition-schema {field}", errors,
            )

    if failed_index > 1:
        restart = load("checkpoint-resume-control.json")
        if restart is None or candidate is None:
            return
        _exact(restart.get("overall_status"), "PASS", "failure prior restart-control status", errors)
        _exact(
            (
                restart.get("roots_equal"), restart.get("counters_equal"),
                restart.get("prefixes_equal"),
            ),
            (True, True, True), "failure prior restart-control equality gates", errors,
        )
        for field in (
            "protocol_commit", "producer_commit", "producer_binary_sha256",
            "factor_base_source_commit",
        ):
            _exact(restart.get(field), decision[field], f"failure prior restart {field}", errors)
        _exact(restart.get("factor_base_sha256"), candidate.get("factor_base_sha256"), "failure prior restart factor base", errors)
        _exact(restart.get("shell_id"), candidate.get("shell_id"), "failure prior restart shell", errors)
        _exact(restart.get("fault_argv"), decision["producer_fault_argv"], "failure prior restart fault argv", errors)
        _exact(restart.get("resume_argv"), decision["producer_resume_argv"], "failure prior restart resume argv", errors)
        _exact(restart.get("control_dir"), str(control_dir), "failure prior restart CONTROL_DIR", errors)
        _validate_terminal_output_custody(run_dir, control_dir, decision, errors)
        expected_fault_state = [
            _artifact_record(run_dir / path, path)
            for path in CONTROL_CHECKPOINT_PATHS
        ]
        suffix = bytes.fromhex(
            "503139322d57434d2d554e434f4d4d49545445442d5355464649582d763100"
        )
        expected_injected_state = []
        for relative in CONTROL_CHECKPOINT_PATHS:
            injected = _read_regular_file_bytes(
                run_dir / relative, f"failure restart injected source {relative}",
            )
            if relative in APPEND_PATHS:
                injected += suffix
            expected_injected_state.append({
                "path": relative, "byte_length": len(injected),
                "sha256": sha256_bytes(injected),
            })
        expected_resumed = [
            _artifact_record(control_dir / path, path) for path in PRODUCER_PATHS
        ]
        _exact(restart.get("fault_state_artifacts"), expected_fault_state, "failure prior restart fault-state artifacts", errors)
        _exact(restart.get("injected_state_artifacts"), expected_injected_state, "failure prior restart injected-state artifacts", errors)
        _exact(restart.get("resumed_control_artifacts"), expected_resumed, "failure prior restart resumed-control artifacts", errors)
        _exact(restart.get("control_directory_terminal"), _directory_identity(control_dir), "failure prior restart terminal CONTROL_DIR identity", errors)
        _exact(restart.get("control_retained_after_terminal_validation"), True, "failure prior restart control retention", errors)
        _exact(
            restart.get("control_cleanup_authority"),
            "out_of_band_after_terminal_validation_and_archival_only",
            "failure prior restart cleanup authority", errors,
        )
        for comparison in restart.get("comparisons", []):
            if not isinstance(comparison, dict) or not isinstance(comparison.get("field"), str):
                continue
            relative = comparison["field"]
            try:
                fresh_hash = sha256_path(run_dir / relative)
                resumed_hash = sha256_path(control_dir / relative)
            except (OSError, ValueError) as exc:
                errors.append(f"failure prior restart comparison {relative}: {exc}")
                continue
            _exact(
                (
                    comparison.get("fresh_sha256"),
                    comparison.get("resumed_sha256"), comparison.get("equal"),
                ),
                (fresh_hash, resumed_hash, fresh_hash == resumed_hash),
                f"failure prior restart comparison {relative}", errors,
            )

    if failed_index > 2:
        independent = load("independent-verification.json")
        if independent is None or bindings is None:
            return
        _exact(independent.get("overall_status"), "PASS", "failure prior independent-verifier status", errors)
        _require(
            all(item.get("status") == "PASS" for item in independent.get("checks", [])),
            "failure prior independent-verifier contains a non-PASS check", errors,
        )
        _exact(independent.get("bindings"), bindings, "failure prior independent-verifier bindings", errors)
        _exact(independent.get("verifier_commit"), decision["verifier_commit"], "failure prior independent verifier commit", errors)
        _exact(independent.get("verifier_binary_sha256"), decision["verifier_binary_sha256"], "failure prior independent verifier binary", errors)
        for item in independent.get("source_artifacts", []):
            path_value = item.get("path") if isinstance(item, dict) else None
            if isinstance(path_value, str):
                _check_artifact_record(
                    item, run_dir / path_value, path_value,
                    "failure prior independent source artifact", errors,
                )

    if failed_index > 3:
        agreement = load("independent-agreement.json")
        if agreement is None or bindings is None:
            return
        _exact(agreement.get("overall_status"), "PASS", "failure prior agreement status", errors)
        _exact(
            agreement.get("producer_verification_sha256"),
            sha256_path(run_dir / "verification.json"),
            "failure prior agreement producer-verification hash", errors,
        )
        _exact(
            agreement.get("independent_verification_sha256"),
            sha256_path(run_dir / "independent-verification.json"),
            "failure prior agreement independent-verification hash", errors,
        )
        agreement_map = {
            item.get("field"): item for item in agreement.get("comparisons", [])
            if isinstance(item, dict)
        }
        for field, expected in bindings.items():
            item = agreement_map.get(field, {})
            _exact(
                (item.get("producer"), item.get("verifier"), item.get("equal")),
                (str(expected), str(expected), True),
                f"failure prior agreement binding {field}", errors,
            )

    # Audit and receipt are within final custody.  If the supervisor records
    # either as completed before a later custody failure, it may not smuggle a
    # semantic FAIL through the schema-valid completion test.
    if failed_phase == "final_custody" and "independent-verifier-receipt.json" in completed_paths:
        receipt = load("independent-verifier-receipt.json")
        if receipt is not None:
            _exact(receipt.get("overall_status"), "PASS", "failure completed receipt status", errors)
            _exact(receipt.get("decision_id"), decision["decision_id"], "failure completed receipt decision", errors)
            _exact(receipt.get("decision_custody"), custody, "failure completed receipt custody", errors)
            for field in (
                "protocol_commit", "factor_base_source_commit", "producer_commit",
                "verifier_commit", "supervisor_commit", "supervisor_binary_sha256",
            ):
                _exact(receipt.get(field), decision[field], f"failure completed receipt {field}", errors)
            if "dependency-audit.json" in completed_paths:
                _exact(
                    receipt.get("dependency_audit_sha256"),
                    sha256_path(run_dir / "dependency-audit.json"),
                    "failure completed receipt dependency-audit hash", errors,
                )


def _validate_distinct_single_link_files(
    paths: list[tuple[str, Path]], label: str, errors: list[str],
    forbidden_inodes: set[tuple[int, int]] | None = None,
) -> None:
    observed: dict[tuple[int, int], str] = {}
    for relative, path in paths:
        try:
            metadata = os.lstat(path)
        except OSError as exc:
            errors.append(f"{label} {relative}: cannot stat: {exc}")
            continue
        if not stat.S_ISREG(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode):
            errors.append(f"{label} {relative}: not a regular nofollow file")
            continue
        _require(metadata.st_nlink == 1, f"{label} {relative}: link count is not one", errors)
        key = (metadata.st_dev, metadata.st_ino)
        if forbidden_inodes is not None and key in forbidden_inodes:
            errors.append(f"{label} {relative}: aliases an immutable input")
        if key in observed:
            errors.append(f"{label} {relative}: aliases {observed[key]}")
        else:
            observed[key] = relative


def _immutable_input_inodes(decision: dict[str, Any]) -> set[tuple[int, int]]:
    paths: list[Path] = [
        Path(decision["paths"]["decision_json"]),
        *(Path(decision["paths"][f"{role}_bin"]) for role in ("producer", "verifier", "supervisor")),
        *(Path(decision["paths"]["predecessor_dir"]) / name for name in PREDECESSOR_PATHS),
        *PROTECTED_PROTOCOL_PATHS.values(),
    ]
    entry_count = 0
    aggregate_path_bytes = 0
    for role in ("producer", "verifier", "supervisor"):
        repository = Path(decision["paths"][f"{role}_repository_path"])
        package = Path(decision["paths"][f"{role}_package_path"])
        pending: list[tuple[Path, int]] = [(package, 0)]
        while pending:
            directory, depth = pending.pop()
            if depth > PROTOCOL_TOPOLOGY_DEPTH_CAP:
                raise ValueError("immutable-input inventory exceeds directory depth cap")
            entries = _bounded_sorted_scandir(
                directory, PROTOCOL_TOPOLOGY_ENTRY_CAP - entry_count,
                "immutable-input inventory",
            )
            for entry in entries:
                entry_count += 1
                path = Path(entry.path)
                relative = path.relative_to(package).as_posix()
                encoded = relative.encode("utf-8")
                if len(encoded) > PROTOCOL_TOPOLOGY_PATH_BYTES_CAP:
                    raise ValueError(f"immutable-input path exceeds byte cap: {relative}")
                aggregate_path_bytes += len(encoded)
                if aggregate_path_bytes > FILESYSTEM_WALK_AGGREGATE_PATH_BYTES_CAP:
                    raise ValueError("immutable-input inventory exceeds aggregate path-byte cap")
                metadata = entry.stat(follow_symlinks=False)
                if directory == package and entry.name == "target":
                    continue
                if stat.S_ISDIR(metadata.st_mode) and not stat.S_ISLNK(metadata.st_mode):
                    pending.append((path, depth + 1))
                elif stat.S_ISREG(metadata.st_mode):
                    paths.append(path)
        for relative in ("Cargo.lock", *SOURCE_BUILD_OPTIONAL_ROOT_PATHS):
            candidate = repository / relative
            if os.path.lexists(candidate):
                paths.append(candidate)
    result: set[tuple[int, int]] = set()
    for path in paths:
        try:
            metadata = os.lstat(path)
        except OSError:
            continue
        if stat.S_ISREG(metadata.st_mode):
            result.add((metadata.st_dev, metadata.st_ino))
    return result


def _directory_custody_entries(path: Path) -> list[dict[str, Any]]:
    if not os.path.lexists(path):
        return []
    result: list[dict[str, Any]] = []
    entries = _bounded_sorted_scandir(
        path, PROTOCOL_TOPOLOGY_ENTRY_CAP, "failure custody inventory",
    )
    aggregate_path_bytes = 0
    for entry in entries:
        encoded_name = entry.name.encode("utf-8")
        if len(encoded_name) > PROTOCOL_TOPOLOGY_PATH_BYTES_CAP:
            raise ValueError(f"failure custody path exceeds byte cap: {entry.name}")
        aggregate_path_bytes += len(encoded_name)
        if aggregate_path_bytes > FILESYSTEM_WALK_AGGREGATE_PATH_BYTES_CAP:
            raise ValueError("failure custody inventory exceeds aggregate path-byte cap")
        metadata = entry.stat(follow_symlinks=False)
        if stat.S_ISREG(metadata.st_mode):
            file_type = "regular"
        elif stat.S_ISDIR(metadata.st_mode):
            file_type = "directory"
        elif stat.S_ISLNK(metadata.st_mode):
            file_type = "symlink"
        else:
            file_type = "other"
        record: dict[str, Any] = {
            "path": entry.name,
            "file_type": file_type,
            "device": str(metadata.st_dev),
            "inode": str(metadata.st_ino),
            "link_count": metadata.st_nlink,
        }
        if file_type == "regular":
            try:
                raw = _read_regular_file_bytes(
                    Path(entry.path), f"failure custody entry {entry.name}",
                )
            except (OSError, ValueError):
                record["file_type"] = "other"
            else:
                record["byte_length"] = len(raw)
                record["sha256"] = sha256_bytes(raw)
        result.append(record)
    return result


def _validate_post_run_impl(
    run_dir: Path, decision: dict[str, Any], custody: dict[str, Any],
) -> list[str]:
    """Validate a complete Role-2 directory against raw bytes and its decision."""
    errors: list[str] = []
    try:
        entries = _bounded_sorted_scandir(
            run_dir, PROTOCOL_TOPOLOGY_ENTRY_CAP, "post-run inventory",
        )
    except (OSError, ValueError) as exc:
        return [f"post-run inventory unavailable: {exc}"]
    for entry in entries:
        if entry.is_symlink():
            errors.append(f"post-run path is a symlink: {entry.name}")
    control_dir = Path(decision["paths"]["control_dir"])
    size_errors = _evidence_size_errors(run_dir, control_dir)
    errors.extend(size_errors)
    if size_errors:
        return errors
    raw_path = run_dir / "raw-result.json"
    raw_result = _load_json_artifact(raw_path, "raw-result.json", errors)
    if raw_result is None:
        return errors
    if raw_result.get("schema") == "p192-wcm-role2-box0-failure-v1":
        _require(not (run_dir / "manifest.yaml").exists(), "failure directory must not contain manifest.yaml", errors)
        _require(not (run_dir / TERMINAL_CUSTODY_PATH).exists(), "failure directory must not contain a PASS terminal seal", errors)
        failed_phase = raw_result.get("failed_phase")
        failure_stream_roles: dict[str, list[str]] = {}
        for stream_name in ("stdout", "stderr"):
            stream_path = run_dir / f"{stream_name}.log"
            try:
                stream_metadata = os.lstat(stream_path)
                if (
                    not stat.S_ISREG(stream_metadata.st_mode)
                    or stat.S_ISLNK(stream_metadata.st_mode)
                ):
                    raise ValueError("not a nofollow regular file")
                stream_bytes = _read_regular_file_bytes(
                    stream_path, f"failure {stream_name}.log",
                )
            except (OSError, ValueError) as exc:
                errors.append(
                    f"failure {stream_name}.log unavailable or nonregular: {exc}"
                )
                failure_stream_roles[stream_name] = []
            else:
                failure_stream_roles[stream_name] = _parse_failure_framed_stream(
                    stream_bytes, stream_name, errors,
                )
        _exact(
            failure_stream_roles["stdout"], failure_stream_roles["stderr"],
            "failure stdout/stderr captured role prefix", errors,
        )
        frame_count_bounds = FAILURE_FRAME_COUNT_BOUNDS.get(failed_phase)
        if frame_count_bounds is not None:
            minimum, maximum = frame_count_bounds
            for stream_name, roles in failure_stream_roles.items():
                _require(
                    _failure_frame_count_is_admissible(failed_phase, len(roles)),
                    f"failure {stream_name}.log frame count outside "
                    f"{failed_phase} bounds {minimum}..{maximum}",
                    errors,
                )
        _exact(raw_result.get("decision_custody"), custody, "failure decision custody", errors)
        for field in (
            "protocol_commit", "factor_base_source_commit", "producer_commit",
            "verifier_commit", "supervisor_commit",
        ):
            _exact(raw_result.get(field), decision.get(field), f"failure {field}", errors)
        _exact(raw_result.get("run_dir"), str(run_dir), "failure run_dir", errors)
        _exact(raw_result.get("control_dir"), str(control_dir), "failure control_dir", errors)
        control_exists = os.path.lexists(control_dir)
        _exact(raw_result.get("control_state"), "retained", "failure control state", errors)
        _exact(raw_result.get("control_retained"), True, "failure control retained", errors)
        _exact(raw_result.get("control_created_before_failure"), True, "failure control created/retained", errors)
        _exact(control_exists, True, "terminal failure CONTROL_DIR retention", errors)
        control_is_nofollow_directory = False
        if control_exists:
            try:
                control_metadata = os.lstat(control_dir)
                control_is_nofollow_directory = stat.S_ISDIR(control_metadata.st_mode)
            except OSError as exc:
                errors.append(f"failure retained CONTROL_DIR cannot be lstatted: {exc}")
            _require(control_is_nofollow_directory, "failure retained CONTROL_DIR is not a nofollow directory", errors)
        run_custody = [
            record for record in _directory_custody_entries(run_dir)
            if record["path"] != "raw-result.json"
        ]
        control_custody = (
            _directory_custody_entries(control_dir)
            if control_is_nofollow_directory else []
        )
        if failed_phase == "canonical_producer":
            _exact(
                control_custody, [],
                "canonical-producer failure empty CONTROL_DIR", errors,
            )
        custody_inode_owner: dict[tuple[str, str], str] = {}
        immutable_failure_inodes = {
            (str(device), str(inode))
            for device, inode in _immutable_input_inodes(decision)
        }
        for scope, records in (("RUN_DIR", run_custody), ("CONTROL_DIR", control_custody)):
            for record in records:
                relative = record.get("path", "<invalid>")
                _exact(
                    record.get("file_type"), "regular",
                    f"failure {scope} custody requires a flat regular leaf {relative}", errors,
                )
                _exact(
                    record.get("link_count"), 1,
                    f"failure {scope} custody requires link count one {relative}", errors,
                )
                inode_key = (str(record.get("device")), str(record.get("inode")))
                owner = f"{scope}/{relative}"
                if inode_key in immutable_failure_inodes:
                    errors.append(f"failure custody leaf {owner} aliases an immutable input")
                if inode_key in custody_inode_owner:
                    errors.append(
                        f"failure custody leaf {owner} aliases {custody_inode_owner[inode_key]}"
                    )
                else:
                    custody_inode_owner[inode_key] = owner
        try:
            raw_identity = _file_identity(raw_path, "raw-result.json")
            _exact(
                raw_identity.get("link_count"), 1,
                "failure raw-result.json link count", errors,
            )
            raw_inode_key = (raw_identity["device"], raw_identity["inode"])
            if raw_inode_key in immutable_failure_inodes:
                errors.append("failure raw-result.json aliases an immutable input")
            if raw_inode_key in custody_inode_owner:
                errors.append(
                    "failure raw-result.json aliases " + custody_inode_owner[raw_inode_key]
                )
        except (OSError, ValueError) as exc:
            errors.append(f"failure raw-result.json identity cannot be retained: {exc}")
        reported_failure_custody = raw_result.get("terminal_failure_custody", {})
        control_identity = (
            _directory_identity(control_dir)
            if control_is_nofollow_directory else None
        )
        expected_failure_custody = {
            "custody_check_id": "post_directory_creation_terminal_failure_v1",
            "inode_custody_scope": "original_supervised_workspace_only",
            "run_entries_before_failure_record": run_custody,
            "control_directory_before_children": control_identity,
            "control_directory_terminal": control_identity,
            "control_entries": control_custody,
            "failure_record_excluded_from_own_inventory": True,
            "pass_manifest_transition": reported_failure_custody.get(
                "pass_manifest_transition"
            ),
            "provisional_pass_manifest": reported_failure_custody.get(
                "provisional_pass_manifest"
            ),
            "provisional_success_raw_result": reported_failure_custody.get(
                "provisional_success_raw_result"
            ),
            "stale_pass_manifest_present_before_finalization": reported_failure_custody.get(
                "stale_pass_manifest_present_before_finalization"
            ),
            "stale_pass_manifest_removed": reported_failure_custody.get(
                "stale_pass_manifest_present_before_finalization"
            ),
            "pass_manifest_absent_after_finalization": True,
            "in_transaction_control_cleanup_performed": False,
        }
        _exact(raw_result.get("terminal_failure_custody"), expected_failure_custody, "failure terminal custody", errors)
        if reported_failure_custody.get("pass_manifest_transition") == "post_manifest_failure_cleanup":
            prior_raw = reported_failure_custody.get("provisional_success_raw_result")
            if isinstance(prior_raw, dict):
                _require(
                    prior_raw != _artifact_record(raw_path, "raw-result.json"),
                    "provisional success raw result aliases the terminal failure record",
                    errors,
                )
        invalid, unresolved = _failure_count_source(run_dir, errors)
        _exact(raw_result.get("invalid_count"), invalid, "failure invalid count", errors)
        _exact(raw_result.get("unresolved_count"), unresolved, "failure unresolved count", errors)
        actual_completed: list[dict[str, Any]] = []
        for relative in FAILURE_COMPLETION_ORDER:
            path = run_dir / relative
            if _schema_valid_completed_artifact(run_dir, relative, decision):
                actual_completed.append(_artifact_record(path, relative))
        completed_paths = {record["path"] for record in actual_completed}
        phase_names = list(FAILURE_PHASE_ARTIFACTS)
        if failed_phase in FAILURE_PHASE_ARTIFACTS:
            failed_index = phase_names.index(failed_phase)
            for index, phase_name in enumerate(phase_names):
                phase_paths = set(FAILURE_PHASE_ARTIFACTS[phase_name])
                if index < failed_index:
                    _require(
                        phase_paths.issubset(completed_paths),
                        f"failure chronology lacks completed prior phase {phase_name}", errors,
                    )
                elif index > failed_index:
                    _require(
                        completed_paths.isdisjoint(phase_paths),
                        f"failure chronology contains later phase {phase_name}", errors,
                    )
        _validate_failure_prior_phase_passes(
            run_dir, control_dir, decision, custody, failed_phase,
            completed_paths, errors,
        )
        required_paths = FAILURE_PHASE_REQUIRED_PATHS.get(raw_result.get("failed_phase"), [])
        incomplete_artifact = any(path not in completed_paths for path in required_paths)
        expected_status, expected_phase, expected_reason = _terminal_failure_expectation(
            raw_result, invalid, unresolved, incomplete_artifact,
        )
        _exact(raw_result.get("status"), expected_status, "failure terminal status", errors)
        _exact(raw_result.get("failed_phase"), expected_phase, "failure phase", errors)
        _exact(raw_result.get("failure_reason"), expected_reason, "failure reason", errors)
        _exact(raw_result.get("completed_artifacts"), actual_completed, "failure completed artifacts", errors)
        return errors

    expected_names = set(STAGE_PATHS + CUSTODY_PATHS + [TERMINAL_CUSTODY_PATH])
    actual_names = {entry.name for entry in entries}
    _exact(actual_names, expected_names, "PASS final directory path set", errors)
    if actual_names != expected_names:
        return errors
    for relative in STAGE_PATHS + CUSTODY_PATHS + [TERMINAL_CUSTODY_PATH]:
        _validate_regular_file(run_dir / relative, f"PASS path {relative}", errors)
    _validate_distinct_single_link_files(
        [(relative, run_dir / relative) for relative in STAGE_PATHS + CUSTODY_PATHS + [TERMINAL_CUSTODY_PATH]],
        "PASS output", errors, forbidden_inodes=_immutable_input_inodes(decision),
    )
    run_producer_identities, control_producer_identities = _validate_terminal_output_custody(
        run_dir, control_dir, decision, errors,
    )
    if errors:
        return errors
    postrun_run_directory_identity = _directory_identity(run_dir)
    postrun_control_directory_identity = _directory_identity(control_dir)
    postrun_full_run_inventory = [
        _file_identity(run_dir / relative, relative)
        for relative in sorted(expected_names)
    ]
    postrun_full_control_inventory = [
        _file_identity(control_dir / relative, relative)
        for relative in sorted(PRODUCER_PATHS)
    ]

    disposition_schema = _load_json_artifact(run_dir / "disposition-schema.json", "disposition-schema.json", errors)
    candidate = _load_json_artifact(run_dir / "candidate-stream.json", "candidate-stream.json", errors)
    producer_verification = _load_json_artifact(run_dir / "verification.json", "verification.json", errors)
    independent_verification = _load_json_artifact(run_dir / "independent-verification.json", "independent-verification.json", errors)
    restart = _load_json_artifact(run_dir / "checkpoint-resume-control.json", "checkpoint-resume-control.json", errors)
    agreement = _load_json_artifact(run_dir / "independent-agreement.json", "independent-agreement.json", errors)
    audit = _load_json_artifact(run_dir / "dependency-audit.json", "dependency-audit.json", errors)
    receipt = _load_json_artifact(run_dir / "independent-verifier-receipt.json", "independent-verifier-receipt.json", errors)
    environment = _load_json_artifact(run_dir / "environment.json", "environment.json", errors)
    success_raw = raw_result
    manifest = _load_json_artifact(run_dir / "manifest.yaml", "manifest.yaml", errors)
    terminal_seal = _load_json_artifact(
        run_dir / TERMINAL_CUSTODY_PATH, TERMINAL_CUSTODY_PATH, errors,
    )
    retained = _load_jsonl_artifact(run_dir / "retained-candidates.jsonl", "retained-candidates.jsonl", errors)
    complete = _load_jsonl_artifact(run_dir / "complete-relations.jsonl", "complete-relations.jsonl", errors)
    partial = _load_jsonl_artifact(run_dir / "partial-relations.jsonl", "partial-relations.jsonl", errors)
    checkpoints = _load_jsonl_artifact(
        run_dir / "checkpoint-chain.jsonl",
        "checkpoint-chain.jsonl",
        errors,
        index_field="shard_index",
    )
    required_documents = (
        disposition_schema, candidate, producer_verification, independent_verification,
        restart, agreement, audit, receipt, environment, manifest, terminal_seal, retained, complete,
        partial, checkpoints,
    )
    if any(document is None for document in required_documents):
        return errors
    assert disposition_schema is not None and candidate is not None
    assert producer_verification is not None and independent_verification is not None
    assert restart is not None and agreement is not None and audit is not None
    assert receipt is not None and environment is not None and manifest is not None
    assert terminal_seal is not None
    assert retained is not None and complete is not None and partial is not None and checkpoints is not None

    predecessor = Path(decision["paths"]["predecessor_dir"])
    try:
        postrun_decision_identity = _file_identity(
            Path(decision["paths"]["decision_json"]),
        )
        postrun_protected_identities = {
            name: _file_identity(
                Path(decision["paths"]["protocol_repository_path"]) / relative,
            )
            for name, relative in PROTECTED_PROTOCOL_RELATIVE_PATHS.items()
        }
        postrun_binary_identities = {
            role: _file_identity(Path(decision["paths"][f"{role}_bin"]))
            for role in ("producer", "verifier", "supervisor")
        }
        postrun_predecessor_identities = {
            relative: _file_identity(predecessor / relative)
            for relative in PREDECESSOR_PATHS
        }
        postrun_predecessor_identities[
            "pre_execution_repository_custody"
        ] = _file_identity(
            Path(decision["predecessor_repository_custody"][
                "pre_execution_retained_path"
            ]),
        )
        postrun_repository_identities = {
            "protocol": _directory_identity(
                Path(decision["paths"]["protocol_repository_path"]),
            ),
            "predecessor": _directory_identity(
                Path(decision["paths"]["predecessor_repository_path"]),
            ),
            **{
                role: _directory_identity(
                    Path(decision["paths"][f"{role}_repository_path"]),
                )
                for role in ("producer", "verifier", "supervisor")
            },
        }
    except (OSError, ValueError) as exc:
        errors.append(f"post-run entry immutable-input snapshot failed: {exc}")
        return errors
    protocol_repository = Path(decision["paths"]["protocol_repository_path"])
    postrun_protocol_profile = decision["selective_worktree_profiles"]["protocol"]
    postrun_predecessor_profile = decision["selective_worktree_profiles"]["predecessor"]
    postrun_predecessor_pre_profile = decision["selective_worktree_profiles"][
        "predecessor_pre_execution"
    ]
    postrun_predecessor_repository = Path(
        decision["paths"]["predecessor_repository_path"]
    )
    protocol_historical_rows = _historical_repository_object_custody(
        protocol_repository,
        (
            (
                decision["protocol_commit"],
                (postrun_protocol_profile, postrun_predecessor_pre_profile),
            ),
            (custody["decision_commit"], ()),
        ),
        "post-run Role-2 protocol historical custody", errors,
    ) or []
    predecessor_historical_rows = _historical_repository_object_custody(
        postrun_predecessor_repository,
        (
            (
                decision["predecessor_role1"]["protocol_commit"],
                (postrun_protocol_profile, postrun_predecessor_pre_profile),
            ),
            (
                decision["predecessor_role1"]["decision_commit"],
                (postrun_predecessor_pre_profile,),
            ),
        ),
        "post-run Role-1 predecessor historical custody", errors,
    ) or []
    protocol_shared_payload_rows = {
        str(row["object_id"]): row
        for row in protocol_historical_rows if row.get("kind") == "blob"
    }
    predecessor_historical_by_oid = {
        str(row["object_id"]): row for row in predecessor_historical_rows
    }
    for object_id, row in sorted(protocol_shared_payload_rows.items()):
        _exact(
            predecessor_historical_by_oid.get(object_id), row,
            f"post-run cross-repository shared-base payload {object_id}", errors,
        )
    postrun_entry_preflight = _repository_git_preflight_errors(
        protocol_repository, postrun_protocol_profile,
    )
    errors.extend(
        f"post-run entry protocol: {item}" for item in postrun_entry_preflight
    )
    if postrun_entry_preflight:
        return errors
    try:
        postrun_protocol_git_storage = _git_head_index_storage_identities(
            protocol_repository,
        )
    except (OSError, ValueError) as exc:
        errors.append(f"post-run entry protocol Git storage snapshot failed: {exc}")
        return errors
    postrun_entry_head_raw = _git_stdout(
        protocol_repository, ["rev-parse", "HEAD"],
        "post-run entry protocol HEAD", errors,
    )
    postrun_entry_head = (
        "" if postrun_entry_head_raw is None
        else postrun_entry_head_raw.rstrip(b"\n").decode("ascii", "replace")
    )
    postrun_entry_protocol_state = _protocol_output_state(
        protocol_repository, run_dir, control_dir,
        custody["decision_commit"], postrun_protocol_profile, errors,
        protocol_historical_rows,
    )

    shared_producer_bindings = _validate_canonical_producer_phase(
        run_dir, decision, errors,
    )
    if shared_producer_bindings is None:
        return errors

    try:
        disposition_bytes = _read_regular_file_bytes(
            run_dir / "disposition.bin", "PASS disposition.bin",
        )
        status_counts, statuses, disposition_hashes = parse_disposition_details(disposition_bytes)
    except Exception as exc:
        errors.append(f"disposition.bin: {exc}")
        return errors
    _exact(candidate.get("status_counts"), status_counts, "candidate/disposition status counts", errors)
    _exact(status_counts.get("invalid"), 0, "PASS invalid count", errors)
    _exact(status_counts.get("unresolved"), 0, "PASS unresolved count", errors)
    for index, v, x in box0_pairs():
        primitive = math.gcd(abs((x - TRACE_T * v) // 2), v) == 1
        if (statuses[index] == 0) == primitive:
            errors.append(f"disposition primitivity mismatch at candidate {index}")
            break
    candidate_raw, candidate_shard, candidate_shell = _candidate_roots()
    disposition_raw, disposition_shard, disposition_shell = _disposition_roots(disposition_bytes)
    shard = candidate["candidate_shards"][0]
    _exact(shard.get("records_sha256"), candidate_raw, "candidate raw shard hash", errors)
    _exact(shard.get("candidate_shard_sha256"), candidate_shard, "candidate domain shard hash", errors)
    _exact(candidate.get("candidate_shell_sha256"), candidate_shell, "candidate shell root", errors)
    disposition_entry = candidate["disposition"]
    _exact(disposition_entry["shards"][0].get("records_sha256"), disposition_raw, "disposition raw shard hash", errors)
    _exact(disposition_entry["shards"][0].get("disposition_shard_sha256"), disposition_shard, "disposition domain shard hash", errors)
    _exact(disposition_entry.get("shell_sha256"), disposition_shell, "disposition shell root", errors)
    _check_artifact_record(candidate["disposition_schema"], run_dir / "disposition-schema.json", "disposition-schema.json", "candidate disposition schema", errors)
    _check_artifact_record(disposition_entry["artifact"], run_dir / "disposition.bin", "disposition.bin", "candidate disposition artifact", errors)
    for key, relative in (
        ("retained_candidates", "retained-candidates.jsonl"),
        ("complete_relations", "complete-relations.jsonl"),
        ("partial_relations", "partial-relations.jsonl"),
        ("checkpoint_chain", "checkpoint-chain.jsonl"),
    ):
        _check_artifact_record(candidate[key]["artifact"], run_dir / relative, relative, f"candidate {key}", errors)

    expected_retained = [index for index, status in enumerate(statuses) if status in (1, 2, 3)]
    expected_complete = [index for index, status in enumerate(statuses) if status == 1]
    expected_partial = [index for index, status in enumerate(statuses) if status in (2, 3)]
    _exact([row["candidate_index"] for row in retained], expected_retained, "retained membership", errors)
    _exact([row["candidate_index"] for row in complete], expected_complete, "complete relation membership", errors)
    _exact([row["candidate_index"] for row in partial], expected_partial, "partial relation membership", errors)
    retained_by_index = {row["candidate_index"]: row for row in retained}
    for row in retained:
        expected_hashes = disposition_hashes.get(row["candidate_index"])
        _exact(
            (row.get("candidate_certificate_sha256"), row.get("factorization_certificate_sha256")),
            expected_hashes, f"retained/disposition hashes {row['candidate_index']}", errors,
        )
        _exact(row.get("status"), statuses[row["candidate_index"]], f"retained status {row['candidate_index']}", errors)
    for label, rows in (("complete", complete), ("partial", partial)):
        for row in rows:
            source = retained_by_index.get(row["candidate_index"], {})
            _exact(row.get("candidate_id"), source.get("candidate_id"), f"{label}/retained candidate id", errors)
            _exact(row.get("candidate_certificate_sha256"), source.get("candidate_certificate_sha256"), f"{label}/retained candidate hash", errors)
            _exact(row.get("factorization_certificate_sha256"), source.get("factorization_certificate_sha256"), f"{label}/retained factorization hash", errors)

    _exact(len(checkpoints), 1, "checkpoint line count", errors)
    if len(checkpoints) == 1:
        checkpoint = checkpoints[0]
        _exact(checkpoint.get("protocol_commit"), decision["protocol_commit"], "checkpoint protocol commit", errors)
        _exact(checkpoint.get("producer_commit"), decision["producer_commit"], "checkpoint producer commit", errors)
        _exact(checkpoint.get("producer_binary_sha256"), decision["producer_binary_sha256"], "checkpoint producer binary", errors)
        _exact(checkpoint.get("factor_base_sha256"), candidate["factor_base_sha256"], "checkpoint factor base", errors)
        _exact(checkpoint.get("candidate_shard_sha256"), candidate_shard, "checkpoint candidate shard", errors)
        _exact(checkpoint.get("disposition_shard_sha256"), disposition_shard, "checkpoint disposition shard", errors)
        counters = checkpoint.get("phase_counters", {})
        expected_counters = {
            "seen": "262148", "primitive": "168990", "duplicate": "93158",
            "complete": str(status_counts["complete"]),
            "one_lp": str(status_counts["one_large_prime"]),
            "two_lp": str(status_counts["two_large_prime"]),
            "rejected": str(status_counts["rejected"]),
            "invalid": str(status_counts["invalid"]),
            "unresolved": str(status_counts["unresolved"]),
        }
        _exact(counters, expected_counters, "checkpoint/status counters", errors)
        for relative in APPEND_PATHS:
            data = _read_regular_file_bytes(
                run_dir / relative, f"PASS checkpoint input {relative}",
            )
            expected_prefix = {"byte_length": str(len(data)), "prefix_sha256": sha256_bytes(data)}
            _exact(checkpoint["committed_outputs"].get(relative), expected_prefix, f"checkpoint prefix {relative}", errors)

    predecessor_error_count = len(errors)
    for relative in PREDECESSOR_PATHS:
        _validate_regular_file(predecessor / relative, f"post-run predecessor {relative}", errors)
    if len(errors) != predecessor_error_count:
        return errors
    predecessor_records = candidate["predecessor"]
    predecessor_fields = (
        ("factor_base", "factor-base.json"),
        ("factor_base_sidecar", "factor-base.sha256"),
        ("producer_verification", "verification.json"),
        ("independent_verification", "independent-verification.json"),
        ("independent_agreement", "independent-agreement.json"),
        ("supervisor_receipt", "independent-verifier-receipt.json"),
    )
    _exact(predecessor_records.get("run_id"), decision["predecessor_run_id"], "candidate predecessor run id", errors)
    for field, relative in predecessor_fields:
        _check_artifact_record(predecessor_records[field], predecessor / relative, relative, f"candidate predecessor {field}", errors)
    try:
        factor_base = decode_canonical_json(_read_regular_file_bytes(
            predecessor / "factor-base.json", "PASS predecessor factor base",
        ))
        _exact(factor_base.get("source_commit"), decision["factor_base_source_commit"], "predecessor factor-base source commit", errors)
        sidecar = _read_regular_file_bytes(
            predecessor / "factor-base.sha256", "PASS predecessor factor-base sidecar",
        )
        expected_sidecar = f'{sha256_path(predecessor / "factor-base.json")}  factor-base.json\n'.encode("ascii")
        _exact(sidecar, expected_sidecar, "predecessor factor-base sidecar", errors)
        for name in ("verification.json", "independent-verification.json", "independent-agreement.json", "independent-verifier-receipt.json"):
            predecessor_doc = decode_canonical_json(_read_regular_file_bytes(
                predecessor / name, f"PASS predecessor {name}",
            ))
            _exact(predecessor_doc.get("overall_status"), "PASS", f"predecessor {name} status", errors)
            _exact(predecessor_doc.get("protocol_commit"), decision["protocol_commit"], f"predecessor {name} protocol commit", errors)
            _exact(predecessor_doc.get("source_commit"), decision["factor_base_source_commit"], f"predecessor {name} source commit", errors)
    except Exception as exc:
        errors.append(f"predecessor canonical replay failed: {exc}")

    for field in ("protocol_commit", "producer_commit", "producer_binary_sha256", "factor_base_source_commit", "factor_base_sha256", "shell_id"):
        _exact(candidate.get(field), disposition_schema.get(field), f"candidate/disposition-schema {field}", errors)
    for field in ("protocol_commit", "producer_commit", "factor_base_source_commit"):
        _exact(candidate.get(field), decision.get(field), f"candidate/decision {field}", errors)
    _exact(candidate.get("producer_binary_sha256"), decision["producer_binary_sha256"], "candidate producer binary", errors)
    _exact(candidate.get("factor_base_sha256"), sha256_path(predecessor / "factor-base.json"), "candidate factor base hash", errors)
    bindings = _binding_values_from_candidate(candidate)
    _exact(bindings, shared_producer_bindings, "PASS shared canonical-producer replay", errors)
    _exact(producer_verification.get("bindings"), bindings, "producer verification bindings", errors)
    _exact(independent_verification.get("bindings"), bindings, "independent verification bindings", errors)
    _exact(producer_verification.get("overall_status"), "PASS", "producer verification status", errors)
    _exact(independent_verification.get("overall_status"), "PASS", "independent verification status", errors)
    _exact(independent_verification.get("verifier_commit"), decision["verifier_commit"], "independent verifier commit", errors)
    _exact(independent_verification.get("verifier_binary_sha256"), decision["verifier_binary_sha256"], "independent verifier binary", errors)
    for item in producer_verification.get("artifacts", []):
        _check_artifact_record(item, run_dir / item["path"], item["path"], "producer verification artifact", errors)
    for item in independent_verification.get("source_artifacts", []):
        _check_artifact_record(item, run_dir / item["path"], item["path"], "independent source artifact", errors)

    _exact(agreement.get("producer_verification_sha256"), sha256_path(run_dir / "verification.json"), "agreement producer verification hash", errors)
    _exact(agreement.get("independent_verification_sha256"), sha256_path(run_dir / "independent-verification.json"), "agreement independent verification hash", errors)
    _exact(agreement.get("overall_status"), "PASS", "agreement status", errors)
    agreement_map = {row["field"]: row for row in agreement.get("comparisons", [])}
    for field, expected in bindings.items():
        row = agreement_map.get(field, {})
        _exact((row.get("producer"), row.get("verifier"), row.get("equal")), (str(expected), str(expected), True), f"agreement binding {field}", errors)

    _exact(restart.get("fault_argv"), decision["producer_fault_argv"], "restart fault argv", errors)
    _exact(restart.get("resume_argv"), decision["producer_resume_argv"], "restart resume argv", errors)
    _exact(restart.get("overall_status"), "PASS", "restart status", errors)
    for field in (
        "protocol_commit", "producer_commit", "producer_binary_sha256",
        "factor_base_source_commit",
    ):
        _exact(restart.get(field), decision[field], f"restart/decision {field}", errors)
    _exact(restart.get("factor_base_sha256"), candidate["factor_base_sha256"], "restart factor base", errors)
    _exact(restart.get("shell_id"), candidate["shell_id"], "restart shell", errors)
    _exact(restart.get("control_dir"), str(control_dir), "restart retained control dir", errors)
    suffix = bytes.fromhex("503139322d57434d2d554e434f4d4d49545445442d5355464649582d763100")
    expected_fault_state = [
        _artifact_record(run_dir / path, path) for path in CONTROL_CHECKPOINT_PATHS
    ]
    expected_injected_state = []
    for relative in CONTROL_CHECKPOINT_PATHS:
        injected = _read_regular_file_bytes(
            run_dir / relative, f"PASS restart injected source {relative}",
        )
        if relative in APPEND_PATHS:
            injected += suffix
        expected_injected_state.append({
            "path": relative,
            "byte_length": len(injected),
            "sha256": sha256_bytes(injected),
        })
    expected_resumed_control = [
        _artifact_record(control_dir / path, path) for path in PRODUCER_PATHS
    ]
    _exact(restart.get("fault_state_artifacts"), expected_fault_state, "restart fault-state artifacts", errors)
    _exact(restart.get("injected_state_artifacts"), expected_injected_state, "restart injected-state artifacts", errors)
    _exact(restart.get("resumed_control_artifacts"), expected_resumed_control, "restart resumed control artifacts", errors)
    _exact(restart.get("control_directory_terminal"), _directory_identity(control_dir), "restart control directory identity", errors)
    _exact(restart.get("control_retained_after_terminal_validation"), True, "restart control retained", errors)
    _exact(
        restart.get("control_cleanup_authority"),
        "out_of_band_after_terminal_validation_and_archival_only",
        "restart control cleanup authority", errors,
    )
    for comparison in restart.get("comparisons", []):
        relative = comparison["field"]
        fresh_hash = sha256_path(run_dir / relative)
        resumed_hash = sha256_path(control_dir / relative)
        _exact((comparison.get("fresh_sha256"), comparison.get("resumed_sha256"), comparison.get("equal")), (fresh_hash, resumed_hash, fresh_hash == resumed_hash), f"restart comparison {relative}", errors)

    role_commits = {
        "producer": decision["producer_commit"],
        "verifier": decision["verifier_commit"],
        "supervisor": decision["supervisor_commit"],
    }
    _exact(
        audit.get("verifier_forbidden_dependency_scan"),
        _verifier_dependency_scan_record(decision),
        "dependency audit canonical verifier dependency scan", errors,
    )
    expected_build_custody = _verifier_build_custody(decision)
    _exact(
        audit.get("verifier_build_custody"), expected_build_custody,
        "dependency audit verifier build custody", errors,
    )
    recomputed_sources: dict[str, list[dict[str, str]]] = {}
    recomputed_source_build_inputs: dict[str, list[dict[str, Any]]] = {}
    for role, commit in role_commits.items():
        git_record = audit.get(f"{role}_git", {})
        expected_git = {
            "git_head": commit,
            "git_top_level": decision["paths"][f"{role}_repository_path"],
            "package_root": decision["paths"][f"{role}_package_path"],
            "worktree_clean": True,
        }
        _exact(git_record, expected_git, f"dependency audit {role} Git binding", errors)
        repository = Path(expected_git["git_top_level"])
        package = Path(expected_git["package_root"])
        try:
            executable_identity = _file_identity(Path(decision["paths"][f"{role}_bin"]))
            _exact(
                audit.get(f"{role}_executable_before"), executable_identity,
                f"dependency audit {role} executable before", errors,
            )
            _exact(
                audit.get(f"{role}_executable_after"), executable_identity,
                f"dependency audit {role} executable after", errors,
            )
            rows = _collect_rust_hash_rows(package)
            recomputed_sources[role] = rows
            _exact(audit.get(f"{role}_rust_sources"), rows, f"dependency audit {role} complete Rust inventory", errors)
            source_build_rows = _source_build_input_rows(
                repository, package, commit, f"terminal {role}", errors,
            )
            if source_build_rows is not None:
                recomputed_source_build_inputs[role] = source_build_rows
                _exact(
                    audit.get(f"{role}_source_build_inputs_before"), source_build_rows,
                    f"dependency audit {role} source/build inputs before", errors,
                )
                _exact(
                    audit.get(f"{role}_source_build_inputs_after"), source_build_rows,
                    f"dependency audit {role} source/build inputs after", errors,
                )
                digest = _source_input_digest(source_build_rows)
                _exact(
                    audit.get(f"{role}_source_build_tree_sha256_before"), digest,
                    f"dependency audit {role} source/build digest before", errors,
                )
                _exact(
                    audit.get(f"{role}_source_build_tree_sha256_after"), digest,
                    f"dependency audit {role} source/build digest after", errors,
                )
            _validate_regular_file(package / "Cargo.toml", f"dependency audit {role} Cargo.toml", errors)
            active_lock = package / "Cargo.lock"
            _validate_regular_file(active_lock, f"dependency audit {role} active Cargo.lock", errors)
            cargo_toml_bytes = _read_regular_file_bytes(
                package / "Cargo.toml", f"dependency audit {role} Cargo.toml",
            )
            cargo_lock_bytes = _read_regular_file_bytes(
                active_lock, f"dependency audit {role} Cargo.lock",
            )
            _exact(
                audit.get(f"{role}_cargo_toml_sha256"), sha256_bytes(cargo_toml_bytes),
                f"dependency audit {role} Cargo.toml hash", errors,
            )
            _exact(
                audit.get(f"{role}_cargo_lock_sha256"), sha256_bytes(cargo_lock_bytes),
                f"dependency audit {role} active Cargo.lock hash", errors,
            )
            _exact(
                audit.get(f"{role}_cargo_lock_path"), str(active_lock),
                f"dependency audit {role} active Cargo.lock path", errors,
            )
            if role == "verifier":
                errors.extend(_verifier_dependency_errors(
                    cargo_toml_bytes,
                    cargo_lock_bytes,
                    Path(decision["paths"]["verifier_repository_path"]),
                    package,
                    Path(decision["paths"]["producer_repository_path"]),
                    Path(decision["paths"]["producer_package_path"]),
                ))
                scanned = cargo_toml_bytes + b"\n" + b"\n".join(
                    _read_regular_file_bytes(
                        package / row["path"],
                        f"dependency audit verifier Rust source {row['path']}",
                    )
                    for row in rows
                )
                for marker in FORBIDDEN_VERIFIER_SOURCE_MARKERS:
                    _require(
                        marker not in scanned,
                        f"dependency audit verifier contains forbidden source marker {marker.decode('ascii')}",
                        errors,
                    )
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            errors.append(f"dependency audit {role} source recomputation failed: {exc}")
    if set(recomputed_sources) == set(role_commits):
        producer_hashes = {row["sha256"] for row in recomputed_sources["producer"]}
        verifier_hashes = {row["sha256"] for row in recomputed_sources["verifier"]}
        _require(
            producer_hashes.isdisjoint(verifier_hashes),
            "dependency audit hides identical producer/verifier Rust source hashes", errors,
        )
    producer_source_root = Path(decision["paths"]["producer_package_path"])
    verifier_source_root = Path(decision["paths"]["verifier_package_path"])
    try:
        expected_clone_screen = compute_source_clone_screen(producer_source_root, verifier_source_root)
        _exact(
            audit.get("source_clone_screen"), expected_clone_screen,
            "dependency audit independently recomputed source clone screen", errors,
        )
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        errors.append(f"dependency audit source clone recomputation failed: {exc}")

    _exact(receipt.get("decision_id"), decision["decision_id"], "receipt decision id", errors)
    _exact(receipt.get("decision_custody"), custody, "receipt decision custody", errors)
    _exact(receipt.get("run_id"), decision["run_id"], "receipt run id", errors)
    for field in ("protocol_commit", "factor_base_source_commit", "producer_commit", "verifier_commit", "supervisor_commit", "supervisor_binary_sha256"):
        _exact(receipt.get(field), decision.get(field), f"receipt/decision {field}", errors)
    _exact(
        receipt.get("verifier_build_custody"), expected_build_custody,
        "receipt verifier build custody", errors,
    )
    predecessor_inventory = [_artifact_record(predecessor / path, path) for path in PREDECESSOR_PATHS]
    producer_inventory = [_artifact_record(run_dir / path, path) for path in PRODUCER_PATHS]
    _exact(receipt.get("predecessor_artifacts_before"), predecessor_inventory, "receipt predecessor before", errors)
    _exact(receipt.get("predecessor_artifacts_after"), predecessor_inventory, "receipt predecessor after", errors)
    _exact(receipt.get("producer_artifacts_before_verifier"), producer_inventory, "receipt producer before", errors)
    _exact(receipt.get("producer_artifacts_after_verifier"), producer_inventory, "receipt producer after", errors)
    predecessor_fd_snapshots = [
        _file_identity(predecessor / path, path) for path in PREDECESSOR_PATHS
    ]
    predecessor_snapshot_sha256 = _identity_bundle_digest(predecessor_fd_snapshots)
    _exact(
        receipt.get("predecessor_retained_fd_snapshots"), predecessor_fd_snapshots,
        "receipt retained predecessor FD snapshots", errors,
    )
    _exact(
        receipt.get("run_producer_artifacts_terminal"), run_producer_identities,
        "receipt terminal RUN_DIR producer identities", errors,
    )
    _exact(
        receipt.get("control_producer_artifacts_terminal"), control_producer_identities,
        "receipt terminal CONTROL_DIR producer identities", errors,
    )
    binary_identities = {
        role: _file_identity(Path(decision["paths"][f"{role}_bin"]))
        for role in ("producer", "verifier", "supervisor")
    }
    _exact(receipt.get("binary_identities_before"), binary_identities, "receipt binary identities before", errors)
    _exact(receipt.get("binary_identities_after"), binary_identities, "receipt binary identities after", errors)
    expected_source_build_digests = {
        role: _source_input_digest(recomputed_source_build_inputs[role])
        for role in ("producer", "verifier", "supervisor")
        if role in recomputed_source_build_inputs
    }
    _exact(
        receipt.get("source_build_tree_sha256_before"),
        expected_source_build_digests,
        "receipt source/build tree digests before", errors,
    )
    _exact(
        receipt.get("source_build_tree_sha256_after"),
        expected_source_build_digests,
        "receipt source/build tree digests after", errors,
    )

    execution = receipt.get("execution_custody", {})
    supervisor_execution = execution.get("supervisor", {})
    supervisor_path = decision["paths"]["supervisor_bin"]
    _exact(supervisor_execution.get("raw_argv0"), supervisor_path, "supervisor raw argv0", errors)
    _exact(supervisor_execution.get("current_exe"), supervisor_path, "supervisor current_exe", errors)
    _exact(supervisor_execution.get("decision_supervisor_path"), supervisor_path, "supervisor decision path", errors)
    _exact(
        supervisor_execution.get("proc_self_exe_sha256"), decision["supervisor_binary_sha256"],
        "supervisor /proc/self/exe hash", errors,
    )
    _exact(supervisor_execution.get("source_before"), binary_identities["supervisor"], "supervisor source before", errors)
    _exact(supervisor_execution.get("source_terminal"), binary_identities["supervisor"], "supervisor source terminal", errors)
    sealed_images = execution.get("sealed_images", [])
    _exact([image.get("role") for image in sealed_images], ["producer", "verifier"], "sealed image role order", errors)
    expected_sealed_ids: dict[str, str] = {}
    for image in sealed_images:
        role = image.get("role")
        if role not in {"producer", "verifier"}:
            continue
        expected_sealed_ids[role] = image.get("sealed_image_id")
        _exact(image.get("source_path"), decision["paths"][f"{role}_bin"], f"{role} sealed source path", errors)
        _exact(image.get("source_before"), binary_identities[role], f"{role} sealed source before", errors)
        _exact(image.get("source_terminal"), binary_identities[role], f"{role} sealed source terminal", errors)
        _exact(image.get("open_flags"), EXECUTION_CONTROLS["child_open_flags"], f"{role} sealed open flags", errors)
        _exact(image.get("memfd_flags"), EXECUTION_CONTROLS["child_memfd_flags"], f"{role} memfd flags", errors)
        _exact(image.get("seals"), EXECUTION_CONTROLS["child_memfd_seals"], f"{role} memfd seals", errors)
        _exact(image.get("memfd_byte_length"), binary_identities[role]["byte_length"], f"{role} memfd length", errors)
        _exact(image.get("memfd_sha256"), binary_identities[role]["sha256"], f"{role} memfd hash", errors)
        _exact(image.get("logical_argv0"), decision["paths"][f"{role}_bin"], f"{role} logical argv0", errors)
        _exact(
            image.get("launch_path"), SEALED_EXEC_FD_PATHS[role],
            f"{role} sealed launch path ABI", errors,
        )
        _exact(image.get("opened_once"), True, f"{role} image opened once", errors)
        _exact(image.get("launch_count"), 3 if role == "producer" else 1, f"{role} sealed launch count", errors)
        _exact(image.get("source_descriptor_cloexec"), True, f"{role} source descriptor CLOEXEC", errors)
        _exact(image.get("target_fd_cloexec_cleared"), True, f"{role} target FD CLOEXEC clearing", errors)

    predecessor_interface = execution.get("predecessor_fd_interface", {})
    _exact(predecessor_interface.get("file_names"), PREDECESSOR_PATHS, "predecessor FD interface file order", errors)
    _exact(predecessor_interface.get("open_flags"), ["O_RDONLY", "O_CLOEXEC", "O_NOFOLLOW"], "predecessor FD interface open flags", errors)
    _exact(predecessor_interface.get("snapshot_sha256"), predecessor_snapshot_sha256, "predecessor FD interface snapshot", errors)
    _exact(predecessor_interface.get("retained_through_terminal"), True, "predecessor FDs retained", errors)
    _exact(predecessor_interface.get("child_reads_from_inherited_fds_only"), True, "predecessor child FD-only reads", errors)
    _exact(predecessor_interface.get("snapshot_strategy"), "sealed_memfd_from_once_opened_nofollow_fd", "predecessor snapshot strategy", errors)
    _exact(predecessor_interface.get("original_paths_rechecked_terminally"), True, "predecessor original path terminal recheck", errors)
    _exact(predecessor_interface.get("original_paths_rechecked_before_each_child"), True, "predecessor original path prelaunch rechecks", errors)
    _exact(predecessor_interface.get("source_descriptors_cloexec"), True, "predecessor source descriptors CLOEXEC", errors)
    _exact(predecessor_interface.get("child_target_fd_cloexec_cleared"), True, "predecessor target FD CLOEXEC clearing", errors)
    _exact(
        predecessor_interface.get("handoff_order"),
        ["open_original_nofollow_once", "copy_to_sealed_memfd", "duplicate_to_fixed_child_fd", "clear_target_FD_CLOEXEC", "exec_child", "retain_original_and_sealed_sources_through_terminal"],
        "predecessor FD handoff order", errors,
    )
    snapshot_images = predecessor_interface.get("snapshot_images", [])
    _exact([item.get("name") for item in snapshot_images], PREDECESSOR_PATHS, "predecessor snapshot-image order", errors)
    for item, expected_identity in zip(snapshot_images, predecessor_fd_snapshots):
        name = item.get("name")
        _exact(item.get("original_before"), expected_identity, f"predecessor snapshot original before {item.get('name')}", errors)
        _exact(item.get("original_terminal"), expected_identity, f"predecessor snapshot original terminal {item.get('name')}", errors)
        _exact(item.get("memfd_flags"), EXECUTION_CONTROLS["child_memfd_flags"], f"predecessor snapshot memfd flags {item.get('name')}", errors)
        _exact(item.get("seals"), EXECUTION_CONTROLS["child_memfd_seals"], f"predecessor snapshot seals {item.get('name')}", errors)
        _exact(item.get("snapshot_byte_length"), expected_identity["byte_length"], f"predecessor snapshot length {item.get('name')}", errors)
        _exact(item.get("snapshot_sha256"), expected_identity["sha256"], f"predecessor snapshot hash {item.get('name')}", errors)
        _exact(
            item.get("retained_fd_path"), PREDECESSOR_SNAPSHOT_FD_PATHS.get(name),
            f"predecessor snapshot retained FD ABI for {name}", errors,
        )
        _exact(item.get("source_descriptor_cloexec"), True, f"predecessor source CLOEXEC for {name}", errors)
        _exact(item.get("target_fd_cloexec_cleared"), True, f"predecessor target CLOEXEC clearing for {name}", errors)
    child_fd_receipts = predecessor_interface.get("children", [])
    _exact([item.get("role") for item in child_fd_receipts], [item["role"] for item in SUPERVISOR_CHILDREN], "predecessor inherited-FD child order", errors)
    for child_fd in child_fd_receipts:
        _exact(child_fd.get("snapshot_sha256"), predecessor_snapshot_sha256, f"predecessor inherited-FD snapshot {child_fd.get('role')}", errors)
        _exact(child_fd.get("target_fd_cloexec_cleared"), True, f"predecessor child target CLOEXEC clearing {child_fd.get('role')}", errors)
        _exact(child_fd.get("reads_inherited_fds_only"), True, f"predecessor child FD-only reads {child_fd.get('role')}", errors)
        inherited = child_fd.get("inherited_fds", [])
        _exact([item.get("name") for item in inherited], PREDECESSOR_PATHS, f"predecessor inherited-FD names {child_fd.get('role')}", errors)
        for item in inherited:
            _exact(
                item.get("fd_path"), PREDECESSOR_SNAPSHOT_FD_PATHS.get(item.get("name")),
                f"predecessor inherited FD ABI for {child_fd.get('role')}/{item.get('name')}", errors,
            )

    protocol_root = Path(decision["paths"]["protocol_repository_path"])
    expected_directories = [
        _directory_identity(protocol_root / EXPERIMENT_RELATIVE_DIRECTORY),
        _directory_identity(protocol_root / RUNS_RELATIVE_DIRECTORY),
        _directory_identity(protocol_root / CONTROLS_RELATIVE_DIRECTORY),
        _directory_identity(run_dir),
        _directory_identity(control_dir),
    ]
    directory_custody = receipt.get("directory_custody", {})
    _exact(directory_custody.get("identities"), expected_directories, "retained directory identities", errors)
    _exact(directory_custody.get("open_flags"), ["O_RDONLY", "O_CLOEXEC", "O_DIRECTORY", "O_NOFOLLOW"], "directory open flags", errors)
    for field in (
        "opened_once_and_retained", "exclusive_fd_relative_leaf_creation",
        "fd_relative_io_only", "same_directory_atomic_rename_only",
        "path_identity_checked_before_each_child", "path_identity_checked_terminally",
    ):
        _exact(directory_custody.get(field), True, f"directory custody {field}", errors)
    _exact(directory_custody.get("fixed_fd_paths"), DIRECTORY_FD_PATHS, "directory fixed FD ABI", errors)
    _exact(directory_custody.get("source_descriptors_cloexec"), True, "directory source descriptors CLOEXEC", errors)
    _exact(directory_custody.get("child_target_fd_cloexec_cleared"), True, "directory target FD CLOEXEC clearing", errors)
    _exact(
        directory_custody.get("creation_open_retention_order"),
        ["open_and_retain_existing_parents", "mkdirat_run_and_control_exclusive", "open_created_run_and_control_nofollow", "verify_path_fd_identity", "duplicate_to_fixed_child_fds", "clear_target_FD_CLOEXEC", "launch_children", "terminal_path_fd_recheck"],
        "directory creation/open/retention order", errors,
    )
    _exact(directory_custody.get("children_use_inherited_directory_fds_only"), True, "child inherited-directory-FD-only I/O", errors)
    _exact(directory_custody.get("logical_paths_are_identity_labels_only"), True, "child logical paths identity-only", errors)
    expected_directory_children = [
        {
            "role": child["role"],
            "directory_fds": DIRECTORY_FD_PATHS,
            "target_fd_cloexec_cleared": True,
            "openat_only": True,
            "logical_paths_identity_only": True,
        }
        for child in SUPERVISOR_CHILDREN
    ]
    _exact(directory_custody.get("children"), expected_directory_children, "child directory FD handoff", errors)

    expected_children = (
        ("canonical_producer", decision["producer_binary_sha256"], decision["producer_commit"], decision["producer_fresh_argv"], 0),
        ("checkpoint_fault_control", decision["producer_binary_sha256"], decision["producer_commit"], decision["producer_fault_argv"], 75),
        ("checkpoint_resume_control", decision["producer_binary_sha256"], decision["producer_commit"], decision["producer_resume_argv"], 0),
        ("isolated_independent_verifier", decision["verifier_binary_sha256"], decision["verifier_commit"], decision["independent_verifier_argv"], 0),
    )
    stdout_hashes = _parse_framed_stream(
        _read_regular_file_bytes(run_dir / "stdout.log", "PASS stdout.log"),
        "stdout", errors,
    )
    stderr_hashes = _parse_framed_stream(
        _read_regular_file_bytes(run_dir / "stderr.log", "PASS stderr.log"),
        "stderr", errors,
    )
    for child, expected in zip(receipt.get("children", []), expected_children):
        role, binary_hash, commit, argv, exit_code = expected
        _exact(child.get("role"), role, "receipt child role", errors)
        _exact(child.get("binary_sha256"), binary_hash, f"receipt child binary {role}", errors)
        _exact(child.get("commit"), commit, f"receipt child commit {role}", errors)
        _exact(child.get("argv"), argv, f"receipt child argv {role}", errors)
        _exact((child.get("expected_exit_code"), child.get("observed_exit_code")), (exit_code, exit_code), f"receipt child exit {role}", errors)
        _exact(child.get("stdout_sha256"), stdout_hashes.get(role), f"receipt child stdout {role}", errors)
        _exact(child.get("stderr_sha256"), stderr_hashes.get(role), f"receipt child stderr {role}", errors)
        image_role = "producer" if role != "isolated_independent_verifier" else "verifier"
        _exact(child.get("sealed_image_id"), expected_sealed_ids.get(image_role), f"receipt child sealed image {role}", errors)
        _exact(child.get("running_image_sha256"), binary_hash, f"receipt child running image {role}", errors)
        _exact(child.get("logical_argv0"), decision["paths"][f"{image_role}_bin"], f"receipt child logical argv0 {role}", errors)
        _exact(
            child.get("actual_exec_path"), SEALED_EXEC_FD_PATHS[image_role],
            f"receipt child actual exec path ABI {role}", errors,
        )
        matching_image = next((image for image in sealed_images if image.get("role") == image_role), {})
        _exact(child.get("actual_exec_path"), matching_image.get("launch_path"), f"receipt child/image launch path {role}", errors)
        _exact(child.get("source_executable_before_launch"), binary_identities[image_role], f"receipt child source before {role}", errors)
        _exact(child.get("source_executable_after_launch"), binary_identities[image_role], f"receipt child source after {role}", errors)
        _exact(child.get("predecessor_snapshot_sha256"), predecessor_snapshot_sha256, f"receipt child predecessor snapshot {role}", errors)
    _exact(receipt.get("checkpoint_resume_control_sha256"), sha256_path(run_dir / "checkpoint-resume-control.json"), "receipt restart hash", errors)
    _exact(receipt.get("independent_agreement_sha256"), sha256_path(run_dir / "independent-agreement.json"), "receipt agreement hash", errors)
    _exact(receipt.get("independent_verification_sha256"), sha256_path(run_dir / "independent-verification.json"), "receipt independent verification hash", errors)
    _exact(receipt.get("dependency_audit_sha256"), sha256_path(run_dir / "dependency-audit.json"), "receipt audit hash", errors)
    _exact(receipt.get("overall_status"), "PASS", "receipt status", errors)

    _exact(environment.get("decision_custody"), custody, "environment decision custody", errors)
    for field in ("protocol_commit", "factor_base_source_commit", "producer_commit", "verifier_commit", "supervisor_commit", "producer_binary_sha256", "verifier_binary_sha256", "supervisor_binary_sha256"):
        _exact(environment.get(field), decision.get(field), f"environment/decision {field}", errors)
    for role in ("producer", "verifier", "supervisor"):
        _exact(
            environment.get(f"{role}_build", {}).get("binary_byte_length"),
            decision[f"{role}_binary_byte_length"],
            f"environment/decision {role} binary length", errors,
        )
    _exact(success_raw.get("decision_custody"), custody, "raw-result decision custody", errors)
    for field in ("protocol_commit", "factor_base_source_commit", "producer_commit", "verifier_commit", "supervisor_commit"):
        _exact(success_raw.get(field), decision.get(field), f"raw-result/decision {field}", errors)
    _exact(success_raw.get("run_id"), decision["run_id"], "raw-result run id", errors)
    _exact(success_raw.get("run_dir"), str(run_dir), "raw-result run_dir", errors)
    _exact(success_raw.get("control_dir"), str(control_dir), "raw-result control_dir", errors)
    control_artifact_inventory = [
        _artifact_record(control_dir / path, path) for path in PRODUCER_PATHS
    ]
    control_tree_sha256 = _artifact_inventory_digest(control_artifact_inventory)
    _exact(success_raw.get("control_tree_sha256"), control_tree_sha256, "raw-result control tree hash", errors)
    _exact(success_raw.get("candidate_stream_sha256"), sha256_path(run_dir / "candidate-stream.json"), "raw-result candidate hash", errors)
    _exact(success_raw.get("checkpoint_resume_control_sha256"), sha256_path(run_dir / "checkpoint-resume-control.json"), "raw-result restart hash", errors)
    _exact(success_raw.get("agreement_sha256"), sha256_path(run_dir / "independent-agreement.json"), "raw-result agreement hash", errors)
    _exact(success_raw.get("audit_sha256"), sha256_path(run_dir / "dependency-audit.json"), "raw-result audit hash", errors)
    _exact(success_raw.get("receipt_sha256"), sha256_path(run_dir / "independent-verifier-receipt.json"), "raw-result receipt hash", errors)

    try:
        command = decode_canonical_json(_read_regular_file_bytes(
            run_dir / "command.txt", "PASS command.txt",
        ))
        _exact(command, decision["supervisor_argv"], "command/supervisor argv", errors)
    except Exception as exc:
        errors.append(f"command.txt: {exc}")
    run = manifest.get("run", {})
    _exact(run.get("id"), decision["run_id"], "manifest run id", errors)
    _exact(run.get("code", {}).get("repository"), decision["paths"]["supervisor_repository_path"], "manifest supervisor repository", errors)
    _exact(run.get("code", {}).get("commit"), decision["supervisor_commit"], "manifest supervisor commit", errors)
    _exact(run.get("code", {}).get("supervisor_binary_sha256"), decision["supervisor_binary_sha256"], "manifest supervisor binary", errors)
    _exact(run.get("environment", {}).get("sha256"), sha256_path(run_dir / "environment.json"), "manifest environment hash", errors)
    parameters = run.get("inputs", {}).get("parameters", {})
    _exact(parameters.get("predecessor_run_id"), decision["predecessor_run_id"], "manifest predecessor id", errors)
    _exact(parameters.get("factor_base_sha256"), candidate["factor_base_sha256"], "manifest factor base hash", errors)
    _exact(parameters.get("decision_id"), decision["decision_id"], "manifest decision id", errors)
    _exact(parameters.get("decision_commit"), custody["decision_commit"], "manifest decision commit", errors)
    _exact(parameters.get("decision_sha256"), custody["decision_sha256"], "manifest decision hash", errors)
    _exact(parameters.get("control_dir"), str(control_dir), "manifest control dir", errors)
    _exact(parameters.get("control_tree_sha256"), control_tree_sha256, "manifest control tree hash", errors)
    _exact(run.get("result", {}).get("certificate", {}).get("sha256"), sha256_path(run_dir / "candidate-stream.json"), "manifest certificate hash", errors)
    expected_manifest_inventory = [_artifact_record(run_dir / path, path) for path in MANIFEST_ARTIFACT_PATHS]
    _exact(run.get("artifacts"), expected_manifest_inventory, "manifest artifact inventory", errors)

    terminal_run_inventory = [
        _file_identity(run_dir / path, path)
        for path in STAGE_PATHS + CUSTODY_PATHS
    ]
    if set(recomputed_source_build_inputs) != {"producer", "verifier", "supervisor"}:
        errors.append("terminal source/build input snapshots are incomplete")
        return errors
    # No Git command may follow the terminal scan for its repository.  Scan
    # implementation repositories first, then make the protocol scan the final
    # Git-bearing operation of full post-run admission.
    selective_profiles = decision["selective_worktree_profiles"]
    source_sparse_profile = selective_profiles["source"]
    protocol_sparse_profile = selective_profiles["protocol"]
    predecessor_sparse_profile = selective_profiles["predecessor"]
    for role in ("producer", "verifier", "supervisor"):
        repository = Path(decision["paths"][f"{role}_repository_path"])
        package = Path(decision["paths"][f"{role}_package_path"])
        preflight = _repository_git_preflight_errors(repository, source_sparse_profile)
        errors.extend(f"terminal {role}: {item}" for item in preflight)
        if preflight:
            continue
        terminal_role_head = _git_stdout(
            repository, ["rev-parse", "HEAD"], f"terminal {role} HEAD", errors,
        )
        if terminal_role_head is not None:
            _exact(
                terminal_role_head.rstrip(b"\n").decode("ascii", "replace"),
                role_commits[role], f"terminal {role} HEAD", errors,
            )
        errors.extend(_protocol_repository_topology_errors(
            repository, role_commits[role], (package / "target",),
            source_sparse_profile,
            forbid_tracked_excluded=True,
        ))
    predecessor_repository = Path(
        decision["paths"]["predecessor_repository_path"]
    )
    predecessor_preflight = _repository_git_preflight_errors(
        predecessor_repository, predecessor_sparse_profile,
    )
    errors.extend(
        f"terminal predecessor archive: {item}"
        for item in predecessor_preflight
    )
    if not predecessor_preflight:
        predecessor_head_raw = _git_stdout(
            predecessor_repository, ["rev-parse", "HEAD"],
            "terminal predecessor archive HEAD", errors,
        )
        if predecessor_head_raw is not None:
            predecessor_head = predecessor_head_raw.rstrip(b"\n").decode(
                "ascii", "replace",
            )
            _exact(
                predecessor_head,
                decision["predecessor_role1"]["archive_commit"],
                "terminal predecessor archive HEAD", errors,
            )
            errors.extend(_protocol_repository_topology_errors(
                predecessor_repository, predecessor_head, (),
                predecessor_sparse_profile,
                additional_object_custody=predecessor_historical_rows,
            ))
    protocol_repository = Path(decision["paths"]["protocol_repository_path"])
    current_protocol_state: dict[str, Any] = {
        "mode": "unavailable", "unexpected_paths": [],
    }
    protocol_preflight = _repository_git_preflight_errors(
        protocol_repository, protocol_sparse_profile,
    )
    errors.extend(f"terminal protocol: {item}" for item in protocol_preflight)
    if not protocol_preflight:
        current_protocol_state = _protocol_terminal_state(
            protocol_repository, run_dir,
            control_dir, custody["decision_commit"],
            protocol_sparse_profile, errors, protocol_historical_rows,
        )
        current_head_raw = _git_stdout(
            protocol_repository, ["rev-parse", "HEAD"],
            "terminal full protocol HEAD", errors,
        )
        if current_head_raw is not None:
            current_head = current_head_raw.rstrip(b"\n").decode("ascii", "replace")
            _exact(
                current_head, postrun_entry_head,
                "terminal protocol HEAD/post-run entry stability", errors,
            )
            errors.extend(_protocol_repository_topology_errors(
                protocol_repository, current_head, (run_dir, control_dir),
                protocol_sparse_profile,
            ))
    # Re-run output-state admission after every other process.  In committed
    # archive mode this is the terminal streaming read/self-hash of every
    # selected evidence blob, closing mutation of an object after an earlier
    # tree walk but before final custody.  No process or Git command follows.
    if not protocol_preflight:
        final_protocol_state = _protocol_output_state(
            protocol_repository, run_dir, control_dir,
            custody["decision_commit"], protocol_sparse_profile, errors,
            protocol_historical_rows,
        )
        _exact(
            final_protocol_state, current_protocol_state,
            "terminal protocol output-state stability", errors,
        )
        _exact(
            final_protocol_state, postrun_entry_protocol_state,
            "post-run entry/terminal protocol selected-policy payload custody",
            errors,
        )
        current_protocol_state = final_protocol_state
        final_protocol_preflight = _repository_git_preflight_errors(
            protocol_repository, protocol_sparse_profile,
        )
        errors.extend(
            f"terminal protocol after output stream: {item}"
            for item in final_protocol_preflight
        )
        try:
            _exact(
                _git_head_index_storage_identities(protocol_repository),
                postrun_protocol_git_storage,
                "terminal protocol Git storage identities", errors,
            )
            _exact(
                _git_head_commit_no_git(protocol_repository),
                postrun_entry_head,
                "terminal protocol no-Git HEAD", errors,
            )
        except (OSError, ValueError) as exc:
            errors.append(f"terminal protocol no-Git seal failed: {exc}")

    # No process or Git command follows this point.  Recheck every external
    # object snapshotted at post-run entry after Cargo/Role-1 replay and all
    # repository topology checks.
    errors.extend(_terminal_immutable_input_errors(
        decision,
        decision_identity=postrun_decision_identity,
        protected_identities=postrun_protected_identities,
        binary_identities=postrun_binary_identities,
        source_build_rows=recomputed_source_build_inputs,
        predecessor_identities=postrun_predecessor_identities,
        repository_identities=postrun_repository_identities,
    ))
    _exact(current_protocol_state.get("unexpected_paths"), [], "terminal protocol unexpected paths", errors)
    recorded_protocol_state = terminal_seal.get("protocol_terminal_state", {})
    _exact(
        recorded_protocol_state.get("runtime_mode"),
        "exact_untracked_output_trees",
        "terminal seal original runtime mode", errors,
    )
    _exact(recorded_protocol_state.get("unexpected_paths"), [], "recorded terminal protocol unexpected paths", errors)
    _exact(
        recorded_protocol_state.get("allowed_output_roots"),
        [
            run_dir.relative_to(Path(decision["paths"]["protocol_repository_path"])).as_posix(),
            control_dir.relative_to(Path(decision["paths"]["protocol_repository_path"])).as_posix(),
        ],
        "recorded terminal protocol allowed roots", errors,
    )
    # This is the final output-tree admission stage after every Git/Cargo/
    # historical-checker process.  It performs only nofollow filesystem reads
    # and binds both complete inventories, including terminal-custody.json
    # which is necessarily excluded from its own recorded pre-seal inventory.
    try:
        final_run_entries = _bounded_sorted_scandir(
            run_dir, PROTOCOL_TOPOLOGY_ENTRY_CAP,
            "terminal RUN_DIR no-process inventory",
        )
        final_control_entries = _bounded_sorted_scandir(
            control_dir, PROTOCOL_TOPOLOGY_ENTRY_CAP,
            "terminal CONTROL_DIR no-process inventory",
        )
        _exact(
            {entry.name for entry in final_run_entries}, expected_names,
            "terminal no-process RUN_DIR exact path set", errors,
        )
        _exact(
            {entry.name for entry in final_control_entries}, set(PRODUCER_PATHS),
            "terminal no-process CONTROL_DIR exact path set", errors,
        )
        final_run_inventory = [
            _file_identity(run_dir / relative, relative)
            for relative in sorted(expected_names)
        ]
        final_control_inventory = [
            _file_identity(control_dir / relative, relative)
            for relative in sorted(PRODUCER_PATHS)
        ]
        _exact(
            final_run_inventory, postrun_full_run_inventory,
            "terminal no-process RUN_DIR identities/bytes", errors,
        )
        _exact(
            final_control_inventory, postrun_full_control_inventory,
            "terminal no-process CONTROL_DIR identities/bytes", errors,
        )
        _exact(
            _directory_identity(run_dir), postrun_run_directory_identity,
            "terminal no-process RUN_DIR directory identity", errors,
        )
        _exact(
            _directory_identity(control_dir), postrun_control_directory_identity,
            "terminal no-process CONTROL_DIR directory identity", errors,
        )
    except (OSError, ValueError) as exc:
        errors.append(f"terminal no-process output custody failed: {exc}")
    expected_terminal_seal = {
        "schema": "p192-wcm-role2-terminal-custody-v1",
        "run_id": decision["run_id"],
        "decision_id": decision["decision_id"],
        "decision_commit": custody["decision_commit"],
        "decision_path_terminal": decision["paths"]["decision_json"],
        "decision_sha256_terminal": custody["decision_sha256"],
        "protocol_commit": decision["protocol_commit"],
        "protocol_head_at_runtime": custody["decision_commit"],
        "protocol_terminal_state": recorded_protocol_state,
        "manifest_sha256": sha256_path(run_dir / "manifest.yaml"),
        "raw_result_sha256": sha256_path(run_dir / "raw-result.json"),
        "receipt_sha256": sha256_path(run_dir / "independent-verifier-receipt.json"),
        "protected_protocol_blobs": decision["protected_protocol_blobs"],
        "binary_identities": binary_identities,
        "source_build_commits": role_commits,
        "source_build_tree_sha256": {
            role: _source_input_digest(recomputed_source_build_inputs[role])
            for role in ("producer", "verifier", "supervisor")
        },
        "verifier_build_custody": expected_build_custody,
        "predecessor_retained_fd_snapshots": predecessor_fd_snapshots,
        "run_directory_identity": _directory_identity(run_dir),
        "control_directory_identity": _directory_identity(control_dir),
        "run_inventory_before_terminal_seal": terminal_run_inventory,
        "control_inventory": control_producer_identities,
        "sealed_image_sha256": {
            image["role"]: image["memfd_sha256"] for image in sealed_images
        },
        "post_manifest_directory_fsync": True,
        "path_and_fd_rechecks_complete": True,
        "control_dir_retained": True,
        "inode_custody_scope": "original_supervised_workspace_only",
        "overall_status": "PASS",
    }
    _exact(terminal_seal, expected_terminal_seal, "post-manifest terminal custody seal", errors)
    return errors


def validate_post_run(
    run_dir: Path, decision: dict[str, Any], custody: dict[str, Any],
) -> list[str]:
    """Fail closed instead of propagating a raced or special-file read error."""
    try:
        return _validate_post_run_impl(run_dir, decision, custody)
    except (OSError, ValueError) as exc:
        return [f"post-run filesystem custody failure: {exc}"]


def collect_contract_errors(addendum_doc: Any, overlay: Any) -> list[str]:
    errors: list[str] = []
    addendum = addendum_doc.get("role2_box0_interface_addendum", {})
    _exact(addendum.get("schema"), "p192-wcm-role2-box0-interface-addendum-v1", "addendum schema", errors)
    _exact(addendum.get("interface_revision"), 4, "addendum interface revision", errors)
    _exact(addendum.get("supersedes_unexecuted_revision"), 3, "superseded addendum interface revision", errors)
    _require(
        isinstance(addendum.get("revision_note"), str)
        and "supersedes the unexecuted revision 3" in addendum["revision_note"],
        "addendum revision note does not identify the unexecuted superseded revision",
        errors,
    )
    _exact(addendum.get("execution_authorized"), False, "addendum authorization", errors)
    _exact(addendum.get("scientific_status"), "not_started", "scientific status", errors)
    _exact(addendum.get("result_status"), "no_result", "result status", errors)
    _exact(addendum.get("scientific_results"), [], "scientific results", errors)

    stage = addendum.get("stage_binding", {})
    _exact(stage.get("producer_argv_template"), PRODUCER_TEMPLATE, "producer argv", errors)
    _exact(stage.get("independent_verifier_argv_template"), VERIFIER_TEMPLATE, "verifier argv", errors)
    _exact(stage.get("checkpoint_fault_argv_template"), FAULT_TEMPLATE, "fault argv", errors)
    _exact(stage.get("checkpoint_resume_argv_template"), RESUME_TEMPLATE, "resume argv", errors)
    _exact(stage.get("supervisor_argv_template"), SUPERVISOR_TEMPLATE, "supervisor argv", errors)

    shell = addendum.get("shell_contract", {})
    total, primitive, duplicate = box0_counts()
    _exact((total, primitive, duplicate), (262148, 168990, 93158), "computed BOX-0 counts", errors)
    _exact((shell.get("candidate_count"), shell.get("primitive_count"), shell.get("duplicate_count")), (total, primitive, duplicate), "declared BOX-0 counts", errors)
    boundaries = [{"candidate_index": i, "v": v, "x": x} for i, v, x in box0_pairs() if i in {0, 32767, 32768, 65536, 229379, 262147}]
    _exact(shell.get("literal_boundary_records"), boundaries, "BOX-0 boundary records", errors)
    _exact(shell.get("shard_count"), 1, "BOX-0 shard count", errors)

    _exact(addendum.get("checkpoint_and_resume", {}).get("append_paths_in_order"), APPEND_PATHS, "append paths", errors)
    _exact(addendum.get("checkpoint_and_resume", {}).get("recognized_temporary_paths_in_order"), TEMPORARY_PATHS, "temporary paths", errors)
    _exact(
        addendum.get("protected_protocol_paths_in_order"),
        list(PROTECTED_PROTOCOL_RELATIVE_PATHS.values()),
        "protected protocol paths", errors,
    )
    _exact(addendum.get("producer_owned_paths_in_order"), PRODUCER_PATHS, "producer paths", errors)
    _exact(addendum.get("verifier_source_paths_in_order"), PRODUCER_PATHS, "verifier source paths", errors)
    _exact(addendum.get("supervisor_owned_paths_in_order"), SUPERVISOR_PATHS, "supervisor paths", errors)
    _exact(addendum.get("canonical_run_custody_paths_in_order"), CUSTODY_PATHS, "custody paths", errors)
    _exact(addendum.get("exact_role2_stage_paths_in_order"), STAGE_PATHS, "Role-2 stage paths", errors)
    _exact(addendum.get("canonical_v2_custody", {}).get("manifest_artifact_paths_in_order"), MANIFEST_ARTIFACT_PATHS, "manifest artifact paths", errors)
    _exact(addendum.get("producer_verification_checks_in_order"), PRODUCER_CHECKS, "producer checks", errors)
    _exact(addendum.get("independent_verifier_checks_in_order"), INDEPENDENT_CHECKS, "independent checks", errors)
    _exact(addendum.get("agreement_fields_in_order"), AGREEMENT_FIELDS, "agreement fields", errors)
    _exact(addendum.get("supervisor_child_receipts_in_order"), SUPERVISOR_CHILDREN, "supervisor children", errors)
    canonical_paths = addendum.get("canonical_path_contract", {})
    _exact(canonical_paths.get("run_dir"), "PROTOCOL_REPOSITORY_PATH/experiments/EXP-SCURVE-1a8daf/runs/RUN_ID", "canonical RUN_DIR contract", errors)
    _exact(canonical_paths.get("control_dir"), "PROTOCOL_REPOSITORY_PATH/experiments/EXP-SCURVE-1a8daf/controls/RUN_ID-restart", "canonical CONTROL_DIR contract", errors)
    _exact(canonical_paths.get("audit_file"), "RUN_DIR/dependency-audit.json", "canonical AUDIT_FILE contract", errors)
    linux_custody = addendum.get("linux_execution_custody", {})
    _exact(
        (linux_custody.get("platform"), linux_custody.get("host_trust_model"), linux_custody.get("workspace_custody")),
        ("linux", "trusted_local_host", "exclusive"), "Linux execution custody", errors,
    )
    _exact(addendum.get("terminal_admission_path"), TERMINAL_CUSTODY_PATH, "terminal admission path", errors)
    restart = addendum.get("checkpoint_restart_control", {})
    _exact(restart.get("injected_suffix_hex"), "503139322d57434d2d554e434f4d4d49545445442d5355464649582d763100", "restart suffix", errors)
    restart_text = " ".join(str(item) for item in restart.get("procedure", []))
    _require(
        "No supervised in-transaction cleanup is permitted" in restart_text,
        "restart contract does not forbid in-transaction CONTROL_DIR cleanup", errors,
    )
    if "source_identity_preservation" not in addendum.get("predecessor_binding", {}):
        errors.append("immutable producer/factor-base source identity preservation is missing")
    admission_text = " ".join(str(item) for item in addendum.get("admission_gates", []))
    if "Role-2 producer provenance, and Role-2 verifier provenance are separately hash-bound and may name distinct clean commits" in admission_text:
        errors.append("admission gate permits forbidden producer/factor-base commit separation")
    terminal = addendum.get("terminal_status_semantics", {})
    if "failure_precedence_and_reason" not in terminal:
        errors.append("deterministic terminal failure precedence is missing")
    supervisor_custody = addendum.get("supervisor_custody", {})
    _exact(
        supervisor_custody.get("launch_sequence"),
        SUPERVISOR_LAUNCH_SEQUENCE,
        "supervisor launch sequence",
        errors,
    )
    resource = addendum.get("resource_admission", {})
    terminalizable_mapping = resource.get("terminalizable_resource_failure_mapping")
    _require(
        isinstance(terminalizable_mapping, str)
        and "status INCOMPLETE" in terminalizable_mapping
        and "failure_reason incomplete_child_artifact" in terminalizable_mapping
        and "both directories remain retained" in terminalizable_mapping.lower()
        and "every frozen post-run size" in terminalizable_mapping
        and "checker-visible completed" in terminalizable_mapping
        and "required fsyncs" in terminalizable_mapping,
        "terminalizable post-directory resource failure mapping is not frozen",
        errors,
    )
    nonterminalizable_boundary = resource.get("nonterminalizable_resource_boundary")
    _require(
        isinstance(nonterminalizable_boundary, str)
        and "cannot be represented as a checker-valid terminal failure" in nonterminalizable_boundary
        and "retains both directories as-is" in nonterminalizable_boundary
        and "no in-transaction cleanup" in nonterminalizable_boundary
        and "no PASS terminal seal" in nonterminalizable_boundary
        and "hard resource-custody" in nonterminalizable_boundary
        and "operator remediation" in nonterminalizable_boundary
        and "asserts nothing mathematical" in nonterminalizable_boundary,
        "nonterminalizable resource boundary is not frozen",
        errors,
    )
    _require(
        "admitted_failure_mapping" not in resource,
        "obsolete unconditional admitted resource-failure mapping remains present",
        errors,
    )
    paired_setup = resource.get("paired_directory_setup_boundary")
    _require(
        isinstance(paired_setup, str)
        and "pre-evidence setup operation" in paired_setup
        and "freshly-created empty half-directory" in paired_setup
        and "reverse creation order" in paired_setup
        and "fsyncs each affected parent" in paired_setup
        and "hard custody violation requiring operator remediation" in paired_setup
        and "never a schema failure record" in paired_setup
        and "no raw result or PASS claim" in paired_setup,
        "half-directory pre-evidence rollback/refusal boundary is not frozen",
        errors,
    )

    _exact(overlay.get("interface_revision"), 4, "overlay interface revision", errors)
    _exact(overlay.get("supersedes_unexecuted_revision"), 3, "superseded overlay interface revision", errors)
    _require(
        isinstance(overlay.get("revision_note"), str)
        and "supersedes the unexecuted revision 3" in overlay["revision_note"],
        "overlay revision note does not identify the unexecuted superseded revision",
        errors,
    )
    _exact(overlay.get("execution_authorized"), False, "overlay authorization", errors)
    _exact(overlay.get("scientific_results"), [], "overlay scientific results", errors)
    _exact(overlay.get("producer_argv_template"), PRODUCER_TEMPLATE, "overlay producer argv", errors)
    _exact(overlay.get("independent_verifier_argv_template"), VERIFIER_TEMPLATE, "overlay verifier argv", errors)
    _exact(overlay.get("checkpoint_fault_argv_template"), FAULT_TEMPLATE, "overlay fault argv", errors)
    _exact(overlay.get("checkpoint_resume_argv_template"), RESUME_TEMPLATE, "overlay resume argv", errors)
    _exact(overlay.get("supervisor_argv_template"), SUPERVISOR_TEMPLATE, "overlay supervisor argv", errors)
    overlay_resource_boundary = overlay.get("resource_failure_boundary")
    _require(
        isinstance(overlay_resource_boundary, str)
        and "schema-valid INCOMPLETE" in overlay_resource_boundary
        and "hard resource custody" in overlay_resource_boundary
        and "retain both directories" in overlay_resource_boundary
        and "no PASS terminal seal or scientific result" in overlay_resource_boundary,
        "overlay resource failure boundary is not frozen",
        errors,
    )
    _exact(overlay.get("base_required_outputs"), BASE_REQUIRED_OUTPUTS, "overlay base outputs", errors)
    _exact(overlay.get("addendum_required_children"), ADDENDUM_CHILDREN, "overlay addendum outputs", errors)
    _exact(overlay.get("canonical_v2_custody_outputs"), CUSTODY_PATHS, "overlay custody paths", errors)
    return errors


def check_sums() -> list[str]:
    if not SUMS.exists():
        return ["SHA256SUMS is missing"]
    entries: dict[str, str] = {}
    errors: list[str] = []
    try:
        sums_text = _read_regular_file_bytes(
            SUMS, "SHA256SUMS", byte_cap=16777216,
        ).decode("ascii")
    except (OSError, ValueError, UnicodeDecodeError) as exc:
        return [f"SHA256SUMS cannot be read safely: {exc}"]
    for line in sums_text.splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match:
            errors.append("malformed SHA256SUMS line")
            continue
        digest, relative = match.groups()
        if relative in entries:
            errors.append(f"duplicate SHA256SUMS entry: {relative}")
        entries[relative] = digest
    _exact(list(entries), list(PAYLOAD_PATHS), "SHA256SUMS path order", errors)
    for relative in PAYLOAD_PATHS:
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing payload: {relative}")
        elif entries.get(relative) != sha256_path(path):
            errors.append(f"SHA256 mismatch: {relative}")
    return errors


def check_package() -> list[str]:
    errors: list[str] = []
    for relative, expected in IMMUTABLE.items():
        path = ROOT / relative
        if not path.is_file() or sha256_path(path) != expected:
            errors.append(f"immutable base hash mismatch: {relative}")
    addendum = load_yaml(ADDENDUM)
    overlay = load_yaml(OVERLAY)
    errors.extend(collect_contract_errors(addendum, overlay))
    for path in (ARTIFACT_SCHEMA, DECISION_SCHEMA):
        try:
            _schema_validator(load_json(path))
        except Exception as exc:  # jsonschema reports precise context.
            errors.append(f"invalid schema {path.name}: {exc}")
    errors.extend(check_sums())
    return errors


def _write_exclusive_receipt(path: Path, value: dict[str, Any]) -> None:
    """Create one canonical retained receipt without following any link."""
    parent = path.parent
    if not parent.exists():
        if _symlink_component(parent.parent) is not None:
            raise ValueError("receipt staging parent has a symlink component")
        parent.mkdir(mode=0o700)
    if _symlink_component(parent) is not None:
        raise ValueError("receipt staging directory has a symlink component")
    parent_metadata = os.lstat(parent)
    if (
        not stat.S_ISDIR(parent_metadata.st_mode)
        or stat.S_ISLNK(parent_metadata.st_mode)
        or parent_metadata.st_uid != os.geteuid()
        or stat.S_IMODE(parent_metadata.st_mode) != 0o700
    ):
        raise ValueError(
            "receipt staging directory must be a current-user-owned 0700 "
            "nofollow directory"
        )
    parent_identity = _directory_identity(parent)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o600)
    raw = canonical_json_bytes(value)
    try:
        offset = 0
        while offset < len(raw):
            offset += os.write(descriptor, raw[offset:])
        os.fsync(descriptor)
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1:
            raise ValueError("created custody receipt is not a single-link regular file")
    finally:
        os.close(descriptor)
    parent_descriptor = os.open(
        parent, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW,
    )
    try:
        os.fsync(parent_descriptor)
    finally:
        os.close(parent_descriptor)
    if _directory_identity(parent) != parent_identity:
        raise ValueError("receipt staging directory identity changed")
    if _read_regular_file_bytes(
        path, "created custody receipt", byte_cap=16777216,
    ) != raw:
        raise ValueError("created custody receipt bytes changed after fsync")


def _emit_role1_repository_custody(
    phase: str, repository: Path, decision_path: Path, run_id: str,
    output: Path,
) -> list[str]:
    """Decision-independent D1/A1 custody receipt command."""
    errors: list[str] = []
    repository = repository.absolute()
    decision_path = decision_path.absolute()
    output = output.absolute()
    _require(
        _symlink_component(repository) is None,
        "custody repository has a symlink component", errors,
    )
    try:
        decision_relative = decision_path.relative_to(repository).as_posix()
    except ValueError:
        return ["custody Role-1 decision is outside repository"]
    if (
        Path(decision_relative).parent != DECISION_RELATIVE_DIRECTORY
        or re.fullmatch(r"DEC-[0-9]{8}-[0-9a-f]{6}\.yaml",
                        Path(decision_relative).name) is None
    ):
        errors.append("custody Role-1 decision path is not canonical")
    if phase == "pre_role1_execution":
        profile = _role1_pre_execution_profile(decision_relative, run_id)
        expected_output = _role1_pre_execution_retained_path(repository, run_id)
    elif phase == "terminal_role1_archive":
        profile = _role1_terminal_archive_profile(decision_relative, run_id)
        expected_output = _role1_terminal_retained_path(repository, run_id)
    else:
        return ["custody phase is invalid"]
    _exact(output, expected_output, "canonical custody receipt output path", errors)
    _require(
        repository != output and repository not in output.parents,
        "custody retained receipt must be outside its repository", errors,
    )
    _require(
        not os.path.lexists(output),
        "custody retained receipt output already exists", errors,
    )
    if errors:
        return errors
    preflight = _repository_git_preflight_errors(repository, profile)
    errors.extend(preflight)
    if preflight:
        return errors
    head_raw = _git_stdout(
        repository, ["rev-parse", "HEAD"], "custody repository HEAD", errors,
    )
    if head_raw is None:
        return errors
    head = head_raw.rstrip(b"\n").decode("ascii", "replace")
    receipt = _sealed_repository_custody_receipt(
        repository, head, profile, phase, errors,
    )
    if receipt is None or errors:
        return errors
    invoked_checker = Path(__file__).absolute()
    admitted_checker = repository / PROTECTED_PROTOCOL_RELATIVE_PATHS[
        "check_role2_box0_interface.py"
    ]
    _exact(
        invoked_checker, admitted_checker,
        "custody emitter executing-checker path", errors,
    )
    _require(
        _symlink_component(invoked_checker) is None,
        "custody emitter executing checker has a symlink component", errors,
    )
    try:
        invoked_identity = _file_identity(invoked_checker)
    except (OSError, ValueError) as exc:
        errors.append(f"custody emitter executing checker identity unavailable: {exc}")
    else:
        selected_checker = next(
            (
                row for row in receipt["selected_worktree_identities"]
                if row.get("path") == PROTECTED_PROTOCOL_RELATIVE_PATHS[
                    "check_role2_box0_interface.py"
                ]
            ),
            None,
        )
        if selected_checker is None:
            errors.append("custody emitter admitted checker identity is absent")
        else:
            expected_invoked = {**selected_checker, "path": str(invoked_checker)}
            _exact(
                invoked_identity, expected_invoked,
                "custody emitter executing/admitted checker identity", errors,
            )
        _exact(
            invoked_identity.get("sha256"), receipt["custody_checker_sha256"],
            "custody emitter executing/admitted checker bytes", errors,
        )
    if errors:
        return errors
    try:
        _write_exclusive_receipt(output, receipt)
    except (OSError, ValueError) as exc:
        errors.append(f"custody receipt creation failed: {exc}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--decision", type=Path, help="exact committed Role-2 Coordinator decision")
    phase = parser.add_mutually_exclusive_group()
    phase.add_argument("--pre-dispatch", action="store_true", help="validate decision and require fresh output paths")
    phase.add_argument("--post-run", action="store_true", help="validate decision plus a completed run directory")
    parser.add_argument("--run-dir", type=Path, help="exact completed run directory for --post-run")
    parser.add_argument(
        "--emit-role1-repository-custody",
        choices=("pre_role1_execution", "terminal_role1_archive"),
        help="emit one decision-independent sealed D1/A1 custody receipt",
    )
    parser.add_argument("--custody-repository", type=Path)
    parser.add_argument("--custody-role1-decision", type=Path)
    parser.add_argument("--custody-predecessor-run-id")
    parser.add_argument("--custody-output", type=Path)
    args = parser.parse_args(argv)
    custody_arguments = (
        args.custody_repository, args.custody_role1_decision,
        args.custody_predecessor_run_id, args.custody_output,
    )
    if args.emit_role1_repository_custody is not None:
        if args.decision is not None or args.pre_dispatch or args.post_run or args.run_dir:
            parser.error("custody emission is exclusive with Role-2 decision validation")
        if any(item is None for item in custody_arguments):
            parser.error("custody emission requires repository, Role-1 decision, run id, and output")
        errors = _emit_role1_repository_custody(
            args.emit_role1_repository_custody,
            args.custody_repository, args.custody_role1_decision,
            args.custody_predecessor_run_id, args.custody_output,
        )
        if errors:
            for error in errors:
                print(f"FAIL: {error}", file=sys.stderr)
            return 1
        print("PASS: sealed Role-1 repository custody receipt created")
        return 0
    if any(item is not None for item in custody_arguments):
        parser.error("custody arguments require --emit-role1-repository-custody")
    if args.decision is None and (args.pre_dispatch or args.post_run or args.run_dir is not None):
        parser.error("phase and --run-dir require --decision")
    if args.decision is not None and not (args.pre_dispatch or args.post_run):
        parser.error("--decision requires exactly one of --pre-dispatch or --post-run")
    if args.post_run and args.run_dir is None:
        parser.error("--post-run requires --run-dir")
    if not args.post_run and args.run_dir is not None:
        parser.error("--run-dir is accepted only with --post-run")
    errors = check_package()
    if args.decision:
        decision, custody, decision_errors = validate_dispatch_decision(
            args.decision, "post-run" if args.post_run else "pre-dispatch", args.run_dir,
        )
        errors.extend(decision_errors)
        if args.post_run and decision is not None and custody is not None and not decision_errors:
            errors.extend(validate_post_run(args.run_dir, decision, custody))
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    if args.pre_dispatch:
        print("PASS: committed Role-2 decision and fresh dispatch custody are closed")
    elif args.post_run:
        print("PASS: Role-2 post-run bytes and cross-document custody are closed")
    else:
        print("PASS: Role-2 BOX-0 interface is closed and execution_authorized=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
