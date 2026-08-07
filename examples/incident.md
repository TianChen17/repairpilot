# RepairPilot Incident 5ba83717-332a-4d24-a121-6aa41a1c3cc3

**Status:** Verified, owner-approved, published for review, and learned

**Root cause:** Renaming `gross_amount` to `gross_revenue` in `stg_orders.sql`
breaks downstream references and schema tests.

**Risk:** HIGH (100/100)

**Policy action:** BLOCK

**Matched rules:** Breaking schema change; governed/Tier-1 asset; three or more
downstream assets; dashboard impact.

**Patch SHA-256:**
`588e2b4ba90abf9c65a1c53da7913c25d531ccbe9304bc98a82577ed877f13e7`

**dbt invocation:** `84ca016f-e191-41bf-a94a-7af7c05f5d14`

## Evidence

- DataHub MCP identified `Revenue Analytics`, three governed tags, three dbt
  consumers, the Executive Revenue Pulse dashboard, three stored usage queries,
  and passing assertions.
- The original breaking rename failed in an isolated Postgres schema.
- The compatibility repair passed 14 selected dbt tests with zero failures.
- Owner approval was recorded before publication.
- The Incident Document, Assertion, Runbook, and verification tag were written
  back to DataHub.

All referenced business data is synthetic demonstration data.
