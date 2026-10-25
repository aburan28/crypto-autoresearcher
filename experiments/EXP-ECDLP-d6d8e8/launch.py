"""Admitted finite paired Prym rank census; no direct unapproved launch path."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'research/prym_rank_census_20261025'))
from rank_census import run
from runtime_census import main

if __name__ == '__main__':
    raise SystemExit(main('EXP-ECDLP-d6d8e8', run))
