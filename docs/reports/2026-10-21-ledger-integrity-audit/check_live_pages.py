"""Read public Pages metadata and the repository workflow state, without writes."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parent
REPO = "aburan28/crypto-autoresearcher"
META_URL = "https://aburan28.github.io/crypto-autoresearcher/data/meta.json"


def output(*command: str) -> bytes:
    return subprocess.run(command, check=True, capture_output=True).stdout


def main() -> None:
    workflow = json.loads(output("gh", "api", f"repos/{REPO}/actions/workflows/pages.yml"))
    meta_bytes = output("curl", "--fail", "--location", "--silent", "--show-error",
                        "--max-time", "20", META_URL)
    live = json.loads(meta_bytes)
    local = json.loads((ROOT / "evidence/site-build-report.json").read_text())
    print(json.dumps({
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "workflow_state": workflow["state"],
        "workflow_path": workflow["path"],
        "live_meta_url": META_URL,
        "live_meta_sha256": hashlib.sha256(meta_bytes).hexdigest(),
        "live_commit": live["commit"],
        "live_built_at": live.get("built_at"),
        "local_validated_commit": local["commit"],
        "live_differs_from_local_validated": live["commit"] != local["commit"],
        "limit": "read-only state check; does not authorize or perform deployment",
    }, indent=2))


if __name__ == "__main__":
    main()
