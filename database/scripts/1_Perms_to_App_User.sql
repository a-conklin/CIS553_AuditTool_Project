-- Database and app user can be created by the pgadmin GUI
-- couldn't find a great way to do it solely via script

-- Allow access to the schema
GRANT USAGE ON SCHEMA supplieraudit TO sadb_appuser;

-- Allow access to all existing tables
GRANT SELECT, INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA supplieraudit
TO sadb_appuser;

-- Allow access to sequences (needed for SERIAL / inserts)
GRANT USAGE, SELECT
ON ALL SEQUENCES IN SCHEMA supplieraudit
TO sadb_appuser;