#!/usr/bin/env bash
set -euo pipefail
python -m polynomial_ml run --profile quick --seed 20260904 --fit-seed 0 --output /app/output/run
