"""Derive what each client's Q3 filing must say from the activity log, then check the AI-drafted filings against it."""
from __future__ import annotations

from datetime import timedelta

from .rules import (CITE, COOLING_OFF_DAYS, COVERED_LOOKBACK_YEARS, INCOME_THRESHOLD, REGISTER_DAYS, TIME_THRESHOLD, d, issue_codes,
                    ld2_due, ld203_due, round_income)


def derive(firm) -> dict:
    """→ {client: expected filing + facts}, plus firm-level obligations."""
    q0, q1 = firm.QUARTER
    out = {}
    for cid, c in firm.CLIENTS.items():
        contacts = [x for x in firm.CONTACTS if x[2] == cid]
        lobbying = [x for x in contacts if firm.OFFICIALS[x[3]]["covered"]]
        income = sum(c["q3_income"])
        exempt = income <= INCOME_THRESHOLD
        lobbyists, not_lobbyists = [], []
        for sid in sorted({x[1] for x in lobbying}):
            n = sum(1 for x in lobbying if x[1] == sid)
            lob_h, tot_h = firm.TIME.get((sid, cid), (0, 1))
            share = lob_h / tot_h
            if n > 1 and share >= TIME_THRESHOLD:
                first = min(d(x[0]) for x in lobbying if x[1] == sid)
                cutoff = first.replace(year=first.year - COVERED_LOOKBACK_YEARS)
                covered = [h["position"] for h in firm.STAFF[sid]["history"] if h["covered"] and d(h["end"]) >= cutoff]
                lobbyists.append({"staff": sid, "covered": covered, "contacts": n, "time_share": share, "first": str(first)})
            else:
                not_lobbyists.append({"staff": sid, "contacts": n, "time_share": share,
                                      "why": f"{n} contact(s), {share:.0%} of time on this client: not a lobbyist under 2 U.S.C. § 1602(10)"})
        second = sorted(d(x[0]) for x in lobbying)[1] if len(lobbying) > 1 else None
        trigger = min(t for t in (d(c["retained"]), second) if t) if second else d(c["retained"])
        box, rounded = round_income(income)
        out[cid] = {
            "client": c["name"], "income": income, "exempt": exempt, "income_box": box, "income_rounded": rounded,
            "register_by": str(trigger + timedelta(days=REGISTER_DAYS)), "ld1_filed": c["ld1_filed"],
            "issues": sorted(set().union(*[issue_codes(x[4]) for x in lobbying])) if lobbying else [],
            "bills": sorted({b for x in lobbying for b in x[5]}),
            "houses": sorted({firm.OFFICIALS[x[3]]["house"] for x in lobbying if firm.OFFICIALS[x[3]]["house"]}),
            "agencies": sorted({firm.OFFICIALS[x[3]]["agency"] for x in lobbying if firm.OFFICIALS[x[3]]["agency"]}),
            "lobbyists": lobbyists, "not_lobbyists": not_lobbyists,
            "not_lobbying_contacts": [{"date": x[0], "staff": x[1], "official": firm.OFFICIALS[x[3]]["role"], "why": firm.OFFICIALS[x[3]]["basis"]}
                                      for x in contacts if not firm.OFFICIALS[x[3]]["covered"]],
            "ld2_due": str(ld2_due(q1)),
        }
    return out


def check(firm) -> dict:
    exp = derive(firm)
    findings, asof = [], d(firm.AS_OF)

    def f(cid, code, subject, msg, sev="ERROR"):
        findings.append({"client": cid, "code": code, "subject": subject, "msg": msg, "sev": sev, "cite": CITE[code]})

    for cid, e in exp.items():
        if e["exempt"]:
            continue
        if not e["ld1_filed"]:
            late = asof > d(e["register_by"])
            f(cid, "REGISTRATION_LATE" if late else "REGISTRATION_DUE", None,
              f"{e['client']}: Q3 income ${e['income']:,} > ${INCOME_THRESHOLD:,}; LD-1 was due {e['register_by']} and is not filed"
              + (f". File now, then the Q3 LD-2 by {e['ld2_due']}" if late else ""))
            continue
        dr = firm.DRAFTS.get(cid)
        if not dr:
            f(cid, "REGISTRATION_LATE", None, f"{e['client']}: registered, but no Q3 LD-2 draft (due {e['ld2_due']}; no extensions)")
            continue
        # income
        if dr["income_box"] != e["income_box"]:
            f(cid, "INCOME_BOX", None, f"box {dr['income_box']} but income is ${e['income']:,}")
        elif e["income_rounded"] is not None and dr["income"] != e["income_rounded"]:
            f(cid, "INCOME_ROUNDING", None, f"draft reports ${dr['income']:,}; ${e['income']:,} rounds to ${e['income_rounded']:,}")
        # lobbyists and covered positions
        listed = {l["staff"]: l for l in dr["lobbyists"]}
        for l in e["lobbyists"]:
            sid, name = l["staff"], firm.STAFF[l["staff"]]["name"]
            if sid not in listed:
                f(cid, "LOBBYIST_NOT_LISTED", sid, f"{name} made {l['contacts']} lobbying contacts and spent {l['time_share']:.0%} of time on this client but is not listed")
                continue
            got = (listed[sid]["covered"] or "").strip()
            if got and got == firm.STAFF[sid]["title"]:
                f(cid, "CURRENT_TITLE_AS_COVERED", sid, f"{name}: covered position shows current title “{got}”; should be: {'; '.join(l['covered']) or 'none'}")
            elif l["covered"] and not got:
                f(cid, "COVERED_POSITION_MISSING", sid, f"{name}: covered position blank; held “{l['covered'][0]}” within 20 years of first lobbying for this client ({l['first']})")
        # issues, bills, houses, agencies
        for code in sorted(set(e["issues"]) - set(dr["issues"])):
            f(cid, "ISSUE_CODE_MISSING", code, f"contacts were about {code} issues but the code is missing")
        for b in sorted(set(e["bills"]) - set(dr["bills"])):
            dates = [x[0] for x in firm.CONTACTS if x[2] == cid and b in x[5] and firm.OFFICIALS[x[3]]["covered"]]
            f(cid, "BILL_MISSING", b, f"{b} was raised in lobbying contacts on {', '.join(dates)} but is not in specific issues")
        for h in sorted(set(e["houses"]) - set(dr["houses"])):
            f(cid, "HOUSE_MISSING", h, f"{h} was contacted but is not listed")
        for a in sorted(set(e["agencies"]) - set(dr["agencies"])):
            f(cid, "AGENCY_MISSING", a, f"{a} was contacted (covered official) but is not listed")

    # cooling-off: staff contacting their former office within a year of leaving (warning: confirm "senior" status)
    for x in firm.CONTACTS:
        o = firm.OFFICIALS[x[3]]
        for h in firm.STAFF[x[1]]["history"]:
            if h["senior"] and h["office"] == o["office"] and 0 <= (d(x[0]) - d(h["end"])).days < COOLING_OFF_DAYS:
                if not any(z["code"] == "COOLING_OFF" and z["subject"] == x[1] and z["client"] == x[2] for z in findings):
                    dates = [y[0] for y in firm.CONTACTS if y[1] == x[1] and firm.OFFICIALS[y[3]]["office"] == h["office"]
                             and (d(y[0]) - d(h["end"])).days < COOLING_OFF_DAYS]
                    f(x[2], "COOLING_OFF", x[1], f"{firm.STAFF[x[1]]['name']} left {h['office']} on {h['end']} and contacted it on {', '.join(dates)}", sev="WARN")

    lobbyists = sorted({l["staff"] for e in exp.values() if not e["exempt"] for l in e["lobbyists"]})
    calendar = [{"what": f"LD-2 Q3 2026 ({e['client']})", "due": e["ld2_due"]} for e in exp.values() if not e["exempt"]] + \
               [{"what": f"LD-203 H2 2026 ({firm.STAFF[s]['name']} + registrant)", "due": str(ld203_due("2026-12-31"))} for s in lobbyists]
    return {"expected": exp, "findings": findings, "calendar": calendar}


def field_presence(firm) -> list[str]:
    """Baseline: the kind of check a form validator does: are the required fields filled?"""
    out = []
    for cid, dr in firm.DRAFTS.items():
        for k in ("income_box", "issues", "houses", "lobbyists"):
            if not dr.get(k):
                out.append(f"{cid}: {k} empty")
    return out
