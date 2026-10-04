"""30-year and 10-year Treasury paths and the 30-year mortgage rate, 2026-2035.

BASE = the market's expected short rates (Kim-Wright, Federal Reserve Board); alternative = the FOMC dots.
1. Expected one-year rates y1, y2, ... from today:
   - market: Kim-Wright splits each zero-coupon yield (1-10 years) into the expected average short rate
     and a term premium (FRED THREEFYn minus THREEFYTPn). The expected one-year rate in year n is
     n*a(n) - (n-1)*a(n-1); beyond year 10 it is held at the year-10 value.
   - dots: today's effective fed funds, straight lines to the September 2026 FOMC median dots at each
     year-end (2026-2029), to the longer-run dot by end-2030, flat after; y1 = the average of that
     monthly path over the next 12 months, y2 the 12 after, and so on.
2. An n-year Treasury in any month = [(1+y1)(1+y2)...(1+yn)]^(1/n) - 1 + a maturity premium
   (n = 30 and n = 10). Each premium is backed out today (the actual yield minus the compounded
   expectation from today) and held constant, so each path starts exactly at today's yield and then
   rolls: as the window moves, the near-term years drop out and more long-run years come in.
3. Mortgage rate = 30-year Treasury + the median of (Freddie Mac PMMS minus 30y Treasury),
   weekly, 1977-2026 (FRED graph MORTGAGE30US minus DGS30).
Writes data/mortgage_rate_path.csv (BASE, annual), data/mortgage_rate_path_monthly.csv, and the dots
alternative as data/mortgage_rate_path_dots.csv / _dots_monthly.csv.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
D = ROOT / "data" / "processed"

# FOMC Summary of Economic Projections, 16-Sep-2026, Table 1, median fed funds (end of year)
# https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20260916.htm
DOTS = {2026: 4.1, 2027: 4.1, 2028: 3.9, 2029: 3.6}
LONGER_RUN = 3.2
LONGER_RUN_BY = 2030          # reached at end-2030, flat after
MATURITIES = {"30y": 30, "10y": 10}
SOURCES = {"market": "Market (Kim-Wright expected short rates)", "dots": "FOMC dots"}


def fred(sid):
    s = pd.read_csv(RAW / f"fred_{sid}.csv", na_values=".")
    s.columns = ["date", sid]
    s["date"] = pd.to_datetime(s["date"])
    return s.dropna().set_index("date")[sid]


def kim_wright(today):
    """Latest Kim-Wright fit on or before today: expected average short rate a(n), n = 1..10, the
    implied expected one-year rate in each year, and the term premium."""
    rows = []
    for n in range(1, 11):
        y, tp = fred(f"THREEFY{n}_recent"), fred(f"THREEFYTP{n}_recent")
        d = min(y.loc[:today].index.max(), tp.loc[:today].index.max())
        rows.append({"n": n, "date": d.date().isoformat(), "fitted_yield": float(y.loc[d]),
                     "term_premium": float(tp.loc[d])})
    k = pd.DataFrame(rows).set_index("n")
    k["expected_avg_short"] = k.fitted_yield - k.term_premium
    a = k.expected_avg_short
    k["expected_1y_rate"] = [a[1]] + [n * a[n] - (n - 1) * a[n - 1] for n in range(2, 11)]
    return k


def expected_ff(today, ff_now, end_year=2075):
    """Monthly expected fed funds from the dots (month-end points) from today's month to end_year."""
    knots = {pd.Timestamp(today): ff_now}
    for y, v in DOTS.items():
        knots[pd.Timestamp(f"{y}-12-31")] = v
    knots[pd.Timestamp(f"{LONGER_RUN_BY}-12-31")] = LONGER_RUN
    months = pd.date_range(pd.Timestamp(today) + pd.offsets.MonthEnd(0), f"{end_year}-12-31", freq="ME")
    kx = np.array([k.value for k in knots]), np.array(list(knots.values()))
    vals = np.interp([m.value for m in months], *kx)     # flat at the longer run past the last knot
    return pd.Series(vals, index=months)


def expected_market(today, kw, end_year=2075):
    """Monthly expected short rate from Kim-Wright: each 12-month block from today at that year's
    expected one-year rate; flat at the year-10 rate after."""
    months = pd.date_range(pd.Timestamp(today) + pd.offsets.MonthEnd(0), f"{end_year}-12-31", freq="ME")
    y1 = kw.expected_1y_rate.values
    return pd.Series([y1[min(i // 12, 9)] for i in range(len(months))], index=months)


def one_year_rates(ff, i, n):
    """y1..yn (%): average expected short rate over each successive 12 months from month i."""
    return np.array([ff.iloc[i + 12 * k:i + 12 * k + 12].mean() for k in range(n)])


def compounded(y):
    """[(1+y1)...(1+yn)]^(1/n) - 1, in %."""
    return 100 * (np.prod(1 + y / 100) ** (1 / len(y)) - 1)


def build(source="market"):
    """Annual and monthly paths for one source of expected short rates. Writes nothing."""
    y_now = {"30y": fred("DGS30"), "10y": fred("DGS10")}
    pmms, dff = fred("MORTGAGE30US"), fred("DFF")
    sp = pd.read_csv(RAW / "fred_MORTGAGE30US_minus_DGS30.csv", na_values=".")
    sp.columns = ["date", "spread"]
    sp = sp.dropna()
    spread_median = float(sp.spread.median())

    today = y_now["30y"].index.max()
    ff_now = float(dff.loc[:today].iloc[-1])
    kw = kim_wright(today)
    ff = expected_market(today, kw) if source == "market" else expected_ff(today, ff_now)
    months = ff.index[ff.index <= "2035-12-31"]
    monthly = pd.DataFrame({"expected_short_rate": ff.loc[months]})
    info = {"source": SOURCES[source], "as_of": today.date().isoformat(), "fed_funds_now": ff_now,
            "kim_wright_date": kw.date.iloc[0], "kim_wright_10y_term_premium": float(kw.at[10, "term_premium"]),
            "kim_wright": kw}
    for tag, n in MATURITIES.items():
        exp = pd.Series([compounded(one_year_rates(ff, i, n)) for i in range(len(months))], index=months)
        now = float(y_now[tag].loc[:today].iloc[-1])
        mp = now - exp.iloc[0]
        monthly[f"expected_{tag}_compounded"] = exp
        monthly[f"maturity_premium_{tag}"] = mp
        monthly[f"treasury_{tag}"] = exp + mp
        info.update({f"treasury_{tag}_now": now, f"expected_{tag}_now": float(exp.iloc[0]),
                     f"maturity_premium_{tag}": mp, f"y1_to_y{n}_now": one_year_rates(ff, 0, n).round(3).tolist(),
                     f"treasury_{tag}_long_run": float(ff.iloc[-1]) + mp})
    monthly["mortgage_30y"] = monthly.treasury_30y + spread_median
    monthly.index.name = "month_end"

    rows = []
    for yr in range(2026, 2036):
        m = monthly[monthly.index.year == yr]
        row = {"year": yr, "expected_short_rate_avg": m.expected_short_rate.mean()}
        if source == "dots":
            row["fed_funds_end_year_dots"] = float(ff.loc[pd.Timestamp(f"{yr}-12-31")])
        for tag in MATURITIES:
            row[f"expected_{tag}_compounded"] = m[f"expected_{tag}_compounded"].mean()
            row[f"maturity_premium_{tag}"] = info[f"maturity_premium_{tag}"]
            row[f"treasury_{tag}"] = m[f"treasury_{tag}"].mean()
        row["spread"] = spread_median
        row["mortgage_30y"] = m.mortgage_30y.mean()
        if yr == 2026:
            # the year so far is history: actual averages to date, model for the rest
            act_m = pmms[pmms.index.year == 2026]
            frac = len(act_m) / 52
            for tag in MATURITIES:
                act = y_now[tag][y_now[tag].index.year == 2026]
                row[f"treasury_{tag}_rest_of_year"] = row[f"treasury_{tag}"]
                row[f"treasury_{tag}"] = frac * act.mean() + (1 - frac) * row[f"treasury_{tag}"]
            row["mortgage_rest_of_year"] = row["mortgage_30y"]
            row["mortgage_30y"] = frac * act_m.mean() + (1 - frac) * row["mortgage_30y"]
            row["expected_short_rate_avg"] = (frac * dff[dff.index.year == 2026].mean()
                                              + (1 - frac) * row["expected_short_rate_avg"])
        rows.append(row)
    annual = pd.DataFrame(rows).set_index("year")
    info.update({"spread_median_1977_2026": spread_median, "spread_mean": float(sp.spread.mean()),
                 "spread_latest": float(sp.spread.iloc[-1]), "spread_n_weeks": len(sp),
                 "spread_first": str(sp.date.iloc[0])})
    return annual, monthly, info


def write():
    """BASE (market) to mortgage_rate_path*.csv, the dots alternative to mortgage_rate_path_dots*.csv."""
    out = {}
    for source, suffix in [("market", ""), ("dots", "_dots")]:
        annual, monthly, info = build(source)
        annual.to_csv(D / f"mortgage_rate_path{suffix}.csv")
        monthly.to_csv(D / f"mortgage_rate_path{suffix}_monthly.csv")
        out[source] = (annual, monthly, info)
    out["market"][2]["kim_wright"].to_csv(D / "kim_wright_expected_rates.csv")
    return out


def curve_slope_check():
    """Cross-check on the long end: curve slope per year of maturity (bps), today vs its 30-year median."""
    d = pd.concat([fred("DGS10"), fred("DGS20"), fred("DGS30")], axis=1).dropna()
    d = d[d.index >= d.index.max() - pd.DateOffset(years=30)]
    s2010 = (d.DGS20 - d.DGS10) / 10 * 100
    s3020 = (d.DGS30 - d.DGS20) / 10 * 100
    return {"20-10 now (bps/yr)": float(s2010.iloc[-1]), "20-10 median": float(s2010.median()),
            "30-20 now (bps/yr)": float(s3020.iloc[-1]), "30-20 median": float(s3020.median()),
            "as_of": d.index.max().date().isoformat()}


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    for source, (annual, monthly, info) in write().items():
        print(f"\n== {info['source']}")
        print({k: (round(float(v), 3) if isinstance(v, float) else v) for k, v in info.items() if k != "kim_wright"})
        print(annual.round(3).to_string())
    print("Curve-slope check:", {k: (round(float(v), 2) if isinstance(v, float) else v)
                                          for k, v in curve_slope_check().items()})
