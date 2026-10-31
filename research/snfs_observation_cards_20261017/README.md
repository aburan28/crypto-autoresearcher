# Observation cards for the SNFS leads

[Data and next checks](REPORT.md) · [Three-page PDF](report.pdf) · [Derived observations](observations.json)

The cards highlight a rotation-density pattern, an E3 solver degree-step pattern, and repeated field-lift inputs. The owner makes interpretation and relevance calls. Each card includes actual values, source scope, reference/control details, limitations and a proposed next measurement. Ordinary/control values accompany the flagged patterns.

`analyze_archived.py` reads four existing saved JSON files, computes descriptive tables and joins, and calculates an exact binary-word count. It does not rerun a curve or solver program. `observations.json` pins those inputs and the analysis source. `source-provenance.json` additionally pins inspected producer code and the original G3/G4 run statuses. Historical raw output and original manifests/receipts stay unchanged.

The CSV files retain density counts and all 18 historical E3 target joins. `field-lift-repeat-groups.json` retains all 169 repeated seed-inclusive key groups with zero-based raw row indices. `binary-count-checks.json` retains all 27 small direct enumeration checks of the exact combinatorial reference. `verification.json` records mechanical rechecks of the tables; it is not independent scientific review.

Initial generation from the repository root:

```sh
python3 research/snfs_observation_cards_20261017/analyze_archived.py
python3 research/snfs_observation_cards_20261017/verify_saved_summaries.py
PYTHONPATH=/workspace/snfs-toolchains/report:/workspace/snfs-ecdlp-experiments/vendor \
MPLCONFIGDIR=/tmp/snfs-observation-mpl \
XDG_CACHE_HOME=/workspace/snfs-toolchains/cache \
python3 research/snfs_observation_cards_20261017/render_cards.py
```

Data writers create new files exclusively. To recheck the published tables, give the verifier a fresh `--receipt /tmp/<new-name>.json`. To reproduce the numerical analysis into fresh scratch output without rewriting this record:

```python
import importlib.util
from pathlib import Path
import tempfile

source = Path("research/snfs_observation_cards_20261017/analyze_archived.py")
spec = importlib.util.spec_from_file_location("observation_replay", source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.OUT = Path(tempfile.mkdtemp(prefix="snfs-observation-replay-"))
module.main()
print(module.OUT)
```

The replay's checkout-commit metadata identifies the replay's actual revision; numeric tables have the same inputs and definitions. Render only in a fresh copy of the report directory. All three PDF pages were visually inspected. No official scientific status or canonical graph is changed.
