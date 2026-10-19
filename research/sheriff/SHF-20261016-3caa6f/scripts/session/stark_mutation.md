Build and run the B2 mutation controls (sibling checkout layout):

    cd scripts/stark-mutation && cargo run --release   # output: ../../checks/stark-mutation.jsonl

The exit code is the number of mutants the verifiers accepted (4 of 4 here).
