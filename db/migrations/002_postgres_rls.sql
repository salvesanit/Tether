CREATE TABLE IF NOT EXISTS projects (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  codename TEXT NOT NULL DEFAULT 'Aster',
  state TEXT NOT NULL DEFAULT 'scoped'
    CHECK (state IN ('scoped','labelled','rebuilt','in review','signed','shared','received')),
  retention_days INTEGER NOT NULL DEFAULT 30,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  github TEXT,
  role TEXT NOT NULL CHECK (role IN ('leaver','reviewer','successor','admin'))
);

CREATE TABLE IF NOT EXISTS sources (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  kind TEXT NOT NULL CHECK (kind IN ('repo','notes','chat','issues','prs')),
  name TEXT NOT NULL,
  label TEXT CHECK (label IN ('open','internal','restricted','confidential')),
  read_state TEXT NOT NULL DEFAULT 'pending' CHECK (read_state IN ('pending','read','not read')),
  not_read_reason TEXT,
  excluded_channels TEXT NOT NULL DEFAULT '[]',
  sha256 TEXT,
  captured_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS spans (
  id TEXT PRIMARY KEY,
  source_id TEXT NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
  locator TEXT NOT NULL,
  text TEXT NOT NULL,
  text_sha256 TEXT NOT NULL,
  redactions TEXT NOT NULL DEFAULT '[]'
);
CREATE INDEX IF NOT EXISTS idx_spans_locator ON spans(locator);

CREATE TABLE IF NOT EXISTS runs (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  extractor TEXT NOT NULL,
  model_id TEXT,
  prompt_version TEXT,
  params TEXT NOT NULL DEFAULT '{}',
  started_at TEXT NOT NULL,
  finished_at TEXT,
  counts TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS candidates (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
  span_id TEXT REFERENCES spans(id),
  payload TEXT NOT NULL,
  quote_found INTEGER,
  drop_reason TEXT
);

CREATE TABLE IF NOT EXISTS claims (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  run_id TEXT REFERENCES runs(id),
  type TEXT NOT NULL CHECK (type IN ('decision','owner','dependency','risk','repeated problem','open question','next step')),
  text TEXT NOT NULL,
  subject TEXT,
  attribute TEXT,
  value TEXT,
  reason TEXT,
  rejected_options TEXT NOT NULL DEFAULT '[]',
  confidence REAL NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
  confidence_rule TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'uncertain' CHECK (status IN ('verified','uncertain','conflicting','missing')),
  label TEXT NOT NULL CHECK (label IN ('open','internal','restricted','confidential')),
  gap_subject TEXT,
  review_state TEXT NOT NULL DEFAULT 'pending' CHECK (review_state IN ('pending','confirmed','edited','rejected','parked')),
  review_actor TEXT,
  review_reason TEXT,
  risk_estimate REAL,
  risk_rule TEXT,
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_claims_project ON claims(project_id, status);

CREATE TABLE IF NOT EXISTS evidence (
  id TEXT PRIMARY KEY,
  claim_id TEXT NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
  span_id TEXT NOT NULL REFERENCES spans(id),
  quote TEXT NOT NULL,
  locator TEXT NOT NULL,
  captured_at TEXT NOT NULL,
  source_label TEXT
);

CREATE TABLE IF NOT EXISTS conflicts (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  subject TEXT NOT NULL,
  attribute TEXT NOT NULL,
  state TEXT NOT NULL DEFAULT 'open' CHECK (state IN ('open','decided','parked')),
  decided_value TEXT,
  decided_by TEXT,
  reason TEXT
);

CREATE TABLE IF NOT EXISTS conflict_claims (
  conflict_id TEXT NOT NULL REFERENCES conflicts(id) ON DELETE CASCADE,
  claim_id TEXT NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
  PRIMARY KEY (conflict_id, claim_id)
);

CREATE TABLE IF NOT EXISTS gaps (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  subject TEXT NOT NULL,
  question TEXT NOT NULL,
  owner TEXT,
  next_step TEXT,
  state TEXT NOT NULL DEFAULT 'open' CHECK (state IN ('open','closed','parked','suggested')),
  parked_reason TEXT
);

CREATE TABLE IF NOT EXISTS quarantine (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  source_id TEXT NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
  span_id TEXT REFERENCES spans(id),
  reason TEXT NOT NULL,
  excerpt TEXT NOT NULL,
  action TEXT CHECK (action IN ('dismissed','confirmed')),
  acted_by TEXT,
  acted_at TEXT
);

CREATE TABLE IF NOT EXISTS reviews (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  target_type TEXT NOT NULL,
  target_id TEXT NOT NULL,
  actor TEXT NOT NULL,
  action TEXT NOT NULL,
  before TEXT,
  after TEXT,
  reason TEXT,
  at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS versions (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  number TEXT NOT NULL,
  state TEXT NOT NULL DEFAULT 'signed' CHECK (state IN ('signed')),
  payload TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  signed_by TEXT NOT NULL,
  signed_at TEXT NOT NULL,
  UNIQUE (project_id, number)
);

CREATE TABLE IF NOT EXISTS receipts (
  id TEXT PRIMARY KEY,
  version_id TEXT NOT NULL REFERENCES versions(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  at TEXT NOT NULL,
  UNIQUE (version_id, user_id)
);

CREATE TABLE IF NOT EXISTS log (
  id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  at TEXT NOT NULL,
  actor TEXT NOT NULL,
  role TEXT NOT NULL,
  action TEXT NOT NULL,
  object TEXT,
  detail TEXT,
  prev_hash TEXT NOT NULL,
  hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS retention_requests (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  requestor TEXT NOT NULL,
  at TEXT NOT NULL,
  detail TEXT
);

ALTER TABLE sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE sources FORCE ROW LEVEL SECURITY;
ALTER TABLE spans ENABLE ROW LEVEL SECURITY;
ALTER TABLE spans FORCE ROW LEVEL SECURITY;
ALTER TABLE claims ENABLE ROW LEVEL SECURITY;
ALTER TABLE claims FORCE ROW LEVEL SECURITY;
ALTER TABLE evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE evidence FORCE ROW LEVEL SECURITY;
ALTER TABLE versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE versions FORCE ROW LEVEL SECURITY;
ALTER TABLE log ENABLE ROW LEVEL SECURITY;
ALTER TABLE log FORCE ROW LEVEL SECURITY;

CREATE POLICY sources_read ON sources FOR SELECT USING (
  current_setting('app.role', true) IN ('system','reviewer','admin')
  OR (current_setting('app.role', true) = 'leaver' AND label IN ('open','internal','restricted'))
  OR (current_setting('app.role', true) = 'successor' AND label IN ('open','internal'))
);
CREATE POLICY sources_write ON sources FOR ALL USING (
  current_setting('app.role', true) IN ('system','reviewer','admin')
) WITH CHECK (
  current_setting('app.role', true) IN ('system','reviewer','admin')
);

CREATE POLICY claims_read ON claims FOR SELECT USING (
  current_setting('app.role', true) IN ('system','reviewer','admin')
  OR (current_setting('app.role', true) = 'leaver' AND label IN ('open','internal','restricted'))
  OR (current_setting('app.role', true) = 'successor' AND label IN ('open','internal'))
);
CREATE POLICY claims_write ON claims FOR ALL USING (
  current_setting('app.role', true) IN ('system','reviewer','admin')
) WITH CHECK (
  current_setting('app.role', true) IN ('system','reviewer','admin')
);

CREATE POLICY evidence_read ON evidence FOR SELECT USING (
  EXISTS (SELECT 1 FROM claims WHERE claims.id = evidence.claim_id)
);
CREATE POLICY evidence_write ON evidence FOR ALL USING (
  current_setting('app.role', true) IN ('system','reviewer','admin')
) WITH CHECK (
  current_setting('app.role', true) IN ('system','reviewer','admin')
);

CREATE POLICY spans_read ON spans FOR SELECT USING (
  current_setting('app.role', true) IN ('system','reviewer','admin')
  OR EXISTS (
    SELECT 1
      FROM sources
      JOIN evidence ON evidence.span_id = spans.id
      JOIN claims ON claims.id = evidence.claim_id
     WHERE sources.id = spans.source_id
  )
);
CREATE POLICY spans_write ON spans FOR ALL USING (
  current_setting('app.role', true) IN ('system','reviewer','admin')
) WITH CHECK (
  current_setting('app.role', true) IN ('system','reviewer','admin')
);

CREATE POLICY versions_read ON versions FOR SELECT USING (
  current_setting('app.role', true) IN ('system','reviewer','admin')
  OR (current_setting('app.role', true) IN ('leaver','successor') AND state = 'signed')
);
CREATE POLICY versions_write ON versions FOR ALL USING (
  current_setting('app.role', true) IN ('system','reviewer','admin')
) WITH CHECK (
  current_setting('app.role', true) IN ('system','reviewer','admin')
);

CREATE POLICY log_read ON log FOR SELECT USING (
  current_setting('app.role', true) IN ('system','reviewer','admin')
);
CREATE POLICY log_insert ON log FOR INSERT WITH CHECK (
  current_setting('app.role', true) = 'system'
  OR (current_setting('app.role', true) IN ('leaver','reviewer','successor','admin') AND role = current_setting('app.role', true))
);
