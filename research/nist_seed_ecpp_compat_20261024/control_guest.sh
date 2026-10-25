#!/bin/sh
/work/runecpp "$@"
task_status=$?
printf '\nLEGACY_EXIT %s\n' "$task_status"
if [ -f /tmp/certificate ]; then
  printf 'CERTIFICATE_BEGIN\n'
  base64 /tmp/certificate
  printf 'CERTIFICATE_END\n'
fi
exit "$task_status"
