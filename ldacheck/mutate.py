"""Property test: build the correct LD-2s from the activity log, inject one random error, check the engine reports exactly that error."""
from __future__ import annotations

import copy
import random
import types

from .engine import check, derive


def correct_drafts(firm) -> dict:
    out = {}
    for cid, e in derive(firm).items():
        if e["exempt"]:
            continue
        out[cid] = {"income": e["income_rounded"] or 0, "income_box": e["income_box"], "issues": list(e["issues"]), "bills": list(e["bills"]),
                    "houses": list(e["houses"]), "agencies": list(e["agencies"]),
                    "lobbyists": [{"staff": l["staff"], "covered": "; ".join(l["covered"])} for l in e["lobbyists"]]}
    return out


def clean_firm(firm):
    """Same activity, every client registered, correct drafts, nobody inside a cooling-off window."""
    f = types.SimpleNamespace(**{k: copy.deepcopy(getattr(firm, k)) for k in dir(firm) if k.isupper()})
    for c in f.CLIENTS.values():
        c["ld1_filed"] = c["ld1_filed"] or c["retained"]
    for s in f.STAFF.values():
        for h in s["history"]:
            if h["end"] > "2025-06-30":
                h["end"] = "2025-06-30"
    f.DRAFTS = correct_drafts(f)
    return f


def mutations(f, rng):
    """Yield (description, expected code, subject, mutate-fn) applicable to firm f."""
    opts = []
    for cid, dr in f.DRAFTS.items():
        for i, l in enumerate(dr["lobbyists"]):
            opts.append((cid, "LOBBYIST_NOT_LISTED", l["staff"], lambda d, i=i: d["lobbyists"].pop(i)))
            if l["covered"]:
                opts.append((cid, "COVERED_POSITION_MISSING", l["staff"], lambda d, i=i: d["lobbyists"][i].update(covered="")))
                opts.append((cid, "CURRENT_TITLE_AS_COVERED", l["staff"],
                             lambda d, i=i, s=l["staff"]: d["lobbyists"][i].update(covered=f.STAFF[s]["title"])))
        if dr["income_box"] == ">=5000":
            opts.append((cid, "INCOME_ROUNDING", None, lambda d: d.update(income=d["income"] + rng.choice([-3500, 2500, 1000]))))
            opts.append((cid, "INCOME_BOX", None, lambda d: d.update(income_box="<5000")))
        for b in dr["bills"]:
            opts.append((cid, "BILL_MISSING", b, lambda d, b=b: d["bills"].remove(b)))
        for a in dr["agencies"]:
            opts.append((cid, "AGENCY_MISSING", a, lambda d, a=a: d["agencies"].remove(a)))
        for h in dr["houses"]:
            opts.append((cid, "HOUSE_MISSING", h, lambda d, h=h: d["houses"].remove(h)))
        for c in dr["issues"]:
            opts.append((cid, "ISSUE_CODE_MISSING", c, lambda d, c=c: d["issues"].remove(c)))
    return opts


def run(firm, n=300, seed=3):
    rng = random.Random(seed)
    base = clean_firm(firm)
    assert check(base)["findings"] == [], "correct drafts must produce no findings"
    caught = wrong = 0
    by_code = {}
    for _ in range(n):
        f = clean_firm(firm)
        cid, code, subject, fn = rng.choice(mutations(f, rng))
        fn(f.DRAFTS[cid])
        got = {(x["client"], x["code"], x["subject"]) for x in check(f)["findings"]}
        ok = got == {(cid, code, subject)}
        caught += ok
        wrong += not ok
        by_code.setdefault(code, [0, 0])[0 if ok else 1] += 1
    return {"n": n, "exact": caught, "wrong": wrong, "by_code": by_code}
