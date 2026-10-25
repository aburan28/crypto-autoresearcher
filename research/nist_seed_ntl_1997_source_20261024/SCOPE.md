# Scope: period NTL source acquisition and default-call audit

Date: 2026-10-24 UTC. This is a retrospective primary-source audit. The relevant functions were read before this scope file was written; no prospective discovery or original-program replay is claimed.

Acquire and bind the Internet Archive's March 1997 `ntl.tar.Z`, August 1997 `ntl-1.5.tar.Z`, March tour page and May 10 homepage. Check every raw payload against its CDX SHA-1 base32 digest and compute SHA-256. The May homepage advertises NTL 1.5 before the recovered May seed inputs; the tarball's August capture must not be mistaken for a release date.

Compare source bodies of `ProbPrime(const ZZ&,long)` and `SqrRootMod` between the two archives. Inspect default trial count, `RandomLen(long)`, both `RandomBnd` overloads and `zrandomb`. For a large prime input and the recovered 26-bit limb configuration, derive the number of RNG calls consumed by one *default* `ProbPrime` invocation: one small-base draw plus ten full-size draws, each using one limb more than the input. Internal rejection can add state advances. Derive the lower bounds for the six May fields and orders from the exact archived p,n; do not assume an original caller or fit another trial count.

Check whether this one default call can substitute for the observed seven-output prefix in the previously reproduced recipe. This excludes only the named default call as that prefix under the stated configuration; combined calls, caller-selected parameters, earlier initialization, other APIs and other software remain untested. Read the randomized square-root routine's precondition and record it without treating misuse as observed historical behavior.

No NTL executable or point counter is compiled or run in this audit. No source-identical generator is claimed recovered. Archive the source digests/URLs, CDX response, function-body fingerprints and source-derived counts; keep the source archives externally retrievable rather than redistribute them. Produce a dated report, editable diagram/chart and inspected PDF, and update the existing open problem. No ECDLP cost or hypothesis-status transition.
