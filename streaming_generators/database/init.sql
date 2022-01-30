-- NOTE
-- Since this is a sample project and I don't think bringing Django in is necessary,
-- we're going to just set up the database manually. In real life, we'd probably want
-- to use a DBA framework.

CREATE USER pipeline_user;
GRANT ALL PRIVILEGES ON DATABASE postgres TO pipeline_user;
ALTER USER pipeline_user WITH PASSWORD 'pipeline'; -- Beware: you probably shouldn't do this.

\c postgres

CREATE TABLE IF NOT EXISTS message_table (
    id SERIAL PRIMARY KEY,
    message_id VARCHAR(64) NOT NULL,
    message_body VARCHAR(64) NOT NULL,
    message_timestamp INTEGER NOT NULL
);

ALTER TABLE message_table OWNER to pipeline_user;