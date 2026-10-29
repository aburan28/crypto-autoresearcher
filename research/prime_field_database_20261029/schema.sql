PRAGMA foreign_keys = ON;
CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE sources (
  path TEXT PRIMARY KEY, sha256 TEXT NOT NULL, bytes INTEGER NOT NULL,
  kind TEXT NOT NULL
);
-- Decimal text preserves field/subgroup integers beyond SQLite's signed u64.
CREATE TABLE curves (
  curve_uid TEXT PRIMARY KEY, p TEXT NOT NULL, a TEXT NOT NULL,
  b TEXT NOT NULL, subgroup_order TEXT NOT NULL, generator_json TEXT NOT NULL
);
CREATE TABLE bases (
  base_sha256 TEXT PRIMARY KEY, curve_uid TEXT NOT NULL REFERENCES curves,
  fixture_uid TEXT NOT NULL UNIQUE, native_atoms INTEGER NOT NULL,
  projected_columns INTEGER NOT NULL, convention TEXT NOT NULL,
  source_path TEXT NOT NULL REFERENCES sources
);
CREATE TABLE atoms (
  base_sha256 TEXT NOT NULL REFERENCES bases, column_index INTEGER NOT NULL,
  x TEXT NOT NULL, y TEXT NOT NULL,
  PRIMARY KEY(base_sha256, column_index)
);
CREATE TABLE actions (
  base_sha256 TEXT NOT NULL REFERENCES bases, name TEXT NOT NULL,
  eigenvalue TEXT NOT NULL, known_constraint_rank INTEGER NOT NULL,
  additional_rank_after_constraints INTEGER NOT NULL, certificate_json TEXT NOT NULL,
  PRIMARY KEY(base_sha256, name)
);
CREATE TABLE executions (
  execution_id TEXT PRIMARY KEY, source_commit TEXT NOT NULL,
  protocol_sha256 TEXT NOT NULL, physical_executions INTEGER NOT NULL,
  wall_valid INTEGER NOT NULL CHECK(wall_valid=0),
  resource_json TEXT NOT NULL, export_path TEXT NOT NULL REFERENCES sources
);
CREATE TABLE observations (
  observation_id TEXT PRIMARY KEY, base_sha256 TEXT NOT NULL REFERENCES bases,
  execution_id TEXT REFERENCES executions, arm TEXT NOT NULL,
  attempts INTEGER, witnesses INTEGER NOT NULL, unique_equations INTEGER,
  rank INTEGER NOT NULL, nullity INTEGER NOT NULL,
  verification_scope TEXT NOT NULL, source_path TEXT NOT NULL REFERENCES sources
);
CREATE TABLE statuses (
  observation_id TEXT NOT NULL REFERENCES observations, status TEXT NOT NULL,
  count INTEGER NOT NULL, PRIMARY KEY(observation_id, status)
);
CREATE TABLE equations (
  observation_id TEXT NOT NULL REFERENCES observations, row_index INTEGER NOT NULL,
  normalized_affine_json TEXT NOT NULL, coefficients_json TEXT NOT NULL,
  rhs TEXT NOT NULL, source_zero INTEGER NOT NULL, constraint_zero INTEGER NOT NULL,
  old_kernel_syndrome_json TEXT, witness_json TEXT NOT NULL,
  PRIMARY KEY(observation_id, row_index)
);
CREATE INDEX equations_affine ON equations(normalized_affine_json);
CREATE VIEW rank_summary AS
 SELECT c.curve_uid,c.p,c.a,c.b,b.base_sha256,o.arm,o.attempts,o.witnesses,
        o.unique_equations,o.rank,b.projected_columns,o.nullity,o.verification_scope
 FROM observations o JOIN bases b USING(base_sha256) JOIN curves c USING(curve_uid);
CREATE VIEW zero_witness_summary AS
 SELECT observation_id,source_zero,constraint_zero,COUNT(*) AS witnesses,
        COUNT(DISTINCT normalized_affine_json) AS distinct_equations
 FROM equations GROUP BY observation_id,source_zero,constraint_zero;
CREATE VIEW new_completed_equations AS
 SELECT DISTINCT n.observation_id,n.normalized_affine_json
 FROM equations n JOIN observations no ON no.observation_id=n.observation_id
 WHERE no.arm='completed_zero' AND NOT EXISTS (
   SELECT 1 FROM equations old JOIN observations oo ON oo.observation_id=old.observation_id
   WHERE oo.arm='historical_nonzero' AND oo.execution_id=no.execution_id
     AND oo.base_sha256=no.base_sha256 AND old.normalized_affine_json=n.normalized_affine_json
 );
