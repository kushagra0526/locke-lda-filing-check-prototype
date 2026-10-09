"""LDA rules as code. Citations: Lobbying Disclosure Act Guidance (Secretary of the Senate / Clerk of the House, rev. Feb 28, 2025),
2 U.S.C. §§ 1602–1604, and 18 U.S.C. § 207 for post-employment restrictions. Not legal advice."""
from __future__ import annotations

import re
from datetime import date, timedelta

INCOME_THRESHOLD = 3500          # lobbying firm, per client per quarter (Guidance § 4, threshold effective Jan 1, 2025)
TIME_THRESHOLD = 0.20            # lobbyist: >1 contact and ≥20% of time on that client (2 U.S.C. § 1602(10))
REGISTER_DAYS = 45               # LD-1 within 45 days (Guidance § 4)
LD2_DAYS = 20                    # LD-2 within 20 days after quarter end, next business day (Guidance § 6)
COVERED_LOOKBACK_YEARS = 20      # covered positions within 20 years before first acting as lobbyist for the client (Guidance § 5)
COOLING_OFF_DAYS = 365           # 18 U.S.C. § 207(e): one-year restriction for former senior congressional staff (verify status)

CITE = {
    "REGISTRATION_LATE": "Guidance § 4: register within 45 days of retention or the second contact",
    "COVERED_POSITION_MISSING": "Guidance § 5: list covered positions held in the 20 years before first acting as lobbyist for this client",
    "CURRENT_TITLE_AS_COVERED": "Guidance § 5: \"not appropriate to list an individual lobbyist's current position\" as the covered position",
    "LOBBYIST_NOT_LISTED": "2 U.S.C. § 1602(10) + Guidance § 5: list each employee who acted as a lobbyist for the client",
    "INCOME_ROUNDING": "Guidance § 6: income of $5,000 or more is a good-faith estimate rounded to the nearest $10,000",
    "INCOME_BOX": "Guidance § 6: check \"less than $5,000\" or \"$5,000 or more\"",
    "BILL_MISSING": "LD-2 line 16: specific lobbying issues, including bill numbers",
    "AGENCY_MISSING": "LD-2 line 17: Houses of Congress and Federal agencies contacted",
    "HOUSE_MISSING": "LD-2 line 17: Houses of Congress and Federal agencies contacted",
    "ISSUE_CODE_MISSING": "LD-2 line 15: general issue area code for each issue lobbied",
    "COOLING_OFF": "18 U.S.C. § 207(e): 1-year contact ban for former senior congressional staff; scope depends on chamber and role "
                   "(for senior Senate staff it covers the whole Senate). This check only catches contacts with the former office; confirm with counsel",
}

ISSUE_CODES = {"DEF": r"\b(defense|ndaa|counter-(?:uas|drone)|military|acquisition program)\b",
               "HCR": r"\b(health|clinical|medicare|medicaid)\b",
               "SCI": r"\b(ai|artificial intelligence|research)\b",
               "AER": r"\b(space|satellite|nasa)\b",
               "BUD": r"\b(appropriations|budget)\b",
               "GOV": r"\b(digital service|modernization grants?)\b"}


def d(s: str) -> date:
    return date.fromisoformat(s)


def _nth_weekday(y, m, weekday, n):
    first = date(y, m, 1)
    day = first + timedelta(days=(weekday - first.weekday()) % 7)
    return day + timedelta(weeks=n - 1)


def _last_weekday(y, m, weekday):
    nxt = date(y + (m == 12), m % 12 + 1, 1)
    last = nxt - timedelta(days=1)
    return last - timedelta(days=(last.weekday() - weekday) % 7)


def federal_holidays(y: int) -> set[date]:
    def observed(x):
        return x - timedelta(days=1) if x.weekday() == 5 else x + timedelta(days=1) if x.weekday() == 6 else x
    return {observed(date(y, 1, 1)), _nth_weekday(y, 1, 0, 3), _nth_weekday(y, 2, 0, 3), _last_weekday(y, 5, 0),
            observed(date(y, 6, 19)), observed(date(y, 7, 4)), _nth_weekday(y, 9, 0, 1), _nth_weekday(y, 10, 0, 2),
            observed(date(y, 11, 11)), _nth_weekday(y, 11, 3, 4), observed(date(y, 12, 25))}


def next_business_day(x: date) -> date:
    while x.weekday() >= 5 or x in federal_holidays(x.year):
        x += timedelta(days=1)
    return x


def ld2_due(quarter_end: str) -> date:
    return next_business_day(d(quarter_end) + timedelta(days=LD2_DAYS))


def ld203_due(half_end: str) -> date:
    e = d(half_end)
    return next_business_day(date(e.year, 7, 30) if e.month == 6 else date(e.year + 1, 1, 30))


def round_income(x: float) -> tuple[str, int | None]:
    if x < 5000:
        return "<5000", None
    return ">=5000", int((x + 5000) // 10000 * 10000)


def issue_codes(text: str) -> set[str]:
    t = text.lower()
    return {c for c, p in ISSUE_CODES.items() if re.search(p, t)}
