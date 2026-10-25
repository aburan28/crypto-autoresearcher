#set page(paper:"a4",margin:(x:16mm,y:16mm))
#set text(font:"Helvetica",size:9.5pt)
#set par(justify:true)

= A routine call can supply the seven-output FreeLIP prefix

*24 October 2026 UTC. Configured-software result; historical attribution remains unknown.*

The six May 1997 base-point reconstructions use a FreeLIP RNG seeded with a small integer and skip seven outputs before constructing random x-coordinates. In a portable 26-bit FreeLIP 1.0 build, an ordinary eight-base probable-prime call produces the same prefix and all six published x-coordinates.

Both #raw("zprobprime(v,7)") and #raw("zprime(v,8,2)") match, with either the field prime p or group order n as v. The initializer itself consumes no random outputs. These four routine call paths provide *24 of 24* matching point results; manual discard seven adds six baseline matches. The 24 wrong-prefix or 30-bit controls match none.

#image("point_matches.svg",width:100%)

_Each cell compares the first accepted point's x-coordinate with published Gx. The source library supplies the actual calls; a separate Python RNG and point replay verifies every state and output. Source: runs/prefix-v2/results.json and verification.json; editable graph: render.py._

== The scope of the finding

This supplies several call-level reconstructions of an already reported numerical prefix. It does not tell which call, if any, was made historically. The November 1997 X9.62 draft requires at least fifty tests in its specified probable-prime test, so an eight-base call cannot be equated with that standard's mandatory check. An auxiliary or private call remains possible but undocumented.

#image("inference.svg",width:100%)

The same eight-base order test accepted all 21 named large prime orders, including all eleven omissions, and consumed seven states on each. It therefore provides no selector between those curves. The two small controls returned the expected classifications without consuming RNG output.

The first SINGLE_MUL build's first point case exceeded its watchdog. Its failure remains archived; the complete 77-case replay uses the unchanged source with portable PLAIN arithmetic and explicit 26-bit limbs. This does not establish an original compiler mode or processor. See BUILD_AMENDMENT.md.

#set par(justify:false)
*Sources and evidence:* FreeLIP 1.0 archive, SHA-256 cd168c2ba0f9052d84072664b559219506050f583fdf58060517d59422f5bccc; Anthropic's published six small seeds and point recipe; ANSI X9.62 November 1997, section F.2.1. Exact URLs, curve UIDs, code/source/configuration hashes, commands, failure record and limits are in report.md and the linked run records.
