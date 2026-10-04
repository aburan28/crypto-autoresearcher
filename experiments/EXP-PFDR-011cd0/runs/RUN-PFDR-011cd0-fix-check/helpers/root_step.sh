#!/bin/bash
# root_step.sh RUN_DIR -- command...   : run a run-root step, log it into RUN_DIR/{command.txt,stdout.log,stderr.log}
RD=$1; shift; [ "$1" == "--" ] && shift
cd /home/user/crypto-autoresearcher
TS=$(date -u +%FT%TZ)
echo "$*" >> $RD/command.txt
echo "[$TS] \$ $*" >> $RD/stdout.log
echo "[$TS] \$ $*" >> $RD/stderr.log
PYTHONDONTWRITEBYTECODE=1 "$@" >> $RD/stdout.log 2>> $RD/stderr.log
RC=$?
echo "[exit $RC]" >> $RD/stdout.log
echo "$RC"
