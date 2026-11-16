CREATE TABLE IF NOT EXISTS version_views (
  id TEXT PRIMARY KEY,
  version_id TEXT NOT NULL REFERENCES versions(id) ON DELETE CASCADE,
  audience TEXT NOT NULL CHECK (audience IN ('reviewer','admin','leaver','successor')),
  payload TEXT NOT NULL,
  UNIQUE (version_id, audience)
);

ALTER TABLE version_views ENABLE ROW LEVEL SECURITY;
ALTER TABLE version_views FORCE ROW LEVEL SECURITY;

CREATE POLICY version_views_read ON version_views FOR SELECT USING (
  current_setting('app.role', true) IN ('system','reviewer','admin')
  OR audience = current_setting('app.role', true)
);
CREATE POLICY version_views_write ON version_views FOR ALL USING (
  current_setting('app.role', true) IN ('system','reviewer','admin')
) WITH CHECK (
  current_setting('app.role', true) IN ('system','reviewer','admin')
);

INSERT INTO version_views(id, version_id, audience, payload)
SELECT versions.id || ':' || audiences.audience, versions.id, audiences.audience,
       CASE
         WHEN audiences.audience IN ('reviewer','admin') THEN versions.payload
         ELSE jsonb_set(
           jsonb_set(
             versions.payload::jsonb,
             '{items}',
             COALESCE((
               SELECT jsonb_agg(item.value ORDER BY item.ordinal)
               FROM jsonb_array_elements(versions.payload::jsonb->'items')
                    WITH ORDINALITY AS item(value, ordinal)
               WHERE item.value->>'label' = ANY(audiences.labels)
             ), '[]'::jsonb),
             false
           ),
           '{_hidden_items}',
           to_jsonb(
             jsonb_array_length(versions.payload::jsonb->'items') -
             COALESCE((
               SELECT count(*)
               FROM jsonb_array_elements(versions.payload::jsonb->'items') AS item(value)
               WHERE item.value->>'label' = ANY(audiences.labels)
             ), 0)
           ),
           true
         )::text
       END
FROM versions
CROSS JOIN (VALUES
  ('reviewer', ARRAY['open','internal','restricted','confidential']::text[]),
  ('admin', ARRAY['open','internal','restricted','confidential']::text[]),
  ('leaver', ARRAY['open','internal','restricted']::text[]),
  ('successor', ARRAY['open','internal']::text[])
) AS audiences(audience, labels)
WHERE versions.payload <> '{}';

UPDATE versions SET payload='{}' WHERE payload <> '{}';
