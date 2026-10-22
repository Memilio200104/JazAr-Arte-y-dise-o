# Order review execution ledger

Plan and spec: docs/superpowers/{plans,specs}/2026-10-21-order-review*.md.
Approved 2026-10-22. Direct execution in current checkout; baseline 441b9c7.
Preflight: existing customer decorator, catalog queryset and local cart reused. No external provider required.
Task 1 complete: model tests RED (missing module) -> GREEN 2/2. Backup runtime/backups/before-orders-20261022.sqlite3; 91 products and 3 users before migration. Initialized 79 unknown fixed-product stocks to 30; no differing defined stocks.
Tasks 2-3 implemented, tests in progress; 4-5 pending.
Ruling: admin uses a separate review POST after the read-only change form, rather than ModelAdmin save hooks. Prevents generic model saves from bypassing version checks; cost: a separate save-review button.
