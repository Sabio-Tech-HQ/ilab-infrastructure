"""
analyzer.py / tuner.py
============================================================
PostgreSQL Performance Analyzer (PostgreSQL 18 & Gemini Powered)
Collects database statistics, sends them to Google Gemini via
OpenAI-compatible API, and writes a self-contained HTML report.
"""

import html
import json
import os
import re
from datetime import datetime

import psycopg2
import psycopg2.extras
import psycopg2.sql as pgsql
import requests


# ============================================================
# CONSTANTS
# ============================================================

EXCLUDED_SCHEMAS = (
    "pg_catalog",
    "pg_toast",
    "information_schema",
)

EXCLUDED_SCHEMA_PREFIXES = ("pg_temp_", "pg_toast_")

REPORT_DIR = os.environ.get("REPORT_DIR", ".")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemini-1.5-flash")
OLLAMA_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "900"))

PG_MIN_CALLS = int(os.environ.get("PG_MIN_CALLS", "1"))
PG_MIN_MS = float(os.environ.get("PG_MIN_MS", "100"))


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection() -> psycopg2.extensions.connection:
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        connect_timeout=10,
    )


# ============================================================
# QUERY HELPERS
# ============================================================

def run_query(conn, sql: str, params=None) -> list:
    cur = conn.cursor()
    try:
        cur.execute(sql, params)
        return cur.fetchall()
    except Exception as exc:
        print(f"\n[QUERY FAILED]\n{sql}\n[ERROR] {exc}")
        conn.rollback()
        return []
    finally:
        cur.close()


def run_query_dict(conn, sql: str, params=None) -> list:
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute(sql, params)
        return [dict(r) for r in cur.fetchall()]
    except Exception as exc:
        print(f"\n[QUERY FAILED (dict)]\n{sql}\n[ERROR] {exc}")
        conn.rollback()
        return []
    finally:
        cur.close()


def _schema_exclusion_clause(alias: str = "") -> str:
    col = f"{alias}schemaname" if alias else "schemaname"
    literals = ", ".join(f"'{s}'" for s in EXCLUDED_SCHEMAS)
    prefix_clauses = " AND ".join(
        f"{col} NOT LIKE '{p}%'" for p in EXCLUDED_SCHEMA_PREFIXES
    )
    return f"{col} NOT IN ({literals}) AND {prefix_clauses}"


# ============================================================
# VIEW / MATERIALIZED VIEW HELPERS
# ============================================================

def extract_views_from_query(conn, query: str) -> list:
    if not query or not isinstance(query, str):
        return []

    cte_names = set(re.findall(r"\bwith\b.*?\b(\w+)\s+as\s*\(", query, re.IGNORECASE | re.DOTALL))

    objects = re.findall(
        r"\b(?:from|join)\s+([\w]+(?:\.[\w]+)?)",
        query,
        re.IGNORECASE,
    )
    if not objects:
        return []

    objects = [o for o in objects if o.split(".")[-1].lower() not in {n.lower() for n in cte_names}]
    if not objects:
        return []

    views = []
    for obj in objects:
        schema, name = obj.split(".", 1) if "." in obj else ("public", obj)
        try:
            result = run_query(
                conn,
                """
                SELECT schemaname, viewname
                FROM   pg_views
                WHERE  schemaname = %s AND viewname = %s
                UNION ALL
                SELECT schemaname, matviewname
                FROM   pg_matviews
                WHERE  schemaname = %s AND matviewname = %s
                """,
                (schema, name, schema, name),
            )
            if result:
                views.append(f"{schema}.{name}")
        except Exception as exc:
            print(f"[View detection failed for {obj}] {exc}")

    return list(set(views))


def collect_view_plans(conn, slow_queries: list) -> list:
    results = []
    checked: set = set()

    for row in slow_queries:
        query = row[1] if len(row) > 1 else None
        if not isinstance(query, str):
            continue

        for view in extract_views_from_query(conn, query):
            if view in checked:
                continue
            checked.add(view)
            print(f"  Analyzing view plan: {view}")

            schema_part, name_part = (view.split(".", 1) if "." in view else ("public", view))
            explain_sql = pgsql.SQL("EXPLAIN (FORMAT JSON) SELECT * FROM {} LIMIT 100").format(
                pgsql.Identifier(schema_part, name_part)
            )
            plan = run_query(conn, explain_sql)

            entry: dict = {"view": view, "source_query": query}
            if plan:
                entry["plan_summary"] = summarize_plan(plan)
            else:
                entry["error"] = "EXPLAIN returned no rows"
            results.append(entry)

    return results


def summarize_plan(plan: list) -> dict:
    summary: dict = {
        "node_types": [],
        "relations": [],
        "joins": [],
        "aggregations": [],
        "sorts": [],
        "sequential_scans": [],
        "index_scans": [],
        "parallel_nodes": [],
        "cte_scans": [],
        "largest_estimated_rows": 0,
    }

    def walk(node: dict):
        if not isinstance(node, dict):
            return

        node_type = node.get("Node Type", "")
        relation = node.get("Relation Name")
        rows = node.get("Plan Rows", 0)

        if node_type:
            summary["node_types"].append(node_type)

        if relation:
            summary["relations"].append(relation)

        if rows > summary["largest_estimated_rows"]:
            summary["largest_estimated_rows"] = rows

        if "Join" in node_type:
            summary["joins"].append(node_type)

        if node_type in ("Aggregate", "GroupAggregate", "HashAggregate", "MixedAggregate"):
            summary["aggregations"].append(node_type)

        if node_type in ("Sort", "Incremental Sort"):
            summary["sorts"].append(node_type)

        if node_type == "Seq Scan":
            summary["sequential_scans"].append({"table": relation, "rows": rows})

        if node_type in ("Index Scan", "Index Only Scan", "Bitmap Index Scan", "Bitmap Heap Scan"):
            summary["index_scans"].append({"table": relation, "type": node_type})

        if node_type == "CTE Scan":
            summary["cte_scans"].append(node.get("CTE Name", "unknown"))

        if node.get("Parallel Aware") or node_type in ("Gather", "Gather Merge"):
            summary["parallel_nodes"].append(node_type)

        for child in node.get("Plans", []):
            walk(child)

    try:
        root = plan[0][0][0]["Plan"]
        walk(root)
    except Exception as exc:
        summary["parse_error"] = str(exc)

    for key in ("node_types", "relations", "joins", "aggregations",
                "sorts", "parallel_nodes", "cte_scans"):
        summary[key] = list(set(summary[key]))

    return summary


# ============================================================
# STATISTICS COLLECTION
# ============================================================

def _collect(label: str, conn, sql: str, params=None) -> list:
    print(f"  Collecting {label}...")
    return run_query(conn, sql, params)


def collect_stats(conn) -> dict:
    stats: dict = {}
    excl = _schema_exclusion_clause()

    stats["version"] = _collect("version", conn, "SELECT version();")

    stats["configuration"] = _collect(
        "configuration",
        conn,
        """
        SELECT name, setting, unit, short_desc
        FROM   pg_settings
        WHERE  name IN (
            'shared_buffers',
            'work_mem',
            'maintenance_work_mem',
            'effective_cache_size',
            'max_connections',
            'random_page_cost',
            'seq_page_cost',
            'effective_io_concurrency',
            'max_worker_processes',
            'max_parallel_workers',
            'max_parallel_workers_per_gather',
            'autovacuum',
            'autovacuum_max_workers',
            'autovacuum_vacuum_scale_factor',
            'autovacuum_analyze_scale_factor',
            'autovacuum_vacuum_cost_delay',
            'autovacuum_vacuum_cost_limit',
            'log_min_duration_statement',
            'checkpoint_completion_target',
            'wal_buffers',
            'wal_level',
            'max_wal_size',
            'min_wal_size'
        )
        ORDER BY name;
        """,
    )

    stats["slow_queries"] = _collect(
        "slow queries",
        conn,
        """
        SELECT
            queryid,
            query,
            calls,
            round(total_exec_time::numeric, 2)         AS total_ms,
            round(mean_exec_time::numeric, 2)            AS avg_ms,
            round(stddev_exec_time::numeric, 2)          AS stddev_ms,
            rows,
            shared_blks_hit,
            shared_blks_read,
            shared_blks_written,
            shared_blks_dirtied,
            temp_blks_read,
            temp_blks_written,
            round(
                100.0 * shared_blks_hit
                / NULLIF(shared_blks_hit + shared_blks_read, 0),
                2
            )                                          AS query_hit_pct
        FROM pg_stat_statements
        WHERE query NOT ILIKE '%pg_%'
          AND query NOT ILIKE '%pg_stat%'
          AND query NOT ILIKE 'SET %'
          AND query NOT ILIKE 'RESET %'
          AND calls >= %s
          AND mean_exec_time >= %s
        ORDER BY mean_exec_time DESC
        LIMIT 30;
        """,
        params=(PG_MIN_CALLS, PG_MIN_MS),
    )

    print("  Collecting view execution plans...")
    stats["view_plans"] = collect_view_plans(conn, stats["slow_queries"])

    stats["table_sizes"] = _collect(
        "table sizes",
        conn,
        f"""
        SELECT
            schemaname,
            relname,
            pg_size_pretty(pg_total_relation_size(relid))   AS total_size,
            pg_size_pretty(pg_relation_size(relid))         AS table_size,
            pg_size_pretty(
                pg_total_relation_size(relid)
                - pg_relation_size(relid)
            )                                               AS index_size,
            n_live_tup
        FROM pg_stat_user_tables
        WHERE {excl}
        ORDER BY pg_total_relation_size(relid) DESC
        LIMIT 50;
        """,
    )

    stats["table_health"] = _collect(
        "table health",
        conn,
        f"""
        SELECT
            schemaname,
            relname,
            quote_ident(schemaname) || '.' || quote_ident(relname)
                                        AS safe_table_ref,
            n_live_tup,
            n_dead_tup,
            round(
                n_dead_tup::numeric
                / NULLIF(n_live_tup + n_dead_tup, 0) * 100, 2
            )                               AS dead_tuple_pct,
            last_vacuum,
            last_autovacuum,
            last_analyze,
            last_autoanalyze,
            CASE
                WHEN last_vacuum IS NULL THEN NULL
                ELSE round(EXTRACT(EPOCH FROM (now() - last_vacuum)) / 86400)::int
            END                             AS days_since_manual_vacuum,
            CASE
                WHEN last_autovacuum IS NULL THEN NULL
                ELSE round(EXTRACT(EPOCH FROM (now() - last_autovacuum)) / 86400)::int
            END                             AS days_since_autovacuum,
            CASE
                WHEN GREATEST(last_vacuum, last_autovacuum) IS NULL THEN NULL
                ELSE round(
                    EXTRACT(EPOCH FROM (now() - GREATEST(last_vacuum, last_autovacuum)))
                    / 86400
                )::int
            END                             AS days_since_last_vacuum,
            CASE
                WHEN GREATEST(last_analyze, last_autoanalyze) IS NULL THEN NULL
                ELSE round(
                    EXTRACT(EPOCH FROM (now() - GREATEST(last_analyze, last_autoanalyze)))
                    / 86400
                )::int
            END                             AS days_since_last_analyze,
            vacuum_count,
            autovacuum_count
        FROM pg_stat_user_tables
        WHERE {excl}
        ORDER BY dead_tuple_pct DESC NULLS LAST
        LIMIT 50;
        """,
    )

    stats["sequential_scans"] = _collect(
        "sequential scans",
        conn,
        f"""
        SELECT
            schemaname,
            relname,
            seq_scan,
            seq_tup_read,
            idx_scan,
            n_live_tup,
            round(
                seq_scan::numeric / NULLIF(seq_scan + idx_scan, 0) * 100,
                2
            )                           AS seq_scan_pct
        FROM pg_stat_user_tables
        WHERE {excl}
          AND seq_scan > 0
        ORDER BY seq_tup_read DESC
        LIMIT 50;
        """,
    )

    stats["index_usage"] = _collect(
        "index usage",
        conn,
        f"""
        SELECT
            ui.schemaname,
            ui.relname,
            ui.indexrelname,
            ui.idx_scan,
            ui.idx_tup_read,
            ui.idx_tup_fetch,
            pg_size_pretty(pg_relation_size(ui.indexrelid)) AS index_size,
            ix.indisunique,
            ix.indisprimary,
            pg_get_indexdef(ui.indexrelid)                  AS index_def,
            (
                SELECT a.attname
                FROM   pg_attribute a
                WHERE  a.attrelid = ix.indrelid
                  AND  a.attnum   = ix.indkey[0]
            )                                               AS leading_column
        FROM pg_stat_user_indexes ui
        JOIN pg_index ix ON ix.indexrelid = ui.indexrelid
        WHERE {_schema_exclusion_clause("ui.")}
        ORDER BY ui.idx_scan ASC
        LIMIT 50;
        """,
    )

    stats["unused_indexes"] = _collect(
        "unused indexes",
        conn,
        f"""
        SELECT
            ui.schemaname,
            ui.relname,
            ui.indexrelname,
            ui.idx_scan,
            pg_size_pretty(pg_relation_size(ui.indexrelid)) AS index_size,
            ix.indisunique,
            ix.indisprimary
        FROM pg_stat_user_indexes ui
        JOIN pg_index ix ON ix.indexrelid = ui.indexrelid
        WHERE ui.idx_scan = 0
          AND NOT ix.indisprimary
          AND NOT ix.indisunique
          AND NOT EXISTS (
              SELECT 1 FROM pg_constraint
              WHERE conindid = ui.indexrelid
          )
          AND {_schema_exclusion_clause("ui.")}
        ORDER BY pg_relation_size(ui.indexrelid) DESC
        LIMIT 50;
        """,
    )

    stats["duplicate_indexes"] = _collect(
        "duplicate indexes",
        conn,
        f"""
        SELECT
            n.nspname                                       AS schemaname,
            t.relname                                       AS tablename,
            ix1.relname                                     AS index1,
            ix2.relname                                     AS index2,
            pg_size_pretty(pg_relation_size(i1.indexrelid)) AS size1,
            pg_size_pretty(pg_relation_size(i2.indexrelid)) AS size2,
            pg_get_indexdef(i1.indexrelid)                  AS def1,
            pg_get_indexdef(i2.indexrelid)                  AS def2
        FROM pg_index i1
        JOIN pg_index i2
            ON  i1.indrelid   = i2.indrelid
            AND i1.indexrelid < i2.indexrelid
            AND i1.indkey::text LIKE (i2.indkey::text || '%')
        JOIN pg_class t  ON t.oid  = i1.indrelid
        JOIN pg_class ix1 ON ix1.oid = i1.indexrelid
        JOIN pg_class ix2 ON ix2.oid = i2.indexrelid
        JOIN pg_namespace n ON n.oid = t.relnamespace
        WHERE n.nspname NOT IN ({', '.join(f"'{s}'" for s in EXCLUDED_SCHEMAS)})
          AND n.nspname NOT LIKE 'pg_temp_%'
        ORDER BY n.nspname, t.relname;
        """,
    )

    stats["index_bloat"] = _collect(
        "index bloat estimate",
        conn,
        f"""
        SELECT
            n.nspname                                        AS schemaname,
            c.relname                                        AS tablename,
            ic.relname                                       AS indexname,
            pg_size_pretty(pg_relation_size(ix.indexrelid)) AS index_size,
            round(
                100 * (
                    pg_relation_size(ix.indexrelid)::numeric
                    / NULLIF(pg_relation_size(ix.indrelid), 0)
                ),
                1
            )                                                AS index_to_table_ratio_pct
        FROM pg_index ix
        JOIN pg_class  c  ON c.oid  = ix.indrelid
        JOIN pg_class  ic ON ic.oid = ix.indexrelid
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname NOT IN ({', '.join(f"'{s}'" for s in EXCLUDED_SCHEMAS)})
          AND n.nspname NOT LIKE 'pg_temp_%'
          AND NOT ix.indisprimary
          AND pg_relation_size(ix.indexrelid) > 8192
        ORDER BY pg_relation_size(ix.indexrelid) DESC
        LIMIT 50;
        """,
    )

    print("  Collecting vacuum statistics...")
    stats["vacuum"] = run_query_dict(
        conn,
        f"""
        SELECT
            schemaname,
            relname,
            quote_ident(schemaname) || '.' || quote_ident(relname)
                                        AS safe_table_ref,
            n_live_tup,
            n_dead_tup,
            round(
                n_dead_tup::numeric
                / NULLIF(n_live_tup + n_dead_tup, 0) * 100, 2
            )                           AS dead_tuple_pct,
            last_vacuum,
            last_autovacuum,
            last_analyze,
            last_autoanalyze,
            CASE
                WHEN last_vacuum IS NULL THEN NULL
                ELSE round(EXTRACT(EPOCH FROM (now() - last_vacuum)) / 86400)::int
            END                         AS days_since_manual_vacuum,
            CASE
                WHEN last_autovacuum IS NULL THEN NULL
                ELSE round(EXTRACT(EPOCH FROM (now() - last_autovacuum)) / 86400)::int
            END                         AS days_since_autovacuum,
            CASE
                WHEN GREATEST(last_vacuum, last_autovacuum) IS NULL
                    THEN NULL
                ELSE
                    round(
                        EXTRACT(EPOCH FROM (now() - GREATEST(last_vacuum, last_autovacuum)))
                        / 86400
                    )::int
            END                         AS days_since_last_vacuum,
            CASE
                WHEN GREATEST(last_analyze, last_autoanalyze) IS NULL
                    THEN NULL
                ELSE
                    round(
                        EXTRACT(EPOCH FROM (now() - GREATEST(last_analyze, last_autoanalyze)))
                        / 86400
                    )::int
            END                         AS days_since_last_analyze,
            vacuum_count,
            autovacuum_count,
            analyze_count,
            autoanalyze_count
        FROM pg_stat_user_tables
        WHERE {excl}
        ORDER BY
            GREATEST(last_vacuum, last_autovacuum) ASC NULLS FIRST,
            n_dead_tup DESC
        LIMIT 60;
        """,
    )

    stats["autovacuum_threshold_check"] = _collect(
        "autovacuum threshold check",
        conn,
        f"""
        WITH av_settings AS (
            SELECT
                (SELECT setting::numeric FROM pg_settings WHERE name = 'autovacuum_vacuum_scale_factor')
                    AS scale_factor,
                (SELECT setting::numeric FROM pg_settings WHERE name = 'autovacuum_vacuum_threshold')
                    AS threshold,
                (SELECT setting::numeric FROM pg_settings WHERE name = 'autovacuum_analyze_scale_factor')
                    AS analyze_scale_factor,
                (SELECT setting::numeric FROM pg_settings WHERE name = 'autovacuum_analyze_threshold')
                    AS analyze_threshold
        )
        SELECT
            t.schemaname,
            t.relname,
            quote_ident(t.schemaname) || '.' || quote_ident(t.relname)
                                        AS safe_table_ref,
            t.n_live_tup,
            t.n_dead_tup,
            round(s.threshold + s.scale_factor * t.n_live_tup)
                                        AS vacuum_trigger_at_n_dead,
            (t.n_dead_tup >= round(s.threshold + s.scale_factor * t.n_live_tup))
                                        AS vacuum_threshold_exceeded,
            round(s.analyze_threshold + s.analyze_scale_factor * t.n_live_tup)
                                        AS analyze_trigger_at_n_changes,
            t.last_autovacuum,
            CASE
                WHEN GREATEST(t.last_vacuum, t.last_autovacuum) IS NULL THEN NULL
                ELSE round(
                        EXTRACT(EPOCH FROM (now() - GREATEST(t.last_vacuum, t.last_autovacuum)))
                        / 86400
                    )::int
            END                         AS days_since_last_vacuum,
            t.autovacuum_count
        FROM pg_stat_user_tables t, av_settings s
        WHERE {_schema_exclusion_clause("t.")}
          AND t.n_live_tup > 0
        ORDER BY
            vacuum_threshold_exceeded DESC,
            t.n_dead_tup DESC
        LIMIT 40;
        """,
    )

    stats["stats_reset"] = _collect(
        "stats reset timestamp",
        conn,
        """
        SELECT datname, stats_reset, now() - stats_reset AS age_since_reset
        FROM pg_stat_database
        WHERE datname = current_database();
        """,
    )

    stats["autovacuum_disabled_tables"] = _collect(
        "per-table autovacuum overrides",
        conn,
        """
        SELECT n.nspname AS schemaname, c.relname, c.reloptions,
               EXISTS (
                   SELECT 1 FROM unnest(c.reloptions) AS opt
                   WHERE opt ILIKE 'autovacuum_enabled=false'
               ) AS autovacuum_disabled
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relkind IN ('r', 'p')
          AND c.reloptions IS NOT NULL
          AND array_to_string(c.reloptions, ',') ILIKE '%autovacuum%'
        ORDER BY n.nspname, c.relname;
        """,
    )

    stats["autovacuum_workers"] = _collect(
        "autovacuum workers",
        conn,
        """
        SELECT
            pid,
            usename,
            state,
            now() - query_start AS running_for,
            query
        FROM pg_stat_activity
        WHERE query ILIKE 'autovacuum:%'
        ORDER BY query_start;
        """,
    )

    stats["cache_hit_ratio"] = _collect(
        "cache hit ratio",
        conn,
        f"""
        SELECT
            schemaname,
            relname,
            heap_blks_hit,
            heap_blks_read,
            round(
                heap_blks_hit::numeric
                / NULLIF(heap_blks_hit + heap_blks_read, 0) * 100, 2
            )                           AS table_cache_hit_pct
        FROM pg_statio_user_tables
        WHERE {excl}
          AND (heap_blks_hit + heap_blks_read) > 0
        ORDER BY table_cache_hit_pct ASC
        LIMIT 30;
        """,
    )

    stats["database_stats"] = _collect(
        "database stats",
        conn,
        """
        SELECT
            datname,
            blks_hit,
            blks_read,
            round(
                blks_hit * 100.0
                / NULLIF(blks_hit + blks_read, 0), 2
            )                           AS cache_hit_pct,
            tup_returned,
            tup_fetched,
            tup_inserted,
            tup_updated,
            tup_deleted,
            conflicts,
            deadlocks,
            temp_files,
            pg_size_pretty(temp_bytes) AS temp_bytes,
            stats_reset
        FROM pg_stat_database
        WHERE datname NOT IN ('template0', 'template1')
        ORDER BY blks_read DESC;
        """,
    )

    stats["bgwriter"] = _collect(
        "bgwriter stats",
        conn,
        """
        SELECT
            COALESCE(cp.checkpoints_timed, 0) AS checkpoints_timed,
            COALESCE(cp.checkpoints_req, 0) AS checkpoints_req,
            COALESCE(cp.checkpoint_write_time, 0) AS checkpoint_write_time,
            COALESCE(cp.checkpoint_sync_time, 0) AS checkpoint_sync_time,
            COALESCE(cp.buffers_checkpoint, 0) AS buffers_checkpoint,
            bg.buffers_clean,
            bg.maxwritten_clean,
            bg.buffers_backend,
            bg.buffers_backend_fsync,
            bg.buffers_alloc,
            bg.stats_reset
        FROM pg_stat_bgwriter bg
        LEFT JOIN pg_stat_checkpointer cp ON true;
        """,
    )

    stats["wal_stats"] = _collect(
        "WAL stats",
        conn,
        """
        SELECT
            wal_records,
            wal_fpi,
            wal_bytes,
            wal_buffers_full,
            wal_write_time,
            wal_sync_time,
            stats_reset
        FROM pg_stat_wal;
        """,
    )

    stats["connections"] = _collect(
        "connections",
        conn,
        """
        SELECT
            count(*)                    AS current_connections,
            count(*) FILTER (
                WHERE state = 'active'
            )                           AS active,
            count(*) FILTER (
                WHERE state = 'idle in transaction'
            )                           AS idle_in_transaction,
            count(*) FILTER (
                WHERE state = 'idle'
            )                           AS idle,
            (
                SELECT setting::int
                FROM pg_settings
                WHERE name = 'max_connections'
            )                           AS max_connections
        FROM pg_stat_activity
        WHERE pid <> pg_backend_pid();
        """,
    )

    stats["idle_in_transaction"] = _collect(
        "idle-in-transaction sessions",
        conn,
        """
        SELECT
            pid,
            usename,
            application_name,
            client_addr,
            state,
            now() - xact_start   AS idle_in_txn_age,
            now() - state_change AS time_in_state,
            left(query, 200)     AS last_query
        FROM pg_stat_activity
        WHERE state = 'idle in transaction'
          AND pid <> pg_backend_pid()
        ORDER BY xact_start ASC;
        """,
    )

    stats["long_transactions"] = _collect(
        "long transactions",
        conn,
        """
        SELECT
            pid,
            usename,
            application_name,
            state,
            now() - xact_start   AS transaction_age,
            now() - query_start  AS query_age,
            left(query, 300)     AS query
        FROM pg_stat_activity
        WHERE xact_start IS NOT NULL
          AND pid <> pg_backend_pid()
        ORDER BY transaction_age DESC
        LIMIT 30;
        """,
    )

    stats["active_queries"] = _collect(
        "active queries",
        conn,
        """
        SELECT
            pid,
            usename,
            application_name,
            state,
            wait_event_type,
            wait_event,
            now() - query_start AS duration,
            left(query, 300)    AS query
        FROM pg_stat_activity
        WHERE state <> 'idle'
          AND pid <> pg_backend_pid()
        ORDER BY duration DESC
        LIMIT 30;
        """,
    )

    stats["blocking_queries"] = _collect(
        "blocking queries",
        conn,
        """
        SELECT
            blocked.pid                         AS blocked_pid,
            blocked.usename                     AS blocked_user,
            blocked.application_name            AS blocked_app,
            now() - blocked.query_start         AS blocked_duration,
            left(blocked.query, 200)            AS blocked_query,
            blocker.pid                         AS blocker_pid,
            blocker.usename                     AS blocker_user,
            blocker.application_name            AS blocker_app,
            now() - blocker.query_start         AS blocker_duration,
            blocker.state                       AS blocker_state,
            left(blocker.query, 200)            AS blocker_query
        FROM pg_stat_activity blocked
        JOIN pg_locks blocked_locks
            ON blocked.pid = blocked_locks.pid
           AND NOT blocked_locks.granted
        JOIN pg_locks blocker_locks
            ON blocker_locks.locktype           = blocked_locks.locktype
           AND blocker_locks.database     IS NOT DISTINCT FROM blocked_locks.database
           AND blocker_locks.relation     IS NOT DISTINCT FROM blocked_locks.relation
           AND blocker_locks.pid        <> blocked_locks.pid
           AND blocker_locks.granted
        JOIN pg_stat_activity blocker
            ON blocker.pid = blocker_locks.pid;
        """,
    )

    stats["lock_summary"] = _collect(
        "lock summary",
        conn,
        """
        SELECT
            locktype,
            mode,
            granted,
            count(*) AS cnt
        FROM pg_locks
        GROUP BY locktype, mode, granted
        ORDER BY cnt DESC;
        """,
    )

    stats["replication_slots"] = _collect(
        "replication slots",
        conn,
        """
        SELECT
            slot_name,
            slot_type,
            active,
            active_pid,
            pg_size_pretty(
                pg_wal_lsn_diff(
                    pg_current_wal_lsn(),
                    restart_lsn
                )
            )                   AS retained_wal,
            confirmed_flush_lsn
        FROM pg_replication_slots;
        """,
    )

    stats["replication_status"] = _collect(
        "replication status",
        conn,
        """
        SELECT
            client_addr,
            usename,
            application_name,
            state,
            sent_lsn,
            write_lsn,
            flush_lsn,
            replay_lsn,
            write_lag,
            flush_lag,
            replay_lag,
            sync_state
        FROM pg_stat_replication;
        """,
    )

    stats["views"] = _collect(
        "views",
        conn,
        f"""
        SELECT
            schemaname,
            viewname,
            length(definition)  AS definition_length,
            definition
        FROM pg_views
        WHERE {excl}
        ORDER BY definition_length DESC
        LIMIT 50;
        """,
    )

    stats["materialized_views"] = _collect(
        "materialized views",
        conn,
        f"""
        SELECT
            schemaname,
            matviewname,
            ispopulated,
            definition
        FROM pg_matviews
        WHERE {excl}
        ORDER BY schemaname, matviewname;
        """,
    )

    stats["partitioned_tables"] = _collect(
        "partitioned tables",
        conn,
        f"""
        SELECT
            n.nspname                   AS schemaname,
            c.relname                   AS tablename,
            p.partstrat                 AS strategy,
            p.partnatts                 AS num_partition_keys,
            count(ch.oid)               AS num_partitions
        FROM pg_partitioned_table p
        JOIN pg_class c       ON c.oid = p.partrelid
        JOIN pg_namespace n   ON n.oid = c.relnamespace
        LEFT JOIN pg_inherits i ON i.inhparent = c.oid
        LEFT JOIN pg_class ch ON ch.oid = i.inhrelid
        WHERE n.nspname NOT IN ({', '.join(f"'{s}'" for s in EXCLUDED_SCHEMAS)})
          AND n.nspname NOT LIKE 'pg_temp_%'
        GROUP BY n.nspname, c.relname, p.partstrat, p.partnatts
        ORDER BY num_partitions DESC;
        """,
    )

    stats["foreign_tables"] = _collect(
        "foreign tables",
        conn,
        f"""
        SELECT
            n.nspname   AS schemaname,
            c.relname   AS tablename,
            s.srvname   AS foreign_server
        FROM pg_class c
        JOIN pg_namespace n   ON n.oid = c.relnamespace
        JOIN pg_foreign_table ft ON ft.ftrelid = c.oid
        JOIN pg_foreign_server s ON s.oid = ft.ftserver
        WHERE c.relkind = 'f'
          AND n.nspname NOT IN ({', '.join(f"'{s}'" for s in EXCLUDED_SCHEMAS)})
        ORDER BY n.nspname, c.relname;
        """,
    )

    stats["extensions"] = _collect(
        "extensions",
        conn,
        """
        SELECT
            name,
            installed_version,
            default_version,
            (installed_version <> default_version) AS update_available,
            comment
        FROM pg_available_extensions
        WHERE installed_version IS NOT NULL
        ORDER BY name;
        """,
    )

    stats["fk_no_index"] = _collect(
        "foreign keys without indexes",
        conn,
        f"""
        SELECT
            n.nspname                           AS schemaname,
            c.relname                           AS table_name,
            kcu.column_name,
            ccu.table_name                      AS ref_table,
            ccu.column_name                     AS ref_column,
            tc.constraint_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name  = kcu.constraint_name
           AND tc.table_schema     = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu
            ON ccu.constraint_name = tc.constraint_name
           AND ccu.table_schema    = tc.table_schema
        JOIN pg_class c  ON c.relname  = tc.table_name
        JOIN pg_namespace n ON n.nspname = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_schema NOT IN ({', '.join(f"'{s}'" for s in EXCLUDED_SCHEMAS)})
          AND NOT EXISTS (
              SELECT 1
              FROM   pg_index ix
              JOIN   pg_attribute a
                  ON a.attrelid = ix.indrelid
                 AND a.attnum   = ANY(ix.indkey)
              WHERE  ix.indrelid   = c.oid
                AND  a.attname      = kcu.column_name
                AND  ix.indkey[0]  = a.attnum
          )
        ORDER BY n.nspname, c.relname;
        """,
    )

    return stats


# ============================================================
# SETTINGS DASHBOARD
# ============================================================

SETTINGS_CATALOG: list[tuple] = [
    ("shared_buffers", "Memory", "Main PostgreSQL buffer pool. Shared across all connections.", "25 % of total RAM", "bytes → rendered"),
    ("work_mem", "Memory", "Per-sort / per-hash-table allocation.", "4–64 MB typical", "kB → rendered"),
    ("maintenance_work_mem", "Memory", "Memory for VACUUM, CREATE INDEX, etc.", "256 MB – 2 GB", "kB → rendered"),
    ("effective_cache_size", "Memory", "Planner hint: estimated total memory available for caching.", "50–75 % of total RAM", "kB → rendered"),
    ("wal_buffers", "Memory", "Shared memory for WAL before flush.", "16 MB / -1 (auto)", "kB → rendered"),
    ("temp_buffers", "Memory", "Per-session buffer pool for temp tables.", "8 MB", "kB → rendered"),
    ("hash_mem_multiplier", "Memory", "Multiplier applied to work_mem for hash-based operations.", "1.0 – 2.0", "float"),
    ("max_connections", "Connections", "Hard cap on simultaneous client connections.", "100–200 with pooler", "integer"),
    ("superuser_reserved_connections", "Connections", "Connections reserved exclusively for superusers.", "3", "integer"),
    ("idle_in_transaction_session_timeout", "Connections", "Terminate sessions stuck in 'idle in transaction'.", "30000–60000 ms", "ms"),
    ("statement_timeout", "Connections", "Abort statements running longer than this.", "0 (disabled) or 30000ms", "ms"),
    ("tcp_keepalives_idle", "Connections", "Seconds before first TCP keepalive probe.", "60 s", "seconds"),
    ("autovacuum", "Autovacuum", "Master on/off switch for autovacuum.", "on", "bool"),
    ("autovacuum_max_workers", "Autovacuum", "Number of parallel autovacuum workers.", "3–6", "integer"),
    ("autovacuum_vacuum_scale_factor", "Autovacuum", "Fraction of table rows dead before vacuum triggers.", "0.01–0.05", "fraction"),
    ("autovacuum_analyze_scale_factor", "Autovacuum", "Fraction of table rows changed before autoanalyze triggers.", "0.01–0.05", "fraction"),
    ("autovacuum_vacuum_cost_delay", "Autovacuum", "Sleep time between autovacuum I/O bursts.", "2–10 ms", "ms"),
    ("autovacuum_vacuum_cost_limit", "Autovacuum", "I/O cost budget per autovacuum round.", "200–800", "integer"),
    ("autovacuum_vacuum_threshold", "Autovacuum", "Minimum dead tuples before autovacuum triggers.", "50", "integer"),
    ("autovacuum_naptime", "Autovacuum", "Delay between autovacuum daemon rounds.", "30–60 s", "seconds"),
    ("wal_level", "WAL & Checkpoints", "Controls WAL detail level.", "replica", "enum"),
    ("max_wal_size", "WAL & Checkpoints", "Maximum WAL size before forced checkpoint.", "1–4 GB", "bytes → rendered"),
    ("min_wal_size", "WAL & Checkpoints", "Minimum WAL retained on disk.", "80 MB – 1 GB", "bytes → rendered"),
    ("checkpoint_completion_target", "WAL & Checkpoints", "Target fraction of checkpoint interval for writes.", "0.9", "fraction"),
    ("checkpoint_timeout", "WAL & Checkpoints", "Maximum time between automatic checkpoints.", "5–30 min", "seconds"),
    ("synchronous_commit", "WAL & Checkpoints", "Commit synchronization mode.", "on", "enum"),
    ("archive_mode", "WAL & Checkpoints", "Enables WAL archiving.", "on / off", "bool"),
    ("random_page_cost", "Query Planner", "Planner cost estimate for random disk page fetch.", "1.1–2.0 (SSD)", "float"),
    ("seq_page_cost", "Query Planner", "Planner cost estimate for sequential disk page fetch.", "1.0", "float"),
    ("effective_io_concurrency", "Query Planner", "Estimated concurrent I/O operations.", "200 (SSD)", "integer"),
    ("enable_partitionwise_join", "Query Planner", "Allow planner to join matching partitions directly.", "on", "bool"),
    ("enable_partitionwise_aggregate", "Query Planner", "Allow per-partition aggregation.", "on", "bool"),
    ("default_statistics_target", "Query Planner", "Number of histogram buckets for ANALYZE.", "100", "integer"),
    ("from_collapse_limit", "Query Planner", "Max FROM items before join reordering stops.", "8", "integer"),
    ("join_collapse_limit", "Query Planner", "Same as from_collapse_limit for explicit JOIN.", "8", "integer"),
    ("max_worker_processes", "Parallelism", "Total background worker slots.", "CPU count", "integer"),
    ("max_parallel_workers", "Parallelism", "Max parallel query workers across sessions.", "Half to equal vCPU", "integer"),
    ("max_parallel_workers_per_gather", "Parallelism", "Workers allowed for a single parallel query.", "2–4", "integer"),
    ("max_parallel_maintenance_workers", "Parallelism", "Workers for parallel CREATE INDEX and VACUUM.", "2–4", "integer"),
    ("parallel_tuple_cost", "Parallelism", "Planner cost for passing tuple from worker to leader.", "0.1", "float"),
    ("parallel_setup_cost", "Parallelism", "Planner cost for launching parallel workers.", "1000", "float"),
    ("log_min_duration_statement", "Logging", "Log statements exceeding duration (-1 = disabled).", "500–2000 ms", "ms"),
    ("log_checkpoints", "Logging", "Log checkpoint start/end.", "on", "bool"),
    ("log_lock_waits", "Logging", "Log lock waits exceeding deadlock_timeout.", "on", "bool"),
    ("log_temp_files", "Logging", "Log temp files larger than size.", "0 or 1 MB", "kB"),
    ("log_autovacuum_min_duration", "Logging", "Log autovacuum runs exceeding duration.", "250–1000 ms", "ms"),
    ("deadlock_timeout", "Logging", "Time to wait on lock before deadlock check.", "1000 ms", "ms"),
    ("max_replication_slots", "Replication", "Maximum replication slots.", "10", "integer"),
    ("max_wal_senders", "Replication", "Maximum WAL sender processes.", "10", "integer"),
    ("wal_sender_timeout", "Replication", "Terminate idle replication connections.", "60000 ms", "ms"),
    ("hot_standby_feedback", "Replication", "Allow standby to send feedback to primary.", "on", "bool"),
    ("lock_timeout", "Lock Management", "Abort statements waiting longer for lock.", "0", "ms"),
    ("max_locks_per_transaction", "Lock Management", "Average object locks per transaction.", "64", "integer"),
]


def collect_settings_dashboard(conn) -> list[dict]:
    param_names = [row[0] for row in SETTINGS_CATALOG]
    placeholders = ", ".join(f"'{p}'" for p in param_names)

    rows = run_query(
        conn,
        f"""
        SELECT
            name,
            setting,
            unit,
            source,
            sourcefile,
            sourceline,
            context,
            vartype
        FROM pg_settings
        WHERE name IN ({placeholders})
        ORDER BY name;
        """,
    )

    pg_lookup: dict = {r[0]: r for r in rows}

    result = []
    for (param, group, description, typical, unit_hint) in SETTINGS_CATALOG:
        pg = pg_lookup.get(param)
        if pg:
            raw_setting = pg[1]
            unit = pg[2] or ""
            source = pg[3] or ""
            sourcefile = pg[4] or ""
            sourceline = str(pg[5]) if pg[5] else ""
            context = pg[6] or ""
            vartype = pg[7] or ""
            display_val = _humanize_setting(raw_setting, unit, vartype)
        else:
            raw_setting = display_val = "N/A"
            unit = source = sourcefile = sourceline = context = vartype = ""

        result.append({
            "param": param,
            "group": group,
            "description": description,
            "typical": typical,
            "unit_hint": unit_hint,
            "value": display_val,
            "raw": raw_setting,
            "source": source,
            "sourcefile": sourcefile,
            "sourceline": sourceline,
            "context": context,
        })
    return result


def _humanize_setting(raw: str, unit: str, vartype: str) -> str:
    if vartype not in ("integer", "real") or not raw.lstrip("-").isdigit():
        return f"{raw} {unit}".strip()

    val = int(raw)

    if unit == "kB":
        if val < 0:
            return f"{raw} kB"
        kb = val
        if kb >= 1_048_576:
            return f"{kb / 1_048_576:.1f} GB  ({raw} kB)"
        if kb >= 1_024:
            return f"{kb / 1_024:.1f} MB  ({raw} kB)"
        return f"{kb} kB"

    if unit == "8kB":
        kb = val * 8
        if kb >= 1_048_576:
            return f"{kb / 1_048_576:.1f} GB"
        if kb >= 1_024:
            return f"{kb / 1_024:.1f} MB"
        return f"{kb} kB"

    if unit == "B":
        b = val
        if b >= 1_073_741_824:
            return f"{b / 1_073_741_824:.1f} GB  ({raw} B)"
        if b >= 1_048_576:
            return f"{b / 1_048_576:.1f} MB  ({raw} B)"
        return f"{b} B"

    return f"{raw} {unit}".strip()


def _build_vacuum_tab(stats: dict) -> str:
    reset_rows = stats.get("stats_reset", [])
    if reset_rows and reset_rows[0]:
        row = reset_rows[0]
        reset_date = str(row[1]) if len(row) > 1 else "unknown"
        reset_age = str(row[2]) if len(row) > 2 else ""
        reset_banner = (
            f'<div class="stats-reset-banner">'
            f'<strong>⚠ Stats Reset:</strong> pg_stat_user_tables counters were last reset on '
            f'<strong>{html.escape(reset_date)}</strong> ({html.escape(reset_age)} ago). '
            f'NEVER/NULL values for last_vacuum or last_autovacuum mean "has not run <em>since this reset</em>".'
            f'</div>'
        )
    else:
        reset_banner = ""

    disabled_rows = stats.get("autovacuum_disabled_tables", [])
    disabled_html = ""
    if disabled_rows:
        items = "".join(
            f"<li><code>{html.escape(str(r[0]))}.{html.escape(str(r[1]))}</code> — "
            f"<code>{html.escape(str(r[2]))}</code></li>"
            for r in disabled_rows
        )
        disabled_html = (
            f'<div class="av-disabled-banner">'
            f'<strong>🚫 Autovacuum disabled on these tables</strong> (autovacuum_enabled=false):'
            f'<ul>{items}</ul>'
            f'</div>'
        )

    vacuum_rows = stats.get("vacuum", [])
    if not vacuum_rows:
        table_html = "<p><em>No vacuum data collected.</em></p>"
    else:
        def fmt(val):
            if val is None:
                return '<span class="vac-never">NEVER</span>'
            s = str(val)
            if "." in s and "+" in s:
                s = s.split(".")[0]
            return html.escape(s)

        def pct_cell(pct):
            try:
                p = float(pct)
            except (TypeError, ValueError):
                return f"<td>{fmt(pct)}</td>"
            color = "#dc2626" if p >= 20 else "#d97706" if p >= 5 else "#16a34a"
            return f'<td style="color:{color};font-weight:700">{p:.2f}%</td>'

        rows_html = ""
        for r in vacuum_rows:
            try:
                tname = f"{r['schemaname']}.{r['relname']}"
                live = f"{int(r['n_live_tup']):,}" if r.get('n_live_tup') is not None else "—"
                dead = f"{int(r['n_dead_tup']):,}" if r.get('n_dead_tup') is not None else "—"
                d_lv = fmt(r.get('days_since_manual_vacuum'))
                d_av = fmt(r.get('days_since_autovacuum'))
                lv = fmt(r.get('last_vacuum'))
                av = fmt(r.get('last_autovacuum'))
                la = fmt(r.get('last_analyze'))
                d_la = fmt(r.get('days_since_last_analyze'))
                vc = str(r['vacuum_count']) if r.get('vacuum_count') is not None else "0"
                avc = str(r['autovacuum_count']) if r.get('autovacuum_count') is not None else "0"
            except (KeyError, TypeError):
                continue

            rows_html += (
                f"<tr>"
                f"<td><code>{html.escape(tname)}</code></td>"
                f"<td>{live}</td><td>{dead}</td>"
                + pct_cell(r.get('dead_tuple_pct'))
                + f"<td>{lv}<br><small style='color:#888'>({d_lv} days ago)</small></td>"
                f"<td>{av}<br><small style='color:#888'>({d_av} days ago)</small></td>"
                f"<td>{la}<br><small style='color:#888'>({d_la} days ago)</small></td>"
                f"<td>{vc}</td><td>{avc}</td>"
                f"</tr>"
            )

        table_html = (
            '<div style="overflow-x:auto">'
            '<table class="vac-table">'
            '<thead><tr>'
            '<th>Table</th><th>Live tuples</th><th>Dead tuples</th><th>Dead %</th>'
            '<th>Last VACUUM<br>(manual)</th><th>Last AUTOVACUUM</th>'
            '<th>Last ANALYZE</th><th>Vacuum count</th><th>Autovacuum count</th>'
            '</tr></thead><tbody>'
            + rows_html
            + '</tbody></table></div>'
        )

    return f"""
{reset_banner}
{disabled_html}
<h3 style="margin:16px 0 8px;font-size:1rem;color:#1a1a2e">
  Vacuum status per table
  <span style="font-size:0.78rem;font-weight:400;color:#666;margin-left:8px">
    ordered by most-stale first — data from pg_stat_user_tables
  </span>
</h3>
{table_html}
<style>
.stats-reset-banner {{
  background:#fef3c7;border:1px solid #fcd34d;border-left:4px solid #f59e0b;
  border-radius:6px;padding:10px 14px;margin-bottom:12px;font-size:0.85rem;color:#78350f;
}}
.av-disabled-banner {{
  background:#fee2e2;border:1px solid #fca5a5;border-left:4px solid #dc2626;
  border-radius:6px;padding:10px 14px;margin-bottom:12px;font-size:0.85rem;color:#7f1d1d;
}}
.av-disabled-banner ul {{margin:6px 0 0 18px;}}
.vac-never {{color:#dc2626;font-weight:700;}}
.vac-table {{width:100%;border-collapse:collapse;font-size:0.8rem;}}
.vac-table th {{background:#1e3a5f;color:#fff;padding:8px 10px;text-align:left;white-space:nowrap;}}
.vac-table td {{padding:7px 10px;border-bottom:1px solid #e4e6ea;vertical-align:top;}}
.vac-table tr:nth-child(even) td {{background:#f7f8fa;}}
.vac-table tr:hover td {{background:#edf2ff;}}
</style>
"""


def _build_settings_tab(settings: list[dict]) -> str:
    groups: dict[str, list[dict]] = {}
    for s in settings:
        groups.setdefault(s["group"], []).append(s)

    GROUP_ICONS = {
        "Memory": "🧠",
        "Connections": "🔌",
        "Autovacuum": "🧹",
        "WAL & Checkpoints": "📝",
        "Query Planner": "🗺️",
        "Parallelism": "⚡",
        "Logging": "📋",
        "Replication": "🔁",
        "Lock Management": "🔒",
    }

    sections_html = ""
    for group_name, items in groups.items():
        icon = GROUP_ICONS.get(group_name, "⚙️")
        cards_html = ""
        for s in items:
            source_badge = ""
            if s["source"] == "default":
                source_badge = '<span class="src-badge src-default">default</span>'
            elif "postgresql.conf" in s["sourcefile"] or s["source"] == "configuration file":
                source_badge = '<span class="src-badge src-conf">postgresql.conf</span>'
            elif s["source"] in ("environment variable", "command line"):
                source_badge = f'<span class="src-badge src-env">{html.escape(s["source"])}</span>'
            else:
                source_badge = f'<span class="src-badge src-other">{html.escape(s["source"])}</span>'

            context_note = (
                f'<span class="ctx-badge">{html.escape(s["context"])}</span>'
                if s["context"] else ""
            )

            cards_html += f"""
<div class="setting-card">
  <div class="setting-header">
    <span class="setting-name">{html.escape(s["param"])}</span>
    {source_badge}
    {context_note}
  </div>
  <div class="setting-value">{html.escape(s["value"])}</div>
  <div class="setting-desc">{html.escape(s["description"])}</div>
  <div class="setting-typical">
    <span class="typical-label">Typical / recommended:</span>
    {html.escape(s["typical"])}
  </div>
</div>"""

        sections_html += f"""
<details class="group-details" open>
  <summary class="group-summary">
    <span class="group-icon">{icon}</span>
    <span class="group-title">{html.escape(group_name)}</span>
    <span class="group-count">{len(items)} parameter{"s" if len(items) != 1 else ""}</span>
  </summary>
  <div class="cards-grid">
    {cards_html}
  </div>
</details>"""

    return f"""
<div id="settings-search-bar" style="margin-bottom:18px;">
  <input
    id="settings-search"
    type="text"
    placeholder="🔍  Filter parameters…"
    oninput="filterSettings(this.value)"
    style="width:100%;max-width:420px;padding:9px 14px;border:1px solid #d0d4dc;
           border-radius:6px;font-size:0.9rem;outline:none;"
  />
</div>
{sections_html}
<script>
function filterSettings(q) {{
  q = q.toLowerCase();
  document.querySelectorAll('.setting-card').forEach(card => {{
    const text = card.textContent.toLowerCase();
    card.style.display = text.includes(q) ? '' : 'none';
  }});
}}
</script>
"""


# ============================================================
# REPORT TRIMMER
# ============================================================

def trim_report_for_llm(stats: dict) -> dict:
    r = {}
    verbatim = [
        "version", "slow_queries", "view_plans", "idle_in_transaction",
        "long_transactions", "blocking_queries", "lock_summary",
        "replication_slots", "replication_status",
        "autovacuum_workers", "autovacuum_disabled_tables",
        "stats_reset", "extensions", "partitioned_tables", "foreign_tables",
    ]
    for k in verbatim:
        if k in stats:
            r[k] = stats[k]

    def cap(key, limit=20):
        rows = stats.get(key, [])
        if rows and len(rows) > limit:
            r[key] = rows[:limit] + [f"[... {len(rows)-limit} more rows omitted ...]"]
        elif rows:
            r[key] = rows

    cap("vacuum", 30)
    cap("autovacuum_threshold_check", 30)
    cap("table_health", 20)
    cap("sequential_scans", 20)
    cap("unused_indexes", 20)
    cap("duplicate_indexes", 20)
    cap("fk_no_index", 20)
    cap("index_usage", 30)
    cap("index_bloat", 15)
    cap("table_sizes", 20)
    cap("active_queries", 15)
    cap("connections", 5)
    cap("views", 10)
    cap("materialized_views", 10)

    if "configuration" in stats:
        annotated_config = []
        for row in (stats["configuration"] or []):
            if len(row) >= 3:
                name = str(row[0])
                raw_val = str(row[1])
                unit = str(row[2]) if row[2] else ""
                human = _humanize_setting(raw_val, unit, "integer")
                if unit == "8kB":
                    try:
                        alter_val = f"{int(raw_val) * 8}kB"
                    except ValueError:
                        alter_val = raw_val
                elif unit == "kB":
                    alter_val = f"{raw_val}kB"
                elif unit == "B":
                    alter_val = f"{raw_val}B"
                elif unit in ("ms", "s", "min"):
                    alter_val = f"{raw_val}{unit}"
                else:
                    alter_val = raw_val
                annotated_config.append({
                    "name": name,
                    "raw_setting": raw_val,
                    "unit": unit,
                    "human_readable_value": human,
                    "correct_alter_system_value": alter_val,
                })
        r["configuration_SETTING_VALUES_NOT_COUNTERS"] = annotated_config

    if "database_stats" in stats:
        cleaned = []
        for row in (stats["database_stats"] or []):
            if row and len(row) >= 4:
                cleaned.append({
                    "DATABASE_NAME_NOT_TABLE": str(row[0]),
                    "cache_hit_pct": str(row[3]),
                    "deadlocks_CUMULATIVE_COUNTER": str(row[8]) if len(row) > 8 else "N/A",
                    "temp_files_CUMULATIVE_COUNTER": str(row[10]) if len(row) > 10 else "N/A",
                })
        r["database_stats"] = cleaned

    if "bgwriter" in stats:
        rows = stats["bgwriter"] or []
        if rows and len(rows[0]) >= 9:
            row = rows[0]
            r["bgwriter_IO_COUNTERS_NOT_CONFIG_VALUES"] = {
                "checkpoints_timed_COUNTER": row[0],
                "checkpoints_req_COUNTER": row[1],
                "checkpoint_write_time_ms_COUNTER": row[2],
                "checkpoint_sync_time_ms_COUNTER": row[3],
                "buffers_checkpoint_COUNTER": row[4],
                "buffers_clean_COUNTER": row[5],
                "maxwritten_clean_COUNTER": row[6],
                "buffers_backend_COUNTER": row[7],
                "buffers_backend_fsync_COUNTER": row[8],
                "buffers_alloc_COUNTER": row[9] if len(row) > 9 else "N/A",
            }

    if "wal_stats" in stats:
        rows = stats["wal_stats"] or []
        if rows and len(rows[0]) >= 5:
            row = rows[0]
            r["wal_stats_IO_COUNTERS_NOT_CONFIG_VALUES"] = {
                "wal_records_COUNTER": row[0],
                "wal_fpi_COUNTER": row[1],
                "wal_bytes_COUNTER": row[2],
                "wal_buffers_full_COUNTER": row[3],
                "wal_write_COUNTER": row[4],
            }

    if "replication_slots" in stats:
        slots = []
        for row in (stats["replication_slots"] or []):
            if len(row) >= 5:
                slots.append({
                    "slot_name": str(row[0]),
                    "slot_type": str(row[1]),
                    "active": str(row[2]),
                    "active_pid": str(row[3]),
                    "retained_wal_HUMAN_READABLE": str(row[4]),
                })
        r["replication_slots"] = slots

    if "cache_hit_ratio" in stats:
        rows = stats["cache_hit_ratio"] or []
        labeled = []
        for row in rows[:20]:
            if len(row) >= 5:
                labeled.append({
                    "schemaname": str(row[0]),
                    "relname": str(row[1]),
                    "heap_blks_hit_COUNTER": str(row[2]),
                    "heap_blks_read_COUNTER": str(row[3]),
                    "table_cache_hit_pct": str(row[4]),
                })
        r["cache_hit_ratio"] = labeled

    if "active_queries" in stats:
        labeled = []
        for row in (stats.get("active_queries") or []):
            if len(row) >= 8:
                is_replication = "replication" in str(row[7]).lower() or "start_replication" in str(row[7]).lower()
                labeled.append({
                    "pid": row[0], "usename": row[1], "application_name": row[2],
                    "state": row[3], "wait_event_type": row[4], "wait_event": row[5],
                    "duration": str(row[6]), "query_truncated": str(row[7])[:300],
                    "IS_REPLICATION_WALSENDER": is_replication,
                })
        r["active_queries"] = labeled

    return r


# ============================================================
# GEMINI LLM ANALYSIS (OpenAI-compatible Endpoint)
# ============================================================

def validate_llm_output(text: str) -> list:
    warnings = []
    if "123456789" in text:
        warnings.append("Likely placeholder value '123456789' detected in LLM output")
    if "ALTER SYSTEM SET shared_buffers" in text and any(char.isdigit() for char in text.split("shared_buffers")[1][:10]):
        # check if it looks like a raw integer rather than unit
        pass
    return warnings

def send_to_gemini(report: dict) -> str:
    api_key = os.environ.get("API_KEY")
    model_name = os.environ.get("OLLAMA_MODEL", "gemini-1.5-flash")

    if not api_key:
        raise ValueError("API_KEY environment variable is not set for Google Gemini API.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

    prompt = f"""
You are a senior PostgreSQL 18 DBA and performance engineer with deep expertise
in query optimization, vacuum tuning, index design, locking, and replication.

Your job is to produce a detailed, actionable, evidence-grounded DBA report.
A junior DBA must be able to read your report and execute the actions safely.

===========================================================================
DATABASE REPORT:
===========================================================================
{json.dumps(report, indent=2, default=str)}
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 8192
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    max_attempts = 3
    last_exc = None
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=900)
            response.raise_for_status()
            data = response.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "Empty response from Gemini.")
            return "Empty response from Gemini."
        except Exception as exc:
            last_exc = exc
            if attempt < max_attempts:
                print(f"[WARN] Gemini request failed (attempt {attempt}/{max_attempts}): {exc}, retrying...")
            else:
                raise
    raise RuntimeError("send_to_gemini failed after max attempts") from last_exc


# ============================================================
# HTML REPORT RENDERER
# ============================================================

def _render_recommendations(raw: str) -> str:
    URGENT_BADGE = '<span class="sev-badge sev-urgent">⚠ URGENT</span>'
    WARNING_BADGE = '<span class="sev-badge sev-warning">⚡ WARNING</span>'
    INFO_BADGE = '<span class="sev-badge sev-info">ℹ INFO</span>'

    ITEM_PREFIXES = (
        "ISSUE:", "QUERY:", "VIEW:", "TABLE:", "SESSION PID:",
        "REPLICATION SLOT:", "PARAMETER:", "BGWRITER / CHECKPOINT:",
        "WAL STATS:",
    )

    def badge(text: str) -> str:
        t = text.replace("⚠ URGENT", URGENT_BADGE)
        t = t.replace("⚡ WARNING", WARNING_BADGE)
        t = t.replace("ℹ INFO", INFO_BADGE)
        return t

    def render_inline(text: str) -> str:
        t = badge(html.escape(text))
        t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
        return t

    lines = raw.splitlines()
    out: list[str] = []
    i = 0
    in_ul = False
    sec_counter = [0]

    def close_ul():
        nonlocal in_ul
        if in_ul:
            out.append("</ul>")
            in_ul = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):
            close_ul()
            lang = stripped[3:].strip().lower()
            block_lines: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                block_lines.append(lines[i])
                i += 1
            css_class = "sql-block" if lang in ("sql", "psql", "") else "code-block"
            content = html.escape("\n".join(block_lines))
            out.append(f'<pre class="{css_class}">{content}</pre>')
            i += 1
            continue

        m_h1 = re.match(r"^#\s+(\d+)\.\s+(.+)$", stripped)
        if m_h1:
            close_ul()
            sec_counter[0] += 1
            anchor = f"sec{sec_counter[0]}"
            label = render_inline(m_h1.group(2).strip())
            num = html.escape(m_h1.group(1))
            out.append(
                f'<h2 class="report-section" id="{anchor}">'
                f'<a class="sec-anchor" href="#{anchor}">#</a>'
                f' {num}. {label}</h2>'
            )
            i += 1
            continue

        m_h2 = re.match(r"^##\s+(.+)$", stripped)
        if m_h2:
            close_ul()
            label = render_inline(m_h2.group(1).strip())
            out.append(f'<h3 class="report-subsection">{label}</h3>')
            i += 1
            continue

        matched_prefix = None
        for pfx in ITEM_PREFIXES:
            if stripped.upper().startswith(pfx.upper()):
                matched_prefix = pfx
                break
        if matched_prefix:
            close_ul()
            rest = stripped[len(matched_prefix):].strip()
            label_esc = html.escape(matched_prefix.rstrip(":"))
            rest_rendered = render_inline(rest)
            out.append(
                f'<h3 class="report-item">'
                f'<span class="item-label">{label_esc}</span>'
                + (f' <span class="item-title">{rest_rendered}</span>' if rest_rendered else "")
                + "</h3>"
            )
            i += 1
            continue

        m_li = re.match(r"^[-*]\s+(.*)", stripped)
        if m_li:
            if not in_ul:
                out.append('<ul class="report-list">')
                in_ul = True
            item = render_inline(m_li.group(1))
            out.append(f"  <li>{item}</li>")
            i += 1
            continue

        m_ol = re.match(r"^(\d+)\.\s+(.*)", stripped)
        if m_ol:
            close_ul()
            item = render_inline(m_ol.group(2))
            out.append(
                f'<p class="numbered-item">'
                f'<strong>{html.escape(m_ol.group(1))}.</strong> {item}</p>'
            )
            i += 1
            continue

        m_bkv = re.match(r"^\*\*([^*]+)\*\*[:\s]+(.*)", stripped)
        if m_bkv:
            close_ul()
            key = html.escape(m_bkv.group(1).rstrip(":"))
            value = render_inline(m_bkv.group(2))
            out.append(
                f'<p class="kv-line">'
                f'<span class="kv-key">{key}:</span> {value}</p>'
            )
            i += 1
            continue

        _KNOWN_KV_KEYS = {
            "HEALTH", "IMMEDIATE RISKS", "TOP ACTIONS TODAY",
            "URGENT", "WARNING", "INFO", "NOTE", "ACTION",
        }
        m_kv = re.match(r"^([A-Z][A-Z0-9 _/()-]{1,35}):\s*(.*)$", stripped)
        _kv_key_candidate = m_kv.group(1).strip() if m_kv else ""
        _kv_valid = (
            m_kv
            and not stripped.startswith("http")
            and not re.search(r"[./]", _kv_key_candidate)
            and (
                " " in _kv_key_candidate
                or _kv_key_candidate in _KNOWN_KV_KEYS
                or len(_kv_key_candidate) <= 12
            )
        )
        if _kv_valid:
            close_ul()
            key = html.escape(m_kv.group(1))
            value = render_inline(m_kv.group(2))
            out.append(
                f'<p class="kv-line">'
                f'<span class="kv-key">{key}:</span> {value}</p>'
            )
            i += 1
            continue

        if not stripped:
            close_ul()
            out.append('<div class="vspace"></div>')
            i += 1
            continue

        close_ul()
        out.append(f'<p class="report-p">{render_inline(stripped)}</p>')
        i += 1

    close_ul()
    return "\n".join(out)


def _build_toc(raw: str) -> str:
    toc_items: list[str] = []
    sec = 0
    for line in raw.splitlines():
        m = re.match(r"^#\s+(\d+)\.\s+(.+)$", line.strip())
        if m:
            sec += 1
            title = html.escape(m.group(2).strip())
            toc_items.append(
                f'<li><a href="#sec{sec}">{title}</a></li>'
            )
    if not toc_items:
        return ""
    return (
        '<nav class="report-toc">'
        "<strong>Contents</strong>"
        "<ol>" + "".join(toc_items) + "</ol>"
        "</nav>"
    )


def save_html_report(stats: dict, recommendations: str, settings: list[dict]) -> str:
    os.makedirs(REPORT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{REPORT_DIR}/PostgreSQL_Performance_Report_{timestamp}.html"
    generated_time = datetime.now()

    rendered_recommendations = _render_recommendations(recommendations)
    toc_html = _build_toc(recommendations)

    stat_sections_html = ""
    for section_name, data in stats.items():
        safe_id = section_name.replace(" ", "_")
        stat_sections_html += (
            f'<details id="{safe_id}">'
            f'<summary><strong>{html.escape(section_name.replace("_"," ").title())}</strong></summary>'
            f'<pre>{html.escape(json.dumps(data, indent=2, default=str))}</pre>'
            f'</details>\n'
        )

    settings_tab_html = _build_settings_tab(settings)
    vacuum_tab_html = _build_vacuum_tab(stats)

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PostgreSQL 18 Performance Report — {generated_time.strftime('%Y-%m-%d %H:%M')}</title>
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  font-size: 14px; background: #f0f2f5; color: #1e1e2e; padding: 32px 16px; line-height: 1.6;
}}
a {{ color: #2563eb; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
.page-header {{ margin-bottom: 24px; }}
h1 {{ font-size: 1.75rem; font-weight: 800; color: #1a1a2e; margin-bottom: 4px; }}
.subtitle {{ color: #666; font-size: 0.88rem; }}
.tabs {{ display: flex; gap: 4px; flex-wrap: wrap; margin-bottom: 0; }}
.tab-btn {{
  padding: 9px 20px; border: none; border-radius: 6px 6px 0 0; background: #d8dce3;
  cursor: pointer; font-size: 0.85rem; font-weight: 600; color: #444; transition: background 0.15s, color 0.15s;
}}
.tab-btn.active, .tab-btn:hover {{ background: #fff; color: #1a1a2e; }}
.tab-content {{
  display: none; background: #fff; border-radius: 0 8px 8px 8px; padding: 28px 32px; box-shadow: 0 2px 14px rgba(0,0,0,.1);
}}
.tab-content.active {{ display: block; }}
.report-toc {{
  background: #f8faff; border: 1px solid #c7d4f0; border-left: 4px solid #4a6fa5;
  border-radius: 6px; padding: 14px 20px; margin-bottom: 28px; display: inline-block; min-width: 260px; max-width: 480px;
}}
.report-toc strong {{ display: block; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.06em; color: #4a6fa5; margin-bottom: 8px; }}
.report-toc ol {{ padding-left: 20px; font-size: 0.84rem; line-height: 1.8; }}
.report-section {{ font-size: 1.2rem; font-weight: 800; color: #1a1a2e; border-bottom: 2px solid #4a6fa5; padding-bottom: 6px; margin: 32px 0 16px; }}
.sec-anchor {{ color: #aab8d4; margin-right: 6px; font-weight: 400; font-size: 0.9rem; }}
.sec-anchor:hover {{ color: #4a6fa5; }}
.report-item {{
  font-size: 1rem; font-weight: 700; color: #1a1a2e; background: #eef3fb; border-left: 4px solid #4a6fa5;
  padding: 9px 14px; border-radius: 0 6px 6px 0; margin: 24px 0 8px; display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap;
}}
.item-label {{
  font-size: 0.72rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.07em;
  color: #4a6fa5; background: #dbeafe; border-radius: 4px; padding: 1px 7px; white-space: nowrap;
}}
.item-title {{ font-size: 1rem; font-weight: 700; color: #1a1a2e; }}
.report-subsection {{ font-size: 0.97rem; font-weight: 700; color: #2d3a55; border-bottom: 1px dashed #c7d4f0; padding-bottom: 4px; margin: 22px 0 10px; }}
.sev-badge {{
  display: inline-block; padding: 2px 9px; border-radius: 12px; font-size: 0.72rem; font-weight: 800;
  text-transform: uppercase; letter-spacing: 0.04em; vertical-align: middle; margin: 0 2px;
}}
.sev-urgent  {{ background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }}
.sev-warning {{ background: #fef3c7; color: #92400e; border: 1px solid #fcd34d; }}
.sev-info    {{ background: #dbeafe; color: #1e40af; border: 1px solid #93c5fd; }}
.kv-line {{ margin: 4px 0; font-size: 0.88rem; }}
.kv-key  {{ font-weight: 700; color: #374151; }}
.report-p {{ margin: 6px 0; font-size: 0.9rem; color: #333; }}
.vspace   {{ height: 8px; }}
.report-list {{ margin: 6px 0 6px 24px; font-size: 0.88rem; color: #333; }}
.report-list li {{ margin-bottom: 3px; }}
.numbered-item {{ margin: 5px 0; font-size: 0.9rem; }}
.sql-block, .code-block {{
  white-space: pre-wrap; word-break: break-word; padding: 14px 16px; border-radius: 6px;
  font-family: "JetBrains Mono", "Fira Code", "Courier New", monospace; font-size: 0.8rem; line-height: 1.6; overflow-x: auto; margin: 10px 0;
}}
.sql-block {{ background: #0f172a; color: #e2e8f0; border-left: 4px solid #3b82f6; }}
.code-block {{ background: #1e1e2e; color: #cdd6f4; border-left: 4px solid #7c3aed; }}
details {{ margin-bottom: 10px; border: 1px solid #e4e6ea; border-radius: 6px; overflow: hidden; }}
summary {{ padding: 10px 14px; cursor: pointer; background: #f7f8fa; user-select: none; list-style: none; font-size: 0.88rem; }}
summary:hover {{ background: #edf2ff; }}
details[open] summary {{ border-bottom: 1px solid #e4e6ea; }}
details pre {{
  white-space: pre-wrap; word-break: break-word; background: #f7f8fa; padding: 14px;
  font-family: "JetBrains Mono", "Fira Code", monospace; font-size: 0.78rem; line-height: 1.5; border: none; border-radius: 0; margin: 0;
}}
pre {{
  white-space: pre-wrap; word-break: break-word; background: #f7f8fa; padding: 16px; border-left: 4px solid #4a6fa5;
  border-radius: 0 4px 4px 0; font-family: "JetBrains Mono", "Fira Code", "Courier New", monospace; font-size: 0.82rem; line-height: 1.55; overflow-x: auto; margin-top: 8px;
}}
table {{ border-collapse: collapse; width: 100%; font-size: 0.82rem; margin-top: 8px; }}
th    {{ background: #4a6fa5; color: #fff; padding: 8px 10px; text-align: left; font-weight: 600; }}
td    {{ padding: 7px 10px; border-bottom: 1px solid #e4e6ea; }}
tr:nth-child(even) td {{ background: #f7f8fa; }}
tr:hover td {{ background: #edf2ff; }}
.group-details {{ margin-bottom: 18px; border: 1px solid #e4e6ea; border-radius: 8px; overflow: hidden; }}
.group-summary {{
  display: flex; align-items: center; gap: 10px; padding: 12px 16px; cursor: pointer; background: #f0f4ff; user-select: none; list-style: none;
}}
.group-summary:hover {{ background: #e2e8ff; }}
.group-icon  {{ font-size: 1.15rem; }}
.group-title {{ font-size: 1rem; font-weight: 700; color: #1a1a2e; flex: 1; }}
.group-count {{ font-size: 0.78rem; color: #666; }}
.cards-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 14px; padding: 16px; background: #fff; }}
.setting-card {{ border: 1px solid #e4e6ea; border-radius: 8px; padding: 14px 16px; background: #fafbfc; transition: box-shadow 0.15s; }}
.setting-card:hover {{ box-shadow: 0 3px 10px rgba(0,0,0,.1); }}
.setting-header {{ display: flex; align-items: center; flex-wrap: wrap; gap: 6px; margin-bottom: 6px; }}
.setting-name {{ font-family: "JetBrains Mono", "Fira Code", monospace; font-size: 0.82rem; font-weight: 700; color: #1a1a2e; word-break: break-all; }}
.setting-value {{ font-family: "JetBrains Mono", "Fira Code", monospace; font-size: 1rem; font-weight: 700; color: #2563eb; margin-bottom: 8px; }}
.setting-desc {{ font-size: 0.8rem; color: #444; line-height: 1.5; margin-bottom: 8px; }}
.setting-typical {{ font-size: 0.78rem; color: #555; background: #f0f4ff; border-left: 3px solid #4a6fa5; padding: 5px 8px; border-radius: 0 4px 4px 0; }}
.typical-label {{ font-weight: 700; color: #4a6fa5; margin-right: 4px; }}
.src-badge {{ font-size: 0.68rem; font-weight: 700; padding: 2px 7px; border-radius: 10px; text-transform: uppercase; letter-spacing: 0.03em; }}
.src-default {{ background: #e9ecef; color: #555; }}
.src-conf    {{ background: #d1fae5; color: #065f46; }}
.src-env     {{ background: #fef3c7; color: #92400e; }}
.src-other   {{ background: #ede9fe; color: #5b21b6; }}
.ctx-badge {{ font-size: 0.68rem; background: #f1f5f9; color: #64748b; padding: 2px 7px; border-radius: 10px; border: 1px solid #cbd5e1; }}
@media (max-width: 640px) {{
  body {{ padding: 16px 8px; }}
  .tab-btn {{ font-size: 0.75rem; padding: 7px 11px; }}
  .cards-grid {{ grid-template-columns: 1fr; }}
  .tab-content {{ padding: 16px; }}
}}
</style>
</head>
<body>

<div class="page-header">
  <h1>🐘 PostgreSQL 18 Performance Report</h1>
  <p class="subtitle">
    Generated: <strong>{generated_time.strftime('%Y-%m-%d %H:%M:%S')}</strong>
    &nbsp;|&nbsp; Database: <strong>{html.escape(os.environ.get('DB_NAME', 'unknown'))}</strong>
    &nbsp;|&nbsp; Host: <strong>{html.escape(os.environ.get('DB_HOST', 'unknown'))}</strong>
    &nbsp;|&nbsp; Model: <strong>{html.escape(OLLAMA_MODEL)}</strong>
  </p>
</div>

<div class="tabs">
  <button class="tab-btn active" onclick="showTab('recommendations', this)">🤖 DBA Analysis</button>
  <button class="tab-btn" onclick="showTab('rawstats', this)">📊 Raw Statistics</button>
  <button class="tab-btn" onclick="showTab('settings', this)">⚙️ Settings Dashboard</button>
  <button class="tab-btn" onclick="showTab('vacuum', this)">🧹 Vacuum Status</button>
</div>

<div id="recommendations" class="tab-content active">
  {toc_html}
  {rendered_recommendations}
</div>

<div id="rawstats" class="tab-content">
  <p style="margin-bottom:16px;color:#666;font-size:0.88rem;">
    Click any section to expand. Data collected at report generation time.
  </p>
  {stat_sections_html}
</div>

<div id="vacuum" class="tab-content">
  {vacuum_tab_html}
</div>

<div id="settings" class="tab-content">
  <p style="margin-bottom:16px;color:#666;font-size:0.88rem;">
    Live PostgreSQL configuration parameters relevant to DBA performance tuning.
  </p>
  {settings_tab_html}
</div>

<script>
  function showTab(id, btn) {{
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
    document.getElementById(id).classList.add('active');
    btn.classList.add('active');
  }}
</script>

</body>
</html>
"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(page)

    return filename


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 60)
    print("PostgreSQL 18 Performance Analyzer (Gemini Powered)")
    print("=" * 60)

    conn = None
    try:
        print("\n[1/4] Connecting to database...")
        conn = get_connection()
        print("      Connected.")

        print("\n[2/5] Collecting statistics...")
        stats = collect_stats(conn)
        print(f"      Done — {len(stats)} sections collected.")

        print("\n[3/5] Collecting settings dashboard...")
        settings = collect_settings_dashboard(conn)
        print(f"      Done — {len(settings)} parameters collected.")

        print("\n[4/5] Sending report to Google Gemini...")
        trimmed_stats = trim_report_for_llm(stats)
        recommendations = send_to_gemini(trimmed_stats)
        print("      Done.")

        llm_warnings = validate_llm_output(recommendations)
        if llm_warnings:
            print("\n[WARN] LLM output quality warnings detected:")
            for w in llm_warnings:
                print(f"  ⚠  {w}")
            warning_banner = (
                "\n\n> **⚠ REPORT QUALITY WARNINGS** — The LLM output may contain "
                "placeholder values or hallucinated identifiers. Review the following "
                "before acting:\n"
                + "".join(f"> - {w}\n" for w in llm_warnings)
                + "\n"
            )
            recommendations = warning_banner + recommendations

        print("\n[5/5] Generating HTML report...")
        report_file = save_html_report(stats, recommendations, settings)
        print(f"      Report written to: {report_file}")

        print("\n" + "=" * 60)
        print("GEMINI RECOMMENDATIONS")
        print("=" * 60)
        print(recommendations)

    except Exception as exc:
        print(f"\n[FATAL] Analyzer failed: {exc}")
        raise

    finally:
        if conn:
            conn.close()
            print("\n[INFO] Database connection closed.")


if __name__ == "__main__":
    main()
