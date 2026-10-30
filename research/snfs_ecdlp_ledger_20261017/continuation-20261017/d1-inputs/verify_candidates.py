"""Refusal controls for the source parser; original source bytes stay untouched."""
from pathlib import Path
import hashlib
import json
import re
import tempfile
from prepare_candidates import parse


folder = Path(__file__).resolve().parent
source = folder / "rank-30-source.html"
original = source.read_bytes()
text = original.decode()
point = re.search(r"P<sub>1</sub>\s*=\s*\[\s*(-?\d+)", text)
if point is None:
    raise ValueError("Expected literal first source point")
perturbed = text[:point.start(1)] + str(int(point[1])+1) + text[point.end(1):]
controls = {}
with tempfile.TemporaryDirectory(prefix="snfs-d1-parser-") as scratch:
    path = Path(scratch) / "fixture.html"
    path.write_text(perturbed)
    try:
        parse(path, 30)
    except ValueError as exc:
        controls["perturbed_coordinate"] = str(exc)
    path.write_text(text.replace("P<sub>30</sub>", "P<sub>29</sub>"))
    try:
        parse(path, 30)
    except ValueError as exc:
        controls["duplicate_index"] = str(exc)
assert set(controls) == {"perturbed_coordinate", "duplicate_index"}
assert source.read_bytes() == original
result = dict(scope="Software ingestion refusal controls, not rank validation",
              controls=controls, both_refused=True,
              original_source_sha256=hashlib.sha256(original).hexdigest(),
              original_unchanged=True)
with (folder / "parser-refusal-controls.json").open("x") as handle:
    json.dump(result,handle,indent=2);handle.write("\n")
print(json.dumps(result,indent=2))
