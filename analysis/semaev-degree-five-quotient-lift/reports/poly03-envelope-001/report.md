# n=47 polynomial03 degree-five structural profile

The published, independently checked degree-four certificate for original `fresh-n47-poly-03` yields **30,546 degree-five working coordinates**. Two independent border enumerations both give 9,118 border coordinates. The frozen bounded native allocation formula gives **13,075,449,685 bytes** at chunk 60,000. This is an input-specific structural calculation, not a degree-five closure, measured peak memory, or new last-fall-degree lower bound.

| Original n=47 input | D4 codimension | D5 border | D5 working coordinates | Source-derived allocation envelope, chunk 60,000 |
|---|---:|---:|---:|---:|
| polynomial03 | 21,428 | 9,118 | 30,546 | 13,075,449,685 B |
| random00 | 61,196 | 126,387 | 187,583 | 92,117,754,292 B |

Polynomial03 has about 6.14 times fewer working coordinates and a 7.05 times smaller allocation envelope than random00 under the same source formula. This is a useful next candidate for a degree-five closure attempt after reconciling the active random00 Job. The formula cannot by itself establish that a particular host will complete the closure; production workspace, checker, allocator behavior, time, and any expansion of the quotient still matter.

The polynomial03 seed came from the [published certificate and readback receipt](../../highmem-archive/fresh-n47-poly-03-D5-cascade01-highmem01-D4.publication.json), decompressed to SHA-256 `44cd6ccd9a42cf88de8ba427d3891f1cd9be8235e402df3346aec6b8b8e0b53f`. Its published checker reports `VALID`, degree-four codimension at least 21,428 and an exact zero count, supporting the existing named-instance last-fall-degree bound at least five. The [frozen protocol](../../poly03-envelope-protocol-001.json) was committed before the [profile result](../../validation/poly03-envelope-001/result.json); the [manifest](../../validation/poly03-envelope-001/manifest.json) pins the data. The random00 comparison uses its separately [validated profile](../../validation/rand00-envelope-001/result.json).
