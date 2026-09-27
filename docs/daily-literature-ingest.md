# Daily crypto paper intake

The [`daily-literature` workflow](../.github/workflows/daily-literature.yml)
runs at 13:37 UTC each day, with a manual `workflow_dispatch` option. GitHub
may delay a scheduled job. It checks the latest IACR ePrint RSS entries and the
arXiv API (`cs.CR` and `math.NT`, sorted by last update) with a seven-day
overlap. A broad target-and-result term filter selects potential ECC and PQC
attacks, resource estimates, and speedups. The filter is an intake heuristic,
not an exhaustive literature search or an attack classification.

For each new candidate, the script downloads the canonical publisher PDF,
checks that it looks complete, computes SHA-256, and conditionally writes it to
`s3://<bucket>/knowledge/source/papers/<source>/<source-id>/paper.pdf`. It
first writes an immutable, deterministic `.metadata.json` sidecar required by
the existing KB worker; the later PDF event can then be indexed if the
S3→EventBridge→SQS worker is deployed. It refuses to overwrite a PDF or
sidecar with different or unrecorded bytes. This path is under the KB's
`knowledge/source/` ingestion prefix, though the workflow itself does not
require that worker to be deployed.

It then extracts page-tagged text from the PDF (up to 80 pages/60,000
characters) and requests a structured distillation from the model. The
collector rejects model evidence quotes that do not literally occur on the
cited extracted page. The `knowledge/literature/KN-LIT-*.md` record includes
the reported contribution, affected scope, cost, limits, page pointers,
source ID, model and usage metadata, and the S3 URI/hash/version receipt. The
full PDF stays out of Git. **This is a machine-distilled candidate record:**
`confidence: reported`, `citation_verified: feed-and-pdf`. Quote matching is
not scientific or mathematical verification; extraction can omit formulas,
figures, appendices and the rest of a truncated paper. Read the PDF and write
a superseding KN-LIT entry for a useful paper; do not silently edit the
draft's substantive assertions or promote it to a verified finding.

## One-time configuration

1. Provision or choose a versioned private S3 bucket. The KB Terraform example
   in `kb/infra/terraform/main.tf` defaults to `crypto-autoresearcher`, but
   that infrastructure is **not** automatically applied. Use the actual bucket
   name in the GitHub repository variable `LITERATURE_S3_BUCKET`.
2. Create an IAM OIDC provider for `https://token.actions.githubusercontent.com`
   (audience `sts.amazonaws.com`) and a dedicated role. Set repository variable
   `LITERATURE_S3_ROLE_ARN` to that role's ARN. Optional variable
   `LITERATURE_AWS_REGION` defaults to `us-west-2`. Limit the role trust to the
   scheduled workflow's **default branch**, not a pull request:

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [{
       "Effect": "Allow",
       "Principal": {"Federated": "arn:aws:iam::<account-id>:oidc-provider/token.actions.githubusercontent.com"},
       "Action": "sts:AssumeRoleWithWebIdentity",
       "Condition": {
         "StringEquals": {
           "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
           "token.actions.githubusercontent.com:sub": "repo:aburan28/crypto-autoresearcher:ref:refs/heads/main"
         }
       }
     }]
   }
   ```

   The role needs this S3 permission for the chosen bucket. If the bucket
   enforces a customer KMS key, additionally grant the necessary KMS rights
   and adjust the `AES256` request in `archive_pdf` to the bucket's policy.

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [{
       "Effect": "Allow",
       "Action": ["s3:PutObject", "s3:GetObject"],
       "Resource": "arn:aws:s3:::<bucket>/knowledge/source/papers/*"
     }]
   }
   ```

3. Allow GitHub Actions to create pull requests in **Settings → Actions →
   General → Workflow permissions**, and permit a write-capable `GITHUB_TOKEN`
   (`contents` and `pull-requests`). The workflow never merges or approves a
   PR. Optionally set secret `LITERATURE_PR_TOKEN` to a narrowly scoped GitHub
   App or fine-grained token with Contents and Pull requests write permissions
   so a bot-created PR can trigger the normal PR CI. Events created by the
   default `GITHUB_TOKEN` do not trigger other workflows.
4. Set GitHub secret `ANTHROPIC_API_KEY` for PDF text distillation. The repo's
   Claude workflows use the same secret. The optional repository variable
   `LITERATURE_MODEL` defaults to `claude-opus-5` from the repo's current
   research binding; choose a model with structured JSON support if that
   binding changes. The job sends bounded, untrusted text extracted from each
   PDF to the model. It fails when the key is absent, extraction yields too
   little text, a response is incomplete, or a quote fails the page check;
   this is safer than issuing a claim with no check. API use is billable.
5. Merge the workflow PR into `main`, then run **Actions → daily-literature →
   Run workflow** once and inspect the log, S3 receipt, and review PR. Scheduled
   workflows only execute from the default branch. Do not configure untrusted
   pull request triggers for a workflow with an S3 role.

## Operational limits and recovery

- IDs are allocated and checked by `tools/allocate_id.py`, then the source
  indexes are rebuilt. Entries already in `knowledge/literature/` are matched
  by ePrint/arXiv ID or normalized title. The single bot branch keeps pending
  records between runs even after they fall outside the feed's lookback. It
  merges main into that branch and refuses substantive merge conflicts.
- The workflow fails instead of silently dropping results if over 20 **new**
  matches appear or arXiv fills the 800-result API page within the lookback.
  Widen the limits and rerun manually. The IACR RSS feed is a rolling feed;
  if it does not cover all seven days, the job logs a warning, so prolonged
  missed schedules require manual backfill rather than an assumption of full
  coverage. It is appropriate to supplement this with targeted searches.
- Download/network/authentication failure stops the run. A PDF already written
  before a later error is reused only if its S3 SHA-256 metadata matches the
  fresh download; no KN entry is committed for a failed download. A sidecar
  published immediately before a failing PDF upload can remain orphaned until
  the next run. The S3 object and PR record together form the receipt.
- The CLI's `--abstract-only` switch is for limited manual intake when PDF
  extraction/model access is unavailable. The scheduled workflow intentionally
  requires full PDF text distillation. If an exceptional paper has no extractable
  text, log it for manual/OCR curation rather than accepting an invented note.
- Run `python3 -m unittest tools.test_daily_literature_ingest -v` for offline
  parser/idempotency tests. A live end-to-end check requires the actual role,
  bucket, upstream feeds, and write-enabled GitHub token.
