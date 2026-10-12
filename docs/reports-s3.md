# Reports in S3

The [`reports-s3` workflow](../.github/workflows/reports-s3.yml) copies the
reports the `research-visuals` skill asks for to S3 once they are on `main`:

| In the repository | In S3 |
| --- | --- |
| `experiments/<EXP-ID>/reports/run-*/`, `reports/review-<DEC-ID>/` | `…/reports/crypto-autoresearcher/experiments/<EXP-ID>/reports/…` |
| `research/**/*.pdf` (search-round reports) | `…/reports/crypto-autoresearcher/research/…` |
| `docs/reports/**` | `…/reports/crypto-autoresearcher/docs/reports/…` |
| (one per push that uploaded anything) | `s3://crypto-autoresearcher/reports/crypto-autoresearcher/_manifests/<commit>.json` |

Each object keeps its repository path under `reports/crypto-autoresearcher/`. The manifest
lists every file the push uploaded with its SHA-256, size and S3 URI, the
commit, and the workflow run. Sessions never upload: the job runs on each push
to `main` that adds or changes a report, so S3 holds reports that merged.
Removing a report from the repository does not delete its S3 copy.

## Configuration

Repository variables (all optional):

- `REPORTS_S3_BUCKET`: the bucket; default `crypto-autoresearcher` (encrypted
  with SSE-S3, public access blocked).
- `REPORTS_AWS_REGION`: default `us-west-2`.
- `REPORTS_S3_ROLE_ARN`: an IAM role the job assumes through GitHub OIDC.

Credentials, in the order the job tries them:

1. **OIDC role (preferred).** No long-lived key. Create (or reuse) the IAM
   OIDC provider for `https://token.actions.githubusercontent.com`, audience
   `sts.amazonaws.com`, and a role that only `main` of this repository may
   assume:

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [{
       "Effect": "Allow",
       "Principal": {"Federated": "arn:aws:iam::<account-id>:oidc-provider/token.actions.githubusercontent.com"},
       "Action": "sts:AssumeRoleWithWebIdentity",
       "Condition": {"StringEquals": {
         "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
         "token.actions.githubusercontent.com:sub": "repo:aburan28/crypto-autoresearcher:ref:refs/heads/main"
       }}
     }]
   }
   ```

   Set `REPORTS_S3_ROLE_ARN` to its ARN.
2. **Access keys.** Repository secrets `AWS_ACCESS_KEY_ID` and
   `AWS_SECRET_ACCESS_KEY`. This repository has none today; add them, or prefer the role.

Either identity needs only:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "s3:PutObject",
    "Resource": "arn:aws:s3:::crypto-autoresearcher/reports/crypto-autoresearcher/*"
  }]
}
```

With neither configured, the job uploads nothing and says so in a notice, so
`main` never turns red for lack of configuration. Credentials that cannot write
the prefix fail the job.

## Backfill and reading

Run the workflow by hand (**Actions → reports-s3 → Run workflow**) to upload
every report already on `main`. To read one:

```sh
aws s3 ls --recursive s3://crypto-autoresearcher/reports/crypto-autoresearcher/
aws s3 presign s3://crypto-autoresearcher/reports/crypto-autoresearcher/<path> --expires-in 604800
```

A presigned link opens the private object for its lifetime (here 7 days)
without making the bucket public.
