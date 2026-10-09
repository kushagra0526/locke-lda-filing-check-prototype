"""Q3 2026 LDA check for an invented lobbying firm → out/report.html

    python demo.py
"""
from __future__ import annotations

import html
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "data"))

import firm  # noqa: E402

from ldacheck.engine import check, field_presence  # noqa: E402
from ldacheck.mutate import run as mutation_run  # noqa: E402


def main() -> int:
    r = check(firm)
    truth = set(firm.TRUTH)
    got = {(x["client"], x["code"], x["subject"]) for x in r["findings"]}
    base = field_presence(firm)
    mut = mutation_run(firm)
    print(f"\n== Q3 2026 filings, as of {firm.AS_OF}: {len(firm.CLIENTS)} clients, {len(firm.STAFF)} staff, {len(firm.CONTACTS)} contacts")
    for x in r["findings"]:
        print(f"  [{x['sev']}] {firm.CLIENTS[x['client']]['name']}: {x['code']}: {x['msg']}\n        ↳ {x['cite']}")
    print(f"\n  planted errors found: {len(truth & got)}/{len(truth)} · false flags: {len(got - truth)} · field-presence check finds: {len(base)}")
    print("  correctly NOT flagged:")
    for cid, e in r["expected"].items():
        if e["exempt"]:
            print(f"    {e['client']}: Q3 income ${e['income']:,} ≤ $3,500, so no registration required")
        for n in e["not_lobbyists"]:
            print(f"    {firm.STAFF[n['staff']]['name']} for {e['client']}: {n['why']}")
        for c in e["not_lobbying_contacts"]:
            print(f"    {c['date']} contact with {c['official']}: {c['why']}")
    print("    Devon Price's House staff job (2001–2004) is more than 20 years before he first lobbied for Northwind, so it is not listed")
    print(f"\n  mutation test: {mut['exact']}/{mut['n']} single-error mutations of correct filings reported exactly ({mut['wrong']} wrong)")
    print("\n== filing calendar")
    for c in r["calendar"]:
        print(f"  {c['due']}  {c['what']}")
    report(r, truth, got, base, mut)
    print("\nreport: out/report.html")
    return 0 if got == truth and mut["wrong"] == 0 else 1


def report(r, truth, got, base, mut):
    e = html.escape
    out = HERE / "out"
    out.mkdir(exist_ok=True)
    frows = "".join(f"<tr><td>{e(firm.CLIENTS[x['client']]['name'])}</td><td class={'w' if x['sev'] == 'WARN' else 'b'}>{x['code']}</td>"
                    f"<td>{e(x['msg'])}</td><td class=c>{e(x['cite'])}</td></tr>" for x in r["findings"])
    neg = []
    for cid, ex in r["expected"].items():
        if ex["exempt"]:
            neg.append(f"{ex['client']}: Q3 income ${ex['income']:,} ≤ $3,500, so no registration required")
        neg += [f"{firm.STAFF[n['staff']]['name']} for {ex['client']}: {n['why']}" for n in ex["not_lobbyists"]]
        neg += [f"{c['date']} contact with {c['official']}: {c['why']}" for c in ex["not_lobbying_contacts"]]
    neg.append("Devon Price: House staff job 2001–2004 is more than 20 years before he first lobbied for Northwind, so it is not listed")
    ex = r["expected"]["northwind"]
    lrows = "".join(f"<li>{e(firm.STAFF[l['staff']]['name'])}: {e('; '.join(l['covered']) or 'no covered position in 20 years')}</li>" for l in ex["lobbyists"])
    crows = "".join(f"<tr><td>{c['due']}</td><td>{e(c['what'])}</td></tr>" for c in r["calendar"])
    mrows = "".join(f"<tr><td>{k}</td><td>{v[0]}</td><td>{v[1]}</td></tr>" for k, v in sorted(mut["by_code"].items()))
    (out / "report.html").write_text(f"""<!doctype html><meta charset=utf-8><title>LDA check</title>
<style>body{{font:14px/1.45 'Segoe UI',system-ui,sans-serif;margin:28px;max-width:1400px;color:#1d1d1f;background:#fafaf8}}h1{{font-size:23px;margin:0}}
h2{{font-size:17px;margin:24px 0 8px}}.sub{{color:#666}}table{{border-collapse:collapse;background:#fff}}td,th{{border-top:1px solid #e5e5e0;padding:5px 10px;text-align:left;vertical-align:top}}
.b{{color:#b91c1c;font-weight:600}}.w{{color:#b45309;font-weight:600}}.c{{color:#555;font-size:12px;max-width:360px}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}
.kpi{{display:flex;gap:24px;margin:10px 0}}.kpi div{{background:#fff;border:1px solid #e5e5e0;border-radius:8px;padding:10px 16px}}.kpi b{{font-size:22px;display:block}}</style>
<h1>LDA filings for Q3 2026: what the activity log says vs what the drafts say</h1>
<div class=sub>Invented firm, staff, clients and bill numbers. Rules from the LDA Guidance (rev. Feb 28, 2025), 2 U.S.C. §§ 1602–1604, 18 U.S.C. § 207. As of {firm.AS_OF}. Not legal advice.</div>
<div class=kpi><div><b>{len(truth & got)}/{len(truth)}</b>planted errors found, {len(got - truth)} false</div><div><b>{len(base)}</b>found by a required-fields check</div>
<div><b>{mut['exact']}/{mut['n']}</b>random single-error mutations reported exactly</div><div><b>Oct 20</b>LD-2 due, no extensions</div></div>
<h2>Findings</h2><table><tr><th>client</th><th>code</th><th>what</th><th>rule</th></tr>{frows}</table>
<div class=grid><div><h2>Correctly not flagged</h2><ul>{''.join(f'<li>{e(x)}</li>' for x in neg)}</ul>
<h2>Northwind LD-2: lobbyists as they must be listed</h2><ul>{lrows}</ul><p>Income ${ex['income']:,} → report <b>${ex['income_rounded']:,}</b> · issues {', '.join(ex['issues'])} · bills {', '.join(ex['bills'])} · {', '.join(ex['houses'])} · {', '.join(ex['agencies'])}</p></div>
<div><h2>Filing calendar</h2><table>{crows}</table><h2>Mutation test by error type</h2><table><tr><th>error</th><th>exact</th><th>wrong</th></tr>{mrows}</table></div></div>
<p class=sub>Unofficial prototype by Kushagra Pratap Singh. Not affiliated with Locke.</p>""", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
