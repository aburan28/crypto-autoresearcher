#!/bin/sh
# Launch the r=6 CTRL arm the instant the r=6 M1 arm releases its 8 GB, so the
# paired comparison is not lost to polling latency. 2 threads: the engine is
# value-partitioned, so 2 threads halves each thread's write footprint (2 GB)
# and uses the 2 threads this task is permitted.
cd "$(dirname "$0")"
while [ ! -s arm_r6_M1.json ]; do sleep 5; done
sleep 2
K=6fe52e2e9b3ea04085c370f9bc609245; B=e35f00e7631cdd862e59d126e72b8fc9
CTRL=02030101010203010101020303010102
echo "CMD ARM2 r6_CTRL ./cnt soft 6 0 $K $B $CTRL 8 0 2  (launched $(date -u +%H:%M:%SZ))" >> commands.txt
./cnt soft 6 0 $K $B $CTRL 8 0 2 > arm_r6_CTRL.json 2> arm_r6_CTRL.err
