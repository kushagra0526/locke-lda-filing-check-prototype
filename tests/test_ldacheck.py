import copy
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "data"))

import firm  # noqa: E402

from ldacheck.engine import check, derive, field_presence  # noqa: E402
from ldacheck.mutate import clean_firm, run  # noqa: E402
from ldacheck.rules import ld2_due, ld203_due, next_business_day, round_income  # noqa: E402


def test_planted_found_exactly_and_baseline_blind():
    got = {(x["client"], x["code"], x["subject"]) for x in check(firm)["findings"]}
    assert got == set(firm.TRUTH)
    assert field_presence(firm) == []


def test_hard_negatives():
    e = derive(firm)
    assert e["bluegrid"]["exempt"]
    assert [n["staff"] for n in e["helix"]["not_lobbyists"]] == ["emery"]
    assert "Commerce, Dept of (DOC)" not in e["northwind"]["agencies"]
    devon = next(l for l in e["northwind"]["lobbyists"] if l["staff"] == "devon")
    assert devon["covered"] == []


def test_rounding_and_box():
    assert round_income(4999) == ("<5000", None)
    assert round_income(43500) == (">=5000", 40000)
    assert round_income(45000) == (">=5000", 50000)
    assert round_income(12000) == (">=5000", 10000)


def test_due_dates_roll_to_business_days():
    assert ld2_due("2026-09-30") == date(2026, 10, 20)
    assert ld203_due("2026-12-31") == date(2027, 2, 1)            # Jan 30, 2027 is a Saturday
    assert next_business_day(date(2026, 1, 19)) == date(2026, 1, 20)  # MLK Day
    assert ld2_due("2026-03-31") == date(2026, 4, 20)


def test_registration_clock_uses_retention_date():
    e = derive(firm)
    assert e["orbital"]["register_by"] == "2026-08-29"


def test_cooling_off_window():
    import types
    f = types.SimpleNamespace(**{k: copy.deepcopy(getattr(firm, k)) for k in dir(firm) if k.isupper()})
    f.STAFF["avery"]["history"][0]["end"] = "2025-06-30"
    assert not any(x["code"] == "COOLING_OFF" for x in check(f)["findings"])


def test_correct_drafts_clean_and_mutations_exact():
    assert check(clean_firm(firm))["findings"] == []
    r = run(firm, n=150, seed=9)
    assert r["wrong"] == 0
