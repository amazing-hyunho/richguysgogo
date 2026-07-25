from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.core.database import connect
from committee.industry_cycle import price_repository
from committee.industry_cycle.price_models import AssetPriceRecord


def _record(**overrides) -> AssetPriceRecord:
    defaults = dict(
        asset_id="SOXX",
        market="US",
        currency="USD",
        trade_date="2026-07-01",
        open_price=100.0,
        high_price=105.0,
        low_price=99.0,
        close_price=103.0,
        adj_close_price=103.0,
        volume=1_000_000.0,
        adjustment_status="adjusted",
        source="yahoo_chart",
        source_ref="SOXX",
        available_at="2026-07-01T23:59:59+00:00",
        collected_at="2026-07-01T21:05:00+00:00",
    )
    defaults.update(overrides)
    return AssetPriceRecord(**defaults)


class UpsertDedupTests(unittest.TestCase):
    def test_recollecting_same_day_does_not_duplicate(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            for _ in range(3):
                price_repository.upsert_asset_price_daily(_record(), db_path=db_path)
            rows = price_repository.get_prices("SOXX", db_path=db_path)
            self.assertEqual(len(rows), 1)
            self.assertEqual(price_repository.count_prices("SOXX", db_path=db_path), 1)

    def test_recollecting_with_updated_value_overwrites_in_place(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            price_repository.upsert_asset_price_daily(_record(close_price=103.0), db_path=db_path)
            price_repository.upsert_asset_price_daily(_record(close_price=104.5), db_path=db_path)
            rows = price_repository.get_prices("SOXX", db_path=db_path)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["close_price"], 104.5)

    def test_bulk_upsert_dedups_across_records(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            records = [
                _record(trade_date="2026-07-01"),
                _record(trade_date="2026-07-02"),
                _record(trade_date="2026-07-01"),  # duplicate key within the same batch
            ]
            written = price_repository.bulk_upsert_asset_price_daily(records, db_path=db_path)
            self.assertEqual(written, 3)  # all attempted, but...
            rows = price_repository.get_prices("SOXX", db_path=db_path)
            self.assertEqual(len(rows), 2)  # ...only 2 distinct trade_dates stored

    def test_missing_price_stays_null_not_zero(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            price_repository.upsert_asset_price_daily(
                _record(close_price=None, adj_close_price=None, volume=None), db_path=db_path
            )
            rows = price_repository.get_prices("SOXX", db_path=db_path)
            self.assertIsNone(rows[0]["close_price"])
            self.assertIsNone(rows[0]["adj_close_price"])
            self.assertIsNone(rows[0]["volume"])

    def test_missing_required_field_raises(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            with self.assertRaises(ValueError):
                price_repository.upsert_asset_price_daily(
                    {"asset_id": "", "market": "US", "currency": "USD", "trade_date": "2026-07-01"},
                    db_path=db_path,
                )

    def test_missing_available_at_defaults_to_end_of_trade_date(self) -> None:
        """A caller that forgets to pass `available_at` must not end up with
        a permanently-unqueryable row (NULL fails `is_known_by` forever)."""
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            price_repository.upsert_asset_price_daily(_record(available_at=None), db_path=db_path)
            rows = price_repository.get_prices("SOXX", db_path=db_path)
            self.assertEqual(rows[0]["available_at"], "2026-07-01T23:59:59+00:00")


class AsOfQueryTests(unittest.TestCase):
    def test_future_available_at_is_excluded(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            price_repository.upsert_asset_price_daily(
                _record(trade_date="2026-07-01", available_at="2026-07-01T23:59:59+00:00"), db_path=db_path
            )
            price_repository.upsert_asset_price_daily(
                _record(trade_date="2026-07-02", available_at="2026-08-01T00:00:00+00:00"), db_path=db_path
            )
            visible = price_repository.get_prices_as_of("SOXX", "2026-07-15", db_path=db_path)
            self.assertEqual(len(visible), 1)
            self.assertEqual(visible[0]["trade_date"], "2026-07-01")

    def test_future_trade_date_is_excluded_even_if_available_at_is_backdated(self) -> None:
        """Defends against a malformed/late-arriving row whose available_at
        was (incorrectly) backdated before its own trade_date — the explicit
        `trade_date <= as_of` guard must still block it."""
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            price_repository.upsert_asset_price_daily(
                _record(trade_date="2026-12-31", available_at="2026-01-01T00:00:00+00:00"), db_path=db_path
            )
            visible = price_repository.get_prices_as_of("SOXX", "2026-07-15", db_path=db_path)
            self.assertEqual(visible, [])

    def test_future_trade_date_is_excluded(self) -> None:
        """A trade_date after `as_of` must never be returned, regardless of
        available_at (required test: '미래 거래일 가격은 조회 불가')."""
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            price_repository.upsert_asset_price_daily(
                _record(
                    trade_date="2026-08-15",
                    available_at="2026-08-15T23:59:59+00:00",
                    collected_at="2026-08-16T00:00:00+00:00",
                ),
                db_path=db_path,
            )
            visible = price_repository.get_prices_as_of("SOXX", "2026-08-14", db_path=db_path)
            self.assertEqual(visible, [])

    def test_rows_without_available_at_are_not_knowable(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            price_repository.upsert_asset_price_daily(_record(trade_date="2026-07-01"), db_path=db_path)
            # Force available_at to NULL directly (upsert always defaults it).
            with connect(db_path) as conn:
                conn.execute("UPDATE asset_price_daily SET available_at = NULL WHERE asset_id = 'SOXX';")
            visible = price_repository.get_prices_as_of("SOXX", "2099-01-01", db_path=db_path)
            self.assertEqual(visible, [])

    def test_start_end_range_filter(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            for d in ("2026-06-01", "2026-07-01", "2026-08-01"):
                price_repository.upsert_asset_price_daily(
                    _record(trade_date=d, available_at=f"{d}T23:59:59+00:00"), db_path=db_path
                )
            rows = price_repository.get_prices("SOXX", start="2026-06-15", end="2026-07-15", db_path=db_path)
            self.assertEqual([r["trade_date"] for r in rows], ["2026-07-01"])

    def test_2015_price_backfilled_in_2026_is_visible_to_2020_as_of_query(self) -> None:
        """Core bug fix regression test: backfilling old prices "today" must
        not make them invisible to a historical as-of backtest, because
        `available_at` is derived from `trade_date`, not from
        `collected_at`/fetch wall-clock."""
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            price_repository.upsert_asset_price_daily(
                _record(
                    trade_date="2015-03-02",
                    available_at="2015-03-02T23:59:59+00:00",
                    collected_at="2026-07-25T10:00:00+00:00",  # backfilled "today", years later
                ),
                db_path=db_path,
            )
            visible = price_repository.get_prices_as_of("SOXX", "2020-01-01", db_path=db_path)
            self.assertEqual(len(visible), 1)
            self.assertEqual(visible[0]["trade_date"], "2015-03-02")
            self.assertEqual(visible[0]["collected_at"], "2026-07-25T10:00:00+00:00")

    def test_recollection_does_not_erase_past_as_of_visibility(self) -> None:
        """Re-collecting the same (asset_id, trade_date) — e.g. a nightly
        re-sync — must not push `available_at` forward and must not hide the
        row from an as-of query that could already see it."""
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            price_repository.upsert_asset_price_daily(
                _record(
                    trade_date="2018-05-10",
                    available_at="2018-05-10T23:59:59+00:00",
                    collected_at="2026-01-01T00:00:00+00:00",
                ),
                db_path=db_path,
            )
            before = price_repository.get_prices_as_of("SOXX", "2019-01-01", db_path=db_path)
            self.assertEqual(len(before), 1)

            # Re-collect the same day much later, with a naive caller that
            # (incorrectly) tries to pass today's date as available_at too.
            price_repository.upsert_asset_price_daily(
                _record(
                    trade_date="2018-05-10",
                    close_price=999.0,
                    available_at="2026-07-25T23:59:59+00:00",  # attempted overwrite; must be ignored
                    collected_at="2026-07-25T09:00:00+00:00",
                ),
                db_path=db_path,
            )
            after = price_repository.get_prices_as_of("SOXX", "2019-01-01", db_path=db_path)
            self.assertEqual(len(after), 1)
            self.assertEqual(after[0]["trade_date"], "2018-05-10")
            self.assertEqual(after[0]["available_at"], "2018-05-10T23:59:59+00:00")
            # The OHLC value itself did refresh...
            self.assertEqual(after[0]["close_price"], 999.0)

    def test_collected_at_refreshes_on_recollection(self) -> None:
        """`collected_at` is audit/freshness metadata and must update freely
        on re-collection (unlike `available_at`)."""
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            price_repository.upsert_asset_price_daily(
                _record(trade_date="2018-05-10", collected_at="2026-01-01T00:00:00+00:00"), db_path=db_path
            )
            price_repository.upsert_asset_price_daily(
                _record(trade_date="2018-05-10", collected_at="2026-07-25T09:00:00+00:00"), db_path=db_path
            )
            rows = price_repository.get_prices("SOXX", db_path=db_path)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["collected_at"], "2026-07-25T09:00:00+00:00")

    def test_bare_date_and_iso_datetime_as_of_are_handled_consistently(self) -> None:
        """`as_of` and `available_at` may each be a bare date or a full ISO
        datetime; gating must compare at day-level precision either way."""
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            price_repository.upsert_asset_price_daily(
                _record(trade_date="2020-06-15", available_at="2020-06-15T23:59:59+00:00"), db_path=db_path
            )

            # bare-date as_of, ISO-datetime available_at
            visible_bare = price_repository.get_prices_as_of("SOXX", "2020-06-15", db_path=db_path)
            self.assertEqual(len(visible_bare), 1)

            # ISO-datetime as_of, same day
            visible_iso = price_repository.get_prices_as_of(
                "SOXX", "2020-06-15T00:00:01+00:00", db_path=db_path
            )
            self.assertEqual(len(visible_iso), 1)

            # one calendar day earlier must exclude it in both forms
            self.assertEqual(price_repository.get_prices_as_of("SOXX", "2020-06-14", db_path=db_path), [])
            self.assertEqual(
                price_repository.get_prices_as_of("SOXX", "2020-06-14T23:59:59+00:00", db_path=db_path), []
            )


class ListAndCountTests(unittest.TestCase):
    def test_list_price_assets(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            price_repository.upsert_asset_price_daily(_record(asset_id="SOXX"), db_path=db_path)
            price_repository.upsert_asset_price_daily(
                _record(asset_id="091160.KS", market="KR", currency="KRW"), db_path=db_path
            )
            self.assertEqual(price_repository.list_price_assets(db_path=db_path), ["091160.KS", "SOXX"])


if __name__ == "__main__":
    unittest.main()
