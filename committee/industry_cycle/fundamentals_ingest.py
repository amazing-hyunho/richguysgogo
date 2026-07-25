from __future__ import annotations

"""Phase 2: catalog-driven indicator backfill into `indicator_observation`.

Reads `indicator_catalog` entries (from `config/industry_indicators.json` via
`committee.industry_cycle.indicator_catalog`) and, per entry's `provider`,
fetches raw observations from the matching free-source provider
(`committee.tools.fred_industry_provider` / `kosis_industry_provider`),
applies the entry's `transform` (level / yoy_pct / mom_pct), and persists
each resulting point-in-time observation via
`committee.industry_cycle.repository.insert_indicator_observation`.

Failure isolation (task constraint: "API 키가 없거나 공급자가 실패하면 해당
기능을 격리하고 나머지 작업 계속"): one indicator's provider failure /
missing API key / unsupported provider never raises past `ingest_indicator`
-- it returns an `IngestResult(status="skipped"/"failed", ...)` and the batch
runner (`ingest_catalog`) continues to the next indicator, recording a
`data_quality_event` for visibility.

KOSIS `series_id` convention: since KOSIS tables don't have a single
well-known series id the way FRED does, `series_id` for a KOSIS-backed
indicator is the compound string `"orgId:tblId:itmId"` or
`"orgId:tblId:itmId:objL1"` (see `config/industry_indicators.json`).

ECOS is intentionally NOT wired into this generic ingest path yet --
`committee.tools.bok_trade_provider.fetch_korea_export_yoy` only returns a
single "latest" value (not a vintage-aware historical series), so it does
not fit this module's per-observation point-in-time contract. An indicator
declaring `provider: "ECOS"` is isolated with `status="skipped"` and a
`data_quality_event`, same as any other unsupported provider, rather than
half-integrated.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from committee.industry_cycle import repository
from committee.tools import fred_industry_provider, kosis_industry_provider

SUPPORTED_PROVIDERS = ("FRED", "KOSIS")

_PERIODS_PER_YEAR = {
    "monthly": 12,
    "quarterly": 4,
    "annual": 1,
    "weekly": 52,
    "daily": 365,
}

_KOSIS_PRD_SE = {"monthly": "M", "quarterly": "Q", "annual": "Y"}


@dataclass(frozen=True)
class IngestResult:
    indicator_id: str
    status: str  # 'ok' | 'skipped' | 'failed'
    rows_written: int = 0
    reason: Optional[str] = None


def _parse_kosis_series_id(series_id: str) -> Optional[Dict[str, str]]:
    parts = [p.strip() for p in (series_id or "").split(":") if p.strip()]
    if len(parts) < 3:
        return None
    out = {"org_id": parts[0], "tbl_id": parts[1], "item_id": parts[2]}
    if len(parts) >= 4:
        out["obj_l1"] = parts[3]
    return out


def apply_transform(
    rows: List[Dict[str, Any]],
    *,
    transform: str,
    frequency: Optional[str],
) -> List[Dict[str, Any]]:
    """Apply `transform` to a chronologically-ascending list of `{observed_at, value, ...}`.

    `level`: pass through unchanged. `yoy_pct`/`mom_pct`: compute a percent change against
    the value `periods` entries earlier in the SAME list (periods derived from `frequency`);
    entries without enough prior history to compute the transform are dropped entirely, never
    zero-filled (NULL policy). Rows are assumed to already be one-per-period in `observed_at`
    order -- gaps in the source series will shift what "N periods ago" means, which is an
    accepted best-effort limitation for a rule-based v1 (documented, not silently wrong: it
    never fabricates a value, it only ever compares against whatever the Nth-previous row is).
    """
    if transform == "level":
        return list(rows)
    if transform == "mom_pct":
        periods = 1
    elif transform == "yoy_pct":
        periods = _PERIODS_PER_YEAR.get(frequency or "monthly", 12)
    else:
        raise ValueError(f"unknown transform '{transform}'")

    out: List[Dict[str, Any]] = []
    for i in range(periods, len(rows)):
        cur = rows[i]
        prev = rows[i - periods]
        prev_value = prev.get("value")
        if prev_value in (None, 0):
            continue
        pct = (cur["value"] / prev_value - 1.0) * 100.0
        out.append(
            {
                "observed_at": cur["observed_at"],
                "value": pct,
                "published_at": cur.get("published_at"),
            }
        )
    return out


def ingest_indicator(
    entry: Dict[str, Any],
    *,
    observation_start: Optional[str] = None,
    db_path: Path | None = None,
) -> IngestResult:
    """Backfill one `indicator_catalog` entry's observations. Never raises."""
    indicator_id = str(entry.get("indicator_id") or "").strip()
    provider = str(entry.get("provider") or "").strip().upper()
    series_id = entry.get("series_id")
    transform = entry.get("transform") or "level"
    frequency = entry.get("frequency")

    if not indicator_id:
        return IngestResult(indicator_id=indicator_id, status="failed", reason="missing_indicator_id")

    if provider not in SUPPORTED_PROVIDERS:
        return IngestResult(
            indicator_id=indicator_id,
            status="skipped",
            reason=f"unsupported_provider:{provider or 'unknown'}",
        )
    if not series_id or series_id == "TBD":
        return IngestResult(indicator_id=indicator_id, status="skipped", reason="series_id_not_configured")

    try:
        if provider == "FRED":
            rows = fred_industry_provider.fetch_fred_series_initial_releases(
                series_id, observation_start=observation_start
            )
        else:  # KOSIS
            parsed = _parse_kosis_series_id(series_id)
            if parsed is None:
                return IngestResult(
                    indicator_id=indicator_id, status="failed", reason=f"malformed_kosis_series_id:{series_id}"
                )
            rows = kosis_industry_provider.fetch_kosis_series(
                **parsed, prd_se=_KOSIS_PRD_SE.get(frequency or "monthly", "M")
            )

        if rows is None:
            return IngestResult(indicator_id=indicator_id, status="skipped", reason="provider_unavailable")
        if not rows:
            return IngestResult(indicator_id=indicator_id, status="skipped", reason="no_data_returned")

        rows_sorted = sorted(rows, key=lambda r: r["observed_at"])
        transformed = apply_transform(rows_sorted, transform=transform, frequency=frequency)
        if not transformed:
            return IngestResult(
                indicator_id=indicator_id, status="skipped", reason="insufficient_history_for_transform"
            )

        # `indicator_observation.indicator_id` has a FOREIGN KEY into
        # `indicator_catalog`, so the catalog row must exist first. Upserting
        # it here (from the same config entry) means this module works
        # standalone -- callers do not have to separately run
        # `scripts/sync_industry_master.py` before backfilling observations.
        repository.upsert_indicator_catalog(
            indicator_id=indicator_id,
            provider=entry.get("provider"),
            series_id=str(series_id),
            unit=entry.get("unit"),
            frequency=frequency,
            transform=transform,
            description=entry.get("description"),
            baseline=entry.get("baseline"),
            db_path=db_path,
        )

        for row in transformed:
            repository.insert_indicator_observation(
                indicator_id=indicator_id,
                observed_at=row["observed_at"],
                value=row["value"],
                published_at=row.get("published_at"),
                known_at=row.get("published_at"),
                source_ref=str(series_id),
                db_path=db_path,
            )
        return IngestResult(indicator_id=indicator_id, status="ok", rows_written=len(transformed))
    except Exception as exc:  # noqa: BLE001
        return IngestResult(indicator_id=indicator_id, status="failed", reason=str(exc))


def ingest_catalog(
    catalog_entries: List[Dict[str, Any]],
    *,
    observation_start: Optional[str] = None,
    db_path: Path | None = None,
) -> List[IngestResult]:
    """Ingest every catalog entry, isolating failures so one bad indicator never stops the rest."""
    results: List[IngestResult] = []
    for entry in catalog_entries:
        result = ingest_indicator(entry, observation_start=observation_start, db_path=db_path)
        results.append(result)
        if result.status in ("failed", "skipped") and result.reason not in (
            "series_id_not_configured",
        ):
            repository.record_data_quality_event(
                event_type="indicator_ingest_" + result.status,
                provider=str(entry.get("provider") or ""),
                target=result.indicator_id,
                severity="medium" if result.status == "failed" else "low",
                message=result.reason,
                db_path=db_path,
            )
    return results
