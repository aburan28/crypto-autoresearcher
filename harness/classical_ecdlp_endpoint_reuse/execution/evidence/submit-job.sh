#!/usr/bin/env bash
# Thin Kubernetes submission wrapper; computation stays in the selected image.
set -euo pipefail
usage() {
  cat <<'EOF'
Usage: submit-job --image IMAGE [--name NAME] [--cpu EVEN_INTEGER]
                  [--memory QUANTITY] [--seconds N] [--retries N]
                  [--isolation-profile standard|l2] [--instance-type TYPE]
                  [--wait | --dry-run] -- COMMAND [ARG ...]

Defaults: 2 CPUs, 4Gi memory, 3600 seconds, no retries. Set KUBECONFIG
to the Iso Lab kubeconfig before submitting. --dry-run prints Job JSON.
Image must support UID 1000 and the supplied command (no shell is added).
/work is writable; ISOLAB_OUTPUT_DIR=/work/results. Upload durable outputs
to ISOLAB_RESULTS_URI (S3) before exiting; /work is temporary pod storage.
EOF
}
image=''
name="run-$(date -u +%Y%m%d-%H%M%S)-$(od -An -N3 -tx1 /dev/urandom | tr -d ' \n')"
cpu=2 memory=4Gi seconds=3600 retries=0 mode=submit
isolation_profile=standard
instance_type=''
while (($#)); do
  case "$1" in
    --image|--name|--cpu|--memory|--seconds|--retries)
      (($# >= 2)) || { usage >&2; exit 2; }
      key=${1#--}; printf -v "$key" '%s' "$2"; shift 2 ;;
    --isolation-profile)
      (($# >= 2)) || { usage >&2; exit 2; }
      isolation_profile=$2; shift 2 ;;
    --instance-type)
      (($# >= 2)) || { usage >&2; exit 2; }
      instance_type=$2; shift 2 ;;
    --wait) mode='wait'; shift ;;
    --dry-run) mode=dry; shift ;;
    -h|--help) usage; exit 0 ;;
    --) shift; break ;;
    *) usage >&2; exit 2 ;;
  esac
done
[[ -n "$image" && $# -gt 0 ]] || { usage >&2; exit 2; }
[[ "$name" =~ ^[a-z0-9]([-a-z0-9]*[a-z0-9])?$ && ${#name} -le 55 ]] || { echo 'Invalid job name' >&2; exit 2; }
[[ "$cpu" =~ ^([2468]|[12][02468])$ ]] || { echo 'CPU must be even, 2..28 (whole SMT cores, with system headroom)' >&2; exit 2; }
[[ "$seconds" =~ ^[1-9][0-9]{0,6}$ && "$retries" =~ ^[0-9]$ ]] || { echo 'Invalid deadline or retry count' >&2; exit 2; }
[[ "$memory" =~ ^[1-9][0-9]*(Mi|Gi)$ ]] || { echo 'Memory must be an integer Mi or Gi quantity' >&2; exit 2; }
[[ "$isolation_profile" == standard || "$isolation_profile" == l2 ]] || { echo 'Unknown isolation profile' >&2; exit 2; }
[[ -z "$instance_type" || "$instance_type" =~ ^[a-z][a-z0-9-]*\.[a-z0-9]+$ ]] || { echo 'Invalid EC2 instance type' >&2; exit 2; }
if [[ "$isolation_profile" == l2 && ( "$cpu" -lt 4 || "$retries" != 0 ) ]]; then
  echo 'L2 profile requires at least 4 CPUs and no automatic retries' >&2; exit 2
fi
manifest=$(mktemp)
trap 'rm -f "$manifest"' EXIT
jq -n --arg name "$name" --arg image "$image" --arg cpu "$cpu" --arg profile "$isolation_profile" \
  --arg instance_type "$instance_type" \
  --arg memory "$memory" --argjson seconds "$seconds" --argjson retries "$retries" \
  --args '$ARGS.positional as $command | {
  apiVersion:"batch/v1",kind:"Job",metadata:{name:$name,namespace:"isolab",labels:{"isolab.dev/job":"true"}},
  spec:{backoffLimit:$retries,activeDeadlineSeconds:$seconds,ttlSecondsAfterFinished:86400,
    template:{metadata:{labels:{"isolab.dev/job":"true"},annotations:{"karpenter.sh/do-not-disrupt":"true"}},
      spec:{restartPolicy:"Never",serviceAccountName:"runner",automountServiceAccountToken:false,
        terminationGracePeriodSeconds:60,
        nodeSelector:({"isolab.dev/pool":"cpu-spot"}
          + (if $profile == "l2" then {"isolab.dev/cpu-isolation":"v4"} else {} end)
          + (if $instance_type != "" then {"node.kubernetes.io/instance-type":$instance_type} else {} end)),
        tolerations:[{key:"isolab.dev/workload",value:"cpu",operator:"Equal",effect:"NoSchedule"}],
        affinity:{podAntiAffinity:{requiredDuringSchedulingIgnoredDuringExecution:[{
          labelSelector:{matchLabels:{"isolab.dev/job":"true"}},topologyKey:"kubernetes.io/hostname"}]}},
        securityContext:{runAsNonRoot:true,runAsUser:1000,runAsGroup:1000,fsGroup:1000,seccompProfile:{type:"RuntimeDefault"}},
        containers:[{name:"task",image:$image,command:$command,workingDir:"/work",
          env:[{name:"HOME",value:"/work"},{name:"AWS_REGION",value:"us-east-2"},
            {name:"AWS_DEFAULT_REGION",value:"us-east-2"},
            {name:"POD_UID",valueFrom:{fieldRef:{fieldPath:"metadata.uid"}}},
            {name:"NODE_NAME",valueFrom:{fieldRef:{fieldPath:"spec.nodeName"}}},
            {name:"ISOLAB_JOB_ID",value:$name},
            {name:"ISOLAB_OUTPUT_DIR",value:"/work/results"},
            {name:"ISOLAB_RESULTS_URI",value:("s3://isolab-results-104186811093-us-east-2/runs/"+$name+"/$(POD_UID)/")},
            {name:"RAYON_NUM_THREADS",value:$cpu},{name:"OMP_NUM_THREADS",value:$cpu}],
          resources:{requests:{cpu:$cpu,memory:$memory,"ephemeral-storage":"10Gi"},
                     limits:{cpu:$cpu,memory:$memory,"ephemeral-storage":"10Gi"}},
          securityContext:{allowPrivilegeEscalation:false,readOnlyRootFilesystem:true,capabilities:{drop:["ALL"]}},
          volumeMounts:[{name:"work",mountPath:"/work"},{name:"tmp",mountPath:"/tmp"}]}],
        volumes:[{name:"work",emptyDir:{sizeLimit:"8Gi"}},{name:"tmp",emptyDir:{sizeLimit:"1Gi"}}]}}}}' \
  -- "$@" > "$manifest"
if [[ "$mode" == dry ]]; then cat "$manifest"; exit 0; fi
: "${KUBECONFIG:?Set KUBECONFIG to the Iso Lab kubeconfig}"
kubectl create -f "$manifest"
if [[ "$mode" == wait ]]; then
  # Check both terminal states; waiting only for Complete hides early failures.
  end=$((SECONDS + seconds + 60))
  while ((SECONDS < end)); do
    status=$(kubectl -n isolab get job "$name" -o json)
    if jq -e '.status.conditions[]? | select(.type == "Complete" and .status == "True")' <<< "$status" >/dev/null; then
      kubectl -n isolab logs "job/$name" --all-containers=true
      exit 0
    fi
    if jq -e '.status.conditions[]? | select(.type == "Failed" and .status == "True")' <<< "$status" >/dev/null; then
      kubectl -n isolab logs "job/$name" --all-containers=true || true
      jq '.status' <<< "$status" >&2
      exit 1
    fi
    sleep 5
  done
  echo "Wait timed out; inspect job/$name (the Job deadline still applies)" >&2
  exit 1
fi
printf 'Inspect: kubectl -n isolab get job %s; kubectl -n isolab logs -f job/%s\n' "$name" "$name"
