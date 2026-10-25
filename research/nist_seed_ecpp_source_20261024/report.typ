#set page(paper:"a4",margin:(x:17mm,y:16mm))
#set text(font:"Helvetica",size:10pt)
#set par(justify:true)

= Recovered ECPP source exposes a concrete workflow hypothesis

*24 October 2026 UTC. Retrospective static audit; no named curve order executed.*

A preserved ECPP V3.4.1 package includes C source, arithmetic dependencies, discriminant data, factoring tactics and a certificate checker. Two mirrors supply identical bytes. An October 1996 thesis names the same distribution, giving a pre-May-1997 reference. This does not authenticate today's exact archive bytes as a 1996 capture or connect the package to the NIST/ANSI generator.

== A failed certificate search has a misleading caller label

The code searches a finite discriminant catalog to build a recursive certificate chain. If it exhausts that search, it retries once at the failed depth with additional factoring tactics. A second failure propagates zero to the top-level function. Its command-line caller labels that return “composite.” A successful chain proceeds to the proving phase, which is enabled by default.

#image("failure_path.svg",width:100%)

_Solid edges are inspected source branches. The dashed edge marks missing evidence. No prime input was run through this path, and no original caller was recovered._

If a true prime reaches the failure branch, that label is not a compositeness proof. An external caller could discard its associated curve. Whether any named omitted or published order actually reaches this branch is untested. The source therefore gives a specific candidate mechanism, not an explanation of the eleven omissions or a hidden mathematical weakness.

The 1997 X9.62 draft offers optional GKA certificates. Its curve-generation path does not impose them. The previous N−1 factor proxy did not test this elliptic-curve certificate workflow, so this acquired implementation supplies a new discriminator for that remaining hypothesis.

#pagebreak()

== What the acquired catalog actually contains

The header declares a rank stop at 1,685. The supplied catalog has *1,684 records*, including one special D=0 route for N−1/N+1 and 1,683 CM entries, with maximum D=58,507. These numbers are catalog facts, not a guarantee that every prime has an available certificate in this table.

#image("catalog.svg",width:100%)

_Exact counts of stored absolute h entries; h values and Weber polynomials are not independently certified here. The special zero entry is not an ordinary CM class. Editable graph: render.py; raw metadata: source_audit.json._

Fourteen factoring-parameter rows supply length thresholds and sieve/rho/Pollard settings. Actual behavior also depends on word width, compilation flags, initial state and caller options. A compatibility port must preserve or explicitly amend those details before any curve-label comparison.

== Provenance and limits

The FUNET and GWDG archives are both 1,481,933 bytes, SHA-256 0387e7d180e570d0cf1ff957ed281a46711fb20d50ae0b0669a01a3464d9160f. Their internal version file dates V3.4.1 to September 25, 1991. Chabaud's thesis cover dates its defense to October 22, 1996; printed page 135 (PDF 136) names the exact distribution. The contemporary citation supplies no payload digest. Matching present-day mirrors are not independent historical authentication.

Both direct author-site requests failed to connect. Two bounded archive-prefix queries are retained with their exact scope; empty results do not establish general absence. The source package was read without extracting or executing its bundled code. Twelve selected file hashes, the inventory, all catalog/parameter rows, version and thesis bindings are in source_audit.json.

A separate same-session parser checked the payloads, file hashes, every catalog row, all fourteen parameter rows and source-text guards. Those guards complement a manual branch walk; they are not a compiler proof or a demonstrated false classification of a prime. Both PDF pages were visually inspected.

== The next check remains an execution obligation

REPLAY_REQUIREMENTS.md describes the missing compatibility build, fail-closed launcher/checker and complete 21-order replay with controls and immutable traces. It is not an approved experiment or ready launcher. All-success would exclude this fixed configuration as a selector; any failure requires an exact cause; an all-eleven split would still require wider prediction, independent validation and historical provenance.

The original selection problem remains open. This source audit changes no scientific status, ECDLP frontier, attack cost or isogeny claim.

#set par(justify:false)
*Primary objects:* mirrors.nic.funet.fi/pub/crypt/math/ecpp.V3.4.1.tar.Z; ftp3.gwdg.de/pub/misc/crypt/math/ecpp.V3.4.1.tar.Z; di.ens.fr/reports/1996/liens-96-14.A4.pdf. Full URLs, hashes, commands and source-branch references: report.md, source_audit.json and retrieval.json.
