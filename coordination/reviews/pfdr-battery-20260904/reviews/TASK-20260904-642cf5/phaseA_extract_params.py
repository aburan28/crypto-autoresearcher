#!/usr/bin/env python3
"""PHASE A helper. Loads each EXP-PFDR-5726af run manifest with a YAML loader and
prints ONLY run.inputs.parameters. Nothing else from the manifest is printed or
returned, so the phase-A read set stays within the review plan's allowance."""
import sys, glob, os
import yaml

base = "/home/user/crypto-autoresearcher/experiments/EXP-PFDR-5726af/runs"
want = sys.argv[1:] or ["*"]
for pat in want:
    for d in sorted(glob.glob(os.path.join(base, "RUN-PFDR-5726af-" + pat))):
        mf = os.path.join(d, "manifest.yaml")
        with open(mf) as fh:
            doc = yaml.safe_load(fh)
        params = doc.get("run", {}).get("inputs", {}).get("parameters")
        print("### %s :: run.inputs.parameters" % os.path.basename(d))
        print(yaml.safe_dump(params, sort_keys=False, default_flow_style=False))
        del doc
