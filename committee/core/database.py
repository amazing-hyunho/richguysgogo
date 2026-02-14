from __future__ import annotations

"""
SQLite database foundation (v1).

Purpose
-------
- Persist daily market/flow/stock-level data in a lightweight, file-based DB.
- This is an *additional* layer: it must not replace or break existing snapshot storage.

Key design points
-----------------
- **Fail-safe**: DB errors must not break the nightly pipeline. Callers should use the
  provided `safe_*` wrappers (they log and continue).
- **Modular**: DB connection logic is separated; callers pass primitives/dicts, not LLM output.
- **Future-proof**: tables are normalized enough to extend (e.g., more columns, more series).
- **Data integrity**: we use NULL (not 0.0) for missing/unavailable/not-implemented values.
  This prevents feature corruption later where 0.0 could mean:
    (1) a real zero value, (2) a fetch failure, or (3) not implemented yet.

DB file
-------
`./data/investment.db` (relative to repository root).
"""

from contextlib import contextmanager
from datetime import datetime, timezone, date as dt_date, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
import sqlite3


def _repo_root() -> Path:
    # committee/core/database.py -> parents[2] is the repository root.
    return Path(__file__).resolve().parents[2]


def get_db_path() -> Path:
    """Return the SQLite DB path (`./data/investment.db`)."""
    return _repo_root() / "data" / "investment.db"


@contextmanager
def connect(db_path: Path | None = None) -> Iterable[sqlite3.Connection]:
    """Context-managed SQLite connection.

    - Uses `sqlite3.Row` for convenient dict-like access.
    - Enables foreign keys and WAL journaling for better robustness.
    """
    path = db_path or get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    try:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        yield conn
        conn.commit()
    finally:
        conn.close()


def _utc_now_iso() -> str:
    """UTC timestamp string for created_at columns."""
    return datetime.now(timezone.utc).isoformat()


def init_db(db_path: Path | None = None) -> None:
    """Initialize database and create tables if they do not exist."""
    with connect(db_path) as conn:
        # market_daily: global market indices and FX series (one row per day).
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS market_daily (
                date TEXT PRIMARY KEY,
                kospi_pct REAL,
                kosdaq_pct REAL,
                sp500_pct REAL,
                nasdaq_pct REAL,
                dow_pct REAL,
                usdkrw REAL,
                usdkrw_pct REAL,
                us10y REAL,
                vix REAL,
                created_at TEXT
            );
            """
        )

        # market_flow_daily: market-level flow series (one row per day).
        # Rolling sums (20d/60d) are stored to avoid recomputation in downstream jobs.
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS market_flow_daily (
                date TEXT PRIMARY KEY,
                foreign_net REAL,
                foreign_20d REAL,
                foreign_60d REAL,
                created_at TEXT
            );
            """
        )

        # stock_daily: stock-level features (composite primary key: date + ticker).
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS stock_daily (
                date TEXT,
                ticker TEXT,
                foreign_20d REAL,
                foreign_60d REAL,
                institution_20d REAL,
                volume_ratio REAL,
                eps REAL,
                eps_revision_3m REAL,
                per REAL,
                roe REAL,
                market_cap REAL,
                created_at TEXT,
                PRIMARY KEY (date, ticker)
            );
            """
        )

        # Helpful indexes for history queries.
        conn.execute("CREATE INDEX IF NOT EXISTS idx_stock_daily_ticker_date ON stock_daily(ticker, date);")

        # --- Macro engine tables (v1) ---
        # NULL-based design: missing/unavailable/not-implemented values must be stored as NULL,
        # never as 0.0 placeholders.

        # Phase 1: daily_macro only (no monthly/quarterly yet).
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS daily_macro (
                date TEXT PRIMARY KEY,
                us10y REAL,
                us2y REAL,
                spread_2_10 REAL,
                vix REAL,
                dxy REAL,
                usdkrw REAL,
                created_at TEXT
            );
            """
        )
        # Safe schema migration (Phase 1): ensure `dxy` column exists even if DB was created
        # before DXY support landed. We avoid defaults (0.0) to preserve NULL-based integrity.
        _ensure_column_exists(conn, table="daily_macro", column="dxy", column_ddl="REAL")
        # Phase 4 structural additions (safe migration): policy & real rate columns.
        _ensure_column_exists(conn, table="daily_macro", column="fed_funds_rate", column_ddl="REAL")
        _ensure_column_exists(conn, table="daily_macro", column="real_rate", column_ddl="REAL")

        # Phase 2: monthly_macro table (NULL-based; no 0.0 placeholders).
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS monthly_macro (
                date TEXT PRIMARY KEY,
                unemployment_rate REAL,
                cpi_yoy REAL,
                core_cpi_yoy REAL,
                pce_yoy REAL,
                pmi REAL,
                wage_level REAL,
                wage_yoy REAL,
                created_at TEXT
            );
            """
        )

        # Safe schema migrations for monthly columns (handles DBs created before Phase 2).
        for col in [
            "unemployment_rate",
            "cpi_yoy",
            "core_cpi_yoy",
            "pce_yoy",
            "pmi",
            "wage_level",
            "wage_yoy",
        ]:
            _ensure_column_exists(conn, table="monthly_macro", column=col, column_ddl="REAL")

        # Clean schema migration: remove redundant/ambiguous `wage_growth` by rebuilding table.
        # Why: we now store wage as (wage_level, wage_yoy). A `wage_growth` column is ambiguous:
        # it could be misread as a rate while CES0500000003 is a level series.
        _migrate_monthly_macro_drop_wage_growth(conn)

        # Phase 3: quarterly_macro (NULL-based; no 0.0 placeholders).
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS quarterly_macro (
                date TEXT PRIMARY KEY,
                real_gdp REAL,
                gdp_qoq_annualized REAL,
                created_at TEXT
            );
            """
        )
        for col in ["real_gdp", "gdp_qoq_annualized"]:
            _ensure_column_exists(conn, table="quarterly_macro", column=col, column_ddl="REAL")


def _ensure_column_exists(conn: sqlite3.Connection, *, table: str, column: str, column_ddl: str) -> None:
    """Add a column to an existing table if it's missing (safe migration).

    - Checks existing columns via PRAGMA table_info(table).
    - Runs ALTER TABLE only if the column is missing.
    - Leaves column NULLable by default (no 0.0 placeholder defaults).
    - Logs errors but never raises (DB writes remain best-effort).
    """
    try:
        rows = conn.execute(f"PRAGMA table_info({table});").fetchall()
        existing = {row["name"] if isinstance(row, sqlite3.Row) else row[1] for row in rows}
        if column in existing:
            return
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_ddl};")
    except Exception as exc:  # noqa: BLE001
        print(f"db_schema_migration_failed[{table}.{column}]: {exc}")


def _table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    """Return set of column names for a table (empty if table doesn't exist)."""
    try:
        rows = conn.execute(f"PRAGMA table_info({table});").fetchall()
        cols: set[str] = set()
        for row in rows:
            if isinstance(row, sqlite3.Row):
                cols.add(str(row["name"]))
            else:
                cols.add(str(row[1]))
        return cols
    except Exception:
        return set()


def _migrate_monthly_macro_drop_wage_growth(conn: sqlite3.Connection) -> None:
    """Rebuild `monthly_macro` without `wage_growth` (safe, idempotent).

    Procedure
    ---------
    1) Create `monthly_macro_new` with the clean schema (no wage_growth).
    2) Copy data from `monthly_macro` into new table.
       - If `wage_level` is missing but `wage_growth` exists, map wage_level <- wage_growth.
       - If a source column is missing, insert NULL.
    3) DROP old monthly_macro
    4) RENAME monthly_macro_new -> monthly_macro

    Failure handling
    ---------------
    - Logs errors but never raises (pipeline must remain stable).
    """
    try:
        cols = _table_columns(conn, "monthly_macro")
        if not cols:
            return
        if "wage_growth" not in cols:
            return  # already clean

        # Build expressions that tolerate older schemas.
        def sel(name: str) -> str:
            return name if name in cols else "NULL"

        # wage_level mapping: prefer wage_level, else fall back to wage_growth.
        if "wage_level" in cols and "wage_growth" in cols:
            wage_level_expr = "COALESCE(wage_level, wage_growth)"
        elif "wage_level" in cols:
            wage_level_expr = "wage_level"
        elif "wage_growth" in cols:
            wage_level_expr = "wage_growth"
        else:
            wage_level_expr = "NULL"

        wage_yoy_expr = "wage_yoy" if "wage_yoy" in cols else "NULL"

        conn.execute("DROP TABLE IF EXISTS monthly_macro_new;")
        conn.execute(
            """
            CREATE TABLE monthly_macro_new (
                date TEXT PRIMARY KEY,
                unemployment_rate REAL,
                cpi_yoy REAL,
                core_cpi_yoy REAL,
                pce_yoy REAL,
                pmi REAL,
                wage_level REAL,
                wage_yoy REAL,
                created_at TEXT
            );
            """
        )

        conn.execute(
            f"""
            INSERT INTO monthly_macro_new (
                date,
                unemployment_rate,
                cpi_yoy,
                core_cpi_yoy,
                pce_yoy,
                pmi,
                wage_level,
                wage_yoy,
                created_at
            )
            SELECT
                {sel("date")},
                {sel("unemployment_rate")},
                {sel("cpi_yoy")},
                {sel("core_cpi_yoy")},
                {sel("pce_yoy")},
                {sel("pmi")},
                {wage_level_expr},
                {wage_yoy_expr},
                {sel("created_at")}
            FROM monthly_macro;
            """
        )
        conn.execute("DROP TABLE monthly_macro;")
        conn.execute("ALTER TABLE monthly_macro_new RENAME TO monthly_macro;")
    except Exception as exc:  # noqa: BLE001
        print(f"db_schema_migration_failed[monthly_macro_drop_wage_growth]: {exc}")


def upsert_market_daily(
    *,
    date: str,
    kospi_pct: float,
    kosdaq_pct: float,
    sp500_pct: float,
    nasdaq_pct: float,
    dow_pct: float,
    usdkrw: float,
    usdkrw_pct: float | None,
    us10y: float | None = None,
    vix: float | None = None,
    db_path: Path | None = None,
) -> None:
    """Insert/replace one row into `market_daily`.

    Failure handling philosophy:
    - This function can raise (sqlite3.Error). Callers should wrap with `safe_*` to avoid
      breaking the nightly pipeline.
    """
    created_at = _utc_now_iso()
    init_db(db_path)
    with connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO market_daily (
                date, kospi_pct, kosdaq_pct, sp500_pct, nasdaq_pct, dow_pct,
                usdkrw, usdkrw_pct, us10y, vix, created_at
            ) VALUES (
                :date, :kospi_pct, :kosdaq_pct, :sp500_pct, :nasdaq_pct, :dow_pct,
                :usdkrw, :usdkrw_pct, :us10y, :vix, :created_at
            )
            ON CONFLICT(date) DO UPDATE SET
                kospi_pct=excluded.kospi_pct,
                kosdaq_pct=excluded.kosdaq_pct,
                sp500_pct=excluded.sp500_pct,
                nasdaq_pct=excluded.nasdaq_pct,
                dow_pct=excluded.dow_pct,
                usdkrw=excluded.usdkrw,
                usdkrw_pct=excluded.usdkrw_pct,
                us10y=excluded.us10y,
                vix=excluded.vix,
                created_at=excluded.created_at;
            """,
            {
                "date": date,
                "kospi_pct": float(kospi_pct),
                "kosdaq_pct": float(kosdaq_pct),
                "sp500_pct": float(sp500_pct),
                "nasdaq_pct": float(nasdaq_pct),
                "dow_pct": float(dow_pct),
                "usdkrw": float(usdkrw),
                # NULL-based missing data: never coerce placeholders like 0.0 here.
                "usdkrw_pct": None if usdkrw_pct is None else float(usdkrw_pct),
                "us10y": None if us10y is None else float(us10y),
                "vix": None if vix is None else float(vix),
                "created_at": created_at,
            },
        )


def upsert_market_flow_daily(
    *,
    date: str,
    foreign_net: float | None,
    foreign_20d: float | None = None,
    foreign_60d: float | None = None,
    db_path: Path | None = None,
) -> None:
    """Insert/replace one row into `market_flow_daily`.

    If rolling sums are not provided, they remain NULL until updated by
    `update_market_flow_rollings()` or via the safe wrapper below.
    """
    created_at = _utc_now_iso()
    init_db(db_path)
    with connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO market_flow_daily (
                date, foreign_net, foreign_20d, foreign_60d, created_at
            ) VALUES (
                :date, :foreign_net, :foreign_20d, :foreign_60d, :created_at
            )
            ON CONFLICT(date) DO UPDATE SET
                foreign_net=excluded.foreign_net,
                foreign_20d=excluded.foreign_20d,
                foreign_60d=excluded.foreign_60d,
                created_at=excluded.created_at;
            """,
            {
                "date": date,
                # NULL-based missing data: if flows fetch failed/unavailable, store NULL.
                "foreign_net": None if foreign_net is None else float(foreign_net),
                "foreign_20d": None if foreign_20d is None else float(foreign_20d),
                "foreign_60d": None if foreign_60d is None else float(foreign_60d),
                "created_at": created_at,
            },
        )


def upsert_stock_daily_stub(
    *,
    date: str,
    ticker: str,
    db_path: Path | None = None,
    **kwargs: Any,
) -> None:
    """Stub stock-level insertion (STEP 2 allows stubbing).

    The schema is created so later steps can begin storing stock-level features,
    but nightly integration is limited to market + flow for now.
    """
    _ = (date, ticker, kwargs)  # reserved for future use
    init_db(db_path)
    # Intentionally no-op for now.


def upsert_daily_macro(
    *,
    date: str,
    us10y: float | None = None,
    us2y: float | None = None,
    spread_2_10: float | None = None,
    vix: float | None = None,
    dxy: float | None = None,
    usdkrw: float | None = None,
    fed_funds_rate: float | None = None,
    real_rate: float | None = None,
    db_path: Path | None = None,
) -> None:
    """Upsert one row into `daily_macro` (NULL-based missing data)."""
    created_at = _utc_now_iso()
    init_db(db_path)
    with connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO daily_macro (
                date, us10y, us2y, spread_2_10, vix, dxy, usdkrw, fed_funds_rate, real_rate, created_at
            ) VALUES (
                :date, :us10y, :us2y, :spread_2_10, :vix, :dxy, :usdkrw, :fed_funds_rate, :real_rate, :created_at
            )
            ON CONFLICT(date) DO UPDATE SET
                us10y=excluded.us10y,
                us2y=excluded.us2y,
                spread_2_10=excluded.spread_2_10,
                vix=excluded.vix,
                dxy=excluded.dxy,
                usdkrw=excluded.usdkrw,
                fed_funds_rate=excluded.fed_funds_rate,
                real_rate=excluded.real_rate,
                created_at=excluded.created_at;
            """,
            {
                "date": date,
                "us10y": None if us10y is None else float(us10y),
                "us2y": None if us2y is None else float(us2y),
                "spread_2_10": None if spread_2_10 is None else float(spread_2_10),
                "vix": None if vix is None else float(vix),
                "dxy": None if dxy is None else float(dxy),
                "usdkrw": None if usdkrw is None else float(usdkrw),
                "fed_funds_rate": None if fed_funds_rate is None else float(fed_funds_rate),
                "real_rate": None if real_rate is None else float(real_rate),
                "created_at": created_at,
            },
        )


def upsert_monthly_macro(
    *,
    date: str,
    unemployment_rate: float | None = None,
    cpi_yoy: float | None = None,
    core_cpi_yoy: float | None = None,
    pce_yoy: float | None = None,
    pmi: float | None = None,
    wage_level: float | None = None,
    wage_yoy: float | None = None,
    db_path: Path | None = None,
) -> None:
    """Upsert one row into `monthly_macro` (NULL-based missing data)."""
    created_at = _utc_now_iso()
    init_db(db_path)
    with connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO monthly_macro (
                date, unemployment_rate, cpi_yoy, core_cpi_yoy, pce_yoy, pmi,
                wage_level, wage_yoy, created_at
            ) VALUES (
                :date, :unemployment_rate, :cpi_yoy, :core_cpi_yoy, :pce_yoy, :pmi,
                :wage_level, :wage_yoy, :created_at
            )
            ON CONFLICT(date) DO UPDATE SET
                unemployment_rate=excluded.unemployment_rate,
                cpi_yoy=excluded.cpi_yoy,
                core_cpi_yoy=excluded.core_cpi_yoy,
                pce_yoy=excluded.pce_yoy,
                pmi=excluded.pmi,
                wage_level=excluded.wage_level,
                wage_yoy=excluded.wage_yoy,
                created_at=excluded.created_at;
            """,
            {
                "date": date,
                "unemployment_rate": None if unemployment_rate is None else float(unemployment_rate),
                "cpi_yoy": None if cpi_yoy is None else float(cpi_yoy),
                "core_cpi_yoy": None if core_cpi_yoy is None else float(core_cpi_yoy),
                "pce_yoy": None if pce_yoy is None else float(pce_yoy),
                "pmi": None if pmi is None else float(pmi),
                "wage_level": None if wage_level is None else float(wage_level),
                "wage_yoy": None if wage_yoy is None else float(wage_yoy),
                "created_at": created_at,
            },
        )


def upsert_quarterly_macro(
    *,
    date: str,
    real_gdp: float | None = None,
    gdp_qoq_annualized: float | None = None,
    db_path: Path | None = None,
) -> None:
    """Upsert one row into `quarterly_macro` (Phase 3 schema, NULL-based)."""
    created_at = _utc_now_iso()
    init_db(db_path)
    with connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO quarterly_macro (date, real_gdp, gdp_qoq_annualized, created_at)
            VALUES (:date, :real_gdp, :gdp_qoq_annualized, :created_at)
            ON CONFLICT(date) DO UPDATE SET
                real_gdp=excluded.real_gdp,
                gdp_qoq_annualized=excluded.gdp_qoq_annualized,
                created_at=excluded.created_at;
            """,
            {
                "date": date,
                "real_gdp": None if real_gdp is None else float(real_gdp),
                "gdp_qoq_annualized": None if gdp_qoq_annualized is None else float(gdp_qoq_annualized),
                "created_at": created_at,
            },
        )


def safe_upsert_quarterly_macro(**kwargs: Any) -> None:
    """Fail-safe wrapper for `upsert_quarterly_macro`."""
    try:
        upsert_quarterly_macro(**kwargs)
    except Exception as exc:  # noqa: BLE001
        _log_db_error("upsert_quarterly_macro", exc)


def upsert_market_forward(
    *,
    date: str,
    sp500_forward_eps: float | None = None,
    sp500_forward_pe: float | None = None,
    eps_revision_3m: float | None = None,
    db_path: Path | None = None,
) -> None:
    """Upsert one row into `market_forward` (NULL-based missing data)."""
    created_at = _utc_now_iso()
    init_db(db_path)
    with connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO market_forward (date, sp500_forward_eps, sp500_forward_pe, eps_revision_3m, created_at)
            VALUES (:date, :sp500_forward_eps, :sp500_forward_pe, :eps_revision_3m, :created_at)
            ON CONFLICT(date) DO UPDATE SET
                sp500_forward_eps=excluded.sp500_forward_eps,
                sp500_forward_pe=excluded.sp500_forward_pe,
                eps_revision_3m=excluded.eps_revision_3m,
                created_at=excluded.created_at;
            """,
            {
                "date": date,
                "sp500_forward_eps": None if sp500_forward_eps is None else float(sp500_forward_eps),
                "sp500_forward_pe": None if sp500_forward_pe is None else float(sp500_forward_pe),
                "eps_revision_3m": None if eps_revision_3m is None else float(eps_revision_3m),
                "created_at": created_at,
            },
        )


# --- Rolling calculation helpers (no LLM dependency) ---

_ALLOWED_FLOW_COLUMNS = {"foreign_net", "foreign_20d", "foreign_60d"}


def get_last_n_market_flow(n: int, db_path: Path | None = None) -> List[Dict[str, Any]]:
    """Return last N rows from `market_flow_daily` (descending by date)."""
    init_db(db_path)
    with connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT date, foreign_net, foreign_20d, foreign_60d, created_at
            FROM market_flow_daily
            ORDER BY date DESC
            LIMIT :n;
            """,
            {"n": int(n)},
        ).fetchall()
        return [dict(row) for row in rows]


def calculate_rolling_sum(column: str, n: int, db_path: Path | None = None) -> float | None:
    """Calculate rolling sum over last N rows for a given flow column.

    Security note:
    - `column` is validated against a fixed allowlist to avoid SQL injection.

    NULL semantics:
    - With the NULL-based design, missing data remains NULL in the DB.
    - To avoid silently turning "missing" into "0.0", this function returns NULL-like behavior:
      it returns None when there is insufficient non-NULL history in the window.
    """
    if column not in _ALLOWED_FLOW_COLUMNS:
        raise ValueError(f"Unsupported column for rolling sum: {column}")
    init_db(db_path)
    with connect(db_path) as conn:
        # Use a subquery to limit last N rows, then sum.
        row = conn.execute(
            f"""
            SELECT
              SUM({column}) AS s,
              SUM(CASE WHEN {column} IS NOT NULL THEN 1 ELSE 0 END) AS cnt
            FROM (
                SELECT {column}
                FROM market_flow_daily
                ORDER BY date DESC
                LIMIT :n
            );
            """,
            {"n": int(n)},
        ).fetchone()
        if row is None:
            return None
        cnt = int(row["cnt"] or 0)
        if cnt < int(n):
            return None
        return float(row["s"])


def update_market_flow_rollings(date: str, db_path: Path | None = None) -> None:
    """Update rolling sums (20d/60d) for the given date row in `market_flow_daily`."""
    init_db(db_path)
    foreign_20d = calculate_rolling_sum("foreign_net", 20, db_path=db_path)
    foreign_60d = calculate_rolling_sum("foreign_net", 60, db_path=db_path)
    with connect(db_path) as conn:
        conn.execute(
            """
            UPDATE market_flow_daily
            SET foreign_20d = :foreign_20d,
                foreign_60d = :foreign_60d
            WHERE date = :date;
            """,
            {
                "date": date,
                "foreign_20d": None if foreign_20d is None else float(foreign_20d),
                "foreign_60d": None if foreign_60d is None else float(foreign_60d),
            },
        )


def get_stock_history(ticker: str, n: int, db_path: Path | None = None) -> List[Dict[str, Any]]:
    """Return last N rows for a ticker from `stock_daily` (descending by date)."""
    init_db(db_path)
    with connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM stock_daily
            WHERE ticker = :ticker
            ORDER BY date DESC
            LIMIT :n;
            """,
            {"ticker": ticker.upper().strip(), "n": int(n)},
        ).fetchall()
        return [dict(row) for row in rows]


# --- Safe wrappers: log errors but do not break pipeline ---


def _log_db_error(context: str, exc: Exception) -> None:
    # Keep logging simple and dependency-free for the MVP.
    print(f"db_error[{context}]: {exc}")


def safe_upsert_market_daily(**kwargs: Any) -> None:
    """Fail-safe wrapper for `upsert_market_daily`."""
    try:
        upsert_market_daily(**kwargs)
    except Exception as exc:  # noqa: BLE001 - pipeline must continue
        _log_db_error("upsert_market_daily", exc)


def safe_upsert_market_flow_daily(**kwargs: Any) -> None:
    """Fail-safe wrapper for `upsert_market_flow_daily` + rolling updates."""
    try:
        upsert_market_flow_daily(**kwargs)
        if "date" in kwargs:
            update_market_flow_rollings(str(kwargs["date"]), db_path=kwargs.get("db_path"))
    except Exception as exc:  # noqa: BLE001 - pipeline must continue
        _log_db_error("upsert_market_flow_daily", exc)


def safe_upsert_daily_macro(**kwargs: Any) -> None:
    """Fail-safe wrapper for `upsert_daily_macro`."""
    try:
        upsert_daily_macro(**kwargs)
    except Exception as exc:  # noqa: BLE001
        _log_db_error("upsert_daily_macro", exc)

    # NOTE:
    # `upsert_monthly_macro` is defined earlier in this module with the full Phase 2 signature
    # including wage_level and wage_yoy. A duplicate legacy definition used to live here and
    # caused runtime errors like:
    #   upsert_monthly_macro() got an unexpected keyword argument 'wage_level'
    # That duplicate has been removed to ensure the correct NULL-based schema is used.


def safe_upsert_monthly_macro(**kwargs: Any) -> None:
    """Fail-safe wrapper for `upsert_monthly_macro`."""
    try:
        upsert_monthly_macro(**kwargs)
    except Exception as exc:  # noqa: BLE001
        _log_db_error("upsert_monthly_macro", exc)


def get_sp500_forward_eps_on_or_before(
    *,
    date: str,
    days_back: int,
    db_path: Path | None = None,
) -> float | None:
    """Return sp500_forward_eps from `market_forward` at or before (date - days_back).

    Used to compute eps_revision_3m without depending on LLM.
    Returns None if no historical value exists (NULL-based).
    """
    try:
        target = (dt_date.fromisoformat(date) - timedelta(days=int(days_back))).isoformat()
    except Exception:
        # If parsing fails, fall back to the passed date (best effort).
        target = date
    init_db(db_path)
    with connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT sp500_forward_eps
            FROM market_forward
            WHERE date <= :target_date
            ORDER BY date DESC
            LIMIT 1;
            """,
            {"target_date": target},
        ).fetchone()
        # We query using ISO strings; ordering works for YYYY-MM-DD format.
        if row is None:
            return None
        value = row["sp500_forward_eps"]
        return None if value is None else float(value)


# --- One-time migration helpers (optional) ---


def migrate_placeholders_to_null(db_path: Path | None = None) -> dict[str, int]:
    """Convert legacy 0.0 placeholders into NULL for better data integrity.

    Background
    ----------
    Earlier versions stored 0.0 as a placeholder when:
    - fetch failed (e.g., usdkrw_pct=FAIL)
    - data was not implemented yet (e.g., us10y/vix)
    This makes it impossible to distinguish real 0.0 from missing.

    Migration policy (conservative)
    -------------------------------
    - Only touches columns explicitly called out for NULL-based design:
      - market_daily: usdkrw_pct, us10y, vix
      - market_flow_daily: foreign_net, foreign_20d, foreign_60d
    - For flows, only nullifies rows where the *whole trio* is effectively placeholder
      (0.0/0.0/0.0 or 0.0 with rollings 0.0/NULL), which strongly indicates "no data".
    """
    init_db(db_path)
    counts: dict[str, int] = {}
    with connect(db_path) as conn:
        cur = conn.execute("UPDATE market_daily SET usdkrw_pct=NULL WHERE usdkrw_pct=0.0;")
        counts["market_daily.usdkrw_pct"] = int(cur.rowcount or 0)

        cur = conn.execute("UPDATE market_daily SET us10y=NULL WHERE us10y=0.0;")
        counts["market_daily.us10y"] = int(cur.rowcount or 0)

        cur = conn.execute("UPDATE market_daily SET vix=NULL WHERE vix=0.0;")
        counts["market_daily.vix"] = int(cur.rowcount or 0)

        cur = conn.execute(
            """
            UPDATE market_flow_daily
            SET foreign_net=NULL, foreign_20d=NULL, foreign_60d=NULL
            WHERE foreign_net=0.0
              AND (foreign_20d IS NULL OR foreign_20d=0.0)
              AND (foreign_60d IS NULL OR foreign_60d=0.0);
            """
        )
        counts["market_flow_daily.foreign_*"] = int(cur.rowcount or 0)
    return counts


def safe_migrate_placeholders_to_null(db_path: Path | None = None) -> dict[str, int]:
    """Fail-safe wrapper for `migrate_placeholders_to_null`."""
    try:
        return migrate_placeholders_to_null(db_path=db_path)
    except Exception as exc:  # noqa: BLE001 - migration should never block pipeline
        _log_db_error("migrate_placeholders_to_null", exc)
        return {}

