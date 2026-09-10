"""Evidence-backed supply-chain research; deliberately separate from scores.

The catalogue stores product facts and cycle hypotheses separately. Unknown
exposure/lag remains None, and current research must not leak into backtests.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / "config" / "industry_supply_chains.json"


def validate_catalog(catalog: dict, taxonomy: dict) -> None:
    def require(condition: bool, message: str) -> None:
        if not condition:
            raise ValueError(message)

    require(catalog.get("schema_version") == 1, "unsupported supply-chain schema")
    active = {x["industry_id"] for x in taxonomy["industries"] if x["active"]}
    maps = catalog["industries"]
    require(len({x["industry_id"] for x in maps}) == len(maps), "duplicate industry")
    require({x["industry_id"] for x in maps} == active, "active taxonomy coverage mismatch")
    companies = {x["company_id"]: x for x in catalog["companies"]}
    sources = {x["source_id"]: x for x in catalog["sources"]}
    require(len(companies) == len(catalog["companies"]), "duplicate company")
    require(len(sources) == len(catalog["sources"]), "duplicate source")
    for s in sources.values():
        url = urlparse(s["url"])
        require(url.scheme in {"https", "http"} and bool(url.netloc), "unsafe source URL")
        date.fromisoformat(s["accessed_at"])
        for field in ("published_at", "data_as_of"):
            if s[field] is not None:
                date.fromisoformat(s[field])
    for company in companies.values():
        for observation in company.get("research_observations", []):
            require(observation["source_id"] in sources, "unsourced research observation")
            require(bool(observation["scope"]) and bool(observation["period"]) and bool(observation["unit"]), "research observation needs context")
            date.fromisoformat(observation["known_at"])
    relations = catalog["relationships"]
    require(len({x["relationship_id"] for x in relations}) == len(relations), "duplicate relationship")
    for r in relations:
        require(r["company_id"] in companies, "unknown company")
        require(r["industry_id"] in active, "unknown industry")
        require(r["role"] in {"material", "component", "equipment", "service"}, "invalid role")
        require(r["directness"] in {"direct", "indirect"}, "invalid directness")
        require(r["fact_source_ids"] and all(s in sources for s in r["fact_source_ids"]), "missing fact source")
        known = date.fromisoformat(r["known_at"])
        require(all(known >= date.fromisoformat(sources[s]["accessed_at"]) for s in r["fact_source_ids"]), "knowledge predates research")
        exposure = r["revenue_exposure"]
        if exposure["value_pct"] is not None:
            require(0 <= exposure["value_pct"] <= 100, "invalid revenue exposure")
            require(exposure["source_id"] in sources and exposure["period"] and exposure["scope"], "unsourced exposure")
        hypothesis = r["cycle_hypothesis"]
        require(hypothesis["status"] == "unvalidated" and hypothesis["watch_metrics"] and hypothesis["falsifier"], "hypothesis needs verification plan")
        require(r["lag_months"] is None, "measured lag not supported by schema v1")
        for link in r["external_links"]:
            require(link["source_id"] in sources, "unsourced external link")
            require(link["relationship"] in {"customer", "competitor", "upstream", "end_market"}, "invalid external relation")
    priorities = [x["research_order"] for x in maps]
    require(sorted(priorities) == list(range(1, len(maps) + 1)), "research order must be consecutive")


def load_supply_chain_dashboard_data(path: Path = CATALOG_PATH, *, as_of: str | None = None) -> dict:
    catalog = json.loads(path.read_text(encoding="utf-8"))
    taxonomy = json.loads((ROOT / "config" / "industry_taxonomy.json").read_text(encoding="utf-8"))
    validate_catalog(catalog, taxonomy)
    cutoff = date.fromisoformat(as_of) if as_of else date.today()
    catalog["relationships"] = [r for r in catalog["relationships"] if date.fromisoformat(r["known_at"]) <= cutoff]
    for c in catalog["companies"]:
        c["research_observations"] = [o for o in c.get("research_observations", []) if date.fromisoformat(o["known_at"]) <= cutoff]
    names = {x["industry_id"]: x["name_kr"] for x in taxonomy["industries"]}
    for entry in catalog["industries"]:
        rows = [r for r in catalog["relationships"] if r["industry_id"] == entry["industry_id"]]
        entry["name"] = names[entry["industry_id"]]
        entry["company_count"] = len({r["company_id"] for r in rows})
        entry["relationship_count"] = len(rows)
        entry["status"] = "initial_map" if rows else "pending"
    catalog["industries"].sort(key=lambda x: x["research_order"])
    catalog["summary"] = {
        "industry_count": len(catalog["industries"]),
        "mapped_industry_count": sum(x["status"] == "initial_map" for x in catalog["industries"]),
        "company_count": len({r["company_id"] for r in catalog["relationships"]}),
        "relationship_count": len(catalog["relationships"]),
        "quantified_exposure_count": sum(r["revenue_exposure"]["value_pct"] is not None for r in catalog["relationships"]),
        "research_observation_count": sum(len(c.get("research_observations", [])) for c in catalog["companies"]),
    }
    catalog["view_as_of"] = cutoff.isoformat()
    return catalog
