"""Lag triangles and completion factors."""
from .data import months_between

MAX_LAG = 18


def triangle(payments, valuation):
    """{incurred month: [cumulative paid at lag 0, 1, ...]} up to the valuation date."""
    by = {}
    for month, paid_date, amount in payments:
        if paid_date > valuation:
            continue
        lag = months_between(month, paid_date)
        by.setdefault(month, {})
        by[month][lag] = by[month].get(lag, 0) + amount
    out = {}
    for month, lags in by.items():
        top = months_between(month, valuation)
        cum, row = 0, []
        for k in range(top + 1):
            cum += lags.get(k, 0)
            row.append(cum)
        out[month] = row
    return out


def completion_factors(tri, months=12, max_lag=MAX_LAG):
    """Volume-weighted lag-to-lag development over the latest `months` incurred months at each lag.

    Returns cf[k], the share of the ultimate paid by lag k; claims are complete at `max_lag`.
    """
    ordered = sorted(tri)
    dev = []
    for k in range(max_lag):
        rows = [tri[m] for m in ordered if len(tri[m]) > k + 1][-months:]
        num = sum(r[k + 1] for r in rows)
        den = sum(r[k] for r in rows)
        dev.append(num / den if den else 1.0)
    cf = [1.0] * (max_lag + 1)
    for k in range(max_lag - 1, -1, -1):
        cf[k] = cf[k + 1] / dev[k]
    return cf
