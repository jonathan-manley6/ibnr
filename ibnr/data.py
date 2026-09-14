"""A valuation extract: the plan's records as of its valuation date."""
import csv
import json
from datetime import date
from pathlib import Path


def _rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _day(text):
    return date.fromisoformat(text) if text else None


def month_of(text):
    """'2026-03' or '2026-03-14' -> date(2026, 3, 1)."""
    y, m = text[:7].split("-")
    return date(int(y), int(m), 1)


def months_between(a, b):
    """Whole months from the month of `a` to the month of `b`."""
    return (b.year - a.year) * 12 + b.month - a.month


class Extract:
    def __init__(self, data_dir):
        data = Path(data_dir)
        self.dir = data
        info = json.loads((data / "extract.json").read_text(encoding="utf-8"))
        self.plan = info["plan"]
        self.valuation = date.fromisoformat(info["valuation_date"])
        self.paid = []
        for r in _rows(data / "claims-paid.csv"):
            self.paid.append({"incurred_month": month_of(r["incurred_month"]), "paid_date": _day(r["paid_date"]),
                              "category": r["category"], "provider_group": r["provider_group"], "product": r["product"],
                              "claims": int(r["claims"]), "billed_cents": int(r["billed_cents"]),
                              "paid_cents": int(r["paid_cents"])})
        self.inpatient = []
        for r in _rows(data / "claims-inpatient.csv"):
            self.inpatient.append({"claim_id": r["claim_id"], "auth_id": r["auth_id"], "member_id": r["member_id"],
                                   "product": r["product"], "admit_date": _day(r["admit_date"]),
                                   "discharge_date": _day(r["discharge_date"]), "received_date": _day(r["received_date"]),
                                   "paid_date": _day(r["paid_date"]), "billed_cents": int(r["billed_cents"]),
                                   "paid_cents": int(r["paid_cents"])})

    def payments(self, category):
        """(incurred month, paid date, cents) for a category; inpatient claims are incurred at admission."""
        if category == "IP":
            return [(month_of(c["admit_date"].isoformat()), c["paid_date"], c["paid_cents"]) for c in self.inpatient]
        return [(r["incurred_month"], r["paid_date"], r["paid_cents"]) for r in self.paid if r["category"] == category]
