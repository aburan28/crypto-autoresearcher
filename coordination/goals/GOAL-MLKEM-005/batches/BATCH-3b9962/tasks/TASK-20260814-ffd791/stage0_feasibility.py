#!/usr/bin/env python3
"""
TASK-20260814-ffd791 -- PREREG-8 section 2: Stage 0 feasibility benchmark.

Only runs because infra_verification.py's own section-1 checks all passed
(infra_verification_results.json: overall_pass == true). Does NOT re-verify
section 1 itself.

Two independent sweeps, run as SEPARATE OS subprocesses so a hard wall-clock
cap can be enforced externally (fpylll's own internal MAX_TIME flag uses CPU
process_time, not wall clock, and cannot be trusted alone to bound a single
long SVP-enumeration call within a BKZ tour):

  1. MAIN GRID (section 2.2): one BKZ-beta reduction per (d, beta) cell,
     d in {256, 512} x beta in {40, 55, 70}, each capped at
     PER_BASIS_FEASIBILITY_CAP = 3600s. Records wall-clock, peak RSS,
     tour count, and the measured root-Hermite factor delta_0.

  2. TOY-FLOOR SWEEP (8f8f45's own control, section 2.2/2.3): exhaustive
     search over the CBD(eta2=2) alphabet at toy d in {8, 12, 16, 20},
     each capped at TOY_FLOOR_FEASIBILITY_CAP = 900s, timing ONLY (the
     exhaustive-search wall-clock at increasing d, before any headline
     floor number is committed to -- exactly PREREG-8 section 2.2's own
     text). Selects the largest d that completes.

     PROTOCOL INTERPRETATION, FLAGGED (PREREG-8 does not pin these down):
       - eta = eta2 = 2 is used for the exhaustive alphabet (the error
         term e1/e2's own CBD parameter under this protocol's own scope,
         matching R = ||pi(e)||^2/||e||^2's own "e" -- NOT eta1=3, which
         is the secret/r parameter). This is a deliberate reading, not an
         arbitrary one, but PREREG-8 section 2.2 does not state it
         explicitly and a different reading (eta1=3) would give a larger
         alphabet and slower, more conservative timings.
       - beta_toy = d // 2 is used for the toy sub-cell's own basis
         (PREREG-8 does not specify a beta for the toy-floor arm at all --
         only the (d, beta) main grid's beta values are pinned). Since the
         exhaustive search's own asymptotic cost is O((2 eta+1)^d), driven
         by d and eta only, this choice does not materially change the
         FEASIBILITY timing this sweep exists to measure.

SEED_ROOT = 715923, stage_index = 0 for every draw in this file
(PREREG-8 section 3.5).
"""
import json
import os
import subprocess
import sys
import time

import numpy as np

SEED_ROOT = 715923
PER_BASIS_FEASIBILITY_CAP = 3600
TOY_FLOOR_FEASIBILITY_CAP = 900
HERE = os.path.dirname(os.path.abspath(__file__))

MAIN_CELLS = [(256, 40), (256, 55), (256, 70), (512, 40), (512, 55), (512, 70)]
TOY_DS = [8, 12, 16, 20]
TOY_ETA = 2  # eta2, see module docstring
TOY_CHUNK = 4_000_000


# ---------------------------------------------------------------------------
# Worker entry points -- each runs as its OWN subprocess so the parent can
# enforce a hard wall-clock kill independent of anything fpylll or numpy do
# internally.
# ---------------------------------------------------------------------------

def gram_schmidt(B):
    d = B.shape[0]
    Bstar = np.zeros_like(B, dtype=np.float64)
    mu = np.zeros((d, d), dtype=np.float64)
    for i in range(d):
        Bstar[i] = B[i].astype(np.float64)
        for j in range(i):
            mu[i, j] = np.dot(B[i], Bstar[j]) / np.dot(Bstar[j], Bstar[j])
            Bstar[i] = Bstar[i] - mu[i, j] * Bstar[j]
    r = np.array([np.dot(Bstar[i], Bstar[i]) for i in range(d)])
    return Bstar, mu, r


def worker_main_cell(d, beta, out_path):
    """Runs in its own subprocess: reduce ONE fresh basis at (d, beta),
    record wall-clock, tours, and the measured root-Hermite factor."""
    result = {"d": d, "beta": beta}
    try:
        from fpylll import IntegerMatrix, LLL, BKZ, FPLLL
        from fpylll.algorithms.bkz2 import BKZReduction

        seed = int(
            np.random.default_rng([SEED_ROOT, 0, d, beta, 0, 0]).integers(0, 2 ** 31 - 1)
        )
        FPLLL.set_random_seed(seed)
        result["seed_used"] = seed

        strategies_path = "/usr/share/libfplll8/strategies/default.json"
        if not os.path.exists(strategies_path):
            strategies_path = BKZ.DEFAULT_STRATEGY

        A = IntegerMatrix.random(d, "qary", k=d // 2, q=3329)
        t0 = time.time()
        LLL.reduction(A)
        lll_elapsed = time.time() - t0

        par = BKZ.Param(
            block_size=beta,
            strategies=strategies_path,
            flags=BKZ.AUTO_ABORT,
        )
        bkz = BKZReduction(A)
        t1 = time.time()
        bkz(par, tracer=True)
        bkz_elapsed = time.time() - t1

        n_tours = None
        try:
            if bkz.trace is not None:
                n_tours = sum(1 for child in bkz.trace.children if child.label[0] == "tour")
        except Exception:
            n_tours = None

        M = bkz.M
        log_det = M.get_log_det(0, d)
        r0 = M.get_r(0, 0)
        first_vec_norm = r0 ** 0.5
        # delta_0: ||b1|| ~ delta_0^d * det(L)^(1/d)  =>  delta_0 = (||b1|| / det(L)^(1/d))^(1/d)
        det_l_pow_1_over_d = np.exp(log_det / d)
        delta_0 = (first_vec_norm / det_l_pow_1_over_d) ** (1.0 / d)

        result.update({
            "status": "COMPLETED",
            "lll_elapsed_seconds": lll_elapsed,
            "bkz_elapsed_seconds": bkz_elapsed,
            "total_elapsed_seconds": lll_elapsed + bkz_elapsed,
            "n_tours": n_tours,
            "delta_0_root_hermite_factor": float(delta_0),
            "first_gso_vector_norm": float(first_vec_norm),
            "log_det": float(log_det),
            "strategies_file_used": strategies_path,
        })
    except Exception as exc:  # noqa: BLE001
        import traceback
        result["status"] = "ERROR"
        result["error"] = "%s: %s" % (type(exc).__name__, exc)
        result["traceback"] = traceback.format_exc()

    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)


def worker_toy_floor(d, eta, beta_toy, cap_seconds, out_path):
    """Runs in its own subprocess: exhaustive search over CBD(eta)^d,
    timing only, chunked and mixed-radix generated (no itertools.product
    overhead) so a genuinely large alphabet can be swept until the cap,
    then reports its own elapsed time honestly whether or not it finished
    the full enumeration."""
    result = {"d": d, "eta": eta, "beta_toy": beta_toy}
    try:
        from fpylll import IntegerMatrix, LLL, BKZ, FPLLL

        seed = int(
            np.random.default_rng([SEED_ROOT, 0, d, beta_toy, 2, 0]).integers(0, 2 ** 31 - 1)
        )
        FPLLL.set_random_seed(seed)
        result["seed_used"] = seed

        A = IntegerMatrix.random(d, "qary", k=d // 2, q=3329)
        LLL.reduction(A)
        strategies_path = "/usr/share/libfplll8/strategies/default.json"
        if not os.path.exists(strategies_path):
            strategies_path = BKZ.DEFAULT_STRATEGY
        if beta_toy >= 2:
            par = BKZ.Param(block_size=beta_toy, strategies=strategies_path, flags=BKZ.AUTO_ABORT)
            BKZ.reduction(A, par)

        B = np.array([[A[i, j] for j in range(d)] for i in range(d)], dtype=np.int64)
        Bstar, mu, r = gram_schmidt(B)

        k = d - beta_toy  # project OUT the first k GSO directions, keep last beta_toy
        # P = sum_{i=k}^{d-1} (Bstar_i Bstar_i^T) / r_i   (0-indexed)
        P = np.zeros((d, d), dtype=np.float64)
        for i in range(k, d):
            P += np.outer(Bstar[i], Bstar[i]) / r[i]

        base = 2 * eta + 1
        total_points = base ** d
        result["alphabet_size_total"] = total_points if total_points < 10 ** 18 else "OVERFLOW_TOO_LARGE"

        t0 = time.time()
        best_r = None
        n_evaluated = 0
        idx = 0
        completed = False
        while idx < total_points:
            elapsed = time.time() - t0
            if elapsed >= cap_seconds:
                break
            chunk_end = min(idx + TOY_CHUNK, total_points)
            n = chunk_end - idx
            ids = np.arange(idx, chunk_end, dtype=np.int64)
            digits = np.zeros((n, d), dtype=np.int64)
            tmp = ids.copy()
            for pos in range(d):
                digits[:, pos] = tmp % base
                tmp //= base
            E = digits - eta  # values in {-eta,...,eta}

            norms_sq = np.einsum("ij,ij->i", E, E)
            nonzero = norms_sq > 0
            if np.any(nonzero):
                proj = E[nonzero] @ P
                proj_sq = np.einsum("ij,ij->i", proj, E[nonzero])
                ratio = proj_sq / norms_sq[nonzero]
                chunk_min = float(np.min(ratio))
                if best_r is None or chunk_min < best_r:
                    best_r = chunk_min
            n_evaluated += n
            idx = chunk_end
        else:
            completed = True

        total_elapsed = time.time() - t0
        result.update({
            "status": "COMPLETED" if completed else "NOT_COMPUTED",
            "reason": None if completed else "infeasible within TOY_FLOOR_FEASIBILITY_CAP",
            "elapsed_seconds": total_elapsed,
            "n_points_evaluated": n_evaluated,
            "fraction_of_alphabet_evaluated": (
                n_evaluated / total_points if isinstance(result["alphabet_size_total"], int) else None
            ),
            "r_min_over_evaluated_subset": best_r,
            "note_if_not_completed": (
                None if completed else
                "r_min_over_evaluated_subset is a partial-search value, NOT the exact "
                "combinatorial floor -- exhaustive search did not finish within the cap."
            ),
        })
    except Exception as exc:  # noqa: BLE001
        import traceback
        result["status"] = "ERROR"
        result["error"] = "%s: %s" % (type(exc).__name__, exc)
        result["traceback"] = traceback.format_exc()

    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)


# ---------------------------------------------------------------------------
# Parent orchestration
# ---------------------------------------------------------------------------

def run_capped_subprocess(argv, cap_seconds, out_path, mem_poll_interval=0.5):
    """Launches argv as a subprocess, polls its RSS via psutil, and
    enforces cap_seconds as a HARD wall-clock kill. Returns
    (wall_clock_seconds, peak_rss_mb, timed_out, returncode)."""
    import psutil

    t0 = time.time()
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ps_proc = None
    try:
        ps_proc = psutil.Process(proc.pid)
    except Exception:
        ps_proc = None

    peak_rss = 0
    timed_out = False
    while True:
        ret = proc.poll()
        if ps_proc is not None:
            try:
                rss = ps_proc.memory_info().rss
                for child in ps_proc.children(recursive=True):
                    try:
                        rss += child.memory_info().rss
                    except Exception:
                        pass
                peak_rss = max(peak_rss, rss)
            except Exception:
                pass
        if ret is not None:
            break
        if time.time() - t0 >= cap_seconds:
            timed_out = True
            try:
                proc.terminate()
                proc.wait(timeout=10)
            except Exception:
                proc.kill()
            break
        time.sleep(mem_poll_interval)

    stdout, stderr = b"", b""
    try:
        stdout, stderr = proc.communicate(timeout=15)
    except Exception:
        pass

    wall_clock = time.time() - t0
    return {
        "wall_clock_seconds": wall_clock,
        "peak_rss_mb": peak_rss / (1024 * 1024),
        "timed_out": timed_out,
        "returncode": proc.returncode,
        "stdout_tail": stdout.decode(errors="replace")[-2000:],
        "stderr_tail": stderr.decode(errors="replace")[-2000:],
    }


def main():
    overall = {
        "seed_root": SEED_ROOT,
        "per_basis_feasibility_cap_seconds": PER_BASIS_FEASIBILITY_CAP,
        "toy_floor_feasibility_cap_seconds": TOY_FLOOR_FEASIBILITY_CAP,
        "toy_floor_eta_used": TOY_ETA,
        "main_grid": [],
        "toy_floor_sweep": [],
    }

    t_script_start = time.time()

    print("=== MAIN GRID (section 2.2), 6 cells ===", flush=True)
    for d, beta in MAIN_CELLS:
        out_path = os.path.join(HERE, "_tmp_cell_%d_%d.json" % (d, beta))
        if os.path.exists(out_path):
            os.remove(out_path)
        argv = [sys.executable, os.path.abspath(__file__), "--worker-cell", str(d), str(beta), out_path]
        print("cell (d=%d, beta=%d): launching, cap=%ds" % (d, beta, PER_BASIS_FEASIBILITY_CAP), flush=True)
        proc_info = run_capped_subprocess(argv, PER_BASIS_FEASIBILITY_CAP, out_path)

        cell_result = {"d": d, "beta": beta}
        cell_result.update({
            "subprocess_wall_clock_seconds": proc_info["wall_clock_seconds"],
            "peak_rss_mb": proc_info["peak_rss_mb"],
            "subprocess_timed_out": proc_info["timed_out"],
            "subprocess_returncode": proc_info["returncode"],
        })
        if proc_info["timed_out"] or not os.path.exists(out_path):
            cell_result["status"] = "NOT_COMPUTED"
            cell_result["reason"] = "infeasible within Stage-0 cap" if proc_info["timed_out"] else (
                "worker crashed before writing output (stderr_tail attached)"
            )
            cell_result["stderr_tail"] = proc_info["stderr_tail"]
        else:
            with open(out_path) as f:
                worker_out = json.load(f)
            cell_result.update(worker_out)
        print("  -> %s (%.1fs)" % (cell_result["status"], proc_info["wall_clock_seconds"]), flush=True)
        overall["main_grid"].append(cell_result)
        if os.path.exists(out_path):
            os.remove(out_path)

    print("=== TOY-FLOOR SWEEP (8f8f45's control), d in %s ===" % TOY_DS, flush=True)
    selected_d = None
    for d in TOY_DS:
        beta_toy = max(0, d // 2)
        out_path = os.path.join(HERE, "_tmp_toy_%d.json" % d)
        if os.path.exists(out_path):
            os.remove(out_path)
        argv = [
            sys.executable, os.path.abspath(__file__),
            "--worker-toyfloor", str(d), str(TOY_ETA), str(beta_toy), str(TOY_FLOOR_FEASIBILITY_CAP), out_path,
        ]
        print("toy d=%d (eta=%d, beta_toy=%d): launching, cap=%ds" % (d, TOY_ETA, beta_toy, TOY_FLOOR_FEASIBILITY_CAP), flush=True)
        proc_info = run_capped_subprocess(argv, TOY_FLOOR_FEASIBILITY_CAP, out_path)

        toy_result = {"d": d, "eta": TOY_ETA, "beta_toy": beta_toy}
        toy_result.update({
            "subprocess_wall_clock_seconds": proc_info["wall_clock_seconds"],
            "peak_rss_mb": proc_info["peak_rss_mb"],
            "subprocess_timed_out": proc_info["timed_out"],
        })
        if proc_info["timed_out"] or not os.path.exists(out_path):
            toy_result["status"] = "NOT_COMPUTED"
            toy_result["reason"] = "infeasible within TOY_FLOOR_FEASIBILITY_CAP" if proc_info["timed_out"] else (
                "worker crashed before writing output"
            )
            toy_result["stderr_tail"] = proc_info["stderr_tail"]
        else:
            with open(out_path) as f:
                worker_out = json.load(f)
            toy_result.update(worker_out)
        print("  -> %s (%.1fs)" % (toy_result["status"], proc_info["wall_clock_seconds"]), flush=True)
        overall["toy_floor_sweep"].append(toy_result)
        if toy_result["status"] == "COMPLETED":
            selected_d = d
        if os.path.exists(out_path):
            os.remove(out_path)

    overall["selected_toy_floor_d"] = selected_d
    overall["selected_toy_floor_d_reason"] = (
        "largest d in {8,12,16,20} whose exhaustive search completed within cap"
        if selected_d is not None else
        "NOT COMPUTED: infeasible within budget -- even d=8 did not complete "
        "(8f8f45's own C2-F3)"
    )

    cleared_cells = [c for c in overall["main_grid"] if c.get("status") == "COMPLETED"]
    overall["n_cells_cleared"] = len(cleared_cells)
    overall["n_cells_dropped"] = len(overall["main_grid"]) - len(cleared_cells)
    overall["every_cell_dropped"] = len(cleared_cells) == 0
    overall["termination_branch"] = (
        "T-PROJNOISE-NODATA (Stage 0 dropped every (d,beta) cell)"
        if overall["every_cell_dropped"] else
        "Stage 0 cost report -- %d/%d cells cleared" % (len(cleared_cells), len(overall["main_grid"]))
    )

    overall["total_script_wall_clock_seconds"] = time.time() - t_script_start

    print(json.dumps(overall, indent=2))
    with open(os.path.join(HERE, "stage0_results.json"), "w") as f:
        json.dump(overall, f, indent=2)
    return overall


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--worker-cell":
        worker_main_cell(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    elif len(sys.argv) > 1 and sys.argv[1] == "--worker-toyfloor":
        worker_toy_floor(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5]), sys.argv[6])
    else:
        main()
