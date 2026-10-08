-- Distinguished-point store for van Oorschot–Wiener parallel Pollard's rho (ECDLP).
-- Schema version: 1
--
-- Collision model:
--   Workers insert DPs keyed by (campaign_id, point_key). First writer wins.
--   A later insert of the same point_key with a different (a,b) is a collision:
--   report_dp() writes rho_collisions and returns the prior row for DL recovery.
--   Same (a,b) from a retry/duplicate walk is a no-op (is_new=false, is_collision=false).

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS schema_migrations (
  version     integer PRIMARY KEY,
  applied_at  timestamptz NOT NULL DEFAULT now(),
  note        text
);

CREATE TABLE IF NOT EXISTS rho_campaigns (
  campaign_id   text PRIMARY KEY,
  curve_id      text NOT NULL,
  -- Optional group order n (decimal string or hex); clients may keep n locally.
  order_n       text,
  dp_mask_bits  integer,
  created_at    timestamptz NOT NULL DEFAULT now(),
  meta          jsonb NOT NULL DEFAULT '{}'::jsonb
);

-- First-seen DP table. Primary key is the rho identity that must collide.
CREATE TABLE IF NOT EXISTS distinguished_points (
  campaign_id   text NOT NULL REFERENCES rho_campaigns (campaign_id),
  -- Canonical key: prefer SEC1 compressed (0x02|0x03 || x) or (x || y_parity byte).
  point_key     bytea NOT NULL,
  -- Walk state: a*P + b*Q = DP. Big-endian unsigned integers mod n as bytea.
  a             bytea NOT NULL,
  b             bytea NOT NULL,
  walk_seed     bytea,
  steps         bigint,
  worker_id     text,
  found_at      timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (campaign_id, point_key)
);

-- Insert-heavy: PK supports the hot path (lookup-or-insert by point_key).
-- Monitoring / per-worker stats (not on the hot collision path):
CREATE INDEX IF NOT EXISTS distinguished_points_campaign_found_at_idx
  ON distinguished_points (campaign_id, found_at DESC);

CREATE INDEX IF NOT EXISTS distinguished_points_campaign_worker_idx
  ON distinguished_points (campaign_id, worker_id);

CREATE TABLE IF NOT EXISTS rho_collisions (
  id            bigserial PRIMARY KEY,
  campaign_id   text NOT NULL,
  point_key     bytea NOT NULL,
  a1            bytea NOT NULL,
  b1            bytea NOT NULL,
  a2            bytea NOT NULL,
  b2            bytea NOT NULL,
  worker1       text,
  worker2       text,
  walk_seed1    bytea,
  walk_seed2    bytea,
  detected_at   timestamptz NOT NULL DEFAULT now(),
  UNIQUE (campaign_id, point_key, a1, b1, a2, b2)
);

CREATE INDEX IF NOT EXISTS rho_collisions_campaign_detected_at_idx
  ON rho_collisions (campaign_id, detected_at DESC);

-- Atomically report a DP. Returns one row describing the outcome.
CREATE OR REPLACE FUNCTION report_dp(
  p_campaign_id text,
  p_point_key   bytea,
  p_a           bytea,
  p_b           bytea,
  p_walk_seed   bytea DEFAULT NULL,
  p_steps       bigint DEFAULT NULL,
  p_worker_id   text DEFAULT NULL
) RETURNS TABLE (
  is_new        boolean,
  is_collision  boolean,
  prior_a       bytea,
  prior_b       bytea,
  prior_worker  text,
  collision_id  bigint
) LANGUAGE plpgsql AS $$
DECLARE
  existing distinguished_points%ROWTYPE;
  new_id bigint;
BEGIN
  INSERT INTO distinguished_points (
    campaign_id, point_key, a, b, walk_seed, steps, worker_id
  ) VALUES (
    p_campaign_id, p_point_key, p_a, p_b, p_walk_seed, p_steps, p_worker_id
  )
  ON CONFLICT (campaign_id, point_key) DO NOTHING;

  IF FOUND THEN
    is_new := true;
    is_collision := false;
    prior_a := NULL;
    prior_b := NULL;
    prior_worker := NULL;
    collision_id := NULL;
    RETURN NEXT;
    RETURN;
  END IF;

  SELECT * INTO existing
  FROM distinguished_points
  WHERE campaign_id = p_campaign_id AND point_key = p_point_key;

  -- Duplicate report of the same walk state: ignore.
  IF existing.a = p_a AND existing.b = p_b THEN
    is_new := false;
    is_collision := false;
    prior_a := existing.a;
    prior_b := existing.b;
    prior_worker := existing.worker_id;
    collision_id := NULL;
    RETURN NEXT;
    RETURN;
  END IF;

  INSERT INTO rho_collisions (
    campaign_id, point_key,
    a1, b1, a2, b2,
    worker1, worker2, walk_seed1, walk_seed2
  ) VALUES (
    p_campaign_id, p_point_key,
    existing.a, existing.b, p_a, p_b,
    existing.worker_id, p_worker_id, existing.walk_seed, p_walk_seed
  )
  ON CONFLICT (campaign_id, point_key, a1, b1, a2, b2) DO NOTHING
  RETURNING id INTO new_id;

  IF new_id IS NULL THEN
    SELECT id INTO new_id FROM rho_collisions
    WHERE campaign_id = p_campaign_id AND point_key = p_point_key
      AND a1 = existing.a AND b1 = existing.b AND a2 = p_a AND b2 = p_b;
  END IF;

  is_new := false;
  is_collision := true;
  prior_a := existing.a;
  prior_b := existing.b;
  prior_worker := existing.worker_id;
  collision_id := new_id;
  RETURN NEXT;
END;
$$;

INSERT INTO schema_migrations (version, note)
VALUES (1, 'initial DP store: campaigns, distinguished_points, collisions, report_dp')
ON CONFLICT (version) DO NOTHING;
