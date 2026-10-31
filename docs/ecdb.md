# Querying the curve database (ecdb)

ecdb is the lab's curve database: a Postgres catalogue on RDS (us-west-2)
with an HTTP API and an MCP endpoint. Its guide is
[crypto's `ecdb/docs/AGENTS.md`](https://github.com/isogeny-labs/crypto/blob/main/ecdb/docs/AGENTS.md); read it before the first query.
It holds:

- every curve of crypto's registry, walk outputs and trait catalogue, with
  Jacobians, isogenies, covers, transfer prices, polynomials and GLV data;
- crypto's measured results: the IC leaderboard, the progress timeline, the
  boundary ledger, `benchmarks/` and every ecbench session with its runs;
- this repository's curve capsules and trait snapshot (`ui/curves/`), the NIST-seed candidates, the endomorphism sweep of named curves and the classical-solver fixture curves.

How to reach it:

- **MCP:** server `ecdb` in `.mcp.json`. Export the read token before the
  runtime starts:

  ```sh
  export ECDB_TOKEN=$(aws secretsmanager get-secret-value --region us-west-2 --secret-id ecdb/api --query SecretString --output text | jq -r .read_token)
  ```

- **Shell:** `scripts/ecdb.sh` (`curve <ref> [part]`, `sql '<query>'`,
  `results leaderboard`, `ecbench [session]`), and `check`, which reports
  whether ecdb's copy of this repository's files matches the checkout.

Rules:

- **Token.** Never print, commit or log it. Without AWS access to `ecdb/api`,
  say so and use the repository files.
- **Look up before computing.** Query ecdb for a curve fact or an existing
  measurement before recomputing it, and resolve curve names there. On an
  ambiguous name (409), choose a candidate explicitly.
- **Cite the source, not the query.** Every row names its source file and
  SHA-256, and a claim cites that file or run. Measured rows are the
  producers' frozen records in their own units: compare a ratio only within
  one family, session or dataset.
- **Values.** Keep each value's status: unknown is `null`, never 0.
  Transfer prices are formula estimates, not speedups. Twist and
  isomorphism rows do not transport a logarithm.
- **Keep it current.** When a file ecdb imports from this repository
  changes, `scripts/ecdb.sh check` lists it. Redeploying ecdb (crypto's
  `ecdb/deploy/`) re-imports it.
