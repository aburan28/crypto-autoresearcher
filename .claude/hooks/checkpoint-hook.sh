#!/usr/bin/env bash
# Claude Code hook for scripts/checkpoint.sh (resume checkpoints in S3).
#
#   PostToolUse  Write|Edit|MultiEdit  a spec, leads, protocol or plan file, or
#                .resume/RESUME.md, was written: push a checkpoint of that worktree.
#   PreToolUse   Bash                  the command launches an experiment run:
#                block it unless RESUME.md is complete and the checkpoint is in S3.
#   SessionStart                       point a new session at an existing RESUME.md.
#
# A run that genuinely needs no checkpoint (a smoke test, a unit test that
# happens to match) can opt out with "CHECKPOINT_SKIP=<reason>" in the command.
set -uo pipefail

input="$(cat)"
field() { printf '%s' "$input" | python3 -c '
import json, sys
d = json.load(sys.stdin)
for k in sys.argv[1].split("."):
    d = d.get(k) if isinstance(d, dict) else None
print("" if d is None else d)' "$1"; }

event="$(field hook_event_name)"
cwd="$(field cwd)"
export CHECKPOINT_SESSION="$(field session_id)"

# Commands that start experiment work. Kept broad on purpose: a false positive
# costs one filled-in RESUME.md; a miss costs the run's context.
LAUNCH_RE='(^|[;&|( ]|\$\()(nohup|setsid|disown)\b|tmux +(new|new-session)\b|screen +-[dS]|scripts/run_[A-Za-z0-9_]+|scripts/[A-Za-z0-9_./-]*(sweep|bench|launch|deploy|fanout|tournament)[A-Za-z0-9_.-]*|\bexpspec +run\b|\bautolab\b|\becbench\b|\bsage-run\b|\bicms\b|cargo +run\b[^;&|]*--release|cargo +bench\b|\brunpod\b|aws +ec2 +run-instances|\bsbatch\b|\bmodal +run\b'

case "$event" in
  SessionStart)
    root="$(git -C "${cwd:-.}" rev-parse --show-toplevel 2>/dev/null)" || exit 0
    [ -f "$root/.resume/RESUME.md" ] || exit 0
    echo "This worktree has a resume note: $root/.resume/RESUME.md (read it before continuing the work it describes)."
    [ -f "$root/.resume/.last-push" ] && echo "Last checkpoint: $(cut -d' ' -f3 "$root/.resume/.last-push")"
    [ -f "$root/.resume/restored-from.json" ] && echo "Restored from: $(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["s3"])' "$root/.resume/restored-from.json")"
    exit 0
    ;;
  PostToolUse)
    file="$(field tool_input.file_path)"
    [ -n "$file" ] || exit 0
    dir="$(dirname "$file")"
    [ -d "$dir" ] || exit 0
    root="$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null)" || exit 0
    [ -x "$root/scripts/checkpoint.sh" ] || exit 0
    rel="${file#"$root"/}"
    spec_re="$(sed -n "s/^SPEC_RE='\(.*\)'$/\1/p" "$root/scripts/checkpoint.sh")"
    printf '%s\n' "$rel" | grep -qiE "$spec_re" || exit 0
    if ! out="$(cd "$root" && scripts/checkpoint.sh push 2>&1)"; then
      echo "Resume checkpoint push failed after writing $rel:" >&2
      printf '%s\n' "$out" >&2
      exit 2
    fi
    exit 0
    ;;
  PreToolUse)
    cmd="$(field tool_input.command)"
    bg="$(field tool_input.run_in_background)"
    [[ "$cmd" == *CHECKPOINT_SKIP=* ]] && exit 0
    if [ "$bg" != "True" ] && ! printf '%s' "$cmd" | grep -qE "$LAUNCH_RE"; then
      exit 0
    fi
    root="$(git -C "${cwd:-.}" rev-parse --show-toplevel 2>/dev/null)" || exit 0
    [ -x "$root/scripts/checkpoint.sh" ] || exit 0
    if ! out="$(cd "$root" && scripts/checkpoint.sh gate 2>&1)"; then
      printf '%s\n' "$out" >&2
      echo "(If this command is not an experiment run, prefix it with CHECKPOINT_SKIP=<reason>.)" >&2
      exit 2
    fi
    exit 0
    ;;
esac
exit 0
