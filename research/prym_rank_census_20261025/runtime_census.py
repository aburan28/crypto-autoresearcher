"""New census renderer binding; preserves the previously frozen v2 runtime."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'research/prym_experiment_design_20261019/implementation'))
import native_runtime_v2 as native
from renderer import render


def main(experiment, runner):
    native.render = render
    return native.main(experiment, runner)
