# 08 — Databases (PostgreSQL, MySQL, SQL Server, MongoDB)

> Anchor: You did Oracle→PostgreSQL migration at BMW, SQL optimization, PostgreSQL/MySQL/Elasticsearch. JD wants schema modeling, indexing, query tuning, partitioning, migrations.

---

## A. Relational Fundamentals

### Q1. What is ACID?
ACID is the set of four guarantees that make relational database transactions **reliable** — critical for anything involving money or important data:
- **Atomicity** — "all or nothing." A transaction's operations either **all succeed or all fail together**. If a money transfer debits account A but the credit to B fails, the debit is rolled back — money never vanishes.
- **Consistency** — a transaction moves the database from **one valid state to another**, never violating rules/constraints (foreign keys, unique constraints, checks). Invalid data can't be committed.
- **Isolation** — concurrent transactions don't corrupt each other; each behaves as if it ran alone (controlled by isolation levels — see below).
- **Durability** — once a transaction is **committed, it survives crashes** (it's written to durable storage / the transaction log), so a power failure won't lose it.
SQL databases give you ACID out of the box; it's a major reason to choose them for critical data.

### Q2. What is normalization? The normal forms?
**Normalization** is organizing your tables to **reduce data duplication and avoid anomalies** (where the same fact is stored in multiple places and can get out of sync). You do this by splitting data into related tables connected by keys. The "normal forms" are progressive levels:
- **1NF (First Normal Form)** — each cell holds a single **atomic value** (no lists/repeating groups in a column), and each row is unique.
- **2NF** — 1NF **plus** every non-key column depends on the **whole** primary key (removes "partial dependency" — only relevant with composite keys).
- **3NF** — 2NF **plus** no **transitive dependency** (a non-key column shouldn't depend on another non-key column; e.g., don't store `city` *and* `zip` where zip determines city).
- **BCNF** — a stricter version of 3NF for edge cases.
**Denormalization** is the deliberate opposite — **adding redundancy back** (duplicating some data) to make **reads faster** by avoiding joins. Common in reporting/analytics/read-heavy systems. It's a trade-off: cleaner data (normalized) vs faster reads (denormalized).

### Q3. Types of SQL joins?
A **JOIN** combines rows from two tables based on a related column. The types differ in which non-matching rows they keep:
- **INNER JOIN** — returns **only rows that match in both** tables. (Most common.)
- **LEFT (OUTER) JOIN** — returns **all rows from the left table** + matching rows from the right (nulls where no match). e.g., "all customers, plus their orders if any."
- **RIGHT (OUTER) JOIN** — the mirror image: all rows from the right table + matches from the left.
- **FULL (OUTER) JOIN** — **all rows from both** tables, matched where possible, nulls elsewhere.
- **CROSS JOIN** — the **Cartesian product** (every row of A paired with every row of B) — rarely what you want.
- **SELF JOIN** — a table joined **to itself** (e.g., employees joined to their managers in the same `employees` table).


### Q4. Primary key vs unique key vs foreign key?
All three are **constraints** that enforce data integrity, but with different purposes:
- **Primary key** — the column(s) that **uniquely identify each row**. It's **not null** and there's **exactly one per table**. It's the row's "identity" (e.g., `order_id`). The DB automatically indexes it.
- **Unique key** — also enforces **uniqueness** on a column, but you can have **several** per table, and (in most DBs) it allows **one null**. Use it for other columns that must be unique but aren't the identity (e.g., `email`).
- **Foreign key** — a column that **references another table's primary key**, creating a relationship and enforcing **referential integrity** (you can't insert an order for a customer that doesn't exist, and depending on rules, can't delete a customer who still has orders).

### Q5. `WHERE` vs `HAVING`?
Both filter rows, but at **different stages** of a query:
- **`WHERE`** filters **individual rows *before* they're grouped/aggregated**. e.g., `WHERE status = 'PAID'` keeps only paid rows.
- **`HAVING`** filters ***after* `GROUP BY`**, on the **aggregated result**. e.g., `GROUP BY customer_id HAVING COUNT(*) > 5` keeps only customers with more than 5 orders.
- **Rule:** you can't use an aggregate (`COUNT`, `SUM`) in `WHERE` — that's what `HAVING` is for. Order: `WHERE` → `GROUP BY` → `HAVING`.

### Q6. `DELETE` vs `TRUNCATE` vs `DROP`?
All remove data, but very differently:
- **`DELETE`** — removes **specific rows** (with a `WHERE`), row by row. It's **logged** (so it can be rolled back), fires triggers, and **keeps the table** structure. Slower for large deletes.
- **`TRUNCATE`** — removes **all rows** at once, very **fast** (minimal logging, deallocates pages), **resets the auto-increment counter**, but has **no `WHERE`** and is harder to roll back. Keeps the table structure.
- **`DROP`** — deletes the **entire table** (structure + data + indexes) — it's gone.
- **Quick pick:** need to remove some rows → `DELETE`; wipe a whole table fast → `TRUNCATE`; get rid of the table entirely → `DROP`.

### Q7. What are transactions & isolation levels?
A **transaction** is a group of SQL statements treated as **one unit** (`BEGIN ... COMMIT`, or `ROLLBACK` on failure) — it gives you ACID. **Isolation level** controls how much concurrent transactions can "see" each other's in-progress work, trading **consistency vs concurrency/performance**:
- **READ UNCOMMITTED** — can read others' uncommitted data (**dirty reads**). Fastest, least safe.
- **READ COMMITTED** (common default) — only reads committed data (no dirty reads).
- **REPEATABLE READ** — re-reading the same row in a transaction gives the same value.
- **SERIALIZABLE** — fully isolated, as if transactions ran one after another. Safest, slowest.
The **anomalies** these prevent, in order: **dirty read** (reading uncommitted data), **non-repeatable read** (a row changes between two reads), and **phantom read** (new rows appear between two identical queries). Higher isolation prevents more anomalies but reduces concurrency.

---

## B. Indexing & Query Tuning (JD priority)

### Q8. What is an index? How does it work?
An index is a **separate data structure** (usually a **B-tree**) that the database maintains to **find rows quickly** without scanning the whole table — exactly like the index at the back of a book lets you jump to a topic instead of reading every page. When you query `WHERE email = 'x'` and there's an index on `email`, the DB traverses the B-tree (O(log n)) to the matching rows instead of a **full table scan** (O(n)). **The trade-off:** indexes speed up **reads** but **slow down writes** (every insert/update must also update the indexes) and take extra **storage** — so you index selectively.

### Q9. Types of indexes?
Different index types suit different queries:
- **B-tree** (the default) — great for **equality and range** queries (`=`, `<`, `>`, `BETWEEN`, `ORDER BY`). Handles most cases.
- **Hash** — only **equality** (`=`), no ranges; fast but limited.
- **Composite (multi-column)** — indexes several columns together; **column order matters** (leftmost-prefix rule — see Part 2).
- **Covering index** — includes all columns a query needs so it's answered **from the index alone** (no table lookup).
- **Partial index** (Postgres) — indexes only a **subset of rows** (`WHERE active = true`) to save space.
- **Unique index** — enforces uniqueness.
- **Full-text / GIN** (Postgres) — for searching text/JSONB/arrays.
- **Clustered vs non-clustered** (SQL Server/MySQL InnoDB) — see next question.

### Q10. Clustered vs non-clustered index?
- **Clustered index** — the table's rows are **physically stored in the order of this index**. Because the data *is* the index, there's **only one per table** (in InnoDB/SQL Server it's the primary key by default). Range scans on the clustered key are very fast.
- **Non-clustered index** — a **separate structure** that holds the indexed column(s) plus a **pointer** to the actual row. You can have **many** per table. Looking up via a non-clustered index means finding the pointer, then fetching the row (an extra step, unless it's a covering index).
- **Analogy:** a clustered index is like a phone book sorted by last name (the data itself is ordered); a non-clustered index is like a separate topic index that points to page numbers.

### Q11. How do you optimize a slow query?
A systematic approach (great to walk through step by step):
1. **`EXPLAIN` / `EXPLAIN ANALYZE`** — read the execution plan first. Is it doing a **Seq Scan** (full table) where an **Index Scan** should happen? Are row estimates way off (stale stats)?
2. **Add/adjust indexes** on the columns in `WHERE`, `JOIN`, and `ORDER BY`.
3. **Avoid `SELECT *`** — fetch only the columns you need (less I/O, enables covering indexes).
4. **Fix N+1 queries**, reduce unnecessary joins, and **paginate** large result sets.
5. **Rewrite** correlated subqueries as joins/CTEs; **don't wrap indexed columns in functions** (it disables the index).
6. **Update statistics** (`ANALYZE`), consider **partitioning** for huge tables, add **caching** (Redis) or **materialized views** for expensive repeated queries.
7. Use **connection pooling** and **batch** writes.
Golden rule: **measure with EXPLAIN first, don't guess.**

### Q12. Why might an index not be used?
Even with an index, the planner may skip it if:
- You wrap the column in a **function**: `WHERE UPPER(email) = 'X'` can't use a plain index on `email` (fix with a functional index).
- **Leading wildcard**: `LIKE '%abc'` can't use a B-tree (a trailing wildcard `'abc%'` can). Use full-text/trigram indexes for this.
- **Low selectivity**: if a column has few distinct values (e.g., a boolean), scanning may actually be cheaper, so the planner skips the index.
- **Implicit type cast**: comparing a varchar column to a number forces a conversion that defeats the index.
- **Stale statistics**: the planner's row estimates are wrong → run `ANALYZE`.
- The table is **small** enough that a scan is faster anyway.

### Q13. What is a covering index?
A **covering index** is an index that contains **all the columns a query needs** (both the ones it filters on *and* the ones it returns). Because everything is in the index, the database can answer the query **entirely from the index — an "index-only scan"** — without going back to the table to fetch the row. This is a big performance win for hot queries. In Postgres/SQL Server you can add non-key columns with `INCLUDE (...)`. Example: `CREATE INDEX idx ON orders (customer_id) INCLUDE (status, total)` lets `SELECT status, total FROM orders WHERE customer_id = ?` be answered from the index alone.


---

## C. Partitioning & Scaling

### Q14. What is partitioning?
Splitting a large table into smaller pieces for performance & manageability.
- **Horizontal (sharding)** — split rows (by range/hash/list).
- **Vertical** — split columns.
- Postgres: declarative partitioning (RANGE/LIST/HASH). Benefits: partition pruning, faster maintenance, parallelism.

### Q15. Partitioning vs sharding?
- **Partitioning** — within one DB instance.
- **Sharding** — across multiple DB servers (horizontal scale-out); adds routing + cross-shard query complexity.

### Q16. Replication — types & purpose?
Copy data to replicas for HA + read scaling.
- **Primary-replica (master-slave)** — writes to primary, reads from replicas.
- **Synchronous** (no data loss, slower) vs **asynchronous** (fast, possible lag).
- **Multi-primary** — writes to multiple (conflict resolution needed).

### Q17. How do you scale a relational database?
Vertical (bigger box) → read replicas → caching (Redis) → partitioning → sharding → CQRS/read models. Also connection pooling, query optimization first.

---

## D. PostgreSQL / MySQL / SQL Server specifics

### Q18. PostgreSQL vs MySQL?
- **PostgreSQL** — feature-rich, standards-compliant, advanced types (JSONB, arrays, GIS), MVCC, extensibility, complex queries/analytics. Your migration target at BMW.
- **MySQL** — fast reads, simple, widely used for web; InnoDB (ACID) vs MyISAM.

### Q19. What is MVCC?
**Multi-Version Concurrency Control** — readers don't block writers and vice versa; each txn sees a consistent snapshot. Used by Postgres/InnoDB. (Postgres needs **VACUUM** to clean dead tuples.)

### Q20. What is JSONB in Postgres?
Binary JSON column — index/query semi-structured data with GIN indexes; hybrid relational + document flexibility.

### Q21. Tell me about your Oracle→PostgreSQL migration. (be ready!)
Talk about: schema conversion (data types, sequences vs identity, PL/SQL → PL/pgSQL), data migration (ora2pg/ETL), handling stored procedures, testing/validation, cutover strategy (dual-write / phased), rollback plan, performance tuning post-migration. Emphasize zero-downtime goals + validation.

### Q22. How do you handle DB migrations (schema versioning)?
**Flyway** or **Liquibase** (Java), **Alembic** (Python) — versioned, repeatable migration scripts in source control, applied automatically in CI/CD. Backward-compatible changes for zero-downtime (expand-contract pattern).

### Q23. Expand-contract (parallel change) pattern?
For zero-downtime schema changes: **expand** (add new column/table, dual-write) → migrate data → switch reads → **contract** (drop old). Avoids breaking running services.

---

## E. NoSQL & MongoDB

### Q24. SQL vs NoSQL — when to use which?
- **SQL** — structured data, strong consistency, complex queries/joins, transactions (finance, orders).
- **NoSQL** — flexible/evolving schema, massive scale, high write throughput, denormalized access patterns (catalogs, sessions, IoT, real-time).

### Q25. Types of NoSQL databases?
- **Document** (MongoDB) — JSON-like docs.
- **Key-Value** (Redis, DynamoDB) — simple, fast.
- **Column-family** (Cassandra) — wide-column, write-heavy.
- **Graph** (Neo4j) — relationships.

### Q26. MongoDB core concepts?
Database → **Collections** → **Documents** (BSON). Flexible schema, `_id`, embedded documents vs references, aggregation pipeline, indexes (single/compound/text/geo).

### Q27. Embedding vs referencing in MongoDB?
- **Embed** — related data accessed together, bounded size (denormalize for read speed).
- **Reference** — large/shared/unbounded data, normalize to avoid duplication. Trade-off: read performance vs data duplication/consistency.

### Q28. How does MongoDB scale?
- **Replica sets** — HA + read scaling (primary + secondaries, automatic failover).
- **Sharding** — horizontal scale by shard key (choose carefully — affects distribution & query routing).

### Q29. What is the CAP theorem?
In a network partition you can have only **2 of 3**: Consistency, Availability, Partition-tolerance. Distributed systems must tolerate partitions → choose **CP** (MongoDB default, strong consistency) or **AP** (Cassandra, high availability, eventual consistency).

### Q30. Does MongoDB support transactions?
Yes — multi-document ACID transactions (since 4.0), but they're heavier; prefer schema design that keeps related data in one document.

---

## F. Caching & Performance

### Q31. How do you use caching with databases?
- **Redis/Memcached** as cache layer.
- Patterns: **cache-aside** (lazy load), **write-through**, **write-behind**, **read-through**.
- Set TTLs, handle **cache invalidation** (hardest problem), avoid stampede (locking/jitter).

### Q32. What is connection pooling and why?
Reuse a pool of DB connections instead of opening/closing per request (expensive). HikariCP (Java), pgbouncer (Postgres). Prevents connection exhaustion, improves latency.

### Q33. Backup, failover & disaster recovery? (JD mentions)
- Regular **backups** (full + incremental + WAL/point-in-time recovery).
- **Replication** for HA + automatic **failover**.
- **RPO** (data loss tolerance) & **RTO** (recovery time) targets.
- Test restores; geo-redundant backups; runbooks.

---

## ⚡ SQL snippets to recall
```sql
-- 2nd highest salary
SELECT MAX(salary) FROM emp WHERE salary < (SELECT MAX(salary) FROM emp);
-- or window function
SELECT DISTINCT salary FROM (
  SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) rk FROM emp
) t WHERE rk = 2;

-- Nth per group (top earner per dept)
SELECT * FROM (
  SELECT e.*, ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC) rn FROM emp e
) x WHERE rn = 1;

-- Find duplicates
SELECT email, COUNT(*) FROM users GROUP BY email HAVING COUNT(*) > 1;

-- Running total (window)
SELECT id, amount, SUM(amount) OVER (ORDER BY id) running_total FROM txns;
```

## ⚡ Rapid-Fire
- **OLTP vs OLAP** — transactional (row-store, normalized) vs analytical (column-store, denormalized/warehouse).
- **CTE / WITH** — readable, recursive queries.
- **Window functions** — `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `LAG/LEAD`, `SUM() OVER`.
- **Materialized view** — cached query result, refreshable.
- **Stored procedure vs function** — action vs return value.
- **Deadlock** — consistent lock ordering + short transactions.

---
---

# PART 2 — Advanced & Tough Questions (with detailed explanations + examples)

## T1. Read this EXPLAIN plan — how do you know an index is being used?
```sql
EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 42 AND status = 'PAID';
```
Look for **Index Scan** / **Index Only Scan** (good) vs **Seq Scan** (full table — bad on large tables). Check **rows estimated vs actual** (big mismatch → stale stats → run `ANALYZE`), **actual time**, and whether a **Bitmap Index Scan** is combining indexes. If it's a Seq Scan on a big table with a selective filter, you likely need a (composite) index on `(customer_id, status)`.

## T2. Composite index column order — why does it matter? (leftmost prefix rule)
An index on `(a, b, c)` can serve queries filtering `a`, `a,b`, or `a,b,c` — but **not** `b` alone or `c` alone (no leftmost prefix). Rule: put the **most selective / most-often-equality-filtered** column first, range columns last.
```sql
-- index (customer_id, status, created_at)
WHERE customer_id=42 AND status='PAID'                 -- uses index ✓
WHERE customer_id=42 AND created_at > now()-'7d'        -- uses index on customer_id, then filter ✓
WHERE status='PAID'                                     -- can't use this index ✗
```

## T3. Why does a query stop using an index? (index-defeating patterns)
- **Function on the column:** `WHERE UPPER(email) = 'X'` → index on `email` unused. Fix: functional index `CREATE INDEX ... ON t (UPPER(email))` or store normalized.
- **Leading wildcard:** `LIKE '%abc'` can't use a B-tree (trailing `'abc%'` can). Use full-text/trigram (`pg_trgm`) index.
- **Implicit type cast:** `WHERE varchar_col = 123`.
- **Low selectivity:** boolean/status with few distinct values → planner prefers seq scan (consider partial index).
- **Stale statistics** → run `ANALYZE`/autovacuum.

## T4. Explain the isolation-level anomalies with concrete examples.
- **Dirty read** (READ UNCOMMITTED): T1 reads T2's uncommitted change; T2 rolls back → T1 saw phantom data.
- **Non-repeatable read** (fixed by REPEATABLE READ): T1 reads a row twice, T2 updates+commits in between → different values.
- **Phantom read** (fixed by SERIALIZABLE): T1 runs the same range query twice, T2 inserts a matching row in between → new rows appear.
- **Postgres note:** its REPEATABLE READ uses snapshot isolation (also prevents most phantoms); SERIALIZABLE uses SSI and may abort txns with a serialization error you must retry.

## T5. Optimistic vs pessimistic locking — code + when to use.
```java
@Entity class Account {
   @Version private long version;   // optimistic
   private BigDecimal balance;
}
// On commit, if version changed since read → OptimisticLockException → retry.
// Pessimistic:
@Lock(LockModeType.PESSIMISTIC_WRITE)
@Query("select a from Account a where a.id=:id")
Account findForUpdate(@Param("id") Long id);   // SELECT ... FOR UPDATE
```
**Optimistic** — high read, low write-contention (web apps); no DB locks, retry on conflict. **Pessimistic** — high contention / must-not-fail (inventory decrement, seat booking); locks rows, risks deadlock/blocking.

## T6. Design a concurrency-safe "decrement inventory" — avoid overselling.
Options: (1) atomic conditional update
```sql
UPDATE inventory SET qty = qty - 1 WHERE sku='X' AND qty > 0;  -- 0 rows affected = out of stock
```
(2) `SELECT ... FOR UPDATE` then check+update in a transaction (pessimistic). (3) optimistic `@Version` + retry. The atomic conditional `UPDATE` is often simplest and race-free. In a distributed/async flow, combine with the **Saga + reservation** pattern.

## T7. Deadlocks — reproduce and prevent.
Two transactions lock rows in **opposite order**:
```
T1: UPDATE A; then UPDATE B;
T2: UPDATE B; then UPDATE A;   -> deadlock
```
The DB detects it and kills one (`deadlock detected`). Prevent: **consistent lock ordering**, keep transactions **short**, lower isolation where safe, add proper indexes (lock fewer rows), and **retry** the aborted transaction.

## T8. Zero-downtime schema migration (expand-contract) — a real example.
Renaming `full_name` → split into `first_name`,`last_name` while the app runs:
1. **Expand:** add new nullable columns (non-breaking).
2. **Backfill** in batches; app **dual-writes** old + new.
3. Deploy code that **reads new** columns.
4. **Contract:** stop writing old column, drop it in a later release.
Use **Flyway/Liquibase** versioned migrations in CI/CD. Never do a blocking `ALTER` that rewrites a huge table during peak (in Postgres, adding a NOT NULL with default on old versions rewrote the table — do it in steps).

## T9. Tell me exactly how you did the Oracle→PostgreSQL migration (they WILL ask).
- **Assessment:** inventory schema objects, data types, PL/SQL packages, sequences, jobs.
- **Schema conversion:** map types (NUMBER→numeric/bigint, VARCHAR2→varchar, DATE→timestamp), Oracle sequences → identity/serial, `ROWNUM` → `LIMIT`, `NVL`→`COALESCE`, `SYSDATE`→`now()`; convert PL/SQL → PL/pgSQL (tools: **ora2pg**).
- **Data migration:** bulk load (ora2pg/ETL), validate row counts + checksums.
- **App layer:** JPA/Hibernate dialect swap, fix native queries, test.
- **Cutover:** phased/dual-write or a maintenance-window switch with CDC to minimize downtime; **rollback plan** ready.
- **Post-migration:** tune indexes, `ANALYZE`, configure autovacuum, verify performance. Emphasize **zero data loss + validation**.

## T10. Partitioning in Postgres — concrete example + the win.
```sql
CREATE TABLE events (id bigint, created_at timestamptz, ...)
  PARTITION BY RANGE (created_at);
CREATE TABLE events_2026_01 PARTITION OF events
  FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
```
**Wins:** **partition pruning** (queries on a date range only scan relevant partitions), fast bulk delete (drop old partition instead of `DELETE`), smaller indexes per partition, parallelism. **Gotcha:** the partition key should be in most queries; too many partitions add planning overhead.

## T11. When would you shard, and what breaks when you do?
Shard when a single node can't handle write volume/data size even after replicas + partitioning. Pick a **shard key** that distributes evenly and matches query patterns. What breaks: **cross-shard joins/transactions** (avoid or do app-side), **rebalancing** when adding shards (use consistent hashing), unique constraints across shards, and analytics (need a separate warehouse). Shard as a last resort.

## T12. SQL vs NoSQL for a specific case — justify, don't hand-wave.
- **Financial ledger / orders** → relational (ACID, constraints, joins, transactions).
- **User sessions / feature flags / cache** → key-value (Redis).
- **Product catalog with varying attributes / high read scale** → document (MongoDB) or Postgres JSONB.
- **Time-series/IoT telemetry, huge writes** → wide-column (Cassandra) or a TSDB.
- **Recommendations / fraud (relationships)** → graph (Neo4j).
Great line: "Postgres with **JSONB** often gives me NoSQL flexibility *and* relational guarantees, so I default to it and reach for NoSQL only for a specific access pattern."

## T13. MongoDB schema design — embed vs reference with a real example.
Blog: embed **comments** in a post if bounded and read together (one read, denormalized). Reference **author** (shared across many posts, updated independently). If comments are unbounded (viral post), reference them in a separate collection to avoid the 16MB document limit. Choose a **shard key** that avoids hot spots (not a monotonically increasing `_id`). Aggregation pipeline for analytics.

## T14. Caching consistency — cache-aside pitfalls & fixes.
Cache-aside (lazy): read → miss → load from DB → put in cache. **Pitfalls:** stale data after writes, thundering herd on expiry, cache stampede. **Fixes:** invalidate/update cache on write (or short TTL), **write-through** for critical data, add **jitter** to TTLs, use a lock/`SETNX` to prevent stampede, and accept that "cache invalidation is one of the two hard problems."

## T15. Tough rapid-fire
- **`COUNT(*)` slow on big Postgres tables?** MVCC means no fast exact count; use estimates (`pg_class.reltuples`) or maintain a counter.
- **`WHERE col IN (subquery)` vs `EXISTS`** — `EXISTS` often better for correlated existence checks; the planner may rewrite anyway.
- **Connection pool sizing** — too many connections hurts Postgres (each is a process); use pgbouncer + a right-sized HikariCP (often `~ (cores*2)+effective_spindles`).
- **B-tree vs Hash vs GIN vs BRIN** — range/equality; equality-only; JSONB/arrays/full-text; huge naturally-ordered tables (append-only time-series).
- **Covering index / INCLUDE** — `CREATE INDEX ... INCLUDE (cols)` for index-only scans.
- **Idempotent upsert** — Postgres `INSERT ... ON CONFLICT DO UPDATE`.
- **Soft delete vs hard delete** — `deleted_at` flag preserves history but bloats tables + needs filtered queries/partial indexes.
- **OLTP vs OLAP** — don't run heavy analytics on your transactional DB; replicate to a warehouse (columnar).

---
---

# PART 3 — More Real Interview Questions (Easy Language, No Repeats)

## Q1. What is a primary key in simple terms?
A column (or set of columns) that **uniquely identifies each row** in a table — like a person's Aadhaar/SSN. It can't be null and can't repeat. Every table should have one so you can reliably find and reference a specific row.

## Q2. What is a foreign key?
A column that **points to the primary key of another table**, creating a relationship. Example: an `orders` table has a `customer_id` that references the `customers` table. It enforces **referential integrity** — you can't have an order for a customer that doesn't exist.

## Q3. What is an index, using a simple analogy?
Like the **index at the back of a book**. Instead of reading every page to find a topic, you jump to the right page instantly. A database index lets the DB find rows fast without scanning the whole table. Downside: it takes extra space and slightly slows down writes (the index must be updated too).

## Q4. Should I index every column?
No. Indexes speed up **reads** but slow down **writes** and use storage. Index columns you frequently **search, join, or sort by** (like `email`, `customer_id`). Don't index columns rarely used in queries or with very few distinct values (like a yes/no flag).

## Q5. What is the difference between `WHERE` and `GROUP BY`?
- `WHERE` — filters individual **rows** before grouping.
- `GROUP BY` — **groups** rows that share a value (e.g., all orders per customer) so you can run aggregates like `COUNT`, `SUM`, `AVG` on each group.
Use `HAVING` to filter **after** grouping (on the aggregate).

## Q6. What are aggregate functions? Give examples.
Functions that compute a single value from many rows: `COUNT()` (how many), `SUM()` (total), `AVG()` (average), `MIN()`/`MAX()`. Usually combined with `GROUP BY`:
```sql
SELECT customer_id, COUNT(*), SUM(amount)
FROM orders GROUP BY customer_id;
```

## Q7. What is a JOIN, explained simply?
It combines rows from two tables based on a related column. Example: to show each order **with the customer's name**, you JOIN `orders` and `customers` on `customer_id`. INNER JOIN keeps only matches; LEFT JOIN keeps all orders even if the customer is missing.

## Q8. What is the difference between `DELETE` and `TRUNCATE` (very common)?
- `DELETE FROM t WHERE ...` — removes specific rows, can be rolled back, slower, keeps the table.
- `TRUNCATE TABLE t` — removes **all** rows very fast, resets auto-increment, can't use a WHERE, harder to roll back.
Use DELETE for selective removal, TRUNCATE to quickly empty a whole table.

## Q9. What is a transaction, with a real example?
A group of operations that must **all succeed or all fail together**. Classic example: transferring money — debit account A **and** credit account B. If the credit fails, the debit must be undone (rolled back), or money would vanish. `BEGIN ... COMMIT` (or `ROLLBACK` on error).

## Q10. What is ACID, kept simple?
The four guarantees of a reliable transaction: **A**tomicity (all-or-nothing), **C**onsistency (rules/constraints always hold), **I**solation (concurrent transactions don't corrupt each other), **D**urability (once committed, it survives crashes). SQL databases give you ACID out of the box.

## Q11. What is normalization, in one line, and why denormalize?
**Normalization** = organizing data to avoid duplication (store each fact once, use relationships). You **denormalize** (deliberately duplicate some data) to make reads faster when joins become too expensive — common in reporting/analytics. It's a trade-off: cleaner data vs faster reads.

## Q12. SQL vs NoSQL — the simplest way to decide?
- **SQL** (Postgres/MySQL) — when data is **structured with clear relationships** and you need reliability and complex queries (orders, payments, users).
- **NoSQL** (MongoDB/Redis/Cassandra) — when you need **flexible schema**, huge scale, or a specific access pattern (product catalogs, sessions, caching, IoT data).
Rule of thumb: start with SQL unless you have a clear reason not to.

## Q13. What is a stored procedure?
A block of SQL logic saved **inside the database** that you can call by name (like a function). Good for complex data operations close to the data. Downside: harder to version/test and can hide business logic away from the app — many teams keep logic in the app instead.

## Q14. What is a view?
A **saved query** that acts like a virtual table. You query the view like a table, but it runs the underlying SQL each time. Useful for simplifying complex queries or restricting which columns users see. A **materialized view** stores the result physically (faster, but must be refreshed).

## Q15. What is a connection pool and why do we need one?
Opening a new database connection is slow and expensive. A **connection pool** keeps a set of ready-to-use connections and hands them out to requests, then reuses them. This dramatically improves performance and prevents running out of connections. HikariCP (Java) is the common one.

## Q16. What is the N+1 query problem, in plain words?
You run 1 query to get a list (say 100 orders), then accidentally run 1 more query **per order** to get its details — that's 1 + 100 = 101 queries instead of a couple. It silently kills performance. Fix by fetching related data together (a JOIN or "fetch join").

## Q17. What is a deadlock and how do you avoid it (simple)?
Two transactions each hold a lock the other needs, so both wait forever. The database detects it and kills one. Avoid by keeping transactions **short**, accessing tables in a **consistent order**, and not holding locks longer than necessary.

## Q18. What is replication vs backup — aren't they the same?
No.
- **Replication** — live copies of the database on other servers for **high availability** and read scaling (if one dies, another takes over).
- **Backup** — a point-in-time snapshot stored safely for **disaster recovery** (if data is corrupted or deleted, you restore it).
You need **both** — replication doesn't protect you from "someone deleted all the data" (that deletion replicates too!).

## Q19. What is a NoSQL "document" (MongoDB) vs a SQL "row"?
A SQL **row** is a fixed set of columns in a rigid table. A MongoDB **document** is a flexible JSON-like object that can have nested data and different fields per document. Documents let you store related data together and change the shape without a migration — flexibility vs the strict structure of SQL.

## Q20. When would you use Redis?
Redis is a super-fast **in-memory** key-value store. Use it for **caching** (store results of expensive queries), **sessions**, **rate limiting** counters, leaderboards, and simple pub/sub. It relieves load on your main database and cuts response times, at the cost of being memory-based (with optional persistence).

## Q21. What is a slow query, and what's your first step to fix one?
A query taking too long (blocking users/resources). First step: run **`EXPLAIN`** (or `EXPLAIN ANALYZE`) to see the database's execution plan — it tells you if it's scanning the whole table instead of using an index. Then add the right index, select only needed columns, and avoid functions on filtered columns.

## Q22. How would you store passwords in a database?
**Never** in plain text. Store a **salted hash** using a slow algorithm like **bcrypt** or **Argon2**. Even if the database leaks, attackers can't easily recover the actual passwords. Never use fast hashes (MD5/SHA-256) for passwords — they're too easy to crack.


---
---

# PART 6 — Redis Deep Dive (Caching, Data Structures, Patterns, Pitfalls)

> Anchor: You've used Redis for caching, sessions, and rate limiting in high-throughput microservices. These questions go from fundamentals to the senior-level traps interviewers love.

## R1. What is Redis, and why is it so fast?
Redis (**RE**mote **DI**ctionary **S**erver) is an **in-memory data structure store** used as a cache, database, and message broker. Its speed (sub-millisecond, ~100k+ ops/sec on a single node) comes from several deliberate design choices:
- **In-memory** — all data lives in RAM, so reads/writes avoid slow disk I/O. (It can persist to disk, but the working set is in memory.)
- **Single-threaded command execution** — Redis executes commands on **one main thread** using an **event loop** (multiplexed I/O via epoll/kqueue). This sounds counterintuitive, but it **eliminates lock contention and context-switching overhead**, and each command is inherently **atomic** (no two commands interleave). (Redis 6+ added multi-threaded *I/O* for network read/write, but command execution logic is still effectively serialized.)
- **Efficient data structures** — purpose-built C implementations (e.g., ziplist/listpack for small collections, skip lists for sorted sets) minimize memory and CPU.
- **Simple protocol (RESP)** — a lightweight, easily-parsed wire protocol keeps overhead low.
- **One-liner:** "Redis is fast because it's in-memory, single-threaded (no locking), event-loop driven, and uses optimized data structures — giving atomic, sub-millisecond operations."

## R2. What are the core Redis data types, and when do you use each?
Redis is a "data structure server" — the value isn't just a blob, it's a rich type with its own commands:
- **String** — the basic type (text, numbers, or binary up to 512MB). Uses: **caching** serialized objects/JSON, **counters** (`INCR`/`DECR` are atomic), feature flags, distributed locks (`SET key val NX PX`).
- **Hash** — a map of field→value under one key (like a mini object). Uses: storing an **object's fields** (`user:100 → {name, email, age}`) so you can update one field without rewriting the whole object; good memory efficiency for small objects.
- **List** — an ordered, linked list (push/pop at both ends). Uses: **queues** (`LPUSH`/`RPOP`), recent activity feeds, `BLPOP` for blocking consumers.
- **Set** — an unordered collection of **unique** members. Uses: tags, unique visitors, and **set operations** (`SINTER`, `SUNION`, `SDIFF`) for things like "common friends."
- **Sorted Set (ZSet)** — a set where each member has a **score**, kept **sorted by score**. Uses: **leaderboards** (`ZREVRANGE`), **priority queues**, rate limiting (sliding window with timestamps as scores), time-series.
- **Advanced/specialized:** **Bitmaps** (bit-level ops on strings — e.g., daily active-user flags), **HyperLogLog** (approximate unique counts in ~12KB regardless of cardinality), **Streams** (append-only log with consumer groups — Kafka-like), and **Geospatial** (radius queries).
- **Interview tip:** knowing *which structure fits which problem* (leaderboard → ZSet, unique count → HyperLogLog, queue → List/Stream) signals real experience.

## R3. Explain the main caching patterns (cache-aside, read-through, write-through, write-behind).
These describe **how your app and cache coordinate with the database**:
- **Cache-aside (lazy loading)** — the **most common**. The app checks the cache first; on a **miss**, it reads from the DB, writes the result into the cache, and returns it. The app owns the caching logic.
  ```
  value = cache.get(key)
  if value == null:            # cache miss
      value = db.query(key)
      cache.set(key, value, ttl)
  return value
  ```
  *Pros:* only requested data is cached (memory efficient); cache failure doesn't break reads. *Cons:* first request per key is slow (cold miss); risk of stale data (mitigate with TTL + invalidation on write).
- **Read-through** — the app talks **only to the cache**; the cache library itself loads from the DB on a miss. Same effect as cache-aside but the loading logic lives in the cache layer, not your app.
- **Write-through** — on a write, the app writes to the **cache and DB synchronously** (both before returning). *Pros:* cache is always consistent with DB. *Cons:* every write pays the DB latency; you cache data that may never be read.
- **Write-behind (write-back)** — the app writes to the **cache only**, which **asynchronously** flushes to the DB later (batched). *Pros:* very fast writes, absorbs bursts. *Cons:* **risk of data loss** if Redis dies before the flush; more complex.
- **Practical default:** **cache-aside + TTL + explicit invalidation on update** is the go-to for most read-heavy services.

## R4. How does TTL / key expiration work, and how does Redis actually remove expired keys?
You set a **time-to-live** so keys auto-delete (e.g., `SET key val EX 3600`, or `EXPIRE key 3600`). Redis removes expired keys using **two complementary strategies**:
1. **Lazy (passive) expiration** — when a client **accesses** a key, Redis checks if it's expired; if so, it deletes it then and returns nil. Cheap, but expired keys that are never accessed keep taking memory.
2. **Active expiration** — a background job runs ~10 times/sec, **samples** a random subset of keys with TTLs, and deletes the expired ones. If a high fraction were expired, it repeats to catch up. This bounds the stale-key buildup.
- **Why both:** lazy alone would leak memory for untouched keys; active alone would waste CPU scanning everything. Together they balance CPU vs memory.
- **Gotcha:** because expiration is probabilistic/lazy, a key can remain in memory slightly past its TTL until sampled or accessed — don't rely on *exact* deletion timing.

## R5. What are Redis eviction policies (maxmemory-policy)?
When Redis hits its `maxmemory` limit, the **eviction policy** decides what to drop to make room:
- **`noeviction`** (default) — reject writes with an error (reads still work). Safe when Redis is a **database**, not a cache.
- **`allkeys-lru`** — evict the **Least Recently Used** key from *all* keys. Best general **cache** policy.
- **`allkeys-lfu`** — evict the **Least Frequently Used** (Redis 4+). Better when some keys are consistently hot regardless of recency.
- **`volatile-lru` / `volatile-lfu` / `volatile-ttl` / `volatile-random`** — same idea but only among keys **that have a TTL set** (`volatile-ttl` evicts those closest to expiring).
- **`allkeys-random` / `volatile-random`** — evict a random key (rarely ideal).
- **Note:** Redis uses an **approximated** LRU/LFU (samples a few keys rather than tracking a perfect global order) to save memory/CPU — tunable via `maxmemory-samples`.
- **Interview point:** "For a pure cache I use `allkeys-lru` (or `-lfu` for skewed access); for Redis-as-a-datastore I use `noeviction` and rely on TTLs + capacity planning."

## R6. How does Redis persist data (RDB vs AOF)? Is it durable?
Redis is in-memory but offers **optional persistence** so data survives restarts:
- **RDB (Redis Database) snapshots** — periodically **forks** the process and dumps the entire dataset to a compact binary `.rdb` file. *Pros:* small files, fast restarts, minimal runtime overhead, great for backups. *Cons:* you can **lose data since the last snapshot** (e.g., up to several minutes).
- **AOF (Append-Only File)** — logs **every write command** to a file, replayed on restart. Fsync configurable: `always` (durable, slowest), `everysec` (default — at most ~1s data loss, good balance), `no` (OS decides). *Pros:* far less data loss, human-readable log. *Cons:* larger files, slower restarts (mitigated by periodic AOF rewrite/compaction).
- **Hybrid (recommended)** — enable **both**: AOF for durability + RDB for fast restarts/backups. Redis 7 can also use an RDB preamble inside the AOF for faster loads.
- **Honest answer:** Redis is **not as durable as an ACID RDBMS** — even AOF `everysec` can lose ~1s of writes on a crash. Treat it as a cache/fast store, and keep the system of record in a durable DB for critical data.

## R7. How do you make Redis operations atomic — MULTI/EXEC vs Lua scripts?
Single commands are already atomic (single thread). For **multiple** commands you have options:
- **Transactions (`MULTI`/`EXEC`)** — queue commands after `MULTI`; `EXEC` runs them **sequentially with no other client interleaving**. But note: it's **not** a rollback-style transaction — if one command fails at runtime, others still execute (there's no rollback). `DISCARD` cancels the queued block.
- **Optimistic locking with `WATCH`** — `WATCH key` before `MULTI`; if the watched key is modified by anyone before `EXEC`, the transaction **aborts** (returns nil), and you retry. This implements **compare-and-set** / check-then-act safely.
  ```
  WATCH balance
  val = GET balance
  MULTI
  SET balance (val - 10)
  EXEC        # fails (nil) if balance changed since WATCH -> retry
  ```
- **Lua scripting (`EVAL`)** — the **most powerful**: a Lua script runs **atomically as a single unit** on the server (no other command interleaves), lets you do read-compute-write logic in one round trip, and avoids network chatter. Ideal for atomic **rate limiters**, conditional updates, and multi-key logic.
- **Rule of thumb:** simple grouped writes → `MULTI/EXEC`; check-then-act → `WATCH` (or Lua); complex atomic logic / performance-critical → **Lua**.

## R8. How would you implement a distributed lock with Redis? What are the pitfalls?
A distributed lock coordinates access across multiple app instances.
- **Basic single-instance lock:** `SET lock_key unique_token NX PX 30000`
  - `NX` = set only if the key doesn't exist (acquire only if free).
  - `PX 30000` = auto-expire after 30s so a crashed holder doesn't lock forever.
  - The **unique token** (e.g., a UUID) identifies the owner.
- **Safe release** — you must **not** blindly `DEL` (you might delete someone else's lock after yours expired). Use a **Lua script** to atomically "delete only if the token matches":
  ```lua
  if redis.call("GET", KEYS[1]) == ARGV[1] then
      return redis.call("DEL", KEYS[1])
  else
      return 0
  end
  ```
- **Pitfalls:**
  - **TTL too short** — lock expires mid-work → two holders. Mitigate with a **watchdog** that extends the TTL (as Redisson does).
  - **Clock/GC pauses** — a stalled holder can overrun its lease → correctness risk. A true fencing solution needs a **fencing token** (monotonic number checked by the resource).
  - **Single point of failure** — if the Redis node fails, locks are lost. **Redlock** (locking across N independent masters, needing a majority) improves this but is **debated** (Martin Kleppmann's critique) for strict correctness.
- **Practical advice:** for most apps, single-instance `SET NX PX` + Lua release (or the **Redisson** library with its watchdog) is enough. For strict correctness, add fencing tokens or use a consensus system (ZooKeeper/etcd).

## R9. Explain cache stampede (thundering herd), cache penetration, and cache avalanche — and how to prevent each.
These are the three classic **cache failure modes** senior interviewers probe:
- **Cache stampede / thundering herd** — a **hot key expires**, and thousands of concurrent requests all miss simultaneously and hammer the DB at once.
  - *Fixes:* (1) a **mutex/lock** so only one request rebuilds the value while others wait or serve stale; (2) **early/probabilistic recomputation** (refresh just before expiry); (3) **request coalescing** (single-flight).
- **Cache penetration** — requests for keys that **don't exist anywhere** (often malicious), so every request misses the cache *and* the DB, giving no protection.
  - *Fixes:* (1) **cache the negative result** (store a null/sentinel with a short TTL); (2) a **Bloom filter** in front to reject keys that definitely don't exist; (3) input validation.
- **Cache avalanche** — a **large number of keys expire at the same time** (or Redis restarts/goes down), dumping massive load onto the DB simultaneously.
  - *Fixes:* (1) **randomize/jitter TTLs** (e.g., base + random spread) so keys don't expire together; (2) **high availability** (replicas/cluster) so Redis doesn't fully drop; (3) circuit breakers/rate limiting to protect the DB; (4) multi-level caching.
- **One-liner:** "Stampede = one hot key expiring (fix: lock/early refresh); penetration = querying non-existent keys (fix: cache nulls / Bloom filter); avalanche = mass simultaneous expiry (fix: TTL jitter + HA)."

## R10. How do you keep the cache consistent with the database on updates?
Cache invalidation is famously hard ("one of the two hard things in CS"). Common strategies and their trade-offs:
- **Cache-aside with invalidation** — on update: write the DB, then **delete** the cache key (don't update it). Next read repopulates. **Deleting is safer than updating** because concurrent writes updating the cache can interleave and leave stale values.
- **Write-through** — write DB + cache together (consistent but slower writes).
- **The subtle race:** even "update DB then delete cache" has a window where a concurrent read can repopulate stale data between the DB write and the delete. Mitigations: **delete-before-and-after** (double delete), short TTLs as a safety net, or **read-your-writes** via versioning.
- **TTL as a backstop** — always set a TTL so even a missed invalidation self-heals eventually.
- **Event-driven invalidation** — publish DB change events (CDC / outbox / Debezium) that invalidate cache entries reliably across services.
- **Honest framing:** "I use cache-aside, invalidate by **deleting** the key on writes, always set a **TTL** as a safety net, and for strict cross-service consistency I drive invalidation from change events."

## R11. What is Redis Pub/Sub, and how does it differ from Redis Streams and Kafka?
- **Pub/Sub** — publishers `PUBLISH` to a channel; all currently-**subscribed** clients receive it. It's **fire-and-forget**: messages are **not stored**, so a subscriber that's offline or connects later **misses** them. No acknowledgments, no replay. Good for **real-time, non-critical** fan-out (live notifications, cache-invalidation signals, chat presence).
- **Streams (Redis 5+)** — an **append-only log** with unique IDs; messages are **persisted** in the stream. Supports **consumer groups** (like Kafka), so multiple consumers share the workload, each message is acknowledged (`XACK`), and unprocessed messages can be reclaimed (`XPENDING`/`XCLAIM`). Supports **replay** from any ID. This is Redis's answer to durable messaging.
- **vs Kafka** — Kafka is a distributed, disk-based log built for **very high throughput, long retention, and strong ordering/partitioning at scale**. Redis Streams is lighter, in-memory (with persistence), lower-latency, and simpler — great for moderate volumes where you already run Redis, but not a full Kafka replacement for large event backbones.
- **One-liner:** "Pub/Sub is fire-and-forget with no persistence; Streams add durability, consumer groups, acks, and replay; Kafka is the heavyweight for large-scale, long-retention event streaming."

## R12. How do you scale Redis — replication, Sentinel, and Cluster?
Three layers, each solving a different problem:
- **Replication (primary–replica)** — a primary asynchronously copies data to one or more **read replicas**. Enables **read scaling** and a warm standby. But replication is **async**, so a failover can lose the last few writes, and failover isn't automatic by itself.
- **Redis Sentinel** — adds **automatic high availability**: Sentinel processes **monitor** the primary, and on failure **elect and promote** a replica to primary, then reconfigure clients. It gives HA + failover but **not** horizontal write scaling (still one primary for writes).
- **Redis Cluster** — **horizontal scaling via sharding**. The keyspace is split into **16384 hash slots** distributed across multiple primaries (each with its own replicas). Clients route each key to the owning node (`CRC16(key) mod 16384`). This scales **both reads and writes** and stays available if a minority of nodes fail.
  - **Multi-key caveat:** commands touching multiple keys must land in the **same slot**; use **hash tags** `{...}` (e.g., `user:{123}:profile` and `user:{123}:orders` hash by `123`) to co-locate related keys.
- **Progression to state:** "Start single-node → add replicas for read scaling → Sentinel for automatic failover (HA) → Cluster when one node can't hold the data or handle the write throughput."

## R13. Redis is single-threaded — how does it handle high concurrency, and what can block it?
- **Concurrency model:** a single main thread + an **event loop** processes commands one at a time, extremely fast, so it serves **many concurrent clients** without locks. Redis 6+ uses **multiple threads only for network I/O** (parsing/replies), keeping command *execution* single-threaded and atomic.
- **The danger — slow commands block everything:** because one command runs at a time, a **single O(N) command on a huge key** stalls **all** other clients. Notorious offenders:
  - **`KEYS *`** — scans the entire keyspace (O(N)); **never use in production** — use **`SCAN`** (cursor-based, incremental) instead.
  - Big `SMEMBERS`/`HGETALL`/`LRANGE 0 -1` on large collections, or `FLUSHALL`/`DEL` on huge keys.
- **Fixes:** use **`SCAN`/`HSCAN`/`SSCAN`/`ZSCAN`**, break up big keys, use `UNLINK` (async delete) instead of `DEL` for large keys, and keep individual values reasonably sized.
- **One-liner:** "Redis handles concurrency via a fast single-threaded event loop (atomic commands, no locks) — but one slow O(N) command blocks all clients, so avoid `KEYS`, use `SCAN`, and never store giant keys."

## R14. How do you implement rate limiting with Redis?
Redis is ideal for rate limiting because counters are **atomic** and keys can **auto-expire**:
- **Fixed window (simplest):** one counter per window.
  ```
  key = "rate:" + userId + ":" + currentMinute
  count = INCR key
  if count == 1: EXPIRE key 60
  if count > LIMIT: reject
  ```
  *Downside:* bursty at window edges (2× limit possible across a boundary).
- **Sliding window log (accurate):** store request timestamps in a **Sorted Set** (score = timestamp); on each request, `ZREMRANGEBYSCORE` to drop old entries, `ZADD` the new one, `ZCARD` to count within the window. Accurate but more memory.
- **Token bucket / leaky bucket:** track tokens + last-refill time (often in a **Hash**), refill based on elapsed time; smooths bursts. Best done in a **Lua script** so the read-compute-write is atomic.
- **Best practice:** implement the whole check-and-increment in **one Lua script** to avoid race conditions between multiple app instances.

## R15. Rapid-fire Redis one-liners.
- **`SETNX` / `SET ... NX`** — set only if not exists (basis of locks).
- **`INCR`/`DECR`** — atomic counters (great for metrics, rate limits).
- **`EXPIRE` / `TTL`** — set/inspect a key's time-to-live; `PERSIST` removes it.
- **`SCAN` vs `KEYS`** — always `SCAN` in prod (non-blocking cursor); `KEYS` blocks.
- **`DEL` vs `UNLINK`** — `UNLINK` frees big keys **asynchronously** (non-blocking).
- **Pipelining** — batch many commands in one round trip to cut network latency (not atomic; use `MULTI` for atomicity).
- **`OBJECT ENCODING`** — shows the internal encoding (e.g., listpack vs hashtable) — small collections use compact encodings automatically.
- **Redis vs Memcached** — Redis has **rich data types, persistence, replication, Lua, pub/sub**; Memcached is simpler, pure in-memory key-value, multi-threaded — Redis is the default choice for most needs.
- **Why not store everything in Redis?** RAM is expensive/limited and durability is weaker than an RDBMS — use it as a cache/fast layer, not the system of record for critical data.
- **Big keys are dangerous** — one huge value/collection causes latency spikes, blocking, and uneven cluster slots; keep values small and split large structures.

