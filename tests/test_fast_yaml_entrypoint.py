"""Direct tools load the orchestration code from their own checkout."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]


def test_fast_yaml_ignores_shadow_installed_package():
    with tempfile.TemporaryDirectory() as tmp:
        shadow = Path(tmp) / "shadow"
        package = shadow / "orchestration"
        package.mkdir(parents=True)
        (package / "__init__.py").write_text("\n")
        script = (
            "import sys; "
            f"sys.path.insert(0, {str(ROOT / 'tools')!r}); "
            "import fast_yaml; import orchestration.fast_yaml; "
            "print(orchestration.fast_yaml.__file__)"
        )
        env = os.environ.copy()
        env["PYTHONPATH"] = str(shadow)
        result = subprocess.run(
            [sys.executable, "-c", script], cwd=tmp, env=env,
            capture_output=True, text=True, check=True,
        )
        assert Path(result.stdout.strip()).resolve() == (
            ROOT / "orchestration" / "fast_yaml.py").resolve()
