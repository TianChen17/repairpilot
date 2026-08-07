# Revenue field migration

`gross_revenue` is the canonical revenue field. RepairPilot retains `gross_amount`
as a compatibility alias for one migration window while controlled downstream
models move to `gross_revenue`.

Removal criteria:

1. DataHub query history shows no remaining `gross_amount` consumers.
2. Every downstream owner acknowledges the migration.
3. The `gross_revenue` not-null assertion remains green for seven consecutive runs.
