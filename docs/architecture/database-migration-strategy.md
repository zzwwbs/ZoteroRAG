# Database Migration Strategy

For the MVP, the application will use a simple versioning approach for the SQLite schema:

*   **Schema Version Table:** A `schema_version` table will store the current schema version number.
*   **Migration Scripts:** SQL migration scripts will be stored in `src/zoterorag/data/migrations/` with sequential numbering (e.g., `001_initial.sql`, `002_add_index.sql`).
*   **Automatic Migration:** On startup, `MetadataDBManager` will check the current schema version and apply any pending migrations in order.
*   **Backup Before Migration:** The application will automatically create a backup copy of the database before applying migrations.
*   **Rollback Strategy:** If migration fails, the backup will be restored and an error message displayed to the user.

```python
# Example schema_version table
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL
);
```
