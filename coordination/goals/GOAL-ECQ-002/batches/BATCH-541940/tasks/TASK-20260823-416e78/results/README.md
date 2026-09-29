# results/ — deduplicated

Every file that sat here was BYTE-IDENTICAL to the `raw-result.json` of one run record
(verified by sha256 for all ten). Keeping both doubled the task package to 402 MB for no
information gain.

**Four of the ten were ALREADY COMMITTED** by the orchestrating session's in-flight commits
(`1e429e1b4`, `5b2168aad`, `93ad5e7bc`, `61a428da9`): `certified_candidates.json`,
`selftest_construction.json`, `tuple_envelope_scan_admissible.json` and
`tuple_envelope_scan_raw.json`. Those are RESTORED and left in place — deleting an already
committed artifact removes nothing from the repository (the blobs are in history for good) and
only creates an audit question. **The six never-committed duplicates were removed**; the run
records, which are the canonical immutable evidence, keep the only copy of each.

| results file | canonical copy | sha256 |
| --- | --- | --- |
| `certified_candidates.json` | `runs/RUN-ECQTUP-416e78-004/raw-result.json` | `04bd3e293bf7e48891c82f59566dcad3568f0ec6254fa81f82ffd6ea44e528a0` |
| `null_ladder.json` | `runs/RUN-ECQTUP-416e78-007/raw-result.json` | `b9af4511b3ba6b7d5af51f70795a2f923d6df1ccafe73f90fad97b7773fd635e` |
| `rank_search.json` | `runs/RUN-ECQTUP-416e78-005/raw-result.json` | `b1ce101038fc38ea928146e8dc3d4961ba01a6e7bdc2576728ae13b9bced8c72` |
| `rank_search_ceiling12.json` | `runs/RUN-ECQTUP-416e78-006/raw-result.json` | `a4918454b3b239142813c695a568756f897ac810ca8796ebce76e27187744a04` |
| `rank_search_largespread.json` | `runs/RUN-ECQTUP-416e78-011/raw-result.json` | `899008fa09985e7c536ef2bae9fe4ccb9560481ade66d3024a7a915c640177ec` |
| `selftest_construction.json` | `runs/RUN-ECQTUP-416e78-001/raw-result.json` | `61ec84ba21b24b64e3de499bb7344e06883e43722fd9682bfe6681bec919b57f` |
| `tuple_envelope_scan_admissible.json` | `runs/RUN-ECQTUP-416e78-003/raw-result.json` | `bdf48bee3f4528e47a7338055429106414a4377828b7f8b317b5a220ec3a4cad` |
| `tuple_envelope_scan_largespread.json` | `runs/RUN-ECQTUP-416e78-008/raw-result.json` | `95cdd8bbd95be6267d9117657da9103659bd7c94ab2f2fcab5359740339af04b` |
| `tuple_envelope_scan_raw.json` | `runs/RUN-ECQTUP-416e78-002/raw-result.json` | `4eaaf9041c43b32add78c2b5332669ce483f6196faef4965d69a4a1c6e63bda9` |
| `tuple_envelope_scan_spread57_74.json` | `runs/RUN-ECQTUP-416e78-010/raw-result.json` | `c0813246715f43f6e1ad5c6be29a4aa327d7121d5566ca4f3fe8967cb4b982ac` |

Restore before re-running `scripts/build_deliverables.py ..`:

```sh
cd <this directory>
cp ../runs/RUN-ECQTUP-416e78-004/raw-result.json certified_candidates.json
cp ../runs/RUN-ECQTUP-416e78-007/raw-result.json null_ladder.json
cp ../runs/RUN-ECQTUP-416e78-005/raw-result.json rank_search.json
cp ../runs/RUN-ECQTUP-416e78-006/raw-result.json rank_search_ceiling12.json
cp ../runs/RUN-ECQTUP-416e78-011/raw-result.json rank_search_largespread.json
cp ../runs/RUN-ECQTUP-416e78-001/raw-result.json selftest_construction.json
cp ../runs/RUN-ECQTUP-416e78-003/raw-result.json tuple_envelope_scan_admissible.json
cp ../runs/RUN-ECQTUP-416e78-008/raw-result.json tuple_envelope_scan_largespread.json
cp ../runs/RUN-ECQTUP-416e78-002/raw-result.json tuple_envelope_scan_raw.json
cp ../runs/RUN-ECQTUP-416e78-010/raw-result.json tuple_envelope_scan_spread57_74.json
```

