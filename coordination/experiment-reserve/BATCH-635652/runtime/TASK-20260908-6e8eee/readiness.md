# Isolated BSGS dependency preparation

Prepared local image `sha256:376f4a364f0b4cf1422b0f4ef1855b080e91ac858b47ef94dd8eee764d1eb3a7` from the exact pinned official Python base. A fresh read-only UID65534 container reproduced SymPy1.14.0,mpmath1.3.0 and every inventoried installed-file hash. No solver or fixture generator is included.

Three container starts were retained across two attempts: the initial installer reached successful pip installation/checks but failed writing its inventory; the approved retry completed installation and fresh verification. All three exact containers were removed after terminal inspection. Four wheel download calls used the same two approved hashes with TLS verification. The final local image remains for future tasks.

This is operational dependency preparation only. Independent review,complete source/manifest bindings and the actual group-OOM guard remain necessary before scientific admission. No scientific computation,performance result or8GiB guard pass is claimed.
