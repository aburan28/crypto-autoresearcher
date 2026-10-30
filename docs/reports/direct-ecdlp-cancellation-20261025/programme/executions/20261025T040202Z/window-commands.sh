#!/usr/bin/env bash
set -euo pipefail
g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion -Wshadow '/workspace/deliverables/non-ic-ecdlp-20261025/programme/window-control.cpp' -o '/workspace/programme-execution/20261025T040202Z/window-control'
'/workspace/programme-execution/20261025T040202Z/window-control' --self-test
g++ -std=c++20 -O1 -g -Wall -Wextra -Wpedantic -Wconversion -Wshadow -fsanitize=address,undefined -fno-omit-frame-pointer '/workspace/deliverables/non-ic-ecdlp-20261025/programme/window-control.cpp' -o '/workspace/programme-execution/20261025T040202Z/window-control-sanitized'
env ASAN_OPTIONS=detect_leaks=0 '/workspace/programme-execution/20261025T040202Z/window-control-sanitized' --self-test
