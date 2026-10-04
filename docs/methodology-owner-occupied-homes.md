# Owner-occupied homes by age of householder: methodology and diagnostics

Code: `src/tenure_data.py` (inputs), `src/tenure_model.py` (estimation, diagnostics, backtest, forecast,
uncertainty). Every number below is in `data/processed/model_run.log` or the CSVs next to it.

## 1. The idea in plain English

1. **Cohort ageing.** Each year roughly a fifth of the householders in a five-year age band move up into the next
   band and keep their tenure. Take that ageing out and what is left is the net flow into ownership inside each
   cohort. At 25-34 the normal flow is about +3pp a year; after 55 it is close to zero; at 75+ it is slightly
   negative.
2. **What moves that flow** (estimated 1992-2025, 11 age bands, 352 band-years):
   - house prices relative to income (NAR median existing-home price / NAR median family income): the
     down-payment hurdle;
   - the mortgage-rate payment factor (monthly payment per dollar borrowed on a 30-year fixed loan): the rate part
     of affordability;
   - credit stress (single-family mortgage delinquency rate at US commercial banks): foreclosures and tight
     lending after defaults.

   All three are **last year's values**. This year's prices and rates rise *with* this year's demand, so they come
   out with the wrong sign; last year's are what a household deciding to buy has just lived through. Price and
   rate act only on the buying ages (25-44 and 45-54, with separate slopes). Ownership at 55+ moves only with
   credit stress.
3. **Households by age** come from the Census Bureau's 2023 national population projections (low-immigration
   series in the base case), with each band's 2025 headship held constant, then calibrated so that every ten-year
   age group's 2025-35 change matches the Harvard Joint Center for Housing Studies (JCHS) projections (690k
   households a year in total).
4. **Owner-occupied homes** = households by band x ownership rate by band, summed.

## 2. The model

### 2.1 Data

| Item | Source | Years |
|---|---|---|
| Households and owner households by age, twelve bands | Census CPS/HVS Table 12 (1982-1999) and Table 12a (2000-2025, restated on current population controls) | 1982-2025 |
| Median existing-home price, median family income, NAR mortgage rate | NAR Housing Affordability Index components, via HUD's US Housing Market Conditions workbook (`HousingDemand.xlsx`, sheet `HAI_Annual`) | 1970-2025 |
| 30-year mortgage rate | Freddie Mac PMMS (FRED `MORTGAGE30US`), annual average of weekly values | 1971-2026 |
| Mortgage delinquency rate | Federal Reserve, single-family residential mortgages, all commercial banks (FRED `DRSFRMACBS`) | 1991-2026 |
| Population by single year of age, 2022-2100 | Census 2023 National Population Projections, main / low / zero / high immigration | projection |
| Average rate on outstanding mortgages | FHFA National Mortgage Database (used only in the lock-in test) | 2013-2025 |

**Splicing the Census tables** (`tenure_data.py`). 1982-1992 come from Table 12 on 1980-census controls,
1993-1999 from Table 12 revised on 1990-census controls, and 2000-2025 from Table 12a, restated on today's controls.
Each splice year is printed on both sets of controls in the data step's output. Three flags are kept in the data:

- 2020: pandemic collection problems. The ownership rate is interpolated between 2019 and 2021 only to carry
  cohorts through, and flows that touch 2020 (2020 and 2021) are dropped from estimation, as JCHS also drops 2020.
- 2025: October was not collected (federal funding lapse).
- 1982-88: age "not reported" was not allocated to groups.

**NAR's affordability rebuilt.** NAR's qualifying income is the income at which principal and interest on 80% of
the median price, 30-year fixed at NAR's rate, is 25% of income. The script rebuilds it from the components so the
forecast can vary the rate; the rebuild matches NAR's own figure to 0.05% on average over 1970-2025 (largest gap
2.2%). Payment-to-income splits exactly
into two logs:

`log(PTI) = constant + log(price / income) + log(rate factor)`, where
`rate factor = r / (1 - (1 + r)^-360)` and `r` is the monthly mortgage rate.

### 2.2 The cohort flow

With `h[b,t]` the ownership rate (%) of age band `b` in year `t` and `w[b]` the share of the band that has just
aged into it:

`flow[b,t] = h[b,t] - (1 - w[b]) * h[b,t-1] - w[b] * h[b-1,t-1]`

`w = 1/5` for every five-year band. For the open-ended 75+ band, `w` is the share of 75+ who are exactly 75 in
the Census 2025 projection (0.102).

### 2.3 The regression

Pooled OLS over band-years, 1992-2025 (2020-21 dropped), n = 352:

`flow[b,t] = a[b] + bP[g] * ln(P/I)[t-1] + bR[g] * ln m(r)[t-1] + bD[g] * D[t-1] + e[b,t]`

- `a[b]`: one effect per band, the normal gain in ownership at that age.
- `g`: age group. Price and rate slopes for 25-44 ("young") and 45-54 ("mid") only; delinquency slopes for
  young, mid and 55+ ("old").
- Standard errors are clustered by year (every band shares the year's conditions). Driscoll-Kraay errors (two
  lags, calendar time) are reported beside them.

### 2.4 Estimates

Percentage points of ownership flow a year. Year-clustered p-values in round brackets, Driscoll-Kraay in square
brackets.

| Driver (last year's value) | 25-44 | 45-54 | 55+ |
|---|---|---|---|
| log price / income | -6.88 (p 0.000) [0.000] | -3.23 (p 0.000) [0.001] | not included |
| log mortgage payment factor | -4.05 (p 0.000) [0.000] | -2.58 (p 0.002) [0.000] | not included |
| delinquency rate, % | -0.46 (p 0.000) [0.000] | -0.24 (p 0.000) [0.000] | -0.04 (p 0.047) [0.075] |

In everyday units: a 1pp higher mortgage rate (7% to 8%) raises the payment factor by about 10%, which cuts the
yearly ownership flow by about 0.4pp in each 25-44 band and 0.25pp in each 45-54 band. Over five years that
compounds, through the cohorts, into roughly a 1m difference in owner-occupied homes.

The full coefficient table, including the band effects, is `data/processed/tenure_model_coefficients.csv`.

## 3. Diagnostics

### 3.1 Fit and residuals

| Test | Result | Reading |
|---|---|---|
| R² / adjusted R² | 0.803 / 0.793 | |
| Adjusted R², band effects only | 0.640 | the drivers explain 45% of what ageing leaves unexplained (partial R² 0.446) |
| Wald test, drivers jointly zero | 152.8, p 0.000 | |
| Residual AR(1) within band | 0.06, p 0.37 | no persistence left over |
| Ljung-Box, year-mean residual, lags 1-3 | p 0.58 / 0.85 / 0.78 | clean |
| Jarque-Bera | p 0.18 | normal enough |
| Breusch-Pagan | p 0.008 | heteroskedastic; clustered errors are robust to it |
| Pesaran CD | 6.8, p 0.000; mean pairwise correlation 0.16 | bands share year shocks, hence year-clustered errors |
| VIFs among the three drivers | 2.2 / 2.3 / 2.6 | no collinearity problem |
| VIF in the full design matrix | 2,245 raw; 3.4 with drivers centred | a centring artefact: refitting with centred drivers changes no slope, standard error or fitted value (difference 0.0000) |

Stationarity tests on 35 annual points have little power and are reported in the diagnostics CSV for
completeness. The young-band flow does not reject a unit root (ADF p 0.22) but does not reject stationarity either
(KPSS p 0.08).

### 3.2 Is it the right shape?

| Check | Result |
|---|---|
| Same-year drivers instead of last year's | adjusted R² 0.763 vs 0.793; with both in, same-year price and rate terms turn positive (demand moves prices) while last year's stay negative |
| One payment-to-income slope instead of price and rate separately | rejected (Wald 18.5, p 0.000): rates bite less than prices per unit of payment. A single slope would roughly double the rate sensitivity |
| Price and rate slopes for 55+ | jointly zero, p 0.50: the restriction is fine |
| Young-specific time trend added | trend p 0.54; coefficients barely move: the drivers are not standing in for a slow drift (later marriage, student debt) |
| Squared payment-to-income (nonlinearity) | p 0.26: linear is fine |
| Lock-in term (market rate minus average outstanding rate, x owners) | +0.10, p 0.24, and not estimable before 2022: tested, dropped |

### 3.3 Stability and identification

| Check | Rate effect, 25-44 | Price effect, 25-44 |
|---|---|---|
| Full sample 1992-2025 | -4.05 (p 0.000) | -6.88 (p 0.000) |
| 1992-2007 only | -4.70 (p 0.030) | -7.99 (p 0.000) |
| 2008-2025 only | -4.68 (p 0.000) | -2.60 (p 0.12) |
| Without 2022-25 (the rate shock) | -4.39 (p 0.000) | -8.46 (p 0.000) |
| Without 2007-12 (the crisis) | -3.54 (p 0.000) | -6.24 (p 0.000) |
| Year fixed effects (every common shock removed; relative to 55+) | -3.89 (p 0.000) | -6.17 (p 0.000) |

The rate effect is the steadiest thing in the model: the same size before and after 2008, and it does not depend
on the 2022-25 episode. Recursive estimates (`tenure_model_recursive.csv`) put it between -3.5 and -5.1 for every
end-year from 2007 on. The price/income effect is weaker after 2008, and a Chow-type test rejects equal slopes
across 2008 (Wald 37.8, p 0.000) for that reason. A scenario estimated on 2008-2025 only is in the results.

### 3.4 Out-of-sample backtest

The model is re-estimated using only data up to each origin year, then rolled forward. Errors are in the national
ownership rate; 1pp is about 1.3m owner-occupied homes. RMSE in pp, origins 2005-2019:

| Years ahead | Model, actual conditions | Model, conditions frozen at origin | Ownership rates by age frozen | Ageing only |
|---|---|---|---|---|
| 1 | 0.37 | 0.37 | 0.62 | 0.67 |
| 3 | 0.98 | 0.99 | 1.69 | 1.93 |
| 5 | 1.50 | 1.91 | 2.57 | 3.06 |
| 6 | 1.63 | 2.43 | 2.93 | 3.57 |

- The model's bias is near zero (-0.2 to +0.2pp). The frozen-rates benchmark (the JCHS "base" style) is biased up
  by 1.8pp at six years because it cannot see the 2006-16 fall.
- Origins 2010-19 only: 0.82pp at six years, against 2.02pp for the frozen-rates benchmark.
- Every method is scored with the actual households by age of the target year, which isolates the ownership-rate
  model. Scored instead with the origin year's age mix, the model's six-year error rises from 1.63 to 1.91pp.
  The forecast itself uses the Census projected age mix, not a frozen one.
- The backtest uses data up to each origin only. The caveat is that Census, NAR and Fed history is today's revised
  vintage, not what was known at the time.

**The episode that matters: from 2021 into the rate shock.** Estimated only on data to 2021 and fed the actual
2022-25 rates and prices, the model had the national rate at 63.7% in 2025. The actual rate was 65.25%, so the
model was **1.5pp too low (about 2m owners)**. The frozen-rates benchmark was 0.45pp too high. The miss is in the
35+ groups: owners on cheap mortgages did not sell (lock-in), so fewer of them became renters. History before 2022
never had a wide gap between market and outstanding mortgage rates, so no model can learn this from the past. Two
things limit the damage to the forecast:

- Rolled forward from 2021, even the full-sample model under-shoots by about 0.6pp by 2023, and the gap then stops
  growing (2025 residuals are small and mixed in sign). Lock-in looks like a one-off lift in the level, and that
  lift is already inside the 2025 starting point.
- 2026 so far: Census H1-2026 owner-occupied homes are 0.41m above the 2025 average (the model has +0.31m for the
  whole of 2026). By age, 35-44 is the group to watch: the model has its rate down 1.1pp in 2026, while Census H1
  has it up 0.35pp. That is inside survey noise (about ±0.7pp per quarter), but it is the same lock-in pattern.

**Net read:** if the model is wrong, it is more likely too low than too high for ages 35-54 over the next two to
three years.

### 3.5 What was tried and dropped

Roughly 35 variants were tried while exploring, and none of the p-values above allow for that search. The ones
that bear on the choice are in `tenure_model_spec_search.csv`:

- **Levels, differences and error-correction regressions on the ownership rate:** wrong signs, Durbin-Watson around
  0.1 (spurious). That is why the model works on cohort flows.
- **Same-year payment-to-income alone:** wrong sign. The mortgage rate alone also has the wrong sign (+0.27,
  p 0.002), the classic "rates rise in booms" problem.
- **Adding credit stress is what unlocked it:** once the foreclosure hangover is controlled for, affordability has
  the expected sign.
- **Unemployment and house-price growth:** add nothing once the chosen drivers are in (p 0.56, p 0.18).

### 3.6 Review fixes

The code and run log were reviewed independently before publication. What was found and done:

| Finding | Verdict | Action |
|---|---|---|
| 2022-25 out-of-sample miss (-1.5pp) | valid, already disclosed | kept as the main risk (section 3.4) |
| Structural break in 2008 | valid | added a scenario estimated on 2008-2025 only |
| All net growth is 75+; under-75 owners fall | valid | reported in the results |
| Design-matrix VIF of 2,245 | centring artefact | checked: the centred refit changes nothing, largest VIF 3.4 |
| Backtest scored with actual households by age | by design | quantified (1.63 to 1.91pp at six years) |
| Price/income relief assumption may be optimistic | judgement call | "no relief" scenarios show the cost |
| Driscoll-Kraay errors treated 2019 to 2022 as one year apart | valid bug (inference only) | fixed by using calendar time; conclusions unchanged |
| `households()` failed if 2025 was requested; `price_income_path()` depended on which years were asked | valid robustness bugs | fixed; forecast numbers unchanged |

Confirmed correct in the same review: the cohort algebra (the simulation is the exact inverse of the flows), the
lag timing (2026 uses 2025 facts), the JCHS household calibration (matches to machine precision), and that the
2020 interpolation has no effect on the estimates.

## 4. The forecast

### 4.1 Simulation

The ownership rate by band is rolled forward one year at a time:

`h[b,t] = (1 - w[b]) * h[b,t-1] + w[b] * h[b-1,t-1] + a[b] + slopes x drivers[t-1]`

The under-25 band is held at its 2025 rate (24.2%), as JCHS does: no younger cohort ages into it, and it holds
only 1.4m owners. Rates are clipped to 0-100.

### 4.2 Drivers in the base case

| Driver | Base assumption |
|---|---|
| Mortgage rate | the market path (`docs/methodology-rate-path.md`): 6.54% in 2026 (actual year-to-date average of 6.41% blended with the path for the remaining weeks), 6.87% in 2027, 6.85% from 2029 |
| NAR mortgage rate | PMMS + 0.07pp (the 2021-25 average gap) |
| Price / income | 3.94 (2025) to 3.86 (2026) and 3.73 (2027), then flat: Fannie Mae's house-price forecast of 11-Sep-2026 (+2.3% in 2026, +1.0% in 2027) against NAR median family income at its 2015-25 trend (+4.5% a year). No further relief after 2027 |
| Delinquency | 1.83%, the average of the latest four quarters |

Because the model reads last year's values, the 2026 flow depends only on 2025 facts and any rate path first
bites in 2027.

### 4.3 Households

1. **Raw path:** 2025 households by band x the Census 2023 projection's population growth for that band (each
   band's 2025 headship held constant).
2. **Calibration to JCHS:** a correction that grows linearly to 2035, so each ten-year group's 2025-35 change
   matches JCHS. The main-immigration targets are JCHS's tenure paper Table 3 ("All Households"). JCHS publishes
   only the total for low immigration (6.9m, 690k a year), so the low targets are the main targets minus the
   immigration gap by age implied by the Census main and low series, scaled to that total. JCHS also varies
   headship by race and ethnicity, which lowers growth; this model holds headship by age only, which is why
   calibration is needed.
3. **Zero immigration** gets the same correction as the low series (JCHS has no counterpart).

| 2025-35 change by group (k) | JCHS main | JCHS low (derived) |
|---|---|---|
| <25 | -469 | -537 |
| 25-34 | 1 | -460 |
| 35-44 | 911 | 399 |
| 45-54 | 2,069 | 1,783 |
| 55-64 | -1,789 | -1,957 |
| 65-74 | 376 | 252 |
| 75+ | 7,493 | 7,420 |

### 4.4 Scenarios

| Scenario | What changes |
|---|---|
| Base | market rate path, low-immigration households, Fannie Mae price path, delinquency 1.83% |
| Fed dots path | mortgage rate built the same way from the FOMC median dots of 16-Sep-2026 |
| Mortgage 6.0 / 6.5 / 7.0 / 7.5 / 8.0% flat | flat rate for the remaining weeks of 2026 and every later year |
| Price/income flat at 2025 (no relief) | price/income held at 3.94 |
| 8.0% flat with no price relief | both |
| Delinquency back to its 1991-2006 norm | delinquency moves linearly to 2.18% over three years |
| Model estimated on 2008-2025 only | coefficients from the post-crisis sample |
| 2024-25 young shortfall persists | the mean 2024-25 residual of the 25-44 bands (-0.07pp) added every year |
| Main / zero immigration | Census main or zero series for households |
| Households not calibrated to JCHS | raw Census growth with constant headship |
| Ownership rates by age frozen at 2025 | no model: rates by band held, only households change (the JCHS "base" style) |

### 4.5 Uncertainty

2,000 simulations of the base case (seed 7). Each draws the coefficients from their year-clustered covariance and,
for each forecast year, adds one whole historical year's residuals (all bands together, so shocks stay correlated
across ages). The 10th-90th percentile range is reported.

## 5. Limits and what to watch

- **Lock-in is not in the model.** It is the main reason the near-term path could be too low for 35-54.
- **Price/income drives the result as much as the rate.** The base case assumes a modest fall in price/income to
  2027. If prices fall in real terms under 7-8% mortgages, ownership holds up better than shown. If prices stay
  firm while rates stay high, use the "no relief" rows.
- **The price/income effect was weaker after 2008.** If it now matters less than in 1992-2007, the base case is
  slightly too low.
- **Households:** JCHS-calibrated, low immigration. JCHS main immigration adds 0.6m by 2031 and zero immigration
  takes away 1.2m: the same order as 1pp on mortgage rates.
- **Levels are Census CPS/HVS annual households** (86.66m owner households in 2025). The quarterly owner-occupied
  series (FRED `EOWNOCCUSQ176N`) averages 86.71m for 2025; use growth rates when splicing onto that series.
- **Data vintage:** every series is today's revised history.
