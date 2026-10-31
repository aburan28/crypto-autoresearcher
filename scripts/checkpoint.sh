#!/usr/bin/env bash
# Resume checkpoints in S3: before an experiment runs, everything needed to
# resume it from a fresh session (handoff note, specs and leads, unpushed
# commits, uncommitted changes, untracked files) is uploaded to S3, so a
# session that dies (token exhaustion, crash, reclaimed container) loses
# nothing that was only in its worktree.
#
#   scripts/checkpoint.sh init                 write .resume/RESUME.md from the template
#   scripts/checkpoint.sh push [--force]       upload a checkpoint of this worktree (skips if unchanged)
#   scripts/checkpoint.sh gate                 exit non-zero unless RESUME.md is complete and pushed
#   scripts/checkpoint.sh status               show what the next push would contain
#   scripts/checkpoint.sh list [repo] [--all]  latest checkpoint per branch (default: this repo)
#   scripts/checkpoint.sh restore <repo>/<branch>[/<stamp>] | <presigned-url>  [dir]
#                                              rebuild a worktree from a checkpoint
#   scripts/checkpoint.sh presign-upload [--days N] [--install]
#                                              mint an upload token (needs AWS creds)
#   scripts/checkpoint.sh share <repo>/<branch>[/<stamp>] [--days N]
#                                              presigned GET URL for a checkpoint (needs AWS creds)
#
# Claude Code sessions have no AWS credentials; they use a token: a presigned
# S3 POST policy that can write (not read, list or delete) keys under $PREFIX/
# for up to 7 days, plus index_url, a presigned GET of an index of recent
# checkpoints with their own presigned download URLs, so list, share and
# restore need no credentials either. The token is tried first; the AWS
# profile is only a fallback. Mint one where credentials exist (presign-upload) and give
# it to the session as CHECKPOINT_UPLOAD_TOKEN or in the token file. It is a
# bearer credential: never commit it or paste it into a PR.
#
# Configuration (environment):
#   CHECKPOINT_BUCKET       default setec-astronomy-artifacts
#   CHECKPOINT_PREFIX       default checkpoints
#   CHECKPOINT_AWS_PROFILE  default ecc-challenges-new (used when that profile exists;
#                           otherwise the ambient AWS credentials are used)
#   CHECKPOINT_AWS_REGION   default us-east-2
#   CHECKPOINT_UPLOAD_TOKEN upload token from presign-upload (used when no AWS creds)
#   CHECKPOINT_TOKEN_FILE   default ~/.config/checkpoint/upload-token
#   CHECKPOINT_MAX_FILE_MB  untracked files above this are listed, not uploaded (default 25)
#   CHECKPOINT_MAX_TOTAL_MB cap on the untracked tarball input (default 300)
#
# Layout: s3://$BUCKET/$PREFIX/<repo>/<branch>/<UTC stamp>-<sha>/
#   checkpoint.tar.gz  (meta.json RESUME.md relay/<HANDOFF.md handoff.json relay.jsonl>
#                       files/<spec and lead files>
#                       branch.bundle worktree.patch untracked.tar.gz
#                       skipped-untracked.txt)
#   RESUME.md  meta.json  (copies, for reading without unpacking)
# plus s3://$BUCKET/$PREFIX/<repo>/<branch>/LATEST naming the newest stamp.
# Checkpoint directories are never overwritten; LATEST is only a pointer.
set -euo pipefail

BUCKET="${CHECKPOINT_BUCKET:-setec-astronomy-artifacts}"
PREFIX="${CHECKPOINT_PREFIX:-checkpoints}"
PROFILE="${CHECKPOINT_AWS_PROFILE:-ecc-challenges-new}"
REGION="${CHECKPOINT_AWS_REGION:-us-east-2}"
TOKEN_FILE="${CHECKPOINT_TOKEN_FILE:-$HOME/.config/checkpoint/upload-token}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAX_FILE_MB="${CHECKPOINT_MAX_FILE_MB:-25}"
MAX_TOTAL_MB="${CHECKPOINT_MAX_TOTAL_MB:-300}"

# Repo-relative paths that count as specs, leads or protocols. Matched
# case-insensitively against the path; build output is excluded separately.
SPEC_RE='(^|/)experiments/specs/[^/]+\.ya?ml$|(^|/)[^/]*(^|[ _./-])(leads?|protocol|prereg[a-z]*|spec|specs|plan|handoff|resume)([ _.-][^/]*)?\.(md|ya?ml|json|toml)$'
EXCLUDE_RE='(^|/)(target|node_modules|\.git|cargo-target[^/]*|\.cache[^/]*)/'

REQUIRED_SECTIONS=("Goal" "Lead / hypothesis" "Spec" "State" "Next steps" "Runs in flight" "Stop and success conditions")

die() { echo "checkpoint: $*" >&2; exit 1; }

aws_() {
  if aws configure list-profiles 2>/dev/null | grep -qx "$PROFILE"; then
    env -u AWS_ACCESS_KEY_ID -u AWS_SECRET_ACCESS_KEY -u AWS_SESSION_TOKEN -u AWS_PROFILE \
      aws --profile "$PROFILE" --region "$REGION" "$@"
  else
    aws --region "$REGION" "$@"
  fi
}

have_profile() { aws configure list-profiles 2>/dev/null | grep -qx "$PROFILE"; }

upload_token() {
  if [ -n "${CHECKPOINT_UPLOAD_TOKEN:-}" ]; then printf '%s' "$CHECKPOINT_UPLOAD_TOKEN"
  elif [ -s "$TOKEN_FILE" ]; then tr -d '[:space:]' < "$TOKEN_FILE"
  fi
}

# Which way uploads go: "token" (presigned POST, needs no AWS credentials) or
# "aws" (a credentialed profile or ambient keys). Prints the reason to stderr
# when neither works.
transport() {
  local tok; tok="$(upload_token)"
  if [ -n "$tok" ]; then
    local exp
    exp="$(printf '%s' "$tok" | python3 -c 'import base64,json,sys;print(json.loads(base64.b64decode(sys.stdin.read()))["expires"])' 2>/dev/null)" \
      || { echo "checkpoint: upload token is malformed" >&2; return 1; }
    if [[ "$exp" < "$(date -u +%Y-%m-%dT%H:%M:%SZ)" ]]; then
      echo "checkpoint: upload token expired at $exp; mint a new one with 'scripts/checkpoint.sh presign-upload'" >&2; return 1
    fi
    echo token; return
  fi
  command -v aws >/dev/null && have_profile && { echo aws; return; }
  command -v aws >/dev/null && [ -n "${AWS_ACCESS_KEY_ID:-}" ] && [ -n "${AWS_SECRET_ACCESS_KEY:-}" ] && { echo aws; return; }
  echo "checkpoint: no way to upload: no AWS profile '$PROFILE', no CHECKPOINT_UPLOAD_TOKEN, no $TOKEN_FILE" >&2
  return 1
}

# put <local file> <key>
put() {
  local how="$1" src="$2" key="$3"
  if [ "$how" = aws ]; then
    aws_ s3 cp --only-show-errors "$src" "s3://$BUCKET/$key"
    return
  fi
  local tok args=() line code
  tok="$(upload_token)"
  while IFS= read -r -d '' line; do args+=("$line"); done < <(printf '%s' "$tok" | python3 -c '
import base64, json, sys
t = json.loads(base64.b64decode(sys.stdin.read()))
out = [t["url"]] + [f"{k}={v}" for k, v in t["fields"].items()]
sys.stdout.write("\0".join(out) + "\0")')
  case "$key" in "$PREFIX"/*) ;; *) echo "checkpoint: token cannot write $key" >&2; return 1 ;; esac
  local url="${args[0]}" form=()
  for line in "${args[@]:1}"; do form+=(-F "$line"); done
  code="$(curl -sS -o /dev/null -w '%{http_code}' "${form[@]}" -F "key=$key" -F "file=@$src" "$url")" || return 1
  [ "$code" = 204 ] || [ "$code" = 200 ] || [ "$code" = 201 ] || { echo "checkpoint: presigned upload of $key returned HTTP $code" >&2; return 1; }
}

# Export the profile's keys so checkpoint_presign.py can sign with them.
signing_env() {
  have_profile || { [ -n "${AWS_ACCESS_KEY_ID:-}" ] && return 0; die "signing needs AWS profile '$PROFILE' or AWS_* keys"; }
  eval "$(env -u AWS_ACCESS_KEY_ID -u AWS_SECRET_ACCESS_KEY -u AWS_SESSION_TOKEN -u AWS_PROFILE \
    aws configure export-credentials --profile "$PROFILE" --format env)"
}

top() { git rev-parse --show-toplevel 2>/dev/null || die "not inside a git worktree"; }

repo_name() {
  local url
  url="$(git config --get remote.origin.url 2>/dev/null || true)"
  if [ -n "$url" ]; then basename "${url%.git}"; else basename "$(git rev-parse --path-format=absolute --git-common-dir | sed 's#/\.git$##')"; fi
}

branch_key() {
  local b
  b="$(git symbolic-ref --quiet --short HEAD 2>/dev/null || echo "detached-$(git rev-parse --short HEAD)")"
  printf '%s' "$b" | sed 's#/#__#g; s#[^A-Za-z0-9._=-]#-#g'
}

# GNU stat -f prints filesystem information before failing on BSD format flags.
# Its stdout contaminates a shell fallback, so use the already-required Python
# runtime for both GNU/Linux and macOS metadata without probing either syntax.
file_stat() {
  python3 - "$1" "${2:-fingerprint}" <<'PY'
import pathlib, sys
path = pathlib.Path(sys.argv[1])
info = path.stat()
if sys.argv[2] == "size":
    print(info.st_size)
else:
    print(str(path), info.st_size, info.st_mtime_ns)
PY
}

# Files that differ from what any remote already has: changed in unpushed
# commits, changed in the worktree or index, or untracked.
changed_files() {
  {
    if git rev-parse --verify -q HEAD >/dev/null; then
      local base
      base="$(git rev-list HEAD --not --remotes 2>/dev/null | tail -1)"
      [ -n "$base" ] && git diff --name-only "${base}^" HEAD 2>/dev/null || true
      [ -n "$base" ] && ! git rev-parse -q --verify "${base}^" >/dev/null && git ls-tree -r --name-only HEAD
      git diff --name-only HEAD
    fi
    git ls-files --others --exclude-standard
  } | sort -u | grep -Ev "$EXCLUDE_RE" || true
}

spec_files() {
  { changed_files | grep -iE "$SPEC_RE" || true; } | while IFS= read -r f; do [ -f "$f" ] && printf '%s\n' "$f"; done
  return 0
}

resume_problems() {
  local f=.resume/RESUME.md
  [ -f "$f" ] || { echo "missing $f (run: scripts/checkpoint.sh init, then fill it in)"; return; }
  grep -q 'TODO(checkpoint)' "$f" && echo "$f still has TODO(checkpoint) placeholders"
  local s
  for s in "${REQUIRED_SECTIONS[@]}"; do
    awk -v h="## $s" '
      $0 == h { inside = 1; next }
      inside && /^## / { exit }
      inside && $0 !~ /^[[:space:]]*(<!--.*-->)?[[:space:]]*$/ { found = 1 }
      END { exit found ? 0 : 1 }' "$f" || echo "$f section '## $s' is missing or empty"
  done
  return 0
}

state_hash() {
  local untracked_files metadata="" f entry
  untracked_files="$(git ls-files --others --exclude-standard)" || return 1
  # Collect outside the hash pipeline so metadata failures reach the caller.
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    [[ "$f" =~ $EXCLUDE_RE ]] && continue
    [[ "$f" = .resume/* ]] && continue
    if [ -f "$f" ]; then
      entry="$(file_stat "$f")" || return 1
      metadata+="$entry"$'\n'
    fi
  done <<< "$untracked_files"
  {
    git rev-parse HEAD 2>/dev/null || true
    git diff --binary HEAD 2>/dev/null || true
    [ -f .resume/RESUME.md ] && cat .resume/RESUME.md
    if [ -n "$metadata" ]; then printf '%s' "$metadata"; fi
  } | shasum -a 256 | cut -d' ' -f1
}

cmd_init() {
  cd "$(top)"
  mkdir -p .resume
  [ -f .resume/RESUME.md ] && die ".resume/RESUME.md already exists"
  cat > .resume/RESUME.md <<EOF
# Resume: $(repo_name) @ $(git symbolic-ref --quiet --short HEAD || git rev-parse --short HEAD)

<!-- Written for a fresh session with none of this conversation. A reader must
     be able to continue the work from this file and the checkpoint alone.
     Replace every placeholder line below; keep it current as the work moves. -->

## Goal
TODO(checkpoint): the question this effort answers and why it matters.

## Lead / hypothesis
TODO(checkpoint): the lead being pursued, where it came from (paper, earlier
run, report path), and what result would confirm or kill it.

## Spec
TODO(checkpoint): path to the experiment spec / protocol (e.g.
experiments/specs/EXP-....yaml, research/<slug>/PROTOCOL.md), frozen inputs,
seeds, curve identities, reference and baseline.

## State
TODO(checkpoint): what is done, what was measured so far (numbers with units
and where the raw output lives), what was ruled out, what is half-built.

## Next steps
TODO(checkpoint): ordered list, each with the exact command and the worktree
or host it runs in.

## Runs in flight
TODO(checkpoint): for every run started: command, host / instance id / pid,
log and output paths (local and S3), expected finish, how to check on it,
how to collect results. Write "none" when nothing is running.

## Stop and success conditions
TODO(checkpoint): budget, stop rule, what counts as success or failure.

## Open questions
EOF
  grep -qxF '.resume/' .gitignore 2>/dev/null || echo "note: add '.resume/' to .gitignore" >&2
  echo "wrote $(pwd)/.resume/RESUME.md"
}

cmd_status() {
  cd "$(top)"
  echo "s3 target : s3://$BUCKET/$PREFIX/$(repo_name)/$(branch_key)/"
  echo "unpushed  : $(git rev-list --count HEAD --not --remotes 2>/dev/null || echo 0) commit(s)"
  echo "spec files:"; spec_files | sed 's/^/  /'
  local p; p="$(resume_problems)"
  if [ -n "$p" ]; then echo "RESUME.md : NOT READY"; printf '%s\n' "$p" | sed 's/^/  /'; else echo "RESUME.md : ok"; fi
  local hash; hash="$(state_hash)" || die "cannot hash the current worktree"
  if [ -f .resume/.last-push ] && [ "$(cut -d' ' -f1 .resume/.last-push)" = "$hash" ]; then
    echo "last push : current ($(cut -d' ' -f2- .resume/.last-push))"
  else
    echo "last push : stale or none"
  fi
}

cmd_push() {
  local force=0 session="${CHECKPOINT_SESSION:-}"
  [ "${1:-}" = "--force" ] && force=1
  cd "$(top)"
  mkdir -p .resume
  local hash; hash="$(state_hash)" || die "cannot hash the current worktree"
  if [ $force = 0 ] && [ -f .resume/.last-push ] && [ "$(cut -d' ' -f1 .resume/.last-push)" = "$hash" ]; then
    echo "checkpoint: unchanged since $(cut -d' ' -f2- .resume/.last-push)"; return 0
  fi

  local repo branch sha stamp key stage
  repo="$(repo_name)"; branch="$(branch_key)"
  sha="$(git rev-parse --short=12 HEAD 2>/dev/null || echo nohead)"
  stamp="$(date -u +%Y%m%dT%H%M%SZ)-$sha"
  key="$PREFIX/$repo/$branch/$stamp"
  stage="$(mktemp -d "${TMPDIR:-/tmp}/checkpoint.XXXXXX")"
  trap 'rm -rf -- "$stage"; trap - RETURN' RETURN

  [ -f .resume/RESUME.md ] && cp .resume/RESUME.md "$stage/RESUME.md"
  # Runtime relay handoff (scripts/relay.py), so another runtime or host can take over.
  mkdir -p "$stage/relay"
  for f in HANDOFF.md handoff.json relay.jsonl; do [ -f ".resume/$f" ] && cp ".resume/$f" "$stage/relay/$f"; done
  rmdir "$stage/relay" 2>/dev/null || true

  local f
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    mkdir -p "$stage/files/$(dirname "$f")"; cp "$f" "$stage/files/$f"
  done < <(spec_files)

  local unpushed=0
  if git rev-parse --verify -q HEAD >/dev/null; then
    unpushed="$(git rev-list --count HEAD --not --remotes)"
    if [ "$unpushed" -gt 0 ]; then
      git bundle create -q "$stage/branch.bundle" HEAD --not --remotes
    fi
    git diff --binary HEAD > "$stage/worktree.patch"
    [ -s "$stage/worktree.patch" ] || rm -f "$stage/worktree.patch"
  fi

  local maxb=$((MAX_FILE_MB * 1024 * 1024)) capb=$((MAX_TOTAL_MB * 1024 * 1024)) total=0 sz
  : > "$stage/untracked.list"; : > "$stage/skipped-untracked.txt"
  while IFS= read -r f; do
    [ -f "$f" ] || continue
    sz="$(file_stat "$f" size)" || die "cannot size untracked file $f"
    if [ "$sz" -gt "$maxb" ] || [ $((total + sz)) -gt "$capb" ]; then
      printf '%s\t%s bytes\n' "$f" "$sz" >> "$stage/skipped-untracked.txt"
    else
      printf '%s\n' "$f" >> "$stage/untracked.list"; total=$((total + sz))
    fi
  done < <(git ls-files --others --exclude-standard | grep -Ev "$EXCLUDE_RE" | grep -v '^\.resume/' || true)
  [ -s "$stage/untracked.list" ] && tar -czf "$stage/untracked.tar.gz" -T "$stage/untracked.list"
  [ -s "$stage/skipped-untracked.txt" ] || rm -f "$stage/skipped-untracked.txt"
  rm -f "$stage/untracked.list"

  local upstream; upstream="$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || true)"
  python3 - "$stage/meta.json" <<PY
import json, sys
json.dump({
  "repo": "$repo",
  "origin": "$(git config --get remote.origin.url || true)",
  "branch": "$(git symbolic-ref --quiet --short HEAD || true)",
  "head": "$(git rev-parse HEAD 2>/dev/null || true)",
  "upstream": "$upstream",
  "unpushed_commits": int("$unpushed"),
  "worktree": "$(pwd)",
  "host": "$(hostname)",
  "user": "$(id -un)",
  "created_utc": "$stamp".split("-")[0],
  "session": "$session",
  "s3": "s3://$BUCKET/$key/",
  "restore": "scripts/checkpoint.sh restore $repo/$branch/$stamp",
  "share": "scripts/checkpoint.sh share $repo/$branch/$stamp   # presigned URL, then: restore <url>",
}, open(sys.argv[1], "w"), indent=2)
PY

  local how; how="$(transport)" || die "cannot upload, so nothing was checkpointed"
  local pack; pack="$(mktemp "${TMPDIR:-/tmp}/checkpoint-pack.XXXXXX")"
  tar -czf "$pack" -C "$stage" .
  put "$how" "$pack" "$key/checkpoint.tar.gz" || { rm -f "$pack"; die "upload to s3://$BUCKET/$key/ failed ($how)"; }
  rm -f "$pack"
  [ -f "$stage/RESUME.md" ] && put "$how" "$stage/RESUME.md" "$key/RESUME.md"
  put "$how" "$stage/meta.json" "$key/meta.json"
  printf '%s\n' "$stamp" > "$stage/LATEST"
  put "$how" "$stage/LATEST" "$PREFIX/$repo/$branch/LATEST" || die "uploaded, but updating LATEST failed"
  printf '%s %s s3://%s/%s/\n' "$hash" "$stamp" "$BUCKET" "$key" > .resume/.last-push
  echo "checkpoint: s3://$BUCKET/$key/ ($unpushed unpushed commit(s), $(spec_files | wc -l | tr -d ' ') spec file(s))"
}

cmd_gate() {
  cd "$(top)"
  local p; p="$(resume_problems)"
  if [ -n "$p" ]; then
    {
      echo "checkpoint gate: a resume checkpoint must be in S3 before an experiment runs."
      printf '%s\n' "$p" | sed 's/^/  - /'
      echo "Fill in .resume/RESUME.md (scripts/checkpoint.sh init writes the template) so a fresh"
      echo "session could resume from it alone, then re-run. The checkpoint is pushed automatically."
    } >&2
    return 2
  fi
  cmd_push || { echo "checkpoint gate: push failed, so the run is blocked." >&2; return 2; }
}

cmd_list() {
  local repo="" all=0 a
  for a in "$@"; do case "$a" in --all) all=1 ;; *) repo="$a" ;; esac; done
  [ -z "$repo" ] && [ $all = 0 ] && repo="$(repo_name)"
  local idx
  if idx="$(index_json 2>/dev/null)"; then
    printf '%s' "$idx" | python3 -c '
import json, sys
repo = sys.argv[1]
idx = json.load(sys.stdin)
print("# index generated", idx["generated_utc"], "(new checkpoints appear within ~15 min)")
for e in idx["entries"]:
    if repo and e["repo"] != repo:
        continue
    c = e["checkpoints"][0]
    print(c["stamp"] + "  " + e["repo"] + "/" + e["branch"] + "  (%d recent)" % len(e["checkpoints"]))' "$repo"
    return
  fi
  local base="s3://$BUCKET/$PREFIX/"; [ -n "$repo" ] && base="$base$repo/"
  aws_ s3 ls --recursive "$base" | awk '$4 ~ /\/LATEST$/ {print $1" "$2"  "$4}' | sort -r \
    | sed "s#  $PREFIX/#  #; s#/LATEST\$##"
}

# The token's index_url: a presigned GET of $PREFIX/_index/index.json, which the
# token job rewrites every 15 minutes with presigned GET URLs of recent
# checkpoints. Lets list, share and restore work without AWS credentials.
index_json() {
  local tok url
  tok="$(upload_token)"; [ -n "$tok" ] || return 1
  url="$(printf '%s' "$tok" | python3 -c 'import base64,json,sys;print(json.loads(base64.b64decode(sys.stdin.read())).get("index_url",""))' 2>/dev/null)"
  [ -n "$url" ] || return 1
  curl -fsS "$url"
}

# index_lookup <repo> <branch> [<stamp>]: print "<stamp> <tar_url>"
index_lookup() {
  index_json | python3 -c '
import json, sys
repo, branch, stamp = sys.argv[1], sys.argv[2], (sys.argv[3] if len(sys.argv) > 3 else "")
for e in json.load(sys.stdin)["entries"]:
    if e["repo"] == repo and e["branch"] == branch:
        for c in e["checkpoints"]:
            if not stamp or c["stamp"] == stamp:
                print(c["stamp"], c["tar_url"]); sys.exit(0)
sys.exit(1)' "$@"
}

# resolve <repo>/<branch>[/<stamp>] to "repo branch stamp" (needs AWS creds for LATEST)
resolve_ref() {
  local ref="$1" repo branch stamp=""
  repo="${ref%%/*}"; branch="${ref#*/}"
  case "$branch" in */*) stamp="${branch#*/}"; branch="${branch%%/*}" ;; esac
  [ -n "$stamp" ] || stamp="$(aws_ s3 cp --only-show-errors "s3://$BUCKET/$PREFIX/$repo/$branch/LATEST" - | tr -d '[:space:]')" \
    || die "cannot read LATEST without AWS creds; pass the stamp or a presigned URL"
  echo "$repo $branch $stamp"
}

cmd_share() {
  local ref="" days=7 a
  while [ $# -gt 0 ]; do case "$1" in --days) days="$2"; shift ;; *) ref="$1" ;; esac; shift; done
  [ -n "$ref" ] || die "usage: share <repo>/<branch>[/<stamp>] [--days N]"
  local -a ref_parts
  IFS=/ read -r -a ref_parts <<< "$ref"
  local hit; hit="$(index_lookup "${ref_parts[@]}" 2>/dev/null)" && { echo "${hit#* }"; return; }
  local repo branch stamp; read -r repo branch stamp < <(resolve_ref "$ref")
  signing_env
  python3 "$HERE/checkpoint_presign.py" get "$BUCKET" "$REGION" "$PREFIX/$repo/$branch/$stamp/checkpoint.tar.gz" $((days * 86400))
}

cmd_presign_upload() {
  local days=7 install=0
  while [ $# -gt 0 ]; do case "$1" in --days) days="$2"; shift ;; --install) install=1 ;; esac; shift; done
  signing_env
  local tok; tok="$(python3 "$HERE/checkpoint_presign.py" post "$BUCKET" "$REGION" "$PREFIX/" $((days * 86400)))"
  if [ $install = 1 ]; then
    mkdir -p "$(dirname "$TOKEN_FILE")"; ( umask 077; printf '%s\n' "$tok" > "$TOKEN_FILE" )
    echo "wrote $TOKEN_FILE (expires in $days day(s))" >&2
  else
    printf '%s\n' "$tok"
  fi
}

cmd_restore() {
  local ref="${1:-}" dest="${2:-}"
  [ -n "$ref" ] || die "usage: restore <repo>/<branch>[/<stamp>] | <presigned-url> [dir]"
  local dl; dl="$(mktemp -d "${TMPDIR:-/tmp}/restore.XXXXXX")"
  local repo branch stamp src
  local hit
  local -a ref_parts
  IFS=/ read -r -a ref_parts <<< "$ref"
  if [[ "$ref" != https://* ]] && hit="$(index_lookup "${ref_parts[@]}" 2>/dev/null)"; then
    ref="${hit#* }"
  fi
  if [[ "$ref" == https://* ]]; then
    src="${ref%%\?*}"
    curl -fsS -o "$dl/checkpoint.tar.gz" "$ref" || die "download of $src failed (expired URL?)"
  else
    read -r repo branch stamp < <(resolve_ref "$ref")
    src="s3://$BUCKET/$PREFIX/$repo/$branch/$stamp/checkpoint.tar.gz"
    aws_ s3 cp --only-show-errors "$src" "$dl/checkpoint.tar.gz" || die "download of $src failed"
  fi
  tar -xzf "$dl/checkpoint.tar.gz" -C "$dl"
  read -r repo branch stamp < <(python3 -c '
import json, sys
m = json.load(open(sys.argv[1])); s = m["s3"].rstrip("/").split("/")
print(m["repo"], s[-2], s[-1])' "$dl/meta.json")

  cd "$(top)"
  [ "$(repo_name)" = "$repo" ] || echo "warning: restoring $repo into a checkout of $(repo_name)" >&2
  local head; head="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["head"])' "$dl/meta.json")"
  local newb="restore/${branch//__//}-${stamp%%-*}"
  dest="${dest:-$(dirname "$(git rev-parse --path-format=absolute --git-common-dir | sed 's#/\.git$##')")/$repo-restore-${stamp%%-*}}"
  git fetch -q origin 2>/dev/null || echo "warning: git fetch origin failed; using local refs" >&2
  if [ -f "$dl/branch.bundle" ]; then
    git bundle verify -q "$dl/branch.bundle" >/dev/null 2>&1 || die "bundle prerequisites missing: fetch the base commits first"
    git fetch -q "$dl/branch.bundle" "HEAD:refs/heads/$newb"
  else
    git branch "$newb" "$head" || die "commit $head is not available locally or on origin"
  fi
  git worktree add -q "$dest" "$newb"
  [ -f "$dl/worktree.patch" ] && git -C "$dest" apply --binary "$dl/worktree.patch"
  [ -f "$dl/untracked.tar.gz" ] && tar -xzf "$dl/untracked.tar.gz" -C "$dest"
  mkdir -p "$dest/.resume"
  [ -f "$dl/RESUME.md" ] && cp "$dl/RESUME.md" "$dest/.resume/RESUME.md"
  [ -d "$dl/relay" ] && cp "$dl/relay/"* "$dest/.resume/"
  cp "$dl/meta.json" "$dest/.resume/restored-from.json"
  [ -f "$dl/skipped-untracked.txt" ] && { echo "Not in the checkpoint (too large):"; cat "$dl/skipped-untracked.txt"; }
  rm -rf "$dl"
  echo "restored $src"
  echo "  worktree: $dest (branch $newb)"
  echo "  read:     $dest/.resume/RESUME.md"
  if [ -f "$dest/.resume/HANDOFF.md" ]; then
    echo "  handoff:  $dest/.resume/HANDOFF.md (python3 scripts/relay.py accept)"
  fi
}

case "${1:-}" in
  init) shift; cmd_init "$@" ;;
  push) shift; cmd_push "$@" ;;
  gate) shift; cmd_gate "$@" ;;
  status) shift; cmd_status "$@" ;;
  list) shift; cmd_list "$@" ;;
  restore) shift; cmd_restore "$@" ;;
  share) shift; cmd_share "$@" ;;
  presign-upload) shift; cmd_presign_upload "$@" ;;
  *) sed -n '2,/^set -euo/p' "$0" | sed '$d; s/^# \{0,1\}//'; exit 64 ;;
esac
