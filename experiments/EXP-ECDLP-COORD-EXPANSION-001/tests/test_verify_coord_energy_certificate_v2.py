import copy
import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PRODUCER = load(
    "coord_energy_certificate_v2_verifier_test_producer",
    ROOT / "src" / "coord_energy_certificate_v2.py",
)
VERIFIER = load(
    "coord_energy_certificate_v2_verifier_test",
    ROOT / "src" / "verify_coord_energy_certificate_v2.py",
)


def development_packet():
    return PRODUCER.run([8, 9, 10], [23], 3, 3, True)


def test_independent_development_packet_replays():
    raw = development_packet()
    receipt, projection = VERIFIER.verify(raw, allow_development=True)
    assert receipt["valid"]
    assert receipt["independent_d4_method"] == "direct_ordered_four_loop"
    assert receipt["null_sets_reconstructed"] == 9
    mutations = VERIFIER.mutation_results(raw, projection)
    assert len(mutations) == 14
    assert all(mutations.values())


def test_positive_telemetry_change_breaks_digest():
    raw = development_packet()
    changed = copy.deepcopy(raw)
    changed["peak_rss_bytes"] += 1
    assert changed["telemetry_digest"] != VERIFIER.digest(
        {
            "peak_rss_bytes": changed["peak_rss_bytes"],
            "started_unix_seconds": changed["started_unix_seconds"],
            "finished_unix_seconds": changed["finished_unix_seconds"],
            "total_wall_seconds": changed["total_wall_seconds"],
        }
    )
