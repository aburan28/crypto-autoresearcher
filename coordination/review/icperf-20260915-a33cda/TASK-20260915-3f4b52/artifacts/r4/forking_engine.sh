#!/bin/bash
# a "forking engine": prints a version line, forks a grandchild that holds stdout and lives 300 s,
# then the direct child itself blocks reading stdin (like Singular).
echo "forking-engine version 0.0"
( exec sleep 300 ) &
echo "grandchild pid $!" >&2
read -r line
