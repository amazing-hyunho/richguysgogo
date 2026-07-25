from __future__ import annotations

"""Phase 0 structural-table sync CLI (dry-run by default).

Loads `config/industry_taxonomy.json`, `config/industry_etfs.json`, and
`config/industry_indicators.json`, and syncs them into `industry_master`/
`industry_alias`, `industry_asset_map`, `indicator_catalog`, and
`industry_indicator_map` respectively
(`committee.industry_cycle.repository.sync_*_from_config`). Deterministic:
running this twice with the same config produces the same rows (design doc
section 12, Phase 0 completion criterion: "동일 입력으로 같은 산업·지표
매핑을 재현할 수 있다").

This was part of the module list proposed in the design doc (section 10)
but had not yet been turned into a runnable script -- `run_industry_price_factors.py`
and `run_industry_fundamentals_factors.py` (Phase 1-B/2) already call the same
sync functions inline before computing, so running this script by hand is
optional, not required; it exists for explicit/manual re-sync and for
inspecting what would change before committing to it.
"""

import argparse
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.industry_cycle import indicator_catalog, repository, taxonomy

_ETF_CONFIG_DEFAULT = str(ROOT_DIR / "config" / "industry_etfs.json")

DB_PATH = ROOT_DIR / "data" / "investment.db"


def _load_json(path: Path) -> dict:
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync industry_taxonomy/industry_etfs/industry_indicators config into structural DB tables."
    )
    parser.add_argument("--taxonomy", default=str(taxonomy.TAXONOMY_PATH))
    parser.add_argument("--etfs", default=_ETF_CONFIG_DEFAULT)
    parser.add_argument("--indicators", default=str(indicator_catalog.INDICATOR_CONFIG_PATH))
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually write to the DB. Without this flag, only prints what would be synced.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    taxonomy_config = taxonomy.load_taxonomy(Path(args.taxonomy))
    indicators_config = indicator_catalog.load_indicator_config(Path(args.indicators))

    etfs_path = Path(args.etfs)
    etfs_config = _load_json(etfs_path) if etfs_path.exists() else {"mappings": []}

    n_industries = len(taxonomy_config.get("industries", []))
    n_etf_mappings = len(etfs_config.get("mappings", []))
    n_indicators = len(indicators_config.get("indicators", []))
    n_indicator_mappings = len(indicators_config.get("industry_indicator_mappings", []))

    print(
        f"sync_industry_master_plan industries={n_industries} etf_mappings={n_etf_mappings} "
        f"indicators={n_indicators} indicator_mappings={n_indicator_mappings} execute={args.execute}"
    )

    if not args.execute:
        print("sync_industry_master_dry_run_only (pass --execute to actually write)")
        return

    synced_industries = repository.sync_industry_master_from_config(taxonomy_config, db_path=DB_PATH)
    synced_assets = repository.sync_industry_assets_from_config(etfs_config, db_path=DB_PATH)
    synced_indicators = repository.sync_indicator_catalog_from_config(indicators_config, db_path=DB_PATH)
    synced_indicator_map = repository.sync_industry_indicator_map_from_config(indicators_config, db_path=DB_PATH)

    print(
        f"sync_industry_master_done industries={synced_industries} etf_mappings={synced_assets} "
        f"indicators={synced_indicators} indicator_mappings={synced_indicator_map}"
    )


if __name__ == "__main__":
    main()
