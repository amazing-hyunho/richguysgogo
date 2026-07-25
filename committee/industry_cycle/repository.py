from __future__ import annotations

"""Phase 0 repository for the industry cycle tracker.

Manages only the *structural* tables introduced in Phase 0: industry
taxonomy, external-classification aliases, industry-asset mapping,
theme-industry mapping, the indicator catalog, point-in-time indicator
observations, and data-quality events.

No scoring, signal, price, or model-config tables are touched here — those
belong to Phase 1+ (docs/industry_cycle_mvp_design.md section 12).

Conventions (matching `committee/core/database.py`):
- NULL (never 0.0/"") for missing/unavailable values.
- `init_db()` is called before every write so the module works standalone
  against a fresh DB (tests use a temp `db_path`).
- Functions raise on DB errors; callers needing fail-safe behavior can wrap
  with their own try/except, mirroring the `safe_*` wrappers in
  `committee.core.database`.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from committee.core.database import connect, init_db
from committee.industry_cycle.time_contract import is_known_by


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _country_scope_to_text(country_scope: Iterable[str] | str | None) -> str | None:
    if country_scope is None:
        return None
    if isinstance(country_scope, str):
        return country_scope
    codes = sorted({str(c).strip().upper() for c in country_scope if str(c).strip()})
    return ",".join(codes) if codes else None


def _country_scope_to_list(country_scope_text: str | None) -> List[str]:
    if not country_scope_text:
        return []
    return [c for c in country_scope_text.split(",") if c]


# --- industry_master ---------------------------------------------------------


def upsert_industry_master(
    *,
    industry_id: str,
    name_kr: str | None = None,
    name_en: str | None = None,
    country_scope: Iterable[str] | str | None = None,
    coverage_status: str | None = None,
    active: bool = True,
    notes: str | None = None,
    db_path: Path | None = None,
) -> None:
    """Insert/update one row into `industry_master` (NULL-based)."""
    now = _now_iso()
    init_db(db_path)
    with connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO industry_master (
                industry_id, name_kr, name_en, country_scope, coverage_status,
                active, notes, created_at, updated_at
            ) VALUES (
                :industry_id, :name_kr, :name_en, :country_scope, :coverage_status,
                :active, :notes, :created_at, :updated_at
            )
            ON CONFLICT(industry_id) DO UPDATE SET
                name_kr=excluded.name_kr,
                name_en=excluded.name_en,
                country_scope=excluded.country_scope,
                coverage_status=excluded.coverage_status,
                active=excluded.active,
                notes=excluded.notes,
                updated_at=excluded.updated_at;
            """,
            {
                "industry_id": industry_id.strip(),
                "name_kr": name_kr,
                "name_en": name_en,
                "country_scope": _country_scope_to_text(country_scope),
                "coverage_status": coverage_status,
                "active": 1 if active else 0,
                "notes": notes,
                "created_at": now,
                "updated_at": now,
            },
        )


def list_industries(*, active_only: bool = False, db_path: Path | None = None) -> List[Dict[str, Any]]:
    init_db(db_path)
    with connect(db_path) as conn:
        query = "SELECT * FROM industry_master"
        if active_only:
            query += " WHERE active = 1"
        query += " ORDER BY industry_id;"
        rows = conn.execute(query).fetchall()
        out = []
        for row in rows:
            d = dict(row)
            d["country_scope"] = _country_scope_to_list(d.get("country_scope"))
            out.append(d)
        return out


def get_industry(industry_id: str, db_path: Path | None = None) -> Optional[Dict[str, Any]]:
    init_db(db_path)
    with connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM industry_master WHERE industry_id = :id;",
            {"id": industry_id.strip()},
        ).fetchone()
        if row is None:
            return None
        d = dict(row)
        d["country_scope"] = _country_scope_to_list(d.get("country_scope"))
        return d


# --- industry_alias -----------------------------------------------------------


def upsert_industry_alias(
    *,
    provider: str,
    external_code: str,
    industry_id: str,
    valid_from: str | None = None,
    valid_to: str | None = None,
    db_path: Path | None = None,
) -> None:
    """Insert/update one row into `industry_alias`.

    Uses a manual UPDATE-then-INSERT instead of `ON CONFLICT`, because SQLite
    treats NULL as distinct from NULL for UNIQUE-constraint purposes: two
    upserts with `valid_from=None` would each insert a new row instead of
    colliding, silently breaking the "same input -> same rows" reproducibility
    contract (design doc section 12). Matching on `valid_from IS :valid_from`
    is NULL-safe in SQLite and fixes that.
    """
    now = _now_iso()
    init_db(db_path)
    params = {
        "provider": provider.strip(),
        "external_code": external_code.strip(),
        "industry_id": industry_id.strip(),
        "valid_from": valid_from,
        "valid_to": valid_to,
        "created_at": now,
    }
    with connect(db_path) as conn:
        cur = conn.execute(
            """
            UPDATE industry_alias
            SET industry_id = :industry_id, valid_to = :valid_to
            WHERE provider = :provider AND external_code = :external_code
              AND valid_from IS :valid_from;
            """,
            params,
        )
        if cur.rowcount == 0:
            conn.execute(
                """
                INSERT INTO industry_alias (
                    provider, external_code, industry_id, valid_from, valid_to, created_at
                ) VALUES (
                    :provider, :external_code, :industry_id, :valid_from, :valid_to, :created_at
                );
                """,
                params,
            )


def list_industry_aliases(
    industry_id: str | None = None, db_path: Path | None = None
) -> List[Dict[str, Any]]:
    init_db(db_path)
    with connect(db_path) as conn:
        if industry_id:
            rows = conn.execute(
                "SELECT * FROM industry_alias WHERE industry_id = :id ORDER BY provider, external_code;",
                {"id": industry_id.strip()},
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM industry_alias ORDER BY provider, external_code;"
            ).fetchall()
        return [dict(r) for r in rows]


# --- industry_asset_map -------------------------------------------------------


def upsert_industry_asset_map(
    *,
    asset_id: str,
    industry_id: str,
    asset_type: str | None = None,
    market: str | None = None,
    weight: float | None = None,
    valid_from: str | None = None,
    valid_to: str | None = None,
    db_path: Path | None = None,
) -> None:
    """Insert/update one row into `industry_asset_map` (NULL-safe upsert).

    See `upsert_industry_alias` for why this is a manual UPDATE-then-INSERT
    rather than `ON CONFLICT`: SQLite does not treat two NULL `valid_from`
    values as conflicting, which would otherwise duplicate rows on repeated
    syncs with the same config.
    """
    now = _now_iso()
    init_db(db_path)
    params = {
        "asset_id": asset_id.strip(),
        "asset_type": asset_type,
        "market": market,
        "industry_id": industry_id.strip(),
        "weight": None if weight is None else float(weight),
        "valid_from": valid_from,
        "valid_to": valid_to,
        "created_at": now,
    }
    with connect(db_path) as conn:
        cur = conn.execute(
            """
            UPDATE industry_asset_map
            SET asset_type = :asset_type, market = :market, weight = :weight, valid_to = :valid_to
            WHERE asset_id = :asset_id AND industry_id = :industry_id
              AND valid_from IS :valid_from;
            """,
            params,
        )
        if cur.rowcount == 0:
            conn.execute(
                """
                INSERT INTO industry_asset_map (
                    asset_id, asset_type, market, industry_id, weight, valid_from, valid_to, created_at
                ) VALUES (
                    :asset_id, :asset_type, :market, :industry_id, :weight, :valid_from, :valid_to, :created_at
                );
                """,
                params,
            )


def list_industry_assets(
    industry_id: str | None = None, db_path: Path | None = None
) -> List[Dict[str, Any]]:
    init_db(db_path)
    with connect(db_path) as conn:
        if industry_id:
            rows = conn.execute(
                "SELECT * FROM industry_asset_map WHERE industry_id = :id ORDER BY asset_id;",
                {"id": industry_id.strip()},
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM industry_asset_map ORDER BY industry_id, asset_id;"
            ).fetchall()
        return [dict(r) for r in rows]


# --- industry_indicator_map ----------------------------------------------------


def upsert_industry_indicator_map(
    *,
    industry_id: str,
    indicator_id: str,
    direction: str | None = None,
    weight: float | None = None,
    valid_from: str | None = None,
    valid_to: str | None = None,
    db_path: Path | None = None,
) -> None:
    """Insert/update one row into `industry_indicator_map` (NULL-safe upsert).

    See `upsert_industry_alias` for why this is a manual UPDATE-then-INSERT
    rather than `ON CONFLICT`: SQLite does not treat two NULL `valid_from`
    values as conflicting, which would otherwise duplicate rows on repeated
    syncs with the same config.
    """
    now = _now_iso()
    init_db(db_path)
    params = {
        "industry_id": industry_id.strip(),
        "indicator_id": indicator_id.strip(),
        "direction": direction,
        "weight": None if weight is None else float(weight),
        "valid_from": valid_from,
        "valid_to": valid_to,
        "created_at": now,
    }
    with connect(db_path) as conn:
        cur = conn.execute(
            """
            UPDATE industry_indicator_map
            SET direction = :direction, weight = :weight, valid_to = :valid_to
            WHERE industry_id = :industry_id AND indicator_id = :indicator_id
              AND valid_from IS :valid_from;
            """,
            params,
        )
        if cur.rowcount == 0:
            conn.execute(
                """
                INSERT INTO industry_indicator_map (
                    industry_id, indicator_id, direction, weight, valid_from, valid_to, created_at
                ) VALUES (
                    :industry_id, :indicator_id, :direction, :weight, :valid_from, :valid_to, :created_at
                );
                """,
                params,
            )


def list_industry_indicators(
    industry_id: str | None = None, db_path: Path | None = None
) -> List[Dict[str, Any]]:
    init_db(db_path)
    with connect(db_path) as conn:
        if industry_id:
            rows = conn.execute(
                "SELECT * FROM industry_indicator_map WHERE industry_id = :id ORDER BY indicator_id;",
                {"id": industry_id.strip()},
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM industry_indicator_map ORDER BY industry_id, indicator_id;"
            ).fetchall()
        return [dict(r) for r in rows]


# --- theme_industry_map --------------------------------------------------------


def upsert_theme_industry_map(
    *,
    theme_id: str,
    industry_id: str,
    valid_from: str | None = None,
    valid_to: str | None = None,
    db_path: Path | None = None,
) -> None:
    """Insert/update one row into `theme_industry_map` (NULL-safe upsert).

    See `upsert_industry_alias` for why this is a manual UPDATE-then-INSERT
    rather than `ON CONFLICT`.
    """
    now = _now_iso()
    init_db(db_path)
    params = {
        "theme_id": theme_id.strip(),
        "industry_id": industry_id.strip(),
        "valid_from": valid_from,
        "valid_to": valid_to,
        "created_at": now,
    }
    with connect(db_path) as conn:
        cur = conn.execute(
            """
            UPDATE theme_industry_map
            SET valid_to = :valid_to
            WHERE theme_id = :theme_id AND industry_id = :industry_id
              AND valid_from IS :valid_from;
            """,
            params,
        )
        if cur.rowcount == 0:
            conn.execute(
                """
                INSERT INTO theme_industry_map (
                    theme_id, industry_id, valid_from, valid_to, created_at
                ) VALUES (
                    :theme_id, :industry_id, :valid_from, :valid_to, :created_at
                );
                """,
                params,
            )


def list_theme_industries(
    theme_id: str | None = None, db_path: Path | None = None
) -> List[Dict[str, Any]]:
    init_db(db_path)
    with connect(db_path) as conn:
        if theme_id:
            rows = conn.execute(
                "SELECT * FROM theme_industry_map WHERE theme_id = :id ORDER BY industry_id;",
                {"id": theme_id.strip()},
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM theme_industry_map ORDER BY theme_id, industry_id;"
            ).fetchall()
        return [dict(r) for r in rows]


# --- indicator_catalog ---------------------------------------------------------


def upsert_indicator_catalog(
    *,
    indicator_id: str,
    provider: str | None = None,
    series_id: str | None = None,
    unit: str | None = None,
    frequency: str | None = None,
    transform: str | None = None,
    description: str | None = None,
    baseline: float | None = None,
    db_path: Path | None = None,
) -> None:
    now = _now_iso()
    init_db(db_path)
    with connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO indicator_catalog (
                indicator_id, provider, series_id, unit, frequency, transform, description,
                baseline, created_at, updated_at
            ) VALUES (
                :indicator_id, :provider, :series_id, :unit, :frequency, :transform, :description,
                :baseline, :created_at, :updated_at
            )
            ON CONFLICT(indicator_id) DO UPDATE SET
                provider=excluded.provider,
                series_id=excluded.series_id,
                unit=excluded.unit,
                frequency=excluded.frequency,
                transform=excluded.transform,
                description=excluded.description,
                baseline=excluded.baseline,
                updated_at=excluded.updated_at;
            """,
            {
                "indicator_id": indicator_id.strip(),
                "provider": provider,
                "series_id": series_id,
                "unit": unit,
                "frequency": frequency,
                "transform": transform,
                "description": description,
                "baseline": None if baseline is None else float(baseline),
                "created_at": now,
                "updated_at": now,
            },
        )


def list_indicators(db_path: Path | None = None) -> List[Dict[str, Any]]:
    init_db(db_path)
    with connect(db_path) as conn:
        rows = conn.execute("SELECT * FROM indicator_catalog ORDER BY indicator_id;").fetchall()
        return [dict(r) for r in rows]


# --- indicator_observation (point-in-time) -------------------------------------


def insert_indicator_observation(
    *,
    indicator_id: str,
    observed_at: str,
    value: float | None,
    published_at: str | None = None,
    known_at: str | None = None,
    vintage_at: str | None = None,
    source_ref: str | None = None,
    db_path: Path | None = None,
) -> None:
    """Insert/replace one point-in-time observation.

    NULL policy: `value=None` is stored as NULL, never 0.0.

    Point-in-time metadata contract:
    - When the caller passes an explicit `known_at` (with or without an
      explicit `vintage_at`), it takes full responsibility for point-in-time
      correctness: `vintage_at` defaults to that `known_at` when omitted.
      This is deterministic and caller-controlled, so repeated calls with the
      same `known_at` upsert the same row instead of creating duplicates.
    - When *both* `known_at` and `vintage_at` are omitted (the common case
      for ad hoc/manual inserts and quick scripts), wall-clock "now" cannot
      be used as the default the way it naively was before: two calls with
      the exact same `value`/`published_at`/`source_ref` run at different
      wall-clock times would otherwise resolve to two different vintages,
      creating a spurious duplicate "revision" for data that never actually
      changed. To keep idempotency real rather than nominal, this path looks
      up the most recently inserted row for `(indicator_id, observed_at)`:
        * If it has the exact same `value`/`published_at`/`source_ref`, this
          call is treated as a same-data re-collection and reuses that row's
          `known_at`/`vintage_at` verbatim — a true no-op regardless of when
          the re-run happens.
        * Otherwise (no prior row, or the value/metadata actually changed),
          this is genuinely new/revised data and gets a fresh `known_at` =
          `vintage_at` = "now", landing in a brand-new row rather than
          overwriting the prior one — preserving the past vintage.
    """
    now = _now_iso()
    normalized_value = None if value is None else float(value)
    init_db(db_path)
    with connect(db_path) as conn:
        if known_at is None and vintage_at is None:
            latest = conn.execute(
                """
                SELECT value, published_at, source_ref, known_at, vintage_at
                FROM indicator_observation
                WHERE indicator_id = :indicator_id AND observed_at = :observed_at
                ORDER BY id DESC
                LIMIT 1;
                """,
                {"indicator_id": indicator_id.strip(), "observed_at": observed_at},
            ).fetchone()
            is_same_as_latest = (
                latest is not None
                and latest["value"] == normalized_value
                and latest["published_at"] == published_at
                and latest["source_ref"] == source_ref
            )
            if is_same_as_latest:
                resolved_known_at = latest["known_at"]
                resolved_vintage_at = latest["vintage_at"]
            else:
                resolved_known_at = now
                resolved_vintage_at = now
        else:
            resolved_known_at = known_at or now
            resolved_vintage_at = vintage_at or resolved_known_at

        conn.execute(
            """
            INSERT INTO indicator_observation (
                indicator_id, observed_at, value, published_at, known_at, vintage_at,
                source_ref, created_at
            ) VALUES (
                :indicator_id, :observed_at, :value, :published_at, :known_at, :vintage_at,
                :source_ref, :created_at
            )
            ON CONFLICT(indicator_id, observed_at, vintage_at) DO UPDATE SET
                value=excluded.value,
                published_at=excluded.published_at,
                known_at=excluded.known_at,
                source_ref=excluded.source_ref;
            """,
            {
                "indicator_id": indicator_id.strip(),
                "observed_at": observed_at,
                "value": normalized_value,
                "published_at": published_at,
                "known_at": resolved_known_at,
                "vintage_at": resolved_vintage_at,
                "source_ref": source_ref,
                "created_at": now,
            },
        )


def get_observations_as_of(
    indicator_id: str,
    as_of: str,
    db_path: Path | None = None,
) -> List[Dict[str, Any]]:
    """Return observations for `indicator_id` that were knowable at `as_of`.

    Leakage-safe query: only rows knowable at `as_of` are returned, matching
    the backtest rule from the design doc (5.1):
    "백테스트는 known_at <= signal_date인 데이터만 사용한다".

    The `known_at` column may hold either a bare date ("YYYY-MM-DD") or a
    full ISO datetime ("YYYY-MM-DDTHH:MM:SS+00:00") depending on the caller,
    and `as_of` is typically a bare date. A raw SQL `known_at <= :as_of`
    string comparison is NOT safe here: "2026-07-15T08:00:00+00:00" sorts
    lexicographically *after* "2026-07-15", so a same-day timestamp would be
    incorrectly excluded when `as_of` is a bare date. To avoid depending on
    string ordering, filtering is done in Python via `time_contract.is_known_by`,
    which parses both sides into actual `date` objects (day-level precision)
    before comparing.
    """
    init_db(db_path)
    with connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT * FROM indicator_observation
            WHERE indicator_id = :indicator_id
            ORDER BY observed_at DESC, vintage_at DESC;
            """,
            {"indicator_id": indicator_id.strip()},
        ).fetchall()
    dict_rows = [dict(r) for r in rows]
    return [r for r in dict_rows if is_known_by(r, as_of)]


# --- data_quality_event ---------------------------------------------------------


def record_data_quality_event(
    *,
    event_type: str,
    provider: str | None = None,
    target: str | None = None,
    severity: str | None = None,
    status: str = "open",
    message: str | None = None,
    detected_at: str | None = None,
    db_path: Path | None = None,
) -> int:
    now = _now_iso()
    init_db(db_path)
    with connect(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO data_quality_event (
                provider, target, event_type, severity, status, message,
                detected_at, resolved_at, created_at
            ) VALUES (
                :provider, :target, :event_type, :severity, :status, :message,
                :detected_at, NULL, :created_at
            );
            """,
            {
                "provider": provider,
                "target": target,
                "event_type": event_type,
                "severity": severity,
                "status": status,
                "message": message,
                "detected_at": detected_at or now,
                "created_at": now,
            },
        )
        return int(cur.lastrowid)


def list_data_quality_events(
    status: str | None = None,
    db_path: Path | None = None,
) -> List[Dict[str, Any]]:
    init_db(db_path)
    with connect(db_path) as conn:
        if status:
            rows = conn.execute(
                "SELECT * FROM data_quality_event WHERE status = :status ORDER BY created_at DESC;",
                {"status": status},
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM data_quality_event ORDER BY created_at DESC;"
            ).fetchall()
        return [dict(r) for r in rows]


# --- config -> DB sync (deterministic/reproducible) ------------------------------


def sync_industry_master_from_config(
    taxonomy: Dict[str, Any], db_path: Path | None = None
) -> int:
    """Upsert `industry_master` + `industry_alias` rows from a parsed taxonomy config.

    Deterministic: running this twice with the same config produces the same
    rows — this is the Phase 0 completion criterion from the design doc
    (section 12): "동일 입력으로 같은 산업·지표 매핑을 재현할 수 있다".

    Returns the number of industries synced.
    """
    industries = taxonomy.get("industries", [])
    count = 0
    for entry in industries:
        industry_id = str(entry.get("industry_id", "")).strip()
        if not industry_id:
            continue
        upsert_industry_master(
            industry_id=industry_id,
            name_kr=entry.get("name_kr"),
            name_en=entry.get("name_en"),
            country_scope=entry.get("country_scope"),
            coverage_status=entry.get("coverage_status"),
            active=bool(entry.get("active", True)),
            notes=entry.get("notes"),
            db_path=db_path,
        )
        count += 1
        for alias in entry.get("aliases", []) or []:
            provider = str(alias.get("provider", "")).strip()
            external_code = str(alias.get("external_code", "")).strip()
            if not provider or not external_code:
                continue
            upsert_industry_alias(
                provider=provider,
                external_code=external_code,
                industry_id=industry_id,
                valid_from=alias.get("valid_from"),
                valid_to=alias.get("valid_to"),
                db_path=db_path,
            )
    return count


def sync_industry_assets_from_config(
    mapping: Dict[str, Any], db_path: Path | None = None
) -> int:
    """Upsert `industry_asset_map` rows from a parsed `industry_etfs.json`-shaped config.

    Deterministic in the same sense as `sync_industry_master_from_config`.
    """
    entries = mapping.get("mappings", [])
    count = 0
    for entry in entries:
        asset_id = str(entry.get("asset_id", "")).strip()
        industry_id = str(entry.get("industry_id", "")).strip()
        if not asset_id or not industry_id:
            continue
        upsert_industry_asset_map(
            asset_id=asset_id,
            industry_id=industry_id,
            asset_type=entry.get("asset_type"),
            market=entry.get("market"),
            weight=entry.get("weight"),
            valid_from=entry.get("valid_from"),
            valid_to=entry.get("valid_to"),
            db_path=db_path,
        )
        count += 1
    return count


def sync_indicator_catalog_from_config(
    catalog: Dict[str, Any], db_path: Path | None = None
) -> int:
    """Upsert `indicator_catalog` rows from a parsed `industry_indicators.json`-shaped config."""
    entries = catalog.get("indicators", [])
    count = 0
    for entry in entries:
        indicator_id = str(entry.get("indicator_id", "")).strip()
        if not indicator_id:
            continue
        upsert_indicator_catalog(
            indicator_id=indicator_id,
            provider=entry.get("provider"),
            series_id=entry.get("series_id"),
            unit=entry.get("unit"),
            frequency=entry.get("frequency"),
            transform=entry.get("transform"),
            description=entry.get("description"),
            baseline=entry.get("baseline"),
            db_path=db_path,
        )
        count += 1
    return count


def sync_industry_indicator_map_from_config(
    mapping: Dict[str, Any], db_path: Path | None = None
) -> int:
    """Upsert `industry_indicator_map` rows from a parsed `industry_indicators.json`-shaped
    config's `industry_indicator_mappings` list.

    Deterministic in the same sense as `sync_industry_master_from_config`. Callers
    should sync `industry_master` and `indicator_catalog` first — this table has
    foreign keys into both.
    """
    entries = mapping.get("industry_indicator_mappings", [])
    count = 0
    for entry in entries:
        industry_id = str(entry.get("industry_id", "")).strip()
        indicator_id = str(entry.get("indicator_id", "")).strip()
        if not industry_id or not indicator_id:
            continue
        upsert_industry_indicator_map(
            industry_id=industry_id,
            indicator_id=indicator_id,
            direction=entry.get("direction"),
            weight=entry.get("weight"),
            valid_from=entry.get("valid_from"),
            valid_to=entry.get("valid_to"),
            db_path=db_path,
        )
        count += 1
    return count
