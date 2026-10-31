#set page(paper: "a4", margin: 20mm)
#set text(size: 10.5pt)
= n47 random03 blocked-lift capacity and arithmetic correction
The accepted n47 random03 D4 seed has 61,196 quotient coordinates. Independent border enumerations agree on 126,387 new coordinates, giving 187,583 D5 working coordinates. The fixed-chunk base payload is 68,185,663,280 bytes. This profile did not run D5 closure.

The earlier random02 additional-workspace note omitted two padded 64-bit words in each native map and seed stride. Corrected extra payload is 1,588,508,128 bytes. The source's integer 135/100 margin plus 64 MiB gives a corrected envelope of *94,262,240,264 bytes*, leaving *8,816,974,840 bytes* below the 96 GiB child limit. The old note understated the envelope by 1,498,780 bytes. The active cloud binary enforces its own allocation guard.

#image("capacity.svg", width: 100%)

Source records: validation/rand03-envelope-001/result.json; validation/rand02-envelope-001/result.json; runtime/blocked-envelope-correction-001.json. Original D4 checker acceptance and fresh exact count two are in reports/rand03-d4-local-001. A later D5 result needs fresh counting and independent checking. This source calculation alone establishes no new fall-degree bound.
