"""Minimal scaffold procedure driver for path-justified F_* ⊆ F probes.

Operationalizes recovery_spec common event F on the BATCH-022 no-crypto
scaffold:

  F = { the procedure fails to return a k' with Verify(x,k')=true
        within its declared stopping policy }

Success requires a true Verify result. Named F_* exits that halt without
Verify=true are classified as constituents of common F.

Explicit non-claims:
- No cryptographic Verify body; uses scaffold token Verify only.
- Declared stopping policy is symbolic (no τ / no QM-STOPPING clearance).
- No probability bounds or CollimationSieve API invention.
- Report-only / incomplete-simulator events are handled separately (F_sim).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .scaffold_import import import_scaffold_modules


# Symbolic stopping policy declaration for the scaffold procedure.
# invents_tau must remain False; this is not a Verify-relative τ law.
SYMBOLIC_STOPPING_POLICY = {
    "kind": "scaffold_symbolic_halt",
    "rule": "halt_without_verify_true_is_common_F",
    "invents_tau": False,
    "joint_QSPC_finite": False,
    "note": (
        "Symbolic halt predicate only. Does not supply history-uniform "
        "progress, Verify-relative τ, or jointly finite ΣQ/ΣS/ΣP/ΣC(+H)."
    ),
}


@dataclass
class ProcedureOutcome:
    """Terminal outcome of one scaffold procedure run."""

    exit_kind: str  # "success" | "failure"
    channel: Optional[str]  # F_* name on failure; None on success
    classified_as_common_F: bool
    verify_true_returned: bool
    k_prime_token: Optional[str] = None
    stopping_policy: Dict[str, Any] = field(default_factory=dict)
    events: List[Dict[str, Any]] = field(default_factory=list)
    failures_recorded: List[str] = field(default_factory=list)
    notes: Dict[str, Any] = field(default_factory=dict)


def _classify_common_F(verify_true_returned: bool) -> bool:
    """recovery_spec: failure to return Verify=true within stopping ⇒ ∈ F."""
    return not verify_true_returned


class ScaffoldProcedure:
    """Drive a minimal FC0-EXT scaffold path with injectable failure points."""

    def __init__(self) -> None:
        self.mods = import_scaffold_modules()
        self.FailureChannel = self.mods["types"].FailureChannel
        self.LifetimeError = self.mods["lifetime_hooks"].LifetimeError
        self.LifetimeRegistry = self.mods["lifetime_hooks"].LifetimeRegistry
        self.PublicInstance = self.mods["types"].PublicInstance
        self.CandidateSecret = self.mods["types"].CandidateSecret
        self.CleanupResult = self.mods["types"].CleanupResult
        self.HandleState = self.mods["types"].HandleState
        self.Verify = self.mods["verify"].Verify
        self.VerificationFault = self.mods["verify"].VerificationFault
        self.classify_verify_outcome = self.mods["verify"].classify_verify_outcome

    def _outcome_failure(
        self,
        reg,
        channel,
        events: List[Dict[str, Any]],
        **notes: Any,
    ) -> ProcedureOutcome:
        ch_name = channel.value if hasattr(channel, "value") else str(channel)
        verify_true = False
        return ProcedureOutcome(
            exit_kind="failure",
            channel=ch_name,
            classified_as_common_F=_classify_common_F(verify_true),
            verify_true_returned=verify_true,
            k_prime_token=None,
            stopping_policy=dict(SYMBOLIC_STOPPING_POLICY),
            events=events,
            failures_recorded=[f.value for f in reg.failures],
            notes=dict(notes),
        )

    def _outcome_success(
        self,
        reg,
        k_prime_token: str,
        events: List[Dict[str, Any]],
    ) -> ProcedureOutcome:
        return ProcedureOutcome(
            exit_kind="success",
            channel=None,
            classified_as_common_F=False,
            verify_true_returned=True,
            k_prime_token=k_prime_token,
            stopping_policy=dict(SYMBOLIC_STOPPING_POLICY),
            events=events,
            failures_recorded=[f.value for f in reg.failures],
            notes={"verify_body": "no_crypto_scaffold_token"},
        )

    def run_success_control(self) -> ProcedureOutcome:
        """Happy path: birth through no-crypto Verify=true success exit."""
        reg = self.LifetimeRegistry()
        events: List[Dict[str, Any]] = []
        x = self.PublicInstance(token="x-ok", scaffold_accept_token="k-accept")
        reg.birth_B_input(x)
        events.append({"step": "birth_B_input"})
        reg.birth_B_attempt({"attempts_symbolic": True})
        events.append({"step": "birth_B_attempt"})

        w_l = reg.birth_W_label(x, {"ctx": 0})
        r_l = reg.birth_R_label(x, {"ctx": 0}, {"addr": "symbolic"})
        reg.last_use_W_label(w_l)
        reg.last_use_R_label(r_l)
        assert reg.cleanup_W_label(w_l) == self.CleanupResult.ok
        assert reg.cleanup_R_label(r_l) == self.CleanupResult.ok
        reg.destroy_W_label(w_l)
        reg.destroy_R_label(r_l)
        events.append({"step": "oracle_label_cleaned"})

        w_s = reg.birth_W_sieve({"attempt": 0})
        r_s = reg.birth_R_sieve({"attempt": 0}, {"addr": "symbolic"})
        b_s = reg.birth_B_sieve({"attempt": 0})
        assert reg.cleanup_W_sieve(w_s, "accept") == self.CleanupResult.ok
        assert reg.cleanup_R_sieve(r_s, "accept") == self.CleanupResult.ok
        assert reg.cleanup_B_sieve(b_s, "accept") == self.CleanupResult.ok
        reg.destroy_W_sieve(w_s)
        reg.destroy_R_sieve(r_s)
        reg.destroy_B_sieve(b_s)
        events.append({"step": "sieve_accept_cleaned"})

        t = reg.birth_accepted_transcript({"accepted": True})
        b_post = reg.birth_B_post(t)
        b_rec = reg.birth_B_recovery(b_post, t)
        m = reg.birth_M_tail(
            b_rec,
            width_decl={"unit": "symbolic"},
            enumeration_order_decl={"order": "symbolic"},
            stopping_rule_decl={"invents_tau": False, "rule": "symbolic"},
            shares_B_recovery_decl=False,
        )
        b_cand = reg.birth_B_candidate(m)
        events.append({"step": "birth_B_candidate"})

        k_prime = self.CandidateSecret(token="k-accept")
        result = self.Verify(x, k_prime)
        classified = self.classify_verify_outcome(result)
        events.append(
            {
                "step": "Verify",
                "result": result,
                "classified": classified if isinstance(classified, str) else classified.value,
            }
        )
        if result is not True:
            return self._outcome_failure(
                reg,
                self.FailureChannel.F_verify,
                events,
                reason="success_control_unexpected_false",
            )
        reg.retain_final_verification_record()
        return self._outcome_success(reg, k_prime.token, events)

    def run_fail_F_input(self) -> ProcedureOutcome:
        reg = self.LifetimeRegistry()
        events: List[Dict[str, Any]] = []
        try:
            reg.birth_B_input(self.PublicInstance(token="bad", well_formed=False))
            events.append({"step": "birth_B_input", "unexpected": "no_error"})
            return self._outcome_failure(
                reg,
                self.FailureChannel.F,
                events,
                reason="expected_F_input_not_raised",
            )
        except self.LifetimeError as e:
            events.append(
                {
                    "step": "birth_B_input",
                    "error": str(e),
                    "channel": e.channel.value if e.channel else None,
                }
            )
            return self._outcome_failure(
                reg,
                self.FailureChannel.F_input,
                events,
                injection="malformed_PublicInstance",
                recovery_spec_role="parse_or_parameter_failure",
            )

    def run_fail_F_oracle(self) -> ProcedureOutcome:
        reg = self.LifetimeRegistry()
        events: List[Dict[str, Any]] = []
        x = self.PublicInstance(token="x-oracle", scaffold_accept_token="k*")
        reg.birth_B_input(x)
        reg.birth_B_attempt({"attempts_symbolic": True})
        w = reg.birth_W_label(x, {"ctx": 1})
        # Force non-live state so cleanup_W_label maps to F_oracle.
        w.mark(self.HandleState.cleaned)
        cr = reg.cleanup_W_label(w)
        events.append(
            {
                "step": "cleanup_W_label_non_live",
                "cleanup_result": cr.value,
                "failures": [f.value for f in reg.failures],
            }
        )
        # Halt without Verify: oracle/label failure ⇒ no k' returned.
        return self._outcome_failure(
            reg,
            self.FailureChannel.F_oracle,
            events,
            injection="cleanup_W_label_on_non_live",
            recovery_spec_role="oracle_or_label_approximation_or_implementation_failure",
            cleanup_result=cr.value,
        )

    def run_fail_F_cleanup(self) -> ProcedureOutcome:
        reg = self.LifetimeRegistry()
        events: List[Dict[str, Any]] = []
        x = self.PublicInstance(token="x-cleanup", scaffold_accept_token="k*")
        reg.birth_B_input(x)
        reg.birth_B_attempt({"attempts_symbolic": True})
        w = reg.birth_W_label(x, {})
        try:
            reg.destroy_W_label(w)
            events.append({"step": "destroy_W_label", "unexpected": "no_error"})
            return self._outcome_failure(
                reg,
                self.FailureChannel.F,
                events,
                reason="expected_F_cleanup_not_raised",
            )
        except self.LifetimeError as e:
            # BATCH-022 _destroy raises F_cleanup without appending to
            # reg.failures; record the channel on the procedure outcome.
            if self.FailureChannel.F_cleanup not in reg.failures:
                reg.failures.append(self.FailureChannel.F_cleanup)
            events.append(
                {
                    "step": "destroy_before_cleanup",
                    "error": str(e),
                    "channel": e.channel.value if e.channel else None,
                    "scaffold_note": (
                        "LifetimeError.channel=F_cleanup; failures list "
                        "appended by procedure driver for path accounting"
                    ),
                }
            )
            return self._outcome_failure(
                reg,
                self.FailureChannel.F_cleanup,
                events,
                injection="destroy_before_cleanup",
                recovery_spec_role="retry_or_handoff_cleanup_failure",
                scaffold_failures_append="procedure_driver",
            )

    def run_fail_F_stop(self) -> ProcedureOutcome:
        reg = self.LifetimeRegistry()
        events: List[Dict[str, Any]] = []
        x = self.PublicInstance(token="x-stop", scaffold_accept_token="k*")
        reg.birth_B_input(x)
        reg.birth_B_attempt({"attempts_symbolic": True})
        ch = reg.note_stopping_breach()
        events.append({"step": "note_stopping_breach", "channel": ch.value})
        # Also confirm τ invention remains rejected (no clearance).
        tau_rejected = False
        # Build minimal recovery handles for M_tail τ rejection probe.
        w_s = reg.birth_W_sieve({"attempt": 0})
        r_s = reg.birth_R_sieve({"attempt": 0}, {"addr": "symbolic"})
        b_s = reg.birth_B_sieve({"attempt": 0})
        assert reg.cleanup_W_sieve(w_s, "accept") == self.CleanupResult.ok
        assert reg.cleanup_R_sieve(r_s, "accept") == self.CleanupResult.ok
        assert reg.cleanup_B_sieve(b_s, "accept") == self.CleanupResult.ok
        reg.destroy_W_sieve(w_s)
        reg.destroy_R_sieve(r_s)
        reg.destroy_B_sieve(b_s)
        t = reg.birth_accepted_transcript({"accepted": True})
        b_post = reg.birth_B_post(t)
        b_rec = reg.birth_B_recovery(b_post, t)
        try:
            reg.birth_M_tail(
                b_rec,
                width_decl={"unit": "symbolic"},
                enumeration_order_decl={},
                stopping_rule_decl={"invents_tau": True},
                shares_B_recovery_decl=False,
            )
        except self.LifetimeError as e:
            tau_rejected = e.channel == self.FailureChannel.F_stop
            events.append(
                {
                    "step": "tau_invention_rejected",
                    "channel": e.channel.value if e.channel else None,
                }
            )
        # Halt without Verify under symbolic stopping breach.
        return self._outcome_failure(
            reg,
            self.FailureChannel.F_stop,
            events,
            injection="note_stopping_breach",
            recovery_spec_role="stopping_policy_breach",
            tau_invented=False,
            tau_invention_rejected=tau_rejected,
            qm_stopping_cleared=False,
        )

    def run_fail_F_recovery(self) -> ProcedureOutcome:
        reg = self.LifetimeRegistry()
        events: List[Dict[str, Any]] = []
        x = self.PublicInstance(token="x-rec", scaffold_accept_token="k*")
        reg.birth_B_input(x)
        reg.birth_B_attempt({"attempts_symbolic": True})
        reg.birth_W_sieve({})
        reg.birth_R_sieve({}, {})
        t = reg.birth_accepted_transcript({})
        try:
            reg.birth_B_post(t)
            events.append({"step": "birth_B_post", "unexpected": "no_error"})
            return self._outcome_failure(
                reg,
                self.FailureChannel.F,
                events,
                reason="expected_F_recovery_not_raised",
            )
        except self.LifetimeError as e:
            events.append(
                {
                    "step": "B_post_precondition",
                    "error": str(e),
                    "channel": e.channel.value if e.channel else None,
                }
            )
            return self._outcome_failure(
                reg,
                self.FailureChannel.F_recovery,
                events,
                injection="B_post_while_W_R_sieve_live",
                recovery_spec_role="algebraic_or_reconstruction_error",
            )

    def run_fail_F_tail(self) -> ProcedureOutcome:
        reg = self.LifetimeRegistry()
        events: List[Dict[str, Any]] = []
        x = self.PublicInstance(token="x-tail", scaffold_accept_token="k*")
        reg.birth_B_input(x)
        reg.birth_B_attempt({"attempts_symbolic": True})
        w_s = reg.birth_W_sieve({"attempt": 0})
        r_s = reg.birth_R_sieve({"attempt": 0}, {"addr": "symbolic"})
        b_s = reg.birth_B_sieve({"attempt": 0})
        assert reg.cleanup_W_sieve(w_s, "accept") == self.CleanupResult.ok
        assert reg.cleanup_R_sieve(r_s, "accept") == self.CleanupResult.ok
        assert reg.cleanup_B_sieve(b_s, "accept") == self.CleanupResult.ok
        reg.destroy_W_sieve(w_s)
        reg.destroy_R_sieve(r_s)
        reg.destroy_B_sieve(b_s)
        t = reg.birth_accepted_transcript({"accepted": True})
        b_post = reg.birth_B_post(t)
        b_rec = reg.birth_B_recovery(b_post, t)
        ch = reg.note_tail_exhaustion()
        events.append({"step": "note_tail_exhaustion", "channel": ch.value})
        numeric_rejected = False
        try:
            reg.birth_M_tail(
                b_rec,
                width_decl={"numeric_width": 128},
                enumeration_order_decl={},
                stopping_rule_decl={"invents_tau": False},
                shares_B_recovery_decl=False,
            )
        except self.LifetimeError as e:
            numeric_rejected = e.channel == self.FailureChannel.F_tail
            events.append(
                {
                    "step": "numeric_width_forbidden",
                    "channel": e.channel.value if e.channel else None,
                }
            )
        return self._outcome_failure(
            reg,
            self.FailureChannel.F_tail,
            events,
            injection="note_tail_exhaustion",
            recovery_spec_role="tail_exhaustion_timeout_or_omitted_residual_branch",
            numeric_width_invented=False,
            numeric_width_rejected=numeric_rejected,
        )

    def run_fail_F_verify_false(self) -> ProcedureOutcome:
        """Reach Verify; false result ⇒ F_verify ⊆ F (no-crypto body)."""
        reg = self.LifetimeRegistry()
        events: List[Dict[str, Any]] = []
        x = self.PublicInstance(token="x-v", scaffold_accept_token="k-accept")
        reg.birth_B_input(x)
        reg.birth_B_attempt({"attempts_symbolic": True})
        w_s = reg.birth_W_sieve({"attempt": 0})
        r_s = reg.birth_R_sieve({"attempt": 0}, {"addr": "symbolic"})
        b_s = reg.birth_B_sieve({"attempt": 0})
        assert reg.cleanup_W_sieve(w_s, "accept") == self.CleanupResult.ok
        assert reg.cleanup_R_sieve(r_s, "accept") == self.CleanupResult.ok
        assert reg.cleanup_B_sieve(b_s, "accept") == self.CleanupResult.ok
        reg.destroy_W_sieve(w_s)
        reg.destroy_R_sieve(r_s)
        reg.destroy_B_sieve(b_s)
        t = reg.birth_accepted_transcript({"accepted": True})
        b_post = reg.birth_B_post(t)
        b_rec = reg.birth_B_recovery(b_post, t)
        m = reg.birth_M_tail(
            b_rec,
            width_decl={"unit": "symbolic"},
            enumeration_order_decl={},
            stopping_rule_decl={"invents_tau": False},
            shares_B_recovery_decl=False,
        )
        reg.birth_B_candidate(m)
        k_prime = self.CandidateSecret(token="wrong-token")
        result = self.Verify(x, k_prime)
        classified = self.classify_verify_outcome(result)
        events.append(
            {
                "step": "Verify_false",
                "result": result,
                "classified": classified.value if hasattr(classified, "value") else classified,
            }
        )
        reg.failures.append(self.FailureChannel.F_verify)
        return self._outcome_failure(
            reg,
            self.FailureChannel.F_verify,
            events,
            injection="no_crypto_Verify_returns_false",
            recovery_spec_role="false_Verify_result_or_verification_fault",
            crypto_body=False,
        )

    def run_fail_F_verify_fault(self) -> ProcedureOutcome:
        """Malformed buffers raise VerificationFault ⇒ F_verify ⊆ F."""
        reg = self.LifetimeRegistry()
        events: List[Dict[str, Any]] = []
        x = self.PublicInstance(token="x-fault", well_formed=False)
        try:
            self.Verify(x, self.CandidateSecret(token="k"))
            events.append({"step": "Verify_fault", "unexpected": "no_fault"})
            return self._outcome_failure(
                reg,
                self.FailureChannel.F,
                events,
                reason="expected_VerificationFault",
            )
        except self.VerificationFault as e:
            events.append({"step": "Verify_fault", "error": str(e)})
            reg.failures.append(self.FailureChannel.F_verify)
            return self._outcome_failure(
                reg,
                self.FailureChannel.F_verify,
                events,
                injection="VerificationFault_malformed_buffers",
                recovery_spec_role="false_Verify_result_or_verification_fault",
                crypto_body=False,
            )


FAILURE_RUNNERS = {
    "F_input": "run_fail_F_input",
    "F_oracle": "run_fail_F_oracle",
    "F_cleanup": "run_fail_F_cleanup",
    "F_stop": "run_fail_F_stop",
    "F_recovery": "run_fail_F_recovery",
    "F_tail": "run_fail_F_tail",
    "F_verify": "run_fail_F_verify_false",
}
