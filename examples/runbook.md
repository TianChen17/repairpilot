# Safe dbt Column Rename Runbook

1. Query DataHub column lineage, ownership, governance tags, assertions, and
   usage through the official MCP server.
2. Fail closed if required context cannot be verified.
3. Keep the old field as a compatibility alias for a defined migration window.
4. Migrate controlled consumers and add a contract assertion for the new field.
5. Run the affected dbt selection in an isolated Git worktree and Postgres
   schema.
6. Require the accountable owner to approve verified high-risk repairs.
7. Publish the patch and Evidence Receipt, then write the reusable learning back
   to DataHub.
