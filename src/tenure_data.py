"""Inputs for the owner-occupied-homes forecast, by age of householder.

Writes four tidy CSVs into data/processed/:
  tenure_by_age.csv          households and owner households by age, 1982-2025 (Census CPS/HVS Table 12, 12a)
  affordability_annual.csv   NAR affordability components, mortgage rates, unemployment, house prices, CPI
  population_by_age_proj.csv Census 2023 national population projections by age group, 2022-2040
  nmdb_annual.csv            FHFA NMDB average interest rate on outstanding mortgages, 2013+ (lock-in test only)

Age groups follow the JCHS tenure projections (ten-year bands, under 25 to 75 and over), so the
forecast can be set beside JCHS's published scenarios group by group.
"""
import csv
import re
from pathlib import Path

import numpy as np
import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"

GROUPS = ["<25", "25-34", "35-44", "45-54", "55-64", "65-74", "75+"]
BAND_TO_GROUP = {
    "Less than 25 years": "<25", "25 to 29 years": "25-34", "30 to 34 years": "25-34",
    "35 to 39 years": "35-44", "40 to 44 years": "35-44", "45 to 49 years": "45-54",
    "50 to 54 years": "45-54", "55 to 59 years": "55-64", "60 to 64 years": "55-64",
    "65 to 69 years": "65-74", "70 to 74 years": "65-74", "75 years and over": "75+",
}
T12_URL = "https://www.census.gov/housing/hvs/data/histtab12.xlsx"
T12A_URL = "https://www.census.gov/housing/hvs/data/hist_tab_12a_v2025.xlsx"


def _year(label):
    """'19821' -> (1982, 'orig'); '1993r1' -> (1993, 'rev'); '2025*' -> (2025, 'orig')."""
    s = str(label).strip()
    m = re.match(r"^((?:19|20)\d\d)(r)?", s)
    if not m:
        return None
    return int(m.group(1)), ("rev" if m.group(2) else "orig")


def parse_table12(path, table):
    """Both tables are blocks: a header row of year labels (one per Total/Owner column pair),
    then 'United States, total' and twelve '...N to M years' rows."""
    ws = openpyxl.load_workbook(path, data_only=True, read_only=True).worksheets[0]
    rows = [list(r) for r in ws.iter_rows(values_only=True)]
    out, cols = [], None
    for row in rows:
        a = row[0]
        years = [(j, _year(c)) for j, c in enumerate(row[1:], start=1) if c is not None and _year(c)]
        if years and len(years) >= 2:
            cols = years  # year label sits over the Total column; Owner is the next column
            continue
        if cols is None or not isinstance(a, str):
            continue
        band = re.sub(r"[.\s]+$", "", a.strip().lstrip(".").strip())
        band = re.sub(r"\.{2,}.*$", "", band).strip()
        if band not in BAND_TO_GROUP:
            continue
        for j, (yr, vint) in cols:
            tot, own = row[j], row[j + 1] if j + 1 < len(row) else None
            if isinstance(tot, (int, float)) and isinstance(own, (int, float)):
                out.append({"table": table, "year": yr, "vintage": vint, "band": band,
                            "group": BAND_TO_GROUP[band], "households_k": float(tot), "owners_k": float(own)})
    return pd.DataFrame(out)


def tenure_by_age():
    t12 = parse_table12(RAW / "census_hvs_histtab12.xlsx", "T12")
    t12a = parse_table12(RAW / "census_hvs_hist_tab_12a_v2025.xlsx", "T12a")
    raw = pd.concat([t12, t12a], ignore_index=True)

    def splice(frame, key):
        # Modelling series, one row per year and age:
        #   1982-1992 Table 12 on 1980-census controls; 1993-1999 Table 12 revised on 1990-census
        #   controls; 2000-2025 Table 12a, restated on today's (Vintage 2010/2020/2025) controls.
        pick = pd.concat([
            frame[(frame.table == "T12") & (frame.year <= 1992) & (frame.vintage == "orig")],
            frame[(frame.table == "T12") & (frame.year == 1993) & (frame.vintage == "rev")],
            frame[(frame.table == "T12") & (frame.year.between(1994, 1999))],
            frame[(frame.table == "T12a") & (frame.year >= 2000)],
        ])
        assert pick.groupby(["year", key]).size().max() == 1, "duplicate year/age in the spliced series"
        pick = pick.assign(source=pick.table.map({"T12": T12_URL, "T12a": T12A_URL}))
        pick["flag"] = ""
        pick.loc[pick.year == 2020, "flag"] = "2020: pandemic collection problems (JCHS also drops it)"
        pick.loc[pick.year == 2025, "flag"] = "2025: October not collected (federal funding lapse)"
        pick.loc[pick.year <= 1988, "flag"] = "1982-88: age 'not reported' not allocated to groups"
        return pick

    g = (raw.groupby(["table", "year", "vintage", "group"], as_index=False)[["households_k", "owners_k"]].sum())
    g["rate_pct"] = 100 * g["owners_k"] / g["households_k"]
    pick = splice(g, "group").sort_values(["group", "year"])[
        ["year", "group", "households_k", "owners_k", "rate_pct", "table", "vintage", "flag", "source"]]
    pick.to_csv(OUT / "tenure_by_age.csv", index=False)
    g.to_csv(OUT / "tenure_by_age_all_vintages.csv", index=False)

    b = raw.copy()
    b["rate_pct"] = 100 * b["owners_k"] / b["households_k"]
    bands = splice(b, "band").sort_values(["band", "year"])[
        ["year", "band", "group", "households_k", "owners_k", "rate_pct", "table", "vintage", "flag", "source"]]
    bands.to_csv(OUT / "tenure_by_band.csv", index=False)
    return pick, g


def _fred_annual(sid, how="mean"):
    s = pd.read_csv(RAW / f"fred_{sid}.csv", na_values=".")
    s.columns = ["date", sid]
    s["year"] = pd.to_datetime(s["date"]).dt.year
    s = s.dropna()
    n = s.groupby("year")[sid].count()
    a = s.groupby("year")[sid].agg(how)
    return a, n


def affordability():
    wb = openpyxl.load_workbook(RAW / "hud_HousingDemand.xlsx", data_only=True, read_only=True)
    rows = list(wb["HAI_Annual"].iter_rows(values_only=True))
    hdr = rows[0]
    hai = pd.DataFrame([r for r in rows[1:] if isinstance(r[0], (int, float))], columns=hdr)
    hai = hai.rename(columns={hdr[0]: "year"}).set_index("year")[
        ["ExMedPrice_US", "Mrate_US", "MFI_US", "IQ_US", "COMP_US", "FIXED_US"]]
    hai.index = hai.index.astype(int)
    hai.columns = ["nar_median_price", "nar_mortgage_rate", "nar_median_family_income",
                   "nar_qualifying_income", "nar_hai_composite", "nar_hai_fixed"]

    # NAR's definition: P&I on 80% of the median price, 30-year fixed at NAR's rate; qualifying
    # income = 4 x annual payment (a 25% payment-to-income cap). Rebuilt here so the forecast can
    # vary the rate, and checked against NAR's own qualifying income below.
    r = hai["nar_mortgage_rate"] / 1200
    pay = 0.8 * hai["nar_median_price"] * r / (1 - (1 + r) ** -360)
    hai["pti_pct"] = 100 * 12 * pay / hai["nar_median_family_income"]
    hai["iq_rebuilt"] = 48 * pay
    hai["iq_rebuild_err_pct"] = 100 * (hai["iq_rebuilt"] / hai["nar_qualifying_income"] - 1)
    hai["price_to_income"] = hai["nar_median_price"] / hai["nar_median_family_income"]
    # the two pieces of payment-to-income, in logs: log PTI = const + log(price/income) + log(rate factor)
    hai["log_price_income"] = np.log(hai["price_to_income"])
    hai["log_rate_factor"] = np.log(r / (1 - (1 + r) ** -360))

    pmms, pmms_n = _fred_annual("MORTGAGE30US")
    un, _ = _fred_annual("UNRATE")
    hpi, _ = _fred_annual("USSTHPI")
    cpi, _ = _fred_annual("CPIAUCSL")
    # credit stress: Fed charge-off/delinquency release, single-family mortgages at all commercial
    # banks, 30+ days past due or non-accrual (1991+)
    dq, dq_n = _fred_annual("DRSFRMACBS")
    d = hai.join(pd.DataFrame({"pmms_30y": pmms, "pmms_weeks": pmms_n, "unemployment": un,
                               "fhfa_hpi": hpi, "cpi": cpi, "delinquency": dq, "delinquency_quarters": dq_n}),
                 how="outer")
    d["real_hpi"] = d["fhfa_hpi"] / d["cpi"]
    d["real_hpi_g1"] = 100 * d["real_hpi"].pct_change()
    d["real_hpi_g3"] = 100 * ((d["real_hpi"] / d["real_hpi"].shift(3)) ** (1 / 3) - 1)  # trailing 3y, % a year
    d["cpi_infl"] = 100 * d["cpi"].pct_change()
    d.index.name = "year"
    d = d.sort_index()
    assert (d.index.to_series().diff().dropna() == 1).all(), "affordability years must be consecutive"
    # last year's conditions: what a household deciding to buy this year has just lived through
    for v in ["log_price_income", "log_rate_factor", "delinquency", "pti_pct"]:
        d[v + "_l1"] = d[v].shift(1)
    d = d.loc[1970:]
    d.to_csv(OUT / "affordability_annual.csv")
    return d


BAND_AGES = {  # Table 12 band -> single years of age in the projection files (heads are 15+)
    "Less than 25 years": range(15, 25), "25 to 29 years": range(25, 30), "30 to 34 years": range(30, 35),
    "35 to 39 years": range(35, 40), "40 to 44 years": range(40, 45), "45 to 49 years": range(45, 50),
    "50 to 54 years": range(50, 55), "55 to 59 years": range(55, 60), "60 to 64 years": range(60, 65),
    "65 to 69 years": range(65, 70), "70 to 74 years": range(70, 75), "75 years and over": range(75, 101),
}


def population_projection():
    """Census 2023 national projections, both sexes, all races and origins, single year of age
    summed into the twelve Table 12 bands (group = the JCHS ten-year band each belongs to).
    Also keeps age 75 alone: the share of the 75+ band that entered it this year."""
    frames = []
    for series in ["mid", "low", "zero", "hi"]:
        rows = list(csv.DictReader(open(RAW / f"census_np2023_d1_{series}.csv", encoding="utf-8-sig")))
        for r in rows:
            if (r["SEX"], r["ORIGIN"], r["RACE"]) != ("0", "0", "0"):
                continue
            yr = int(r["YEAR"])
            if yr > 2040:
                continue
            ages = {a: float(r[f"POP_{a}"]) for a in range(0, 101)}
            for band, rng in BAND_AGES.items():
                frames.append({"series": series, "year": yr, "band": band, "group": BAND_TO_GROUP[band],
                               "population_k": sum(ages[a] for a in rng) / 1000})
            frames.append({"series": series, "year": yr, "band": "age 75 exactly", "group": "75+",
                           "population_k": ages[75] / 1000})
    p = pd.DataFrame(frames)
    p["source"] = ("https://www2.census.gov/programs-surveys/popproj/datasets/2023/2023-popproj/np2023_d1_"
                   + p["series"] + ".csv")
    p.to_csv(OUT / "population_by_age_proj.csv", index=False)
    return p


def nmdb():
    """FHFA National Mortgage Database, outstanding mortgages, national, all mortgages: annual averages
    of the quarterly average interest rate (complete years only). Used only by the lock-in test."""
    import zipfile
    z = zipfile.ZipFile(RAW / "fhfa_nmdb_outstanding_national_quarterly.zip")
    df = pd.read_csv(z.open(z.namelist()[0]))
    us = df[(df.GEOID == "USA") & (df.MARKET == "All Mortgages")]
    q = us.pivot_table(index=["YEAR", "QUARTER"], columns="SERIESID", values="VALUE1")
    n = q.groupby(level=0).size()
    out = q.groupby(level=0).mean()[n >= 4][["AVE_INTRATE"]].rename(columns={"AVE_INTRATE": "avg_outstanding_rate_pct"})
    out.index.name = "year"
    out.to_csv(OUT / "nmdb_annual.csv")
    return out


if __name__ == "__main__":
    pd.set_option("display.width", 200)
    t, allv = tenure_by_age()
    a = affordability()
    p = population_projection()
    nmdb()
    wide = t.pivot(index="year", columns="group", values="rate_pct")[GROUPS]
    print("rates by age (spliced):\n", wide.round(1).to_string())
    tot = t.groupby("year")[["households_k", "owners_k"]].sum()
    print("\nsum of groups (k):\n", tot.tail(6).round(0).to_string())
    # splice checks: the same year on two sets of controls
    for yr in [1993, 2000, 2001, 2002]:
        s = allv[allv.year == yr].pivot_table(index="group", columns=["table", "vintage"], values="rate_pct")
        print(f"\nsplice check {yr}:\n", s.round(2).to_string())
    print("\nNAR qualifying-income rebuild error, % (should be ~0):",
          a["iq_rebuild_err_pct"].abs().describe().round(2).to_dict())
    print(a.loc[[1982, 1990, 2000, 2006, 2012, 2021, 2023, 2024, 2025],
                ["nar_mortgage_rate", "pmms_30y", "pti_pct", "nar_hai_fixed", "price_to_income",
                 "unemployment", "real_hpi_g3"]].round(2).to_string())
    pg = p[p.band != "age 75 exactly"]
    print(pg[pg.year.isin([2025, 2030])].pivot_table(index="group", columns=["series", "year"], values="population_k",
                                                      aggfunc="sum").round(0).to_string())
