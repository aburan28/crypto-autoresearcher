"""Isolated source-v4 entry; only parent-admitted benign fixtures run here.

Scientific forwarding requires a separate published activation and accepted
source/semantic reviews. This engineering version issues no scientific token.
"""
from __future__ import annotations
import argparse
import importlib.util
from pathlib import Path
import sys

EXPERIMENT_ID = 'EXP-ECDLP-abf981'



def _scientific_activation_required(_capability):
    # This version never issues such a capability. A future source/semantic
    # review and published activation amendment must define its verifier.
    # Caller dictionaries, booleans and arbitrary callables cannot pass.
    raise PermissionError("separate published scientific activation and accepted semantic/source reviews required")


def prospective_scientific_forward(capability, configuration, directory):
    """Frozen future call sequence; unreachable under this engineering version."""
    context = _scientific_activation_required(capability)
    root = Path(__file__).absolute().parents[3]
    kernel_path = root / "experiments/EXP-ECDLP-abf981/source/run_model_comparison.py"
    spec = importlib.util.spec_from_file_location("finite_yaml_v4_models_kernel", kernel_path)
    kernel = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kernel)
    frozen = kernel.read_frozen_spec(str(root / "experiments/EXP-ECDLP-abf981/specification.yaml"))
    payload = {"manifest_context": context}
    try:
        kernel.finite_payload(frozen, configuration["cell"], payload)
    finally:
        # Partial payload and exact kernel status/scoring_status survive failure.
        # No caller-owned boolean or process exit code replaces scientific gates.
        kernel.scientific_artifact_data(payload)
        kernel.emit_scientific_artifacts(str(directory), payload)
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--launch-context-fd", type=int, required=True)
    args = parser.parse_args()
    root = Path(__file__).absolute().parents[3]
    path = root / "harness/finite_yaml_locked_v3.py"
    spec = importlib.util.spec_from_file_location("_finite_yaml_locked_v3", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.child_entry(EXPERIMENT_ID, ["--launch-context-fd", str(args.launch_context_fd)])


if __name__ == "__main__":
    raise SystemExit(main())
