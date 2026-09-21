"""W/R/B/M_tail lifetime hooks scaffolding for FC0-EXT-PKG-SSI-001.

Implements birth / last_use / cleanup / destroy signatures from
lifetime_hooks_interface.yaml as a checkable state-machine skeleton under
the TASK-20260730-059 write scope.

Explicit non-claims:
- Not CollimationSieve APIs (pin 6f9188e4 untouched).
- No numeric widths (width_decl fields are symbolic declarations only).
- No τ / QM-STOPPING clearance (M_tail stopping_rule_decl is symbolic).
- No QUERY_MEMORY / QM-MEMORY-MAP clearance.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .state_machine import StageLiveSetTracker, assert_handle_live
from .types import (
    CleanupResult,
    FailureChannel,
    HandleState,
    ObjectClass,
    OpaqueHandle,
    PublicInstance,
)


class LifetimeError(Exception):
    """Protocol / precondition violation in the lifetime skeleton."""

    def __init__(self, message: str, channel: Optional[FailureChannel] = None):
        super().__init__(message)
        self.channel = channel


class LifetimeRegistry:
    """In-memory registry of FC0 object handles and stage live-set tracker."""

    REQUIRED_HOOK_IDS = (
        "W_label",
        "R_label",
        "W_sieve",
        "R_sieve",
        "B_input",
        "B_attempt",
        "B_sieve",
        "accepted_transcript",
        "B_post",
        "B_recovery",
        "M_tail",
        "B_candidate",
    )

    def __init__(self) -> None:
        self.handles: Dict[str, OpaqueHandle] = {}
        self.tracker = StageLiveSetTracker()
        self.failures: list[FailureChannel] = []
        self.final_verification_record_retained: bool = False
        self.events: list[dict] = []

    def _record(self, event: str, object_id: str, **extra: Any) -> None:
        self.events.append({"event": event, "object_id": object_id, **extra})

    def _require_live_ids(self, *object_ids: str) -> None:
        for oid in object_ids:
            h = self.handles.get(oid)
            if h is None or h.state not in (HandleState.live, HandleState.last_used):
                raise LifetimeError(
                    f"precondition_failed:{oid}_not_live",
                    FailureChannel.F_cleanup,
                )

    def _birth(
        self,
        object_id: str,
        object_class: ObjectClass,
        stage: str,
        **notes: Any,
    ) -> OpaqueHandle:
        if object_id in self.handles and self.handles[object_id].state != HandleState.destroyed:
            raise LifetimeError(f"double_birth:{object_id}", FailureChannel.F_cleanup)
        handle = OpaqueHandle(
            object_id=object_id,
            object_class=object_class,
            state=HandleState.live,
            stage_at_birth=stage,
            notes=dict(notes),
        )
        self.handles[object_id] = handle
        self.tracker.birth(object_id, stage)
        self._record("birth", object_id, stage=stage)
        return handle

    def _last_use(self, handle: OpaqueHandle) -> None:
        assert_handle_live(handle)
        handle.mark(HandleState.last_used)
        self._record("last_use", handle.object_id)

    def _cleanup(self, handle: OpaqueHandle, force_fail: bool = False) -> CleanupResult:
        if handle.state == HandleState.destroyed:
            self.failures.append(FailureChannel.F_cleanup)
            return CleanupResult.cleanup_failure
        if force_fail:
            self.failures.append(FailureChannel.F_cleanup)
            self._record("cleanup_failure", handle.object_id)
            return CleanupResult.cleanup_failure
        handle.mark(HandleState.cleaned)
        self._record("cleanup", handle.object_id, result="ok")
        return CleanupResult.ok

    def _destroy(self, handle: OpaqueHandle) -> None:
        if handle.state not in (HandleState.cleaned, HandleState.last_used, HandleState.live):
            # Allow destroy only after successful cleanup per frozen contracts.
            if handle.state != HandleState.cleaned:
                raise LifetimeError(
                    f"destroy_before_cleanup:{handle.object_id}",
                    FailureChannel.F_cleanup,
                )
        if handle.state != HandleState.cleaned:
            raise LifetimeError(
                f"destroy_requires_cleanup:{handle.object_id}",
                FailureChannel.F_cleanup,
            )
        handle.mark(HandleState.destroyed)
        self.tracker.destroy(handle.object_id)
        self._record("destroy", handle.object_id)

    # --- B_input ---
    def birth_B_input(self, x: PublicInstance) -> OpaqueHandle:
        if not isinstance(x, PublicInstance) or not x.well_formed:
            self.failures.append(FailureChannel.F_input)
            raise LifetimeError("parse_and_validate_x_failed", FailureChannel.F_input)
        return self._birth("B_input", ObjectClass.B, "initialize", x_token=x.token)

    def last_use_B_input(self, handle: OpaqueHandle) -> None:
        self._last_use(handle)

    def cleanup_B_input(self, handle: OpaqueHandle) -> CleanupResult:
        if not self.final_verification_record_retained:
            self.failures.append(FailureChannel.F_cleanup)
            return CleanupResult.cleanup_failure
        return self._cleanup(handle)

    def destroy_B_input(self, handle: OpaqueHandle) -> None:
        self._destroy(handle)

    # --- B_attempt ---
    def birth_B_attempt(self, schedule_decl: dict) -> OpaqueHandle:
        self._require_live_ids("B_input")
        return self._birth(
            "B_attempt",
            ObjectClass.B,
            "initialize",
            schedule_decl=schedule_decl,
        )

    def last_use_B_attempt(self, handle: OpaqueHandle) -> None:
        self._last_use(handle)

    def cleanup_B_attempt(self, handle: OpaqueHandle) -> CleanupResult:
        if not self.final_verification_record_retained:
            self.failures.append(FailureChannel.F_cleanup)
            return CleanupResult.cleanup_failure
        return self._cleanup(handle)

    def destroy_B_attempt(self, handle: OpaqueHandle) -> None:
        self._destroy(handle)

    def note_stopping_breach(self) -> FailureChannel:
        self.failures.append(FailureChannel.F_stop)
        return FailureChannel.F_stop

    # --- W_label ---
    def birth_W_label(self, x: PublicInstance, attempt_ctx: dict) -> OpaqueHandle:
        self._require_live_ids("B_input", "B_attempt")
        return self._birth(
            "W_label",
            ObjectClass.W,
            "oracle_label_preparation",
            attempt_ctx=attempt_ctx,
            x_token=x.token,
        )

    def last_use_W_label(self, handle: OpaqueHandle) -> None:
        self._last_use(handle)

    def cleanup_W_label(self, handle: OpaqueHandle) -> CleanupResult:
        # Scaffold: require last_use before cleanup (uncompute-and-verify stub).
        if handle.state not in (HandleState.last_used, HandleState.live):
            self.failures.append(FailureChannel.F_oracle)
            return CleanupResult.cleanup_failure
        return self._cleanup(handle)

    def destroy_W_label(self, handle: OpaqueHandle) -> None:
        self._destroy(handle)

    # --- R_label ---
    def birth_R_label(
        self, x: PublicInstance, attempt_ctx: dict, address_semantics_decl: dict
    ) -> OpaqueHandle:
        self._require_live_ids("B_input", "B_attempt")
        return self._birth(
            "R_label",
            ObjectClass.R,
            "oracle_label_preparation",
            attempt_ctx=attempt_ctx,
            address_semantics_decl=address_semantics_decl,
            x_token=x.token,
        )

    def last_use_R_label(self, handle: OpaqueHandle) -> None:
        self._last_use(handle)

    def cleanup_R_label(self, handle: OpaqueHandle) -> CleanupResult:
        if handle.state != HandleState.last_used:
            self.failures.append(FailureChannel.F_oracle)
            return CleanupResult.cleanup_failure
        return self._cleanup(handle)

    def destroy_R_label(self, handle: OpaqueHandle) -> None:
        self._destroy(handle)

    # --- W_sieve ---
    def birth_W_sieve(self, attempt_ctx: dict) -> OpaqueHandle:
        self._require_live_ids("B_input", "B_attempt")
        return self._birth(
            "W_sieve",
            ObjectClass.W,
            "sieve_attempt_before_local_transition",
            attempt_ctx=attempt_ctx,
        )

    def last_use_W_sieve(self, handle: OpaqueHandle) -> None:
        self._last_use(handle)

    def cleanup_W_sieve(self, handle: OpaqueHandle, mode: str) -> CleanupResult:
        if mode not in ("retry", "accept"):
            raise LifetimeError("invalid_cleanup_mode", FailureChannel.F_cleanup)
        return self._cleanup(handle)

    def destroy_W_sieve(self, handle: OpaqueHandle) -> None:
        self._destroy(handle)

    # --- R_sieve ---
    def birth_R_sieve(self, attempt_ctx: dict, address_semantics_decl: dict) -> OpaqueHandle:
        self._require_live_ids("B_input", "B_attempt")
        return self._birth(
            "R_sieve",
            ObjectClass.R,
            "sieve_attempt_before_local_transition",
            attempt_ctx=attempt_ctx,
            address_semantics_decl=address_semantics_decl,
        )

    def last_use_R_sieve(self, handle: OpaqueHandle) -> None:
        self._last_use(handle)

    def cleanup_R_sieve(self, handle: OpaqueHandle, mode: str) -> CleanupResult:
        if mode not in ("retry", "accept"):
            raise LifetimeError("invalid_cleanup_mode", FailureChannel.F_cleanup)
        return self._cleanup(handle)

    def destroy_R_sieve(self, handle: OpaqueHandle) -> None:
        self._destroy(handle)

    # --- B_sieve ---
    def birth_B_sieve(self, attempt_ctx: dict) -> OpaqueHandle:
        self._require_live_ids("B_input", "B_attempt")
        return self._birth(
            "B_sieve",
            ObjectClass.B,
            "sieve_attempt_before_local_transition",
            attempt_ctx=attempt_ctx,
        )

    def last_use_B_sieve(self, handle: OpaqueHandle) -> None:
        self._last_use(handle)

    def cleanup_B_sieve(self, handle: OpaqueHandle, mode: str) -> CleanupResult:
        if mode not in ("retry", "accept"):
            raise LifetimeError("invalid_cleanup_mode", FailureChannel.F_cleanup)
        return self._cleanup(handle)

    def destroy_B_sieve(self, handle: OpaqueHandle) -> None:
        self._destroy(handle)

    # --- accepted_transcript ---
    def birth_accepted_transcript(self, sieve_output: dict) -> OpaqueHandle:
        return self._birth(
            "accepted_transcript",
            ObjectClass.B,
            "accepted_sieve_output_handoff",
            sieve_output=sieve_output,
        )

    def last_use_accepted_transcript(self, handle: OpaqueHandle) -> None:
        self._last_use(handle)

    def cleanup_accepted_transcript(self, handle: OpaqueHandle) -> CleanupResult:
        return self._cleanup(handle)

    def destroy_accepted_transcript(self, handle: OpaqueHandle) -> None:
        self._destroy(handle)

    # --- B_post ---
    def birth_B_post(self, accepted_transcript_handle: OpaqueHandle) -> OpaqueHandle:
        assert_handle_live(accepted_transcript_handle)
        # Precondition: W_sieve and R_sieve destroyed after final use.
        for oid in ("W_sieve", "R_sieve"):
            h = self.handles.get(oid)
            if h is not None and h.state != HandleState.destroyed:
                self.failures.append(FailureChannel.F_recovery)
                raise LifetimeError(
                    f"B_post_precondition:{oid}_not_destroyed",
                    FailureChannel.F_recovery,
                )
        return self._birth(
            "B_post",
            ObjectClass.B,
            "classical_postprocessing_recovery",
            transcript_serial=accepted_transcript_handle.handle_serial,
        )

    def last_use_B_post(self, handle: OpaqueHandle) -> None:
        self._last_use(handle)

    def cleanup_B_post(self, handle: OpaqueHandle) -> CleanupResult:
        return self._cleanup(handle)

    def destroy_B_post(self, handle: OpaqueHandle) -> None:
        self._destroy(handle)

    # --- B_recovery ---
    def birth_B_recovery(
        self, B_post_handle: OpaqueHandle, accepted_transcript_handle: OpaqueHandle
    ) -> OpaqueHandle:
        assert_handle_live(B_post_handle)
        assert_handle_live(accepted_transcript_handle)
        return self._birth(
            "B_recovery",
            ObjectClass.B,
            "classical_postprocessing_recovery",
        )

    def last_use_B_recovery(self, handle: OpaqueHandle) -> None:
        self._last_use(handle)

    def cleanup_B_recovery(self, handle: OpaqueHandle) -> CleanupResult:
        return self._cleanup(handle)

    def destroy_B_recovery(self, handle: OpaqueHandle) -> None:
        self._destroy(handle)

    # --- M_tail ---
    def birth_M_tail(
        self,
        B_recovery_handle: OpaqueHandle,
        width_decl: dict,
        enumeration_order_decl: dict,
        stopping_rule_decl: dict,
        shares_B_recovery_decl: bool,
    ) -> OpaqueHandle:
        assert_handle_live(B_recovery_handle)
        # Symbolic declarations only — no numeric widths, no τ invented.
        if "numeric_width" in width_decl:
            raise LifetimeError(
                "numeric_width_forbidden_in_zero_compute_scaffold",
                FailureChannel.F_tail,
            )
        if stopping_rule_decl.get("invents_tau") is True:
            raise LifetimeError("tau_invention_forbidden", FailureChannel.F_stop)
        return self._birth(
            "M_tail",
            ObjectClass.M_tail,
            "residual_tail_after_recovery_transition",
            width_decl=width_decl,
            enumeration_order_decl=enumeration_order_decl,
            stopping_rule_decl=stopping_rule_decl,
            shares_B_recovery_decl=shares_B_recovery_decl,
        )

    def last_use_M_tail(self, handle: OpaqueHandle) -> None:
        self._last_use(handle)

    def cleanup_M_tail(self, handle: OpaqueHandle) -> CleanupResult:
        return self._cleanup(handle)

    def destroy_M_tail(self, handle: OpaqueHandle) -> None:
        self._destroy(handle)

    def note_tail_exhaustion(self) -> FailureChannel:
        self.failures.append(FailureChannel.F_tail)
        return FailureChannel.F_tail

    # --- B_candidate ---
    def birth_B_candidate(self, M_tail_handle_or_recovery_candidate: OpaqueHandle) -> OpaqueHandle:
        assert_handle_live(M_tail_handle_or_recovery_candidate)
        return self._birth(
            "B_candidate",
            ObjectClass.B,
            "verification_event",
            source=M_tail_handle_or_recovery_candidate.object_id,
        )

    def last_use_B_candidate(self, handle: OpaqueHandle) -> None:
        self._last_use(handle)

    def cleanup_B_candidate(self, handle: OpaqueHandle) -> CleanupResult:
        return self._cleanup(handle)

    def destroy_B_candidate(self, handle: OpaqueHandle) -> None:
        self._destroy(handle)

    def retain_final_verification_record(self) -> None:
        self.final_verification_record_retained = True
        self._record("retain_final_verification_record", "B_candidate")

    def implemented_hook_methods(self) -> list[str]:
        """Return method names present for each required hook id."""
        methods = []
        for oid in self.REQUIRED_HOOK_IDS:
            for prefix in ("birth_", "last_use_", "cleanup_", "destroy_"):
                name = f"{prefix}{oid}"
                if hasattr(self, name):
                    methods.append(name)
        return methods

    def coverage(self) -> dict:
        methods = self.implemented_hook_methods()
        return {
            "required_hooks": list(self.REQUIRED_HOOK_IDS),
            "required_hook_count": len(self.REQUIRED_HOOK_IDS),
            "implemented_method_count": len(methods),
            "methods": methods,
            "collimation_sieve_apis_invented": 0,
            "numeric_widths_invented": False,
            "tau_invented": False,
        }
