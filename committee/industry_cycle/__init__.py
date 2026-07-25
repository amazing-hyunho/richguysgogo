"""Industry cycle tracker (Phase 0: taxonomy, mapping, point-in-time contract).

This package is intentionally isolated from the existing nightly committee
pipeline (`committee/core`, `committee/agents`). Nothing here is imported by
`run_nightly.py` or `sector_stub.py`; it only reuses the shared SQLite
connection helpers in `committee.core.database`.

Scope (Phase 0 only, see docs/industry_cycle_mvp_design.md section 12):
- internal industry taxonomy (`taxonomy.py`, `models.py`)
- indicator catalog + industry-indicator mapping config loader (`indicator_catalog.py`)
- structural DB tables + safe migrations (added to `committee/core/database.py`)
- point-in-time data contract: known_at / observed_at / published_at / vintage_at
  (`time_contract.py`)
- data quality check foundations (`data_quality.py`)
- config -> DB sync helpers (`repository.py`)

Scoring, state machines, candidate ranking, backtesting, and AI explanation
(Phase 1+) are out of scope and not implemented here.
"""
