# research CLI

Native Rust executable wrapping the existing, authoritative orchestration CLI.

## Build and install

```sh
pip install -e .
cargo install --path cli/research --locked
research batch plan --delivery auto --deadline-seconds 86400
research batch status --all
research campaign autopilot --preset anthropic-batch --once
```

The binary is a native executable, but the orchestration engine still requires Python and the repository's dependencies. Set `AUTORESEARCH_PYTHON` to select a Python environment. Run from the repository checkout, or a directory where the repository's editable package is installed.

This initial frontend does not yet implement `research batch costs`, `research budget`, or `research run --batch`; those require corresponding backend features. No inference calls are made by installing or compiling.
