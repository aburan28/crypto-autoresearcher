# F3 source review before second-pass implementation

26 October 2026; `TASK-20261026-821d10`; reader `/root/pass2_labelled`.
This note precedes implementation and data collection. No novelty claim is made.

- **Retrieved primary text, read directly:** Amadori, Pintore and Sala,
  *On the discrete logarithm problem for prime-field elliptic curves*,
  <https://pure.tue.nl/ws/files/91158650/609.pdf>. I read the retained extraction
  `../../../p256_factor_base_parallel_20261025/tracks/f3/sources/aps2018.txt`,
  sections 3, 3.1 equations (9)--(11), 3.2 and 3.3. The retained PDF manifest
  binds the downloaded manuscript to SHA-256
  `970e425f7c50ca741ca3822c4f22d5e90a90b37e8b381eb53bddbf82198f45fb`.
  Section 3 uses labelled points `R_i=a_i G+b_i Q` in a prime-order group and
  seeks one zero sum. Section 3.1 uses disjoint coordinate partitions.
  Section 3.3 replaces the fourth summation polynomial by two third summation
  polynomials sharing one intermediate coordinate. Section 3.2 explicitly
  leaves system-solving cost unresolved and does not claim a rho improvement.
  The published numerical experiments use 11--22-bit fields; this pass does
  not extrapolate their timings to P-256.
- **Internal sources, read:** the first-pass `tracks/f3/labelled.py`,
  `validate.py`, `verify_sage.py`, `report.md` and `result.json`; and
  `corrections/f3-coefficients-mod-r.md`. These establish the earlier m=3
  interface, constructed-control distinction and coefficient qualification.
  They do not certify this new m=4 code. The correction requires the
  aggregated coefficient vector to be nonzero in `F_r^N`, not merely over
  the integers. Label-dependent selection and dependent labels fall outside
  its conditional-uniformity argument.
- **Primary-source gap:** Kudo et al., CANS 2018,
  <https://link.springer.com/chapter/10.1007/978-3-030-00434-7_19>.
  I read the prior access/provenance note, not the full chapter. I do not
  attribute a detailed limitation theorem, benchmark or algorithm to it.
- **Parameter provenance, retrieved before any data:** initial orientation
  used the constants and generator already bound in the first-pass source.
  After source preparation I additionally retrieved and directly read
  *Standards for Efficient Cryptography 2 (SEC 2)*, Version 2.0, 27 January
  2010, section 2.4.2, from <https://www.secg.org/sec2-v2.pdf>. Its title page
  says Version 2.0; running headers say Draft Ver. 2.0. I checked the displayed
  p, a, b, uncompressed G, order n and cofactor h=1 against the source's
  literals. PDF SHA-256 is
  `87b8f3703364ed5b21ba8582e411cc0cbf477bcaa3f4f45e0d6580d1c00d9952`.
  The downloaded PDF/extraction are local and ignored; `sec2-source.json`
  records their provenance. This parameter reading is not a new primality
  or point-count proof. Independent arithmetic checks remain unexecuted.
- **Workflow sources, read:** `AGENTS.md` literature-first and S3 checkpoint
  sections, `docs/experiment-protocol.md`, the experiment-protocol skill,
  the research-visuals skill, the committed handoff and execution-gates note.
  The implementation is Phase A only until root releases the frozen protocol
  and a successful real S3 checkpoint gate. The unresolved disclosure
  approval is not treated as permission.

The chosen implementation is an exact point-pair join realizing the rational
shared-coordinate system, with a separate Jacobian exhaustive oracle. It does
not implement a general Groebner solver, establish natural relation yield, or
improve a generic ECDLP exponent. Structured base points without supplied
labels would require a separate, fully costed labelling mechanism.
