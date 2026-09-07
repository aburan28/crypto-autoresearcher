"""Stage 0: freeze inputs, run the static leak audit, and run the
planted-leak diagnostic. Must pass (audit rejects the planted leak) before
any cell is trusted."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import leak_audit

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    audit = leak_audit.audit_all(here)
    diagnostic = leak_audit.run_planted_leak_diagnostic()
    out = {"leak_audit": audit, "planted_leak_diagnostic": diagnostic}
    print(json.dumps(out, indent=2))
    assert audit["overall_verdict"] == "pass", "real feature/model modules must pass the static audit"
    assert diagnostic["audit_correctly_rejected_planted_leak"], "audit failed to reject planted leak -- BLOCKING"
    with open(sys.argv[1] if len(sys.argv) > 1 else "/tmp/stage0_out.json", "w") as f:
        json.dump(out, f, indent=2)
