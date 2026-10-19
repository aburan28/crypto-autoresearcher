# Host binary build and bounded collector control

Question: can the frozen Rust collector and independent C++ ordered-count checker be reproduced as executable host binaries, and do those exact binaries pass the existing exhaustive small-group control?

The source hashes, build commands, compiler versions, platform, binary paths and binary hashes are bound in `../../binary_build_manifest.json`. Both binaries were compiled on the arm64 macOS host from the stated source-freeze commit. The commands use `-O` for Rust and `-O3 -std=c++17` for C++.

The control command recorded in the manifest exited 0. It checked all 18 nonidentity targets of the order-19 group over F17, compared all triple sets and counts with an exhaustive Python group-law oracle, exercised both Q-column cases and scalar row replay, checked ordered counts with the separate C++ program, and checked transported-base equality under the u=2 isomorphism. The output is in `stdout.txt`; `stderr.txt` is empty.

This is an implementation control on one bounded group. It does not measure P29 or P37 relation yield, target recovery cost, or performance. The executables remain at the absolute host paths in the manifest; a different host must rebuild and recheck their hashes before use. The previous source-level controls remain under `controls/small_group_20261015`.
