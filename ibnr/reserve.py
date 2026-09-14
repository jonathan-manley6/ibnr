"""The reserve by the memo's method: completion factors applied to every incurred month."""
from .data import months_between
from .triangle import MAX_LAG, completion_factors, triangle

CATEGORIES = ("IP", "OP", "PR")


def category_reserve(extract, category):
    tri = triangle(extract.payments(category), extract.valuation)
    cf = completion_factors(tri)
    total = 0
    for month, row in tri.items():
        lag = months_between(month, extract.valuation)
        if lag >= MAX_LAG:
            continue
        paid = row[-1]
        total += paid / cf[lag] - paid
    return round(total)


def reserve(extract):
    by = {c: category_reserve(extract, c) for c in CATEGORIES}
    return {"plan": extract.plan, "valuation_date": extract.valuation.isoformat(),
            "reserve_cents": dict(by, total=sum(by.values()))}
