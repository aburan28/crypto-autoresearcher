"""Isolated source-v4 entry; only parent-admitted benign fixtures run here.

Scientific forwarding requires a separate published activation and accepted
source/semantic reviews. This engineering version issues no scientific token.
"""
from __future__ import annotations
import argparse
import importlib.util
from pathlib import Path
import sys

EXPERIMENT_ID = 'EXP-ECDLP-2cb7f8'



def _scientific_activation_required(_capability):
    # This version never issues such a capability. A future source/semantic
    # review and published activation amendment must define its verifier.
    # Caller dictionaries, booleans and arbitrary callables cannot pass.
    raise PermissionError("separate published scientific activation and accepted semantic/source reviews required")


def prospective_scientific_forward(capability, configuration, directory):
    """Frozen future call sequence; unreachable under this engineering version."""
    context = _scientific_activation_required(capability)
    root = Path(__file__).absolute().parents[3]
    # Exact six-field config admission must precede the fixed kernel import.
    adapter_path = root / "harness/finite_yaml_locked_v3.py"
    adapter_spec = importlib.util.spec_from_file_location("finite_yaml_v4_incidence_admission", adapter_path)
    adapter = importlib.util.module_from_spec(adapter_spec)
    sys.modules[adapter_spec.name] = adapter
    adapter_spec.loader.exec_module(adapter)
    adapter.check_configuration(EXPERIMENT_ID, configuration["run_id"], configuration)
    adapter.validate_recovery_case_arms(adapter.RECOVERY_CASES, adapter.RECOVERY_CASES)
    gates = ("canonical_lock_verified", "scientific_authority_verified", "claim_verified",
             "source_snapshot_verified", "semantic_gate_verified", "memory_limit_enforced")
    if any(context.get(gate) is not True for gate in gates):
        raise PermissionError("all six independent scientific gates required")
    source_dir = root / "experiments/EXP-ECDLP-2cb7f8/source"
    sys.path.insert(0, str(source_dir))
    kernel_spec = importlib.util.spec_from_file_location("finite_yaml_v4_incidence_kernel", source_dir / "run.py")
    kernel = importlib.util.module_from_spec(kernel_spec)
    kernel_spec.loader.exec_module(kernel)
    result = kernel.run_case(configuration, directory, context)
    # Preserve instrument_valid, comparison_eligible, controls_passed and anomalies
    # verbatim; comparison eligibility does not follow from a process exit code.
    return result


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
