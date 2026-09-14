import json
from datetime import date

from ibnr.cli import main
from ibnr.triangle import completion_factors, triangle

JAN, FEB, MAR = date(2026, 1, 1), date(2026, 2, 1), date(2026, 3, 1)


def test_triangle_accumulates_paid_by_lag_to_the_valuation_date():
    pays = [(JAN, date(2026, 1, 20), 100), (JAN, date(2026, 2, 10), 50), (FEB, date(2026, 2, 15), 80),
            (JAN, date(2026, 3, 2), 7)]
    assert triangle(pays, date(2026, 2, 28)) == {JAN: [100, 150], FEB: [80]}


def test_completion_factors_chain_the_lag_to_lag_development():
    tri = {JAN: [6000, 9000, 10000], FEB: [6600, 9900], MAR: [7200]}
    cf = completion_factors(tri)
    assert round(cf[2], 6) == 1.0
    assert round(cf[1], 6) == 0.9
    assert round(cf[0], 6) == 0.6


def _write(root, rows):
    (root / "extract.json").write_text(json.dumps({"plan": "Test Plan", "valuation_date": "2026-03-31"}))
    head = "incurred_month,paid_date,category,provider_group,product,claims,billed_cents,paid_cents\n"
    (root / "claims-paid.csv").write_text(head + "".join(f"{m},{d},OP,All,HMO,1,{2 * c},{c}\n" for m, d, c in rows))
    (root / "claims-inpatient.csv").write_text("claim_id,auth_id,member_id,product,facility,admit_date,discharge_date,"
                                               "received_date,paid_date,billed_cents,allowed_cents,paid_cents\n")
    (root / "authorizations.csv").write_text("auth_id,member_id,product,facility,admit_date,discharge_date,"
                                             "level_of_care\n")
    (root / "facility-contracts.csv").write_text("facility,year,level_of_care,contract,rate_cents,outlier_after_days,"
                                                 "outlier_per_diem_cents\n")
    (root / "inventory.csv").write_text("as_of,category,provider_group,incurred_month,claims,billed_cents\n")
    (root / "membership.csv").write_text("month,product,members\n" + "".join(
        f"2026-0{m}-01,HMO,1000\n" for m in (1, 2, 3)))
    (root / "provider-groups.csv").write_text("provider_group,category,electronic_since\nAll,OP,2019-01-01\n")


def test_reserve_command_writes_the_plan_date_and_integer_cents_by_category(tmp_path):
    _write(tmp_path, [("2026-01", "2026-01-28", 6000), ("2026-01", "2026-02-20", 3000), ("2026-01", "2026-03-12", 1000),
                      ("2026-02", "2026-02-26", 6600), ("2026-02", "2026-03-19", 3300), ("2026-03", "2026-03-30", 7200)])
    out = tmp_path / "out.json"
    assert main(["reserve", "--data", str(tmp_path), "--out", str(out)]) == 0
    got = json.loads(out.read_text())
    assert set(got) == {"plan", "valuation_date", "reserve_cents"}
    assert got["plan"] == "Test Plan"
    assert got["valuation_date"] == "2026-03-31"
    cents = got["reserve_cents"]
    assert set(cents) == {"IP", "OP", "PR", "total"}
    assert all(type(v) is int for v in cents.values())
    assert cents["total"] == cents["IP"] + cents["OP"] + cents["PR"]
