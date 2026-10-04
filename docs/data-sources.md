# Data sources

Every input is in `data/raw/` exactly as downloaded. The SHA-256 prefix lets you check a file against a fresh
download; FRED and Census files are revised over time, so a fresh download will usually differ and will move the
results slightly.

## Files

| File | What it is | Source URL | Downloaded | Used by | SHA-256 (first 12) |
|---|---|---|---|---|---|
| `census_hvs_hist_tab_12a_v2025.xlsx` | US Census Bureau, CPS/HVS Historical Table 12a: households by age and tenure, 2000-2025, current population controls | https://www.census.gov/housing/hvs/data/hist_tab_12a_v2025.xlsx | 2026-09-29 | tenure_data.py | `9f1b4f1215a2` |
| `census_hvs_histtab12.xlsx` | US Census Bureau, CPS/HVS Historical Table 12: households by age of householder and tenure, 1982-2025 (original population controls; used for 1982-1999) | https://www.census.gov/housing/hvs/data/histtab12.xlsx | 2026-09-29 | tenure_data.py | `6079cd5c3f26` |
| `census_hvs_histtab19.xlsx` | US Census Bureau, CPS/HVS Historical Table 19: quarterly homeownership rates by age | https://www.census.gov/housing/hvs/data/histtab19.xlsx | 2026-09-29 | tenure_model.py (2026 first look) | `cd70295f3b91` |
| `census_np2023_d1_hi.csv` | US Census Bureau, 2023 National Population Projections, high-immigration series, population by single year of age, 2022-2100 | https://www2.census.gov/programs-surveys/popproj/datasets/2023/2023-popproj/np2023_d1_hi.csv | 2026-09-29 | tenure_data.py | `d3ff9d25cc0f` |
| `census_np2023_d1_low.csv` | US Census Bureau, 2023 National Population Projections, low-immigration series, population by single year of age, 2022-2100 | https://www2.census.gov/programs-surveys/popproj/datasets/2023/2023-popproj/np2023_d1_low.csv | 2026-09-29 | tenure_data.py | `7b780edb10a0` |
| `census_np2023_d1_mid.csv` | US Census Bureau, 2023 National Population Projections, main series, population by single year of age, 2022-2100 | https://www2.census.gov/programs-surveys/popproj/datasets/2023/2023-popproj/np2023_d1_mid.csv | 2026-09-29 | tenure_data.py | `1532822751d0` |
| `census_np2023_d1_zero.csv` | US Census Bureau, 2023 National Population Projections, zero-immigration series, population by single year of age, 2022-2100 | https://www2.census.gov/programs-surveys/popproj/datasets/2023/2023-popproj/np2023_d1_zero.csv | 2026-09-29 | tenure_data.py | `b43d51c7ac04` |
| `fhfa_nmdb_outstanding_national_quarterly.zip` | FHFA National Mortgage Database, outstanding mortgage statistics, national, quarterly | https://www.fhfa.gov/document/d/nmdb/nmdb-outstanding-mortgage-statistics-national-census-areas-quarterly.zip | 2026-09-29 | tenure_data.py (lock-in test) | `5d64cf8b7096` |
| `fred_CPIAUCSL.csv` | FRED CPIAUCSL: CPI all items (SA) | https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL | 2026-09-30 | tenure_data.py (specification search) | `f8ecddf53a9a` |
| `fred_DFF.csv` | FRED DFF: Effective federal funds rate (%) | https://fred.stlouisfed.org/graph/fredgraph.csv?id=DFF | 2026-09-30 | mortgage_path.py | `b05b07d9ed53` |
| `fred_DGS10.csv` | FRED DGS10: 10-year Treasury constant maturity (%) | https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10 | 2026-09-30 | mortgage_path.py | `f49b5e68f30b` |
| `fred_DGS20.csv` | FRED DGS20: 20-year Treasury constant maturity (%) | https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS20 | 2026-09-30 | mortgage_path.py (curve-slope check) | `8f139c04e124` |
| `fred_DGS30.csv` | FRED DGS30: 30-year Treasury constant maturity (%) | https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS30 | 2026-09-30 | mortgage_path.py | `52c53319af3a` |
| `fred_DRSFRMACBS.csv` | FRED DRSFRMACBS: Delinquency rate on single-family residential mortgages, all commercial banks (%, SA) | https://fred.stlouisfed.org/graph/fredgraph.csv?id=DRSFRMACBS | 2026-09-29 | tenure_data.py, tenure_model.py | `402fb4844920` |
| `fred_EOWNOCCUSQ176N.csv` | FRED EOWNOCCUSQ176N: Owner-occupied housing units (Census HVS, thous.) | https://fred.stlouisfed.org/graph/fredgraph.csv?id=EOWNOCCUSQ176N | 2026-09-29 | tenure_model.py (2026 first look) | `313545b6556c` |
| `fred_MORTGAGE30US.csv` | FRED MORTGAGE30US: Freddie Mac PMMS 30-year fixed mortgage rate (%) | https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US | 2026-09-29 | tenure_data.py, mortgage_path.py, tenure_model.py | `b2b254ffbdb7` |
| `fred_MORTGAGE30US_minus_DGS30.csv` | FRED graph: Freddie Mac PMMS 30-year rate minus 30-year Treasury, weekly, 1977-2026 | https://fred.stlouisfed.org/graph/ (series formula MORTGAGE30US - DGS30, weekly) | 2026-09-30 | mortgage_path.py | `76fb540df23e` |
| `fred_THREEFY10_recent.csv` | Federal Reserve Board Kim-Wright model via FRED: fitted 10-year zero-coupon yield, daily, 2026 | https://fred.stlouisfed.org/graph/fredgraph.csv?id=THREEFY10&cosd=2026-01-01 | 2026-10-02 | mortgage_path.py | `200c45f5acbb` |
| `fred_THREEFY1_recent.csv` | Federal Reserve Board Kim-Wright model via FRED: fitted 1-year zero-coupon yield, daily, 2026 | https://fred.stlouisfed.org/graph/fredgraph.csv?id=THREEFY1&cosd=2026-01-01 | 2026-10-02 | mortgage_path.py | `486f1aec3784` |
| `fred_THREEFY2_recent.csv` | Federal Reserve Board Kim-Wright model via FRED: fitted 2-year zero-coupon yield, daily, 2026 | https://fred.stlouisfed.org/graph/fredgraph.csv?id=THREEFY2&cosd=2026-01-01 | 2026-10-02 | mortgage_path.py | `9a4ee036bd35` |
| `fred_THREEFY3_recent.csv` | Federal Reserve Board Kim-Wright model via FRED: fitted 3-year zero-coupon yield, daily, 2026 | https://fred.stlouisfed.org/graph/fredgraph.csv?id=THREEFY3&cosd=2026-01-01 | 2026-10-02 | mortgage_path.py | `d7fa987dbb82` |
| `fred_THREEFY4_recent.csv` | Federal Reserve Board Kim-Wright model via FRED: fitted 4-year zero-coupon yield, daily, 2026 | https://fred.stlouisfed.org/graph/fredgraph.csv?id=THREEFY4&cosd=2026-01-01 | 2026-10-02 | mortgage_path.py | `f942ed44e27c` |
| `fred_THREEFY5_recent.csv` | Federal Reserve Board Kim-Wright model via FRED: fitted 5-year zero-coupon yield, daily, 2026 | https://fred.stlouisfed.org/graph/fredgraph.csv?id=THREEFY5&cosd=2026-01-01 | 2026-10-02 | mortgage_path.py | `a918cadb6849` |
| `fred_THREEFY6_recent.csv` | Federal Reserve Board Kim-Wright model via FRED: fitted 6-year zero-coupon yield, daily, 2026 | https://fred.stlouisfed.org/graph/fredgraph.csv?id=THREEFY6&cosd=2026-01-01 | 2026-10-02 | mortgage_path.py | `cc19537cc7eb` |
| `fred_THREEFY7_recent.csv` | Federal Reserve Board Kim-Wright model via FRED: fitted 7-year zero-coupon yield, daily, 2026 | https://fred.stlouisfed.org/graph/fredgraph.csv?id=THREEFY7&cosd=2026-01-01 | 2026-10-02 | mortgage_path.py | `37d600e66b95` |
| `fred_THREEFY8_recent.csv` | Federal Reserve Board Kim-Wright model via FRED: fitted 8-year zero-coupon yield, daily, 2026 | https://fred.stlouisfed.org/graph/fredgraph.csv?id=THREEFY8&cosd=2026-01-01 | 2026-10-02 | mortgage_path.py | `393ad604af8d` |
| `fred_THREEFY9_recent.csv` | Federal Reserve Board Kim-Wright model via FRED: fitted 9-year zero-coupon yield, daily, 2026 | https://fred.stlouisfed.org/graph/fredgraph.csv?id=THREEFY9&cosd=2026-01-01 | 2026-10-02 | mortgage_path.py | `0f944d5e2593` |
| `fred_THREEFYTP10_recent.csv` | Federal Reserve Board Kim-Wright model via FRED: 10-year term premium, daily, 2026 | https://fred.stlouisfed.org/graph/fredgraph.csv?id=THREEFYTP10&cosd=2026-01-01 | 2026-10-02 | mortgage_path.py | `410447c9b920` |
| `fred_THREEFYTP1_recent.csv` | Federal Reserve Board Kim-Wright model via FRED: 1-year term premium, daily, 2026 | https://fred.stlouisfed.org/graph/fredgraph.csv?id=THREEFYTP1&cosd=2026-01-01 | 2026-10-02 | mortgage_path.py | `d57e5d450636` |
| `fred_THREEFYTP2_recent.csv` | Federal Reserve Board Kim-Wright model via FRED: 2-year term premium, daily, 2026 | https://fred.stlouisfed.org/graph/fredgraph.csv?id=THREEFYTP2&cosd=2026-01-01 | 2026-10-02 | mortgage_path.py | `6b3755fd0d55` |
| `fred_THREEFYTP3_recent.csv` | Federal Reserve Board Kim-Wright model via FRED: 3-year term premium, daily, 2026 | https://fred.stlouisfed.org/graph/fredgraph.csv?id=THREEFYTP3&cosd=2026-01-01 | 2026-10-02 | mortgage_path.py | `895c17654b45` |
| `fred_THREEFYTP4_recent.csv` | Federal Reserve Board Kim-Wright model via FRED: 4-year term premium, daily, 2026 | https://fred.stlouisfed.org/graph/fredgraph.csv?id=THREEFYTP4&cosd=2026-01-01 | 2026-10-02 | mortgage_path.py | `bad4c6b2e5b1` |
| `fred_THREEFYTP5_recent.csv` | Federal Reserve Board Kim-Wright model via FRED: 5-year term premium, daily, 2026 | https://fred.stlouisfed.org/graph/fredgraph.csv?id=THREEFYTP5&cosd=2026-01-01 | 2026-10-02 | mortgage_path.py | `10b18a46e3f2` |
| `fred_THREEFYTP6_recent.csv` | Federal Reserve Board Kim-Wright model via FRED: 6-year term premium, daily, 2026 | https://fred.stlouisfed.org/graph/fredgraph.csv?id=THREEFYTP6&cosd=2026-01-01 | 2026-10-02 | mortgage_path.py | `827199b3b1b2` |
| `fred_THREEFYTP7_recent.csv` | Federal Reserve Board Kim-Wright model via FRED: 7-year term premium, daily, 2026 | https://fred.stlouisfed.org/graph/fredgraph.csv?id=THREEFYTP7&cosd=2026-01-01 | 2026-10-02 | mortgage_path.py | `14b958a51bed` |
| `fred_THREEFYTP8_recent.csv` | Federal Reserve Board Kim-Wright model via FRED: 8-year term premium, daily, 2026 | https://fred.stlouisfed.org/graph/fredgraph.csv?id=THREEFYTP8&cosd=2026-01-01 | 2026-10-02 | mortgage_path.py | `383efcedfa26` |
| `fred_THREEFYTP9_recent.csv` | Federal Reserve Board Kim-Wright model via FRED: 9-year term premium, daily, 2026 | https://fred.stlouisfed.org/graph/fredgraph.csv?id=THREEFYTP9&cosd=2026-01-01 | 2026-10-02 | mortgage_path.py | `e629fd25f14a` |
| `fred_UNRATE.csv` | FRED UNRATE: Unemployment rate (BLS, %) | https://fred.stlouisfed.org/graph/fredgraph.csv?id=UNRATE | 2026-09-29 | tenure_data.py (specification search) | `ffe86c903f69` |
| `fred_USSTHPI.csv` | FRED USSTHPI: FHFA all-transactions house price index | https://fred.stlouisfed.org/graph/fredgraph.csv?id=USSTHPI | 2026-09-29 | tenure_data.py (specification search) | `c02d4187c8c9` |
| `hud_HousingDemand.xlsx` | HUD, US Housing Market Conditions, HousingDemand.xlsx; sheet HAI_Annual holds the National Association of Realtors affordability components (median price, family income, mortgage rate) | https://www.huduser.gov/portal/periodicals/ushmc/charts/HousingDemand.xlsx | 2026-09-29 | tenure_data.py | `d58976f975ed` |

## Figures typed into the code

These come from documents that are not redistributed here; each is cited where it is used.

| Figure | Value | Source | Where |
|---|---|---|---|
| FOMC median fed funds projections, 16-Sep-2026 | end-2026 4.1, 2027 4.1, 2028 3.9, 2029 3.6, longer run 3.2 | Federal Reserve, Summary of Economic Projections, Table 1: https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20260916.htm | `mortgage_path.py` (`DOTS`, `LONGER_RUN`) |
| House prices, Q4/Q4 | +2.3% (2026), +1.0% (2027) | Fannie Mae Economic & Strategic Research, Housing Forecast, September 2026 (11-Sep-2026): https://www.fanniemae.com/media/document/pdf/housing-forecast-092026 | `tenure_model.py` (`FANNIE_HPI`) |
| JCHS household change 2025-35 by age, main series (thousands) | <25 -469, 25-34 +1, 35-44 +911, 45-54 +2,069, 55-64 -1,789, 65-74 +376, 75+ +7,493 | JCHS, "Projections of Homeownership Rates and Household Growth by Tenure for 2025-2035", Table 3: https://www.jchs.harvard.edu/research-areas/working-papers/projections-homeownership-rates-and-household-growth-tenure-2025-2035 | `tenure_model.py` (`JCHS_MAIN_2535`) |
| JCHS household growth 2025-35, low immigration | 6.9m (690k a year) | JCHS, "Household Growth to Increasingly Feel the Impacts of the Immigration Drop" (August 2026): "the Center's low-series projection of 690,000 additional households per year over 2025-2035": https://www.jchs.harvard.edu/blog/household-growth-increasingly-feel-impacts-immigration-drop | `tenure_model.py` (`JCHS_LOW_TOTAL_2535`) |
| JCHS owner-household growth 2025-35, low immigration | 586k / 466k / 249k a year | same JCHS post, Figure 2 | comparison only (`docs/results.md`) |

## Publishers and terms

- US Census Bureau, Federal Reserve Board, FHFA and HUD publications are US government works.
- FRED is published by the Federal Reserve Bank of St. Louis. Freddie Mac's PMMS (`MORTGAGE30US`) is
  copyrighted by Freddie Mac and reproduced on FRED with permission.
- The affordability components in `hud_HousingDemand.xlsx` are National Association of Realtors data as
  republished by HUD.
- The files are included only so the results can be reproduced. Cite the original publishers, not this
  repository, for the data.
