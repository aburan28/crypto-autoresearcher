"""Independent complete branch replay and finite matrix certificate checker."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'research/prym_rank_census_20261025'))
from check_census import main

if __name__ == '__main__':
    raise SystemExit(main())
