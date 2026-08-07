# `gross_amount` → `gross_revenue` migration

`gross_revenue` is now the canonical field. `gross_amount` remains available as
a compatibility alias for one migration window so existing consumers do not
break.

Consumer owners should migrate references to `gross_revenue`, validate their
queries, and confirm completion with Revenue Analytics before the deprecated
alias is removed.
