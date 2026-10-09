"""An invented lobbying firm's Q3 2026: staff histories, clients, invoices, time, contacts, and the LD-2 drafts an AI agent wrote.

Every person, client, official title holder and bill number here is invented (bill numbers are illustrative).
Official *roles* are real role types so covered-official status can be reasoned about.
"""

AS_OF = "2026-10-10"
QUARTER = ("2026-07-01", "2026-09-30")

STAFF = {
    "avery": {"name": "Avery Hale", "title": "Principal", "joined": "2025-11-15",
              "history": [{"position": "Professional Staff Member, Senate Armed Services Committee", "office": "Senate Armed Services Committee",
                           "branch": "legislative", "covered": True, "senior": True, "start": "2019-02-01", "end": "2025-10-31"}]},
    "blake": {"name": "Blake Moreno", "title": "Head of Policy", "joined": "2025-02-01",
              "history": [{"position": "Associate Director, White House Office of Science and Technology Policy", "office": "OSTP",
                           "branch": "executive", "covered": True, "senior": True, "start": "2021-03-01", "end": "2024-12-31"}]},
    "casey": {"name": "Casey Lin", "title": "Director", "joined": "2025-06-01", "history": []},
    "devon": {"name": "Devon Price", "title": "Senior Advisor", "joined": "2024-01-08",
              "history": [{"position": "Legislative Assistant, House member office", "office": "House member office",
                           "branch": "legislative", "covered": True, "senior": False, "start": "2001-01-03", "end": "2004-12-31"}]},
    "emery": {"name": "Emery Shah", "title": "Engineer", "joined": "2026-01-05", "history": []},
}

OFFICIALS = {
    "sasc_psm": {"role": "Professional Staff Member, Senate Armed Services Committee", "office": "Senate Armed Services Committee", "house": "SENATE", "agency": None, "covered": True,
                 "basis": "legislative staff (2 U.S.C. § 1602(4))"},
    "house_ld": {"role": "Legislative Director, House member office", "office": "House member office", "house": "HOUSE", "agency": None, "covered": True,
                 "basis": "legislative staff (2 U.S.C. § 1602(4))"},
    "hhs_dep": {"role": "Deputy Secretary of Health and Human Services", "office": "HHS", "house": None, "agency": "Health & Human Services, Dept of (HHS)", "covered": True,
                "basis": "Executive Schedule Level II (2 U.S.C. § 1602(3))"},
    "help_adv": {"role": "Health Policy Advisor, Senate HELP Committee", "office": "Senate HELP Committee", "house": "SENATE", "agency": None, "covered": True,
                 "basis": "legislative staff (2 U.S.C. § 1602(4))"},
    "doc_gs13": {"role": "Program Analyst (GS-13), Department of Commerce", "office": "Commerce", "house": None, "agency": "Commerce, Dept of (DOC)", "covered": False,
                 "basis": "career GS employee, not Executive Schedule / Schedule C / EOP: not covered"},
    "dod_usd": {"role": "Under Secretary of Defense for Acquisition and Sustainment", "office": "DOD", "house": None, "agency": "Defense, Dept of (DOD)", "covered": True,
                "basis": "Executive Schedule Level III (2 U.S.C. § 1602(3))"},
    "nasa_dep": {"role": "Deputy Administrator, NASA", "office": "NASA", "house": None, "agency": "National Aeronautics & Space Administration (NASA)", "covered": True,
                 "basis": "Executive Schedule (2 U.S.C. § 1602(3))"},
    "sen_cos": {"role": "Chief of Staff, Senate member office", "office": "Senate member office", "house": "SENATE", "agency": None, "covered": True,
                "basis": "legislative staff (2 U.S.C. § 1602(4))"},
}

CLIENTS = {
    "northwind": {"name": "Northwind Defense Systems", "retained": "2025-12-01", "ld1_filed": "2026-01-10", "q3_income": [14500, 14500, 14500]},
    "helix": {"name": "Helix Health AI", "retained": "2026-03-01", "ld1_filed": "2026-04-02", "q3_income": [4000, 4000, 4000]},
    "bluegrid": {"name": "Bluegrid GovTech", "retained": "2026-06-01", "ld1_filed": None, "q3_income": [1000, 1000, 1000]},
    "orbital": {"name": "Orbital Imaging Co", "retained": "2026-07-15", "ld1_filed": None, "q3_income": [0, 9000, 9000]},
}

# hours this quarter per (staff, client): lobbying activities vs all services to that client (20% test is per client)
TIME = {("avery", "northwind"): (80, 160), ("casey", "northwind"): (60, 150), ("devon", "northwind"): (30, 100),
        ("blake", "helix"): (70, 150), ("emery", "helix"): (6, 130), ("casey", "bluegrid"): (10, 20),
        ("blake", "orbital"): (40, 90), ("casey", "orbital"): (15, 40)}

CONTACTS = [
    ("2026-07-09", "avery", "northwind", "sasc_psm", "FY2027 NDAA provisions on counter-drone procurement", ["S. 4120"]),
    ("2026-07-22", "casey", "northwind", "dod_usd", "counter-UAS acquisition program schedule", []),
    ("2026-08-04", "casey", "northwind", "house_ld", "NDAA amendment on counter-drone procurement", ["H.R. 5310"]),
    ("2026-08-12", "avery", "northwind", "sasc_psm", "NDAA conference: counter-drone language", ["S. 4120"]),
    ("2026-08-19", "casey", "northwind", "dod_usd", "counter-UAS acquisition program follow-up", []),
    ("2026-09-03", "casey", "northwind", "doc_gs13", "export licensing for drone components", []),
    ("2026-09-15", "devon", "northwind", "house_ld", "NDAA conference report", ["H.R. 5310"]),
    ("2026-09-22", "devon", "northwind", "house_ld", "NDAA conference report follow-up", ["H.R. 5310"]),
    ("2026-07-14", "blake", "helix", "hhs_dep", "oversight of AI clinical decision support", []),
    ("2026-07-30", "blake", "helix", "help_adv", "health AI transparency bill", ["S. 3876"]),
    ("2026-08-20", "emery", "helix", "help_adv", "technical briefing on health AI transparency bill", ["S. 3876"]),
    ("2026-09-09", "emery", "helix", "hhs_dep", "technical briefing on clinical decision support", []),
    ("2026-09-24", "blake", "helix", "sen_cos", "health AI transparency bill", ["S. 3876"]),
    ("2026-08-11", "casey", "bluegrid", "sen_cos", "digital service modernization grants", []),
    ("2026-09-17", "casey", "bluegrid", "house_ld", "digital service modernization grants", []),
    ("2026-07-28", "blake", "orbital", "nasa_dep", "commercial satellite imaging procurement", []),
    ("2026-08-05", "blake", "orbital", "sen_cos", "commercial space imaging appropriations", []),
    ("2026-09-10", "casey", "orbital", "nasa_dep", "commercial satellite imaging procurement", []),
]

# what the drafting agent produced for Q3 (planted mistakes are listed in TRUTH)
DRAFTS = {
    "northwind": {"income": 43500, "income_box": ">=5000", "issues": ["DEF"], "bills": ["S. 4120", "H.R. 5310"], "houses": ["SENATE", "HOUSE"],
                  "agencies": ["Defense, Dept of (DOD)"], "lobbyists": [{"staff": "avery", "covered": ""}, {"staff": "devon", "covered": ""}]},
    "helix": {"income": 10000, "income_box": ">=5000", "issues": ["HCR", "SCI"], "bills": [], "houses": ["SENATE"], "agencies": [],
              "lobbyists": [{"staff": "blake", "covered": "Head of Policy"}]},
}

TRUTH = [
    ("northwind", "COVERED_POSITION_MISSING", "avery"),
    ("northwind", "LOBBYIST_NOT_LISTED", "casey"),
    ("northwind", "INCOME_ROUNDING", None),
    ("northwind", "COOLING_OFF", "avery"),
    ("helix", "CURRENT_TITLE_AS_COVERED", "blake"),
    ("helix", "BILL_MISSING", "S. 3876"),
    ("helix", "AGENCY_MISSING", "Health & Human Services, Dept of (HHS)"),
    ("orbital", "REGISTRATION_LATE", None),
]
