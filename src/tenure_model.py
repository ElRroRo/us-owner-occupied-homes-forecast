"""Owner-occupied homes by age of householder, 2026-2035: a cohort-flow model.

Plain English
-------------
Each year about a fifth of the householders in a five-year age band move up into the next band,
taking their tenure with them. Take that ageing out and what is left is the net flow into
ownership inside each cohort that year:

    flow[b,t] = h[b,t] - (1-w) h[b,t-1] - w h[b-1,t-1]          (h = ownership rate, %; w = 1/5)
              = normal gain at that age (band effect)
                + house prices relative to income  + mortgage-rate payment burden  + credit stress
                + noise

Affordability is NAR's affordability data split in two: log(median price / median family income)
and log(the monthly payment per dollar borrowed at NAR's mortgage rate). Payment-to-income is the
sum of the two; the data reject a single slope for both, so each gets its own. Credit stress is
the single-family mortgage delinquency rate at US banks. All three enter as LAST YEAR's values:
this year's prices and rates move with this year's demand (they come out with the wrong sign),
last year's are what a household deciding to buy has just lived through. Price and rate act on
the buying ages only, with separate slopes for 25-44 and 45-54; 55+ ownership moves with credit
stress (foreclosures) but not with price or rate.

Owner-occupied homes = households by band x ownership rate by band, summed. Households by band =
2025 households x Census 2023 population growth for the band, calibrated so each ten-year group's
2025-2035 change matches JCHS.

Run: python tenure_model.py   (after tenure_data.py). Writes CSVs to data/processed/.
"""
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats as st
from statsmodels.stats.diagnostic import acorr_ljungbox, het_breuschpagan
from statsmodels.stats.stattools import jarque_bera
from statsmodels.tsa.stattools import adfuller, kpss

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "data" / "processed"
RAW = ROOT / "data" / "raw"

BANDS = ["Less than 25 years", "25 to 29 years", "30 to 34 years", "35 to 39 years", "40 to 44 years",
         "45 to 49 years", "50 to 54 years", "55 to 59 years", "60 to 64 years", "65 to 69 years",
         "70 to 74 years", "75 years and over"]
SHORT = dict(zip(BANDS, ["<25", "25-29", "30-34", "35-39", "40-44", "45-49", "50-54", "55-59", "60-64",
                         "65-69", "70-74", "75+"]))
GROUP = {"<25": "<25", "25-29": "25-34", "30-34": "25-34", "35-39": "35-44", "40-44": "35-44",
         "45-49": "45-54", "50-54": "45-54", "55-59": "55-64", "60-64": "55-64", "65-69": "65-74",
         "70-74": "65-74", "75+": "75+"}
YOUNG = set(BANDS[1:5])     # 25-44: first-time buyers
MID = set(BANDS[5:7])       # 45-54: still buying and trading
OLD = set(BANDS[7:])        # 55+: rarely buying; ownership moves through exits (foreclosure, moves)
XV = ["log_price_income_l1", "log_rate_factor_l1", "delinquency_l1"]
# which age groups each driver acts on. Price and rate only where people buy: the by-band slopes
# for 55+ are small, mixed in sign and insignificant, and letting them in made the 2022-25 miss worse.
SLOPES = {"log_price_income_l1": ["young", "mid"], "log_rate_factor_l1": ["young", "mid"],
          "delinquency_l1": ["young", "mid", "old"]}
ALL3 = ["young", "mid", "old"]
KEY = [f"{v}|young" for v in XV] + ["log_rate_factor_l1|mid"]


def grp_of(bd):
    return "young" if bd in YOUNG else ("mid" if bd in MID else "old")
LABEL = {"log_price_income_l1": "house price / income (log), last year",
         "log_rate_factor_l1": "mortgage-rate payment factor (log), last year",
         "delinquency_l1": "mortgage delinquency rate (%), last year", "pti_pct": "payment-to-income (%)"}
EST = (1991, 2025)          # delinquency series starts in 1991
DROP = (2020, 2021)         # flows that touch the 2020 survey (pandemic collection problems)
RATE_SCEN = [6.0, 6.5, 7.0, 7.5, 8.0]
BASE_KEY = "Market path"   # BASE: mortgage rate built from market expected short rates (scripts/mortgage_path.py)
DOTS_KEY = "Fed dots path"  # alternative: the same build from the FOMC dots


def dots_path(suffix=""):
    """Mortgage rate by year from data/mortgage_rate_path{suffix}.csv (BASE = market; "_dots" = FOMC
    dots). For 2026 the value is the rate for the rest of the year (x_path blends it with the actual
    weekly average to date)."""
    m = pd.read_csv(D / f"mortgage_rate_path{suffix}.csv").set_index("year")
    out = {int(y): float(v) for y, v in m.mortgage_30y.items()}
    out[2026] = float(m.at[2026, "mortgage_rest_of_year"])
    return out



# JCHS household projections, 2025-2035 change by age (thousands). Main series: tenure paper
# Table 3 ("All Households"). Low-immigration total: 6.9m (690k a year), "the Center's low-series
# projection of 690,000 additional households per year over 2025-2035", JCHS blog, August 2026:
# https://www.jchs.harvard.edu/blog/household-growth-increasingly-feel-impacts-immigration-drop
JCHS_MAIN_2535 = {"<25": -469, "25-34": 1, "35-44": 911, "45-54": 2069, "55-64": -1789, "65-74": 376, "75+": 7493}
JCHS_LOW_TOTAL_2535 = 6900
# Fannie Mae Housing Forecast, 11-Sep-2026: Fannie Mae HPI, % change Q4/Q4
# (https://www.fanniemae.com/media/document/pdf/housing-forecast-092026; only its house prices are used)
FANNIE_HPI = {2026: 2.3, 2027: 1.0}


# ----------------------------------------------------------------------------------------- data
def load():
    b = pd.read_csv(D / "tenure_by_band.csv")
    h_obs = b.pivot(index="year", columns="band", values="rate_pct")[BANDS]
    hh = b.pivot(index="year", columns="band", values="households_k")[BANDS]
    h = h_obs.copy()
    h.loc[2020] = np.nan
    h = h.interpolate()     # 2020 -> midpoint of 2019 and 2021, used only to carry cohorts through
    a = pd.read_csv(D / "affordability_annual.csv").set_index("year")
    pop = pd.read_csv(D / "population_by_age_proj.csv")
    mid = pop[(pop.series == "mid") & (pop.year == 2025)].set_index("band").population_k
    w = {bd: 0.2 for bd in BANDS[1:]}
    w[BANDS[-1]] = mid["age 75 exactly"] / mid["75 years and over"]   # share of 75+ who just turned 75
    return h, h_obs, hh, a, pop, w


def flows(h, w):
    out = []
    for i, bd in enumerate(BANDS[1:], 1):
        y = h[bd] - (1 - w[bd]) * h[bd].shift(1) - w[bd] * h[BANDS[i - 1]].shift(1)
        out.append(pd.DataFrame({"year": y.index, "band": bd, "y": y.values}))
    p = pd.concat(out).dropna().reset_index(drop=True)
    p["young"] = p.band.isin(YOUNG).astype(float)
    p["grp"] = p.band.map(grp_of)
    return p


# ----------------------------------------------------------------------------------- estimation
def design(q, a, xv, slopes=None):
    """slopes: None = SLOPES for the chosen drivers, all three groups for anything else;
    a dict to override; or "by_band" for a slope per five-year band."""
    # the chosen drivers are always merged in, so add-on terms (year effects, splits) can use them
    df = q.merge(a[[c for c in sorted(set(xv) | set(XV) | {"pti_pct", "pti_pct_l1"}) if c in a]].reset_index(),
                 on="year", how="left")
    X = pd.get_dummies(df.band).reindex(columns=BANDS[1:]).astype(float)
    X.columns = ["d:" + SHORT[c] for c in X.columns]      # band effects: the normal gain at each age
    for v in xv:
        if slopes == "by_band":
            for bd in BANDS[1:]:
                X[f"{v}|{SHORT[bd]}"] = df[v] * (df.band == bd)
            continue
        if isinstance(slopes, dict):
            groups = slopes.get(v, SLOPES.get(v, ALL3))
        elif slopes == "all3":
            groups = ALL3
        else:
            groups = SLOPES.get(v, ALL3)
        for g in groups:
            X[f"{v}|{g}"] = df[v] * (df.grp == g)
    return df, X


class Fit:
    """OLS with band effects; year-clustered errors (every band shares the year's conditions),
    and Driscoll-Kraay errors (also allow two years of serial correlation)."""

    def __init__(self, p, a, years=EST, xv=XV, slopes=None, extra=None, drop=DROP):
        q = p[p.year.between(*years) & ~p.year.isin(drop)]
        df, X = design(q, a, xv, slopes)
        if extra is not None:
            X = X.join(extra(df))
        ok = X.notna().all(axis=1) & df.y.notna()
        df, X = df[ok], X[ok]
        order = np.argsort(df.year.values, kind="stable")
        self.df, self.X = df.iloc[order].reset_index(drop=True), X.iloc[order].reset_index(drop=True)
        y = self.df.y.values
        self.m = sm.OLS(y, self.X).fit(cov_type="cluster", cov_kwds={"groups": self.df.year.values})
        # calendar time, so the dropped 2020-21 count as a gap (2019 -> 2022 is three years, beyond the lags)
        codes = (self.df.year - self.df.year.min()).values
        self.dk = sm.OLS(y, self.X).fit(cov_type="hac-groupsum", cov_kwds={"time": codes, "maxlags": 2})
        self.resid = y - self.m.fittedvalues
        sst = ((y - y.mean()) ** 2).sum()
        self.r2 = 1 - (self.resid ** 2).sum() / sst
        n, k = len(y), self.X.shape[1]
        self.r2_adj = 1 - (1 - self.r2) * (n - 1) / (n - k)
        self.n, self.years = n, (int(self.df.year.min()), int(self.df.year.max()))

    @property
    def params(self):
        return self.m.params

    def wald(self, cols, weights=None):
        R = np.zeros((1 if weights else len(cols), self.X.shape[1]))
        idx = [list(self.X.columns).index(c) for c in cols]
        if weights:
            R[0, idx] = weights
        else:
            for i, j in enumerate(idx):
                R[i, j] = 1
        t = self.m.wald_test(R, scalar=True)
        return float(t.statistic), float(t.pvalue)


# ----------------------------------------------------------------------------------- simulation
def band_gain(params, bd, x):
    g = grp_of(bd)
    return params.get("d:" + SHORT[bd], 0.0) + sum(params.get(f"{v}|{g}", 0.0) * x[v] for v in x.index if v in XV)


def simulate(h0, xpath, params, w, shocks=None):
    """Roll the ownership rate by band forward. Under-25s are held at their starting rate
    (JCHS does the same: no younger cohort ages into them, and the band is small)."""
    h = h0[BANDS].astype(float).copy()
    out = {}
    for t in xpath.index:
        new = h.copy()
        x = xpath.loc[t]
        for i, bd in enumerate(BANDS[1:], 1):
            eff = band_gain(params, bd, x) + (shocks[t][bd] if shocks is not None else 0.0)
            new[bd] = (1 - w[bd]) * h[bd] + w[bd] * h[BANDS[i - 1]] + eff
        h = new.clip(0, 100)
        out[t] = h.copy()
    return pd.DataFrame(out).T


def nat_rate(path_row, weights):
    return float((weights[BANDS] * path_row[BANDS]).sum() / weights[BANDS].sum())


# ---------------------------------------------------------------------------------- diagnostics
def diagnostics(p, a, fit, h):
    rows = []

    def add(section, test, stat, pval, reading=""):
        rows.append({"section": section, "test": test, "statistic": stat, "p_value": pval, "reading": reading})

    # 1. fit
    bands_only = Fit(p, a, xv=[])
    add("fit", "R2 (band effects + drivers)", fit.r2, None, f"n={fit.n} band-years, {fit.years[0]}-{fit.years[1]}")
    add("fit", "adjusted R2", fit.r2_adj, None)
    add("fit", "adjusted R2, band effects only", bands_only.r2_adj, None, "how much the normal ageing pattern alone explains")
    part = 1 - (fit.resid ** 2).sum() / (bands_only.resid ** 2).sum()
    add("fit", "partial R2 of the drivers", part, None, "share of what ageing leaves unexplained that the drivers explain")
    names = [c for c in fit.X.columns if "|" in c]
    add("fit", "Wald: drivers add nothing (year-clustered)", *fit.wald(names))

    # 2. stationarity (35 annual points: low power, read with care)
    yy = p[p.young == 1].groupby("year").y.mean().loc[EST[0]:EST[1]].drop(list(DROP), errors="ignore")
    series = [("young-band flow (mean of 25-44 bands)", yy)] + [(LABEL[v], a[v].loc[1991:2025]) for v in XV]
    for name, s in series:
        s = s.dropna()
        ad = adfuller(s, autolag="AIC")
        add("stationarity", f"ADF, {name} (H0: unit root)", ad[0], ad[1])
        kp = kpss(s, regression="c", nlags="auto")
        add("stationarity", f"KPSS, {name} (H0: stationary)", kp[0], kp[1], "KPSS p is capped at 0.10 / floored at 0.01")

    # 3. residuals
    e = pd.DataFrame({"year": fit.df.year, "band": fit.df.band, "e": fit.resid}).sort_values(["band", "year"])
    e["e_l1"] = e.groupby("band").e.shift(1)
    e["gap"] = e.groupby("band").year.diff()
    ar = e[e.gap == 1].dropna()
    mar = sm.OLS(ar.e, sm.add_constant(ar.e_l1)).fit(cov_type="cluster", cov_kwds={"groups": ar.year})
    add("residuals", "AR(1) of residuals within band", mar.params["e_l1"], mar.pvalues["e_l1"],
        "positive = some persistence the drivers miss; Driscoll-Kraay errors (2 lags) allow for it")
    ym = e.groupby("year").e.mean()
    for lag, row in acorr_ljungbox(ym, lags=[1, 2, 3]).iterrows():
        add("residuals", f"Ljung-Box on year-mean residual, lag {lag}", row.lb_stat, row.lb_pvalue)
    bp = het_breuschpagan(fit.resid, sm.add_constant(fit.X[names]))
    add("residuals", "Breusch-Pagan heteroskedasticity (on drivers)", bp[0], bp[1],
        "errors are year-clustered, which is robust to this")
    jb = jarque_bera(fit.resid)
    add("residuals", "Jarque-Bera normality", jb[0], jb[1], f"skew {jb[2]:.2f}, kurtosis {jb[3]:.2f}")
    wide = e.pivot(index="year", columns="band", values="e")
    c = wide.corr().values
    N, T = c.shape[0], len(wide)
    iu = np.triu_indices(N, 1)
    cd = np.sqrt(2 * T / (N * (N - 1))) * np.nansum(c[iu])
    add("residuals", "Pesaran CD, cross-band residual correlation", cd, 2 * (1 - st.norm.cdf(abs(cd))),
        f"mean pairwise corr {np.nanmean(c[iu]):.2f}: bands share year shocks, hence year-clustered errors")

    # 4. collinearity of the drivers (annual, 1991-2025)
    yr = a.loc[1991:2025, XV].dropna()
    cm = yr.corr()
    for i in range(len(XV)):
        for j in range(i + 1, len(XV)):
            add("collinearity", f"corr({LABEL[XV[i]]}, {LABEL[XV[j]]})", cm.iloc[i, j], None)
    for v in XV:
        others = [o for o in XV if o != v]
        r2 = sm.OLS(yr[v], sm.add_constant(yr[others])).fit().rsquared
        add("collinearity", f"VIF among the three drivers only, {LABEL[v]}", 1 / (1 - r2), None, "below 5 is comfortable")

    # In the full design the drivers sit next to band intercepts and are far from zero (log payment
    # factor ~ -5.2), so a raw design-matrix VIF is huge. That is a centring artefact: re-fit with each
    # driver demeaned and the slopes, their errors and every fitted value are unchanged.
    ac = a.copy()
    for v in XV:
        ac[v] = ac[v] - ac[v].loc[1992:2025].mean()
    fcen = Fit(p, ac)
    sl = [c for c in fit.X.columns if "|" in c]
    add("collinearity", "centred-driver refit: max change in any slope", float((fcen.params[sl] - fit.params[sl]).abs().max()),
        None, "0 = slopes do not depend on where the drivers are centred")
    add("collinearity", "centred-driver refit: max change in any slope's std error",
        float((fcen.m.bse[sl] - fit.m.bse[sl]).abs().max()), None, "")
    add("collinearity", "centred-driver refit: max change in fitted flow",
        float(np.abs(fcen.m.fittedvalues.values - fit.m.fittedvalues.values).max()), None, "")

    def dvif(X):
        out = {}
        for c in X.columns:
            o = X.drop(columns=c)
            r2 = 1 - ((X[c] - o @ np.linalg.lstsq(o, X[c], rcond=None)[0]) ** 2).sum() / ((X[c] - X[c].mean()) ** 2).sum()
            out[c] = 1 / (1 - r2) if r2 < 1 else np.inf
        return pd.Series(out)
    vr, vc = dvif(fit.X), dvif(fcen.X)
    add("collinearity", "design-matrix VIF, largest driver column: raw / centred",
        float(vr[sl].max()), float(vc[sl].max()), "second number in p_value column; centred is what matters")

    # 5. functional form
    fu = Fit(p, a, slopes={v: ALL3 for v in XV})
    add("form", "price and rate slopes for 55+ both zero (Wald, unrestricted model)",
        *fu.wald(["log_price_income_l1|old", "log_rate_factor_l1|old"]),
        f"not rejected = 55+ restriction is fine; unrestricted 55+ rate slope "
        f"{fu.params['log_rate_factor_l1|old']:+.2f}, price {fu.params['log_price_income_l1|old']:+.2f}")
    # lock-in: owners with cheap mortgages don't sell, so fewer become renters. The gap between the
    # market rate and the average rate on outstanding mortgages (FHFA NMDB, 2013+) is extended back
    # with a two-speed catch-up fitted to NMDB. Tested, not kept: see reading.
    gap = lockin_gap(a)
    lock = lambda df: pd.DataFrame({"lock": df.year.map(gap.shift(1)).values *
                                    np.array([h.loc[y - 1, b] for y, b in zip(df.year, df.band)]) / 100}, index=df.index)
    fk = Fit(p, a, extra=lock)
    fk19 = Fit(p, a, years=(EST[0], 2019), extra=lock)
    add("form", "lock-in term (rate gap x owners), full sample", fk.params["lock"], fk.m.pvalues["lock"],
        f"adj R2 {fk.r2_adj:.3f}; on 1991-2019 alone {fk19.params['lock']:+.2f} (p {fk19.m.pvalues['lock']:.2f}): "
        "before 2022 the gap never opened, so the effect cannot be learned from history")
    add("form", "rate part = price part (young), Wald",
        *fit.wald(["log_price_income_l1|young", "log_rate_factor_l1|young"], [1, -1]),
        "rejected = a single payment-to-income slope would mis-state the rate effect")
    same = ["log_price_income", "log_rate_factor", "delinquency"]
    fs0 = Fit(p, a, xv=same)
    add("form", "alternative: same-year drivers: adj R2", fs0.r2_adj, None, f"vs {fit.r2_adj:.3f} chosen (last year's)")
    for v in same:
        add("form", f"same-year {v}, young", fs0.params[f"{v}|young"], fs0.m.pvalues[f"{v}|young"])
    fb2 = Fit(p, a, xv=same + XV)
    for v in same + XV:
        add("form", f"both years together: {v}, young", fb2.params[f"{v}|young"], fb2.m.pvalues[f"{v}|young"],
            "same-year terms turn positive: this year's prices and rates move with this year's demand")
    fp = Fit(p, a, xv=["pti_pct_l1", "delinquency_l1"])
    add("form", "alternative: single payment-to-income slope (last year), young", fp.params["pti_pct_l1|young"],
        fp.m.pvalues["pti_pct_l1|young"], f"adj R2 {fp.r2_adj:.3f} vs {fit.r2_adj:.3f} chosen")
    pm = a.pti_pct_l1.loc[1991:2025].mean()
    fq = Fit(p, a, xv=["pti_pct_l1", "delinquency_l1"],
             extra=lambda df: pd.DataFrame({"pti_sq|young": (df.pti_pct_l1 - pm) ** 2 * df.young}))
    add("form", "squared payment-to-income, young (is the squeeze worse at high burdens?)",
        fq.params["pti_sq|young"], fq.m.pvalues["pti_sq|young"], "negative = yes; chosen model is linear")
    trend = lambda df: pd.DataFrame({"trend|young": (df.year - 2008) * df.young,
                                     "trend|other": (df.year - 2008) * (1 - df.young)})
    ft = Fit(p, a, extra=trend)
    add("form", "young-specific time trend added: trend", ft.params["trend|young"], ft.m.pvalues["trend|young"],
        "insignificant = the drivers are not just standing in for a slow drift (later marriage etc.)")
    for cc in KEY:
        add("form", f"with trend: {cc}", ft.params[cc], ft.m.pvalues[cc])

    # 6. stability
    post = lambda df: pd.DataFrame({f"{cc}:post": df[cc.split("|")[0]] * (df.grp == cc.split("|")[1]) * (df.year >= 2008)
                                    for cc in names})
    fc = Fit(p, a, extra=post)
    add("stability", "Chow-type: driver slopes differ from 2008 on (year-clustered)",
        *fc.wald([cc for cc in fc.X.columns if cc.endswith(":post")]))
    for lo, hi in [(1991, 2007), (2008, 2025)]:
        fs = Fit(p, a, years=(lo, hi))
        for cc in KEY:
            add("stability", f"{cc} on {lo}-{hi}", fs.params[cc], fs.m.pvalues[cc], f"n={fs.n}")
    for lo, hi, label in [(2007, 2012, "without 2007-2012 (crisis)"), (2022, 2025, "without 2022-2025 (rate shock)")]:
        fs = Fit(p, a, drop=DROP + tuple(range(lo, hi + 1)))
        for cc in KEY:
            add("stability", f"{cc}, {label}", fs.params[cc], fs.m.pvalues[cc], f"n={fs.n}")

    # 7. identification with year fixed effects: every shock common to all ages removed
    def yfe(df):
        Y = pd.get_dummies(df.year, prefix="y", drop_first=True).astype(float)
        Y.index = df.index
        return Y.join(pd.DataFrame({f"{v}|{g}": df[v] * (df.grp == g) for v in XV for g in ["young", "mid"]}))
    fy = Fit(p, a, xv=[], extra=yfe)
    for cc in KEY:
        add("identification", f"{cc}, with year fixed effects (relative to 55+)", fy.params[cc], fy.m.pvalues[cc],
            "survives removing every shock common to all ages")
    return pd.DataFrame(rows)


def lockin_gap(a):
    """Market 30y rate minus the average rate on outstanding mortgages. FHFA NMDB gives the latter
    from 2013; earlier years come from a two-speed catch-up (slow when the market is above the stock,
    fast when refinancing pulls it down) fitted to the NMDB years."""
    from scipy.optimize import minimize
    nm = pd.read_csv(D / "nmdb_annual.csv").set_index("year").avg_outstanding_rate_pct.dropna()
    mk = a.pmms_30y

    def path(ku, kd, r=8.0):
        out = {}
        for y in range(1975, int(mk.dropna().index.max()) + 1):
            r = r + (ku if mk.loc[y] > r else kd) * (mk.loc[y] - r)
            out[y] = r
        return pd.Series(out)
    res = minimize(lambda x: ((path(*x).loc[nm.index] - nm) ** 2).sum(), [0.06, 0.2], bounds=[(0.01, 0.5), (0.01, 0.8)])
    out = path(*res.x)
    out.loc[nm.index] = nm          # the measured years replace the proxy
    return mk - out


def recursive(p, a):
    out = []
    for T in range(2003, 2026):
        if T in DROP:
            continue
        f = Fit(p, a, years=(EST[0], T))
        r = {"through": T}
        for cc in KEY:
            r[cc], r["p " + cc] = f.params[cc], f.m.pvalues[cc]
        out.append(r)
    return pd.DataFrame(out)


def by_band(p, a):
    f = Fit(p, a, slopes="by_band")
    rows = []
    for bd in BANDS[1:]:
        s = SHORT[bd]
        r = {"band": s, "normal_gain_const": f.params[f"d:{s}"]}
        for v in XV:
            r[v], r["p " + v] = f.params[f"{v}|{s}"], f.m.pvalues[f"{v}|{s}"]
        rows.append(r)
    return pd.DataFrame(rows)


def spec_search(p, a):
    """The variants that bear on the choice of drivers. Roughly 35 were tried while exploring
    (levels, differences, error-correction, 1983+ samples); no p-value here allows for that."""
    specs = [("ageing only", []), ("+ payment-to-income", ["pti_pct"]), ("+ mortgage rate", ["pmms_30y"]),
             ("+ real house-price growth", ["real_hpi_g1"]), ("+ unemployment", ["unemployment"]),
             ("+ PTI + house prices + unemployment", ["pti_pct", "real_hpi_g1", "unemployment"]),
             ("+ delinquency", ["delinquency"]), ("+ PTI + delinquency", ["pti_pct", "delinquency"]),
             ("+ price/income + rate factor + delinquency, same year", ["log_price_income", "log_rate_factor",
                                                                        "delinquency"]),
             ("+ PTI + delinquency, last year", ["pti_pct_l1", "delinquency_l1"]),
             ("+ price/income + rate factor + delinquency, last year  [CHOSEN]", XV),
             ("+ chosen + unemployment", XV + ["unemployment"]), ("+ chosen + house-price growth", XV + ["real_hpi_g1"]),
             ("+ mortgage rate + delinquency", ["pmms_30y", "delinquency"])]
    rows = []
    for name, xv in specs:
        f = Fit(p, a, xv=xv)
        r = {"spec": name, "adj_r2": round(f.r2_adj, 3), "n": f.n}
        for v in xv:
            r[f"{v}|young"] = f"{f.params[f'{v}|young']:+.3f} (p {f.m.pvalues[f'{v}|young']:.3f})"
        rows.append(r)
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------------------- backtest
def backtest(p, a, h, h_obs, hh, w, origins=tuple(range(2005, 2020)) + (2021,), horizon=6):
    """Re-estimate on 1991..origin only, then roll forward. Evaluated on the national rate using
    the actual households by band of each target year (this tests the rate model, not households)."""
    rows = []
    for T in origins:
        f = Fit(p, a, years=(EST[0], T))
        fb = Fit(p, a, years=(EST[0], T), xv=[])
        years = list(range(T + 1, min(T + horizon, 2025) + 1))
        h0 = h.loc[T]
        paths = {
            "model, actual conditions": simulate(h0, a.loc[years, XV], f.params, w),
            # the origin year's conditions (known at T) drive T+1, and are then assumed to persist
            "model, conditions frozen at origin": simulate(h0, pd.DataFrame([a.loc[T + 1, XV]] * len(years),
                                                                            index=years), f.params, w),
            "ageing only (no drivers)": simulate(h0, a.loc[years, XV], fb.params, w),
            "rates by age frozen (JCHS base-style)": pd.DataFrame([h0] * len(years), index=years),
        }
        for yr in years:
            if yr == 2020:
                continue
            wts = hh.loc[yr]
            act = nat_rate(h_obs.loc[yr], wts)
            for name, path in paths.items():
                pr = nat_rate(path.loc[yr], wts)
                rows.append({"origin": T, "year": yr, "horizon": yr - T, "method": name, "pred_rate": pr,
                             "actual_rate": act, "err_pp": pr - act, "err_owners_k": (pr - act) / 100 * wts.sum()})
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------------------- forecast
def pmms_2026_ytd():
    m = pd.read_csv(RAW / "fred_MORTGAGE30US.csv", na_values=".")
    m["d"] = pd.to_datetime(m.iloc[:, 0])
    y = m[m.d.dt.year == 2026].iloc[:, 1].dropna()
    return float(y.mean()), len(y)


def delinquency_now():
    """Average of the latest four quarters."""
    return float(pd.read_csv(RAW / "fred_DRSFRMACBS.csv", na_values=".").iloc[-4:, 1].mean())


def price_income_path(a, years, how="fannie"):
    """House price / income by year. "fannie": Fannie Mae's house-price forecast for 2026 and 2027
    against NAR median family income growing at its 2015-2025 trend, flat after 2027 (no relief
    assumed beyond the forecast's horizon). "flat": held at the 2025 value."""
    pi = float(a.loc[2025, "price_to_income"])
    inc = (a.loc[2025, "nar_median_family_income"] / a.loc[2015, "nar_median_family_income"]) ** 0.1 - 1
    out = {2025: pi}
    for yr in range(2026, max(years) + 1):   # compound every year from 2026, whatever years are asked for
        if how == "fannie" and yr in FANNIE_HPI:
            pi *= (1 + FANNIE_HPI[yr] / 100) / (1 + inc)
        out[yr] = pi
    return {yr: out[yr] for yr in years}


def x_path(a, rate, years, delinq, pi_path="fannie"):
    """PMMS scenario -> the drivers. The year before the first forecast year is history (NAR's own
    2025 figures). 2026 blends the actual weekly PMMS average so far with the scenario for the rest
    of the year. The model reads last year's values, so the 2026 flow depends only on 2025 facts
    and a scenario first bites in 2027."""
    pis = price_income_path(a, years, pi_path)
    spread = float((a.nar_mortgage_rate - a.pmms_30y).loc[2021:2025].mean())
    ytd, n = pmms_2026_ytd()
    y0 = years[0] - 1
    cur = [{"year": y0, "pmms": a.loc[y0, "pmms_30y"], "log_price_income": a.loc[y0, "log_price_income"],
            "log_rate_factor": a.loc[y0, "log_rate_factor"], "pti_pct": a.loc[y0, "pti_pct"],
            "delinquency": a.loc[y0, "delinquency"]}]
    for yr in years:
        rs = rate[yr] if isinstance(rate, dict) else rate
        r = (ytd * n + rs * (52 - n)) / 52 if yr == 2026 else rs
        rr = (r + spread) / 1200
        fac = rr / (1 - (1 + rr) ** -360)
        cur.append({"year": yr, "pmms": r, "price_to_income": pis[yr], "log_price_income": np.log(pis[yr]),
                    "log_rate_factor": np.log(fac), "pti_pct": 100 * 12 * 0.8 * pis[yr] * fac,
                    "delinquency": delinq(yr) if callable(delinq) else delinq})
    cur = pd.DataFrame(cur).set_index("year")
    out = cur.loc[years, ["pmms", "price_to_income", "pti_pct", "delinquency"]].copy()
    for v in ["log_price_income", "log_rate_factor", "delinquency"]:
        out[v + "_l1"] = cur[v].shift(1).loc[years]
    return out


def _hh_raw(hh, pop, series, years):
    """Households by band if each band's headship stays at 2025: 2025 households x population growth."""
    pp = pop[(pop.series == series) & pop.band.isin(BANDS)].pivot(index="year", columns="band",
                                                                   values="population_k")[BANDS]
    return (pp.loc[list(years)] / pp.loc[2025]) * hh.loc[2025, BANDS]


def _by_group(s):
    return s.groupby(lambda bd: GROUP[SHORT[bd]]).sum()


def jchs_targets(hh, pop):
    """2025-2035 household change by ten-year group that each Census series is calibrated to.
    Main = JCHS Table 3. Low = JCHS main minus the immigration gap by age implied by the Census
    main and low series, scaled so the total is JCHS's 6.9m (JCHS publishes the low total only)."""
    base = hh.loc[2025, BANDS]
    mid = _by_group(_hh_raw(hh, pop, "mid", [2035]).loc[2035] - base)
    low = _by_group(_hh_raw(hh, pop, "low", [2035]).loc[2035] - base)
    main = pd.Series(JCHS_MAIN_2535)
    gap = mid - low
    s = (main.sum() - JCHS_LOW_TOTAL_2535) / gap.sum()
    return {"mid": main, "low": main - s * gap, "ours_mid": mid, "ours_low": low}


def households(hh, pop, series, years, calibrate=True):
    """Households by band, 2026-2035. Census 2023 projection growth by age, then a correction that
    grows linearly to 2035 so each ten-year group's decade change matches JCHS (JCHS also varies
    headship by race and ethnicity, which lowers growth; we hold headship by age only). The zero-
    immigration series gets the same correction as the low one (no JCHS counterpart)."""
    years = list(years)
    yrs = list(range(2026, 2036))
    base = hh.loc[2025, BANDS]
    raw = _hh_raw(hh, pop, series, yrs)
    if not calibrate:
        return pd.concat([hh.loc[[2025], BANDS], raw]).loc[years]
    tg = jchs_targets(hh, pop)
    corr = (tg["mid"] - tg["ours_mid"]) if series == "mid" else (tg["low"] - tg["ours_low"])
    share = base / base.groupby(lambda bd: GROUP[SHORT[bd]]).transform("sum")
    for t in yrs:
        for bd in BANDS:
            raw.loc[t, bd] += corr[GROUP[SHORT[bd]]] * share[bd] * (t - 2025) / 10
    return pd.concat([hh.loc[[2025], BANDS], raw]).loc[years]


def forecast(a, h, hh, pop, w, fit, p_all, years=tuple(range(2026, 2036))):
    years = list(years)
    dq_now = delinquency_now()
    dq_norm = float(a.delinquency.loc[1991:2006].mean())
    h0 = h.loc[2025]
    res, paths = [], {}
    # recent misfit: mean residual of the 25-44 bands in 2024-2025
    e = pd.DataFrame({"year": fit.df.year, "young": fit.df.young, "e": fit.resid})
    young_gap = float(e[(e.young == 1) & e.year.isin([2024, 2025])].e.mean())
    gap_shocks = {yr: pd.Series({bd: (young_gap if bd in YOUNG else 0.0) for bd in BANDS}) for yr in years}

    def run(label, rate, series, delinq=dq_now, frozen=False, shocks=None, calibrate=True, pi_path="fannie",
            params=None):
        X = x_path(a, rate, years, delinq, pi_path=pi_path)
        H = households(hh, pop, series, years, calibrate=calibrate)
        path = pd.DataFrame([h0] * len(years), index=years) if frozen else simulate(
            h0, X, fit.params if params is None else params, w, shocks=shocks)
        paths[label] = (path, H)
        res.append({"scenario": label, "pmms": a.loc[2025, "pmms_30y"], "households_series": series, "year": 2025,
                    "households_k": hh.loc[2025].sum(), "owners_k": (hh.loc[2025] * h0 / 100).sum(),
                    "rate_pct": nat_rate(h0, hh.loc[2025]), "pti_pct": a.loc[2025, "pti_pct"],
                    "delinquency": a.loc[2025, "delinquency"]})
        for yr in years:
            res.append({"scenario": label, "pmms": X.at[yr, "pmms"], "households_series": series, "year": yr,
                        "households_k": H.loc[yr].sum(), "owners_k": (H.loc[yr] * path.loc[yr] / 100).sum(),
                        "rate_pct": nat_rate(path.loc[yr], H.loc[yr]), "pti_pct": X.at[yr, "pti_pct"],
                        "delinquency": X.at[yr, "delinquency"]})

    dots = dots_path()
    run(BASE_KEY, dots, "low")
    run(DOTS_KEY, dots_path("_dots"), "low")
    for r in RATE_SCEN:
        run(f"PMMS {r:.1f}%", r, "low")
    run("Market path, main-immigration households", dots, "mid")
    run("Market path, zero-immigration households", dots, "zero")
    run("Market path, delinquency back to 1991-2006 norm", dots, "low",
        delinq=lambda yr: dq_now + (dq_norm - dq_now) * min(1.0, (yr - 2025) / 3))
    run("Market path, price/income flat at 2025 (no relief)", dots, "low", pi_path="flat")
    run("PMMS 8.0%, price/income flat at 2025 (no relief)", 8.0, "low", pi_path="flat")
    run("Market path, 2024-25 young shortfall persists", dots, "low", shocks=gap_shocks)
    # the 2008 break: coefficients from the post-crisis years only (weaker price effect, lower normal gains)
    run("Market path, model estimated on 2008-2025 only", dots, "low", params=Fit(p_all, a, years=(2008, 2025)).params)
    run("Market path, households not calibrated to JCHS", dots, "low", calibrate=False)
    run("rates by age frozen at 2025 (JCHS base-style)", dots, "low", frozen=True)
    return pd.DataFrame(res), paths, {"delinq_now": dq_now, "delinq_norm_1991_2006": dq_norm,
                                      "young_gap_2024_25": young_gap,
                                      "price_to_income_2025": float(a.loc[2025, "price_to_income"]),
                                      "nar_minus_pmms_spread": float((a.nar_mortgage_rate - a.pmms_30y).loc[2021:2025].mean())}


def fan(fit, a, h, hh, pop, w, rate=None, series="low", n=2000, seed=7, years=tuple(range(2026, 2036))):
    """Uncertainty: coefficient draws from the year-clustered covariance, plus a whole year's
    residuals (all bands together) drawn at random from history for each forecast year."""
    rng = np.random.default_rng(seed)
    years = list(years)
    X = x_path(a, dots_path() if rate is None else rate, years, delinquency_now())
    H = households(hh, pop, series, years)
    draws = rng.multivariate_normal(fit.params.values, fit.m.cov_params().values, size=n)
    e = pd.DataFrame({"year": fit.df.year, "band": fit.df.band, "e": fit.resid}).pivot(index="year", columns="band",
                                                                                      values="e")
    out = []
    for i in range(n):
        prm = pd.Series(draws[i], index=fit.params.index)
        sh = {yr: e.loc[rng.choice(e.index.values)].reindex(BANDS).fillna(0) for yr in years}
        path = simulate(h.loc[2025], X, prm, w, shocks=sh)
        out.append({yr: (H.loc[yr] * path.loc[yr] / 100).sum() for yr in years})
    return pd.DataFrame(out)


def steady_state(fit, w, x, h_under25):
    """Where rates by age settle if conditions x hold for good: h[b] = h[b-1] + gain[b] / w[b]."""
    prof = {BANDS[0]: h_under25}
    for i, bd in enumerate(BANDS[1:], 1):
        prof[bd] = prof[BANDS[i - 1]] + band_gain(fit.params, bd, x) / w[bd]
    return pd.Series(prof)


def check_2026(paths, hh, h):
    """First look at 2026: Census Table 19 quarterly rates by age, H1-2026 vs H1-2025."""
    import openpyxl
    ws = openpyxl.load_workbook(RAW / "census_hvs_histtab19.xlsx", data_only=True,
                                read_only=True).worksheets[0]
    cur, q, k = None, {}, 0
    for r in ws.iter_rows(values_only=True):
        if isinstance(r[0], (int, float)) and 1990 < r[0] < 2100:
            cur, k = int(r[0]), 0
            continue
        if cur and len(r) > 6 and isinstance(r[1], (int, float)):
            k += 1
            q[(cur, k)] = r[1:7]
    cols = ["US", "<35", "35-44", "45-54", "55-64", "65+"]
    qq = pd.DataFrame(q, index=cols).T.astype(float)
    h1 = {yr: qq.loc[[(yr, 1), (yr, 2)]].mean() for yr in (2025, 2026) if (yr, 2) in qq.index}
    grp = {"<35": BANDS[:3], "35-44": BANDS[3:5], "45-54": BANDS[5:7], "55-64": BANDS[7:9], "65+": BANDS[9:]}
    path, H = paths[BASE_KEY]
    rows = []
    for g, bs in grp.items():
        m25 = float((hh.loc[2025, bs] * h.loc[2025, bs]).sum() / hh.loc[2025, bs].sum())
        m26 = float((H.loc[2026, bs] * path.loc[2026, bs]).sum() / H.loc[2026, bs].sum())
        rows.append({"group": g, "model_2026_minus_2025_pp": m26 - m25,
                     "census_H1_2026_minus_H1_2025_pp": (h1[2026][g] - h1[2025][g]) if 2026 in h1 else np.nan,
                     "census_H1_2025": h1[2025][g], "census_H1_2026": h1[2026][g] if 2026 in h1 else np.nan})
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------------------- main
if __name__ == "__main__":
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    pd.set_option("display.max_colwidth", 110)
    h, h_obs, hh, a, pop, w = load()
    p = flows(h, w)
    fit = Fit(p, a)

    coef = pd.DataFrame({"coef": fit.params, "se_cluster": fit.m.bse, "p_cluster": fit.m.pvalues,
                         "se_driscoll_kraay": fit.dk.bse, "p_driscoll_kraay": fit.dk.pvalues})
    coef.to_csv(D / "tenure_model_coefficients.csv")
    print(f"MODEL  n={fit.n}  years {fit.years}  R2 {fit.r2:.3f}  adj R2 {fit.r2_adj:.3f}  w75={w[BANDS[-1]]:.3f}")
    print(coef.round(4).to_string())

    diag = diagnostics(p, a, fit, h)
    diag.to_csv(D / "tenure_model_diagnostics.csv", index=False)
    print("\nDIAGNOSTICS\n", diag.round(4).to_string())

    rec = recursive(p, a)
    rec.to_csv(D / "tenure_model_recursive.csv", index=False)
    print("\nRECURSIVE (estimated on 1991..T)\n", rec.round(3).to_string())

    bb = by_band(p, a)
    bb.to_csv(D / "tenure_model_by_band.csv", index=False)
    print("\nSLOPES BY BAND\n", bb.round(3).to_string())

    ss = spec_search(p, a)
    ss.to_csv(D / "tenure_model_spec_search.csv", index=False)
    print("\nSPECIFICATION SEARCH (1991-2025, band effects in all)\n", ss.to_string())

    bt = backtest(p, a, h, h_obs, hh, w)
    bt.to_csv(D / "tenure_backtest.csv", index=False)
    summs = []
    for lo, hi in [(2005, 2019), (2010, 2019)]:
        s = bt[bt.origin.between(lo, hi)].groupby(["method", "horizon"]).agg(
            rmse_pp=("err_pp", lambda x: np.sqrt((x ** 2).mean())), bias_pp=("err_pp", "mean"),
            rmse_owners_k=("err_owners_k", lambda x: np.sqrt((x ** 2).mean())),
            n=("err_pp", "size")).reset_index().assign(origins=f"{lo}-{hi}")
        summs.append(s)
        print(f"\nBACKTEST origins {lo}-{hi}: RMSE of the national ownership rate, pp\n",
              s.pivot(index="horizon", columns="method", values="rmse_pp").round(2).to_string())
        print(" bias, pp\n", s.pivot(index="horizon", columns="method", values="bias_pp").round(2).to_string())
        print(" RMSE, owner households (k)\n", s.pivot(index="horizon", columns="method",
                                                       values="rmse_owners_k").round(0).to_string())
    pd.concat(summs).to_csv(D / "tenure_backtest_summary.csv", index=False)
    print("\nEPISODE: origin 2021 -> 2022-2025 (national rate, %)\n",
          bt[bt.origin == 2021].pivot(index="year", columns="method", values="pred_rate").join(
              bt[bt.origin == 2021].groupby("year").actual_rate.first()).round(2).to_string())

    fc, paths, assum = forecast(a, h, hh, pop, w, fit, p)
    fc.to_csv(D / "owner_occupied_forecast.csv", index=False)
    print("\nASSUMPTIONS", {k: round(v, 3) for k, v in assum.items()}, "PMMS 2026 YTD", pmms_2026_ytd())
    t = fc.pivot_table(index="year", columns="scenario", values="owners_k")
    print("\nOWNER-OCCUPIED HOMES (m)\n", (t.loc[[2025, 2026, 2027, 2028, 2029, 2030, 2031, 2035]] / 1000).round(2).T.to_string())
    g = t.loc[[2025, 2031, 2035]].T
    g["k_per_yr_25_31"] = (g[2031] - g[2025]) / 6
    g["k_per_yr_25_35"] = (g[2035] - g[2025]) / 10
    print(g.round(0).to_string())
    r = fc.pivot_table(index="year", columns="scenario", values="rate_pct").loc[[2025, 2026, 2028, 2031, 2035]]
    print("\nNATIONAL OWNERSHIP RATE (%)\n", r.round(2).T.to_string())
    print("\nDRIVER PATH, base\n", x_path(a, dots_path(), list(range(2026, 2036)), delinquency_now())[
        ["pmms", "price_to_income", "pti_pct", "delinquency"]].round(3).T.to_string())

    path, H = paths[BASE_KEY]
    grp_rows = []
    for yr in [2025, 2026, 2031, 2035]:
        hrow = h.loc[2025] if yr == 2025 else path.loc[yr]
        wrow = hh.loc[2025] if yr == 2025 else H.loc[yr]
        for gname in ["<25", "25-34", "35-44", "45-54", "55-64", "65-74", "75+"]:
            bs = [bd for bd in BANDS if GROUP[SHORT[bd]] == gname]
            grp_rows.append({"year": yr, "group": gname, "rate_pct": float((wrow[bs] * hrow[bs]).sum() / wrow[bs].sum()),
                             "owners_k": float((wrow[bs] * hrow[bs] / 100).sum()), "households_k": float(wrow[bs].sum())})
    gr = pd.DataFrame(grp_rows)
    gr.to_csv(D / "owner_occupied_forecast_by_group.csv", index=False)
    print("\nBY GROUP, base: rate %\n", gr.pivot(index="group", columns="year", values="rate_pct").round(1).to_string())
    print("BY GROUP, base: owners k\n", gr.pivot(index="group", columns="year", values="owners_k").round(0).to_string())

    xb = x_path(a, dots_path(), list(range(2026, 2032)), delinquency_now()).loc[2031]
    ssp = steady_state(fit, w, xb, h.loc[2025, BANDS[0]])
    print("\nSTEADY STATE vs 2025 (base conditions held for good)\n",
          pd.DataFrame({"2025": h.loc[2025], "steady": ssp}).rename(index=SHORT).round(1).T.to_string())

    fn = fan(fit, a, h, hh, pop, w)
    qf = fn.quantile([0.1, 0.5, 0.9]).T / 1000
    qf.to_csv(D / "owner_occupied_fan_base.csv")
    print("\nFAN, base scenario (m): 10th / 50th / 90th percentile\n", qf.loc[[2026, 2028, 2031, 2035]].round(2).to_string())

    c26 = check_2026(paths, hh, h)
    c26.to_csv(D / "tenure_check_2026.csv", index=False)
    print("\n2026 FIRST LOOK, rates by age\n", c26.round(2).to_string())
    q = pd.read_csv(RAW / "fred_EOWNOCCUSQ176N.csv")
    q.columns = ["d", "v"]
    q["d"] = pd.to_datetime(q.d)
    h1 = {yr: q[(q.d.dt.year == yr) & (q.d.dt.month <= 4)].v.mean() for yr in (2025, 2026)}
    y25 = q[q.d.dt.year == 2025].v.mean()
    b = t[BASE_KEY]
    print(f"2026 FIRST LOOK, owner-occupied homes (Census HVS): H1-2026 minus H1-2025 = {h1[2026] - h1[2025]:+.0f}k "
          f"(H1-2025 was a weak half); H1-2026 minus 2025 average = {h1[2026] - y25:+.0f}k;"
          f" model 2026 minus 2025 (annual) = {b[2026] - b[2025]:+.0f}k")
    hb = fc[fc.scenario == BASE_KEY].set_index("year").households_k
    print(f"\nHOUSEHOLDS (calibrated, low immigration): {(hb[2035] - hb[2025]) / 10:.0f}k a year 2025-35 "
          f"(JCHS low 690k); by year: " + ", ".join(f"{y}: {hb[y] - hb[y - 1]:+.0f}" for y in range(2026, 2036)))
    tg = jchs_targets(hh, pop)
    print("household change 2025-35 by group (k):\n", pd.DataFrame(tg).round(0).to_string())
    print("JCHS owner growth 2025-35, low immigration: 586k (rates rise) / 466k (flat by age+race) / 249k (fall)")
