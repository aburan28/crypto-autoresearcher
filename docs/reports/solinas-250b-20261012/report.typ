#set page(paper:"a4",margin:(x:17mm,y:16mm),numbering:"1")
#set text(font:"DejaVu Sans",size:9.5pt)
#set par(leading:0.6em)
= 250-billion campaign preparation
Preparation and engineering observations only. The scientific run has not
been launched; data destination/retention selection is required.12 October2026.

Exactly250,000,000,000 point observations;976,562,500256-point window
observations;443,892,000 independent-start draws. Named cohorts share Q.
Actual published G and fresh rG controls;125 ordinary models (62 R+63 C).
Coefficients and step x matched; group/step orders unmatched; primes reused.

#image("design.svg",width:100%)

#pagebreak()
= Prospective power and launch dependency
#image("power.svg",width:100%)

Primary:18 exact paired+2 approximate field tests; alpha0.0001/20, nominal99.99%
with field-approximation caveat. Separate30-rate CP family, nominal99.99%; union
nominal99.98%. Infer only after the exact fixed target; no interim p-value stop.

Doubling a1e-6 baseline has99.93% modeled power. Doubling the fair-coin run32
reference5.26e-8 has only0.104%. Independent-arm planning assumptions; actual
dependence changes power. Fair coin is a benchmark, not a point-bit IID premise.

Five distinct-seed engineering tests passed. The13,312-point fixture verifies
14-job aggregate/resume/analysis and corrupt-record refusal. Native complete
coordinate hashes, bounded frames and resource stops checked. Fake S3 validates
checksum/error logic, not live AWS access. All125 public model order/membership
preparations passed. No250-billion result or separate research review is claimed.

Current filesystem:32 GB total, approximately550 MB free; no configured AWS
identity in runtime revision121. Full compact data need roughly60 GB (reserve70).
Choose configured S3, larger storage, or explicit bounded aggregate retention.
Aggregate mode stores exact counts/hashes and fixed full-frame samples, rather
than every bit string for later arbitrary ML searches. Old data remain intact.

Agent-free resumable CLI: tasks/solinas_250b/README.md. Source/protocol/input and
power records at tasks/solinas_250b/{PROTOCOL.md,inputs.json,control-preparation.json,
power-plan.json,test_campaign.py}. Storage obstruction: problems/
solinas-250b-storage-unavailable.md. Predecessor: PR2108. Internal sources only;
no new mechanism, official scientific transition or ECDLP-strength/cost claim.
