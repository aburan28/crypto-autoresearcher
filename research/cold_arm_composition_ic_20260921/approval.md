# DEC-20260921-ab908a — conditional approval of RUN-KIC-a15078

**Decision:** approve this complete four-arm common-ARM composition design under standing authorization. Stage A permits implementation, offline build, and frozen controls. Stage B solver controls and Stage C science require accepted P3 source/certificate/cost review and their own committed custody gates.

The design strengthens both IC and rho: PMULL fused multiply/square/reduction, n53 Itoh inversion, and IC’s ARM compact-dual-sign query batch. It preserves generic/x86 paths and charges all P3 certificate and group-validation work. The primary comparison is new IC/new rho only; old rho cannot substitute for it. No timing saving is assumed because common primitives may accelerate rho substantially.

It freezes 24 fresh known-answer targets, all 24 four-arm orders, 96 serial fresh processes, exhaustive native/oracle, P3 certificate, batch-semantic, and eight untimed solver controls. Full wait4 wall/CPU/RSS boundaries, no retry, sampled cooperative cap, and separate build cost bind. This is finite implementation evidence only and changes no research status.
