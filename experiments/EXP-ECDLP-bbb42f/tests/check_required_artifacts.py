import yaml
import os

BASE = "/Volumes/SSD990/crypto-autoresearcher"

spec = yaml.safe_load(open(os.path.join(BASE, "experiments/EXP-ECDLP-bbb42f/specification.yaml")))
required = spec["experiment"]["required_artifacts"]

missing = []
for path in required:
    full = os.path.join(BASE, path)
    exists = os.path.exists(full)
    print(f"{'OK ' if exists else 'MISS'} {path}")
    if not exists:
        missing.append(path)

print()
print("missing:", missing)

# also validate execution_report.yaml and implementation.md parse/exist
er_path = os.path.join(BASE, "experiments/EXP-ECDLP-bbb42f/execution_report.yaml")
with open(er_path) as f:
    er = yaml.safe_load(f)
print("execution_report.yaml parses OK, top-level keys:", list(er["execution_report"].keys()))

impl_path = os.path.join(BASE, "experiments/EXP-ECDLP-bbb42f/implementation.md")
print("implementation.md exists:", os.path.exists(impl_path))
