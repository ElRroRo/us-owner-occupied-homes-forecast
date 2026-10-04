# Results

All figures come from `data/processed/owner_occupied_forecast.csv`, `owner_occupied_forecast_by_group.csv`,
`owner_occupied_fan_base.csv` and `tenure_check_2026.csv`, written by `src/tenure_model.py`. The same numbers, with
every scenario broken down by age, are in `outputs/Owner_Occupied_Forecast.xlsx`. 2025 is actual (Census CPS/HVS
Table 12a). Scenario definitions: [methodology, section 4.4](methodology-owner-occupied-homes.md#44-scenarios).

## 1. Owner-occupied homes (millions)

| Scenario | 2025 | 2026 | 2027 | 2028 | 2029 | 2030 | 2031 | 2032 | 2033 | 2034 | 2035 | k a year 2025-31 | k a year 2025-35 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Base: mortgage from the market rate path** | 86.66 | 86.97 | 87.31 | 87.64 | 87.97 | 88.31 | 88.62 | 88.87 | 89.09 | 89.27 | 89.44 | +326 | +278 |
| Mortgage from the FOMC dots path | 86.66 | 86.97 | 87.31 | 87.65 | 87.99 | 88.33 | 88.65 | 88.92 | 89.15 | 89.35 | 89.53 | +332 | +287 |
| Mortgage 6.0% flat | 86.66 | 86.97 | 87.36 | 87.92 | 88.46 | 89.01 | 89.53 | 90.00 | 90.44 | 90.83 | 91.22 | +479 | +456 |
| Mortgage 6.5% flat | 86.66 | 86.97 | 87.33 | 87.76 | 88.18 | 88.60 | 89.00 | 89.34 | 89.64 | 89.91 | 90.16 | +389 | +350 |
| Mortgage 7.0% flat | 86.66 | 86.97 | 87.30 | 87.61 | 87.90 | 88.20 | 88.47 | 88.69 | 88.87 | 89.01 | 89.14 | +302 | +248 |
| Mortgage 7.5% flat | 86.66 | 86.97 | 87.27 | 87.46 | 87.64 | 87.81 | 87.97 | 88.06 | 88.12 | 88.14 | 88.15 | +218 | +149 |
| Mortgage 8.0% flat | 86.66 | 86.97 | 87.23 | 87.31 | 87.38 | 87.44 | 87.47 | 87.45 | 87.39 | 87.29 | 87.18 | +135 | +52 |
| Base, price/income stays at 2025 (no relief) | 86.66 | 86.97 | 87.23 | 87.36 | 87.48 | 87.59 | 87.69 | 87.73 | 87.73 | 87.70 | 87.65 | +172 | +99 |
| 8.0% flat, price/income stays at 2025 | 86.66 | 86.97 | 87.15 | 87.02 | 86.88 | 86.73 | 86.55 | 86.31 | 86.03 | 85.72 | 85.40 | -19 | -126 |
| Base, delinquency back to its 1991-2006 norm (2.2%) | 86.66 | 86.97 | 87.27 | 87.55 | 87.78 | 88.01 | 88.22 | 88.37 | 88.48 | 88.56 | 88.63 | +259 | +197 |
| Base, model estimated on 2008-2025 only | 86.66 | 86.94 | 87.19 | 87.35 | 87.50 | 87.65 | 87.77 | 87.84 | 87.87 | 87.86 | 87.84 | +185 | +118 |
| Base, 2024-25 young shortfall persists | 86.66 | 86.94 | 87.25 | 87.55 | 87.85 | 88.15 | 88.43 | 88.66 | 88.84 | 88.99 | 89.13 | +295 | +247 |
| Base, JCHS main-immigration households | 86.66 | 87.06 | 87.49 | 87.92 | 88.35 | 88.77 | 89.18 | 89.53 | 89.85 | 90.13 | 90.40 | +420 | +374 |
| Base, zero-immigration households | 86.66 | 86.77 | 86.90 | 87.03 | 87.16 | 87.28 | 87.38 | 87.43 | 87.43 | 87.40 | 87.35 | +120 | +69 |
| Base, households not calibrated to JCHS | 86.66 | 87.02 | 87.41 | 87.79 | 88.17 | 88.55 | 88.91 | 89.22 | 89.48 | 89.71 | 89.92 | +375 | +326 |
| Ownership rates by age frozen at 2025 (no model) | 86.66 | 87.38 | 88.04 | 88.66 | 89.26 | 89.86 | 90.44 | 90.96 | 91.44 | 91.88 | 92.32 | +630 | +566 |

## 2. Change on the year (thousand homes)

| Scenario | 2026 | 2027 | 2028 | 2029 | 2030 | 2031 | 2032 | 2033 | 2034 | 2035 |
|---|---|---|---|---|---|---|---|---|---|---|
| **Base: mortgage from the market rate path** | +311 | +335 | +339 | +330 | +331 | +310 | +256 | +215 | +182 | +167 |
| Mortgage from the FOMC dots path | +311 | +335 | +343 | +338 | +343 | +323 | +270 | +229 | +195 | +181 |
| Mortgage 6.0% flat | +311 | +393 | +554 | +545 | +546 | +525 | +471 | +431 | +398 | +383 |
| Mortgage 6.5% flat | +311 | +360 | +430 | +419 | +419 | +397 | +343 | +302 | +269 | +254 |
| Mortgage 7.0% flat | +311 | +327 | +309 | +297 | +296 | +273 | +218 | +177 | +143 | +129 |
| Mortgage 7.5% flat | +311 | +295 | +192 | +179 | +177 | +152 | +97 | +56 | +22 | +8 |
| Mortgage 8.0% flat | +311 | +262 | +79 | +64 | +61 | +36 | -20 | -62 | -96 | -109 |
| Base, price/income stays at 2025 (no relief) | +311 | +255 | +131 | +119 | +119 | +95 | +41 | -1 | -34 | -48 |
| 8.0% flat, price/income stays at 2025 | +311 | +182 | -130 | -146 | -151 | -179 | -235 | -278 | -312 | -324 |
| Base, delinquency back to its 1991-2006 norm (2.2%) | +311 | +302 | +273 | +230 | +231 | +209 | +155 | +114 | +80 | +67 |
| Base, model estimated on 2008-2025 only | +276 | +254 | +160 | +149 | +149 | +125 | +68 | +26 | -5 | -18 |
| Base, 2024-25 young shortfall persists | +281 | +305 | +309 | +299 | +300 | +279 | +225 | +184 | +151 | +136 |
| Base, JCHS main-immigration households | +403 | +428 | +433 | +425 | +427 | +406 | +352 | +313 | +282 | +269 |
| Base, zero-immigration households | +109 | +132 | +134 | +123 | +124 | +101 | +47 | +3 | -35 | -52 |
| Base, households not calibrated to JCHS | +361 | +385 | +388 | +379 | +380 | +358 | +304 | +263 | +229 | +214 |
| Ownership rates by age frozen at 2025 (no model) | +719 | +660 | +617 | +605 | +602 | +577 | +519 | +478 | +447 | +433 |

## 3. National homeownership rate (%)

| Scenario | 2025 | 2026 | 2027 | 2028 | 2029 | 2030 | 2031 | 2032 | 2033 | 2034 | 2035 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Base: mortgage from the market rate path** | 65.25 | 65.03 | 64.88 | 64.78 | 64.66 | 64.56 | 64.46 | 64.34 | 64.22 | 64.11 | 64.01 |
| Mortgage from the FOMC dots path | 65.25 | 65.03 | 64.88 | 64.78 | 64.67 | 64.58 | 64.48 | 64.38 | 64.26 | 64.16 | 64.08 |
| Mortgage 6.0% flat | 65.25 | 65.03 | 64.93 | 64.98 | 65.02 | 65.08 | 65.12 | 65.16 | 65.19 | 65.23 | 65.29 |
| Mortgage 6.5% flat | 65.25 | 65.03 | 64.90 | 64.86 | 64.81 | 64.78 | 64.73 | 64.68 | 64.62 | 64.57 | 64.53 |
| Mortgage 7.0% flat | 65.25 | 65.03 | 64.88 | 64.75 | 64.61 | 64.48 | 64.35 | 64.21 | 64.06 | 63.92 | 63.80 |
| Mortgage 7.5% flat | 65.25 | 65.03 | 64.85 | 64.64 | 64.41 | 64.20 | 63.98 | 63.75 | 63.52 | 63.30 | 63.09 |
| Mortgage 8.0% flat | 65.25 | 65.03 | 64.83 | 64.53 | 64.22 | 63.93 | 63.63 | 63.31 | 62.99 | 62.69 | 62.40 |
| Base, price/income stays at 2025 (no relief) | 65.25 | 65.03 | 64.83 | 64.56 | 64.30 | 64.04 | 63.78 | 63.51 | 63.24 | 62.98 | 62.73 |
| 8.0% flat, price/income stays at 2025 | 65.25 | 65.03 | 64.77 | 64.32 | 63.86 | 63.41 | 62.95 | 62.49 | 62.02 | 61.56 | 61.12 |
| Base, delinquency back to its 1991-2006 norm (2.2%) | 65.25 | 65.03 | 64.86 | 64.70 | 64.52 | 64.34 | 64.17 | 63.98 | 63.78 | 63.60 | 63.44 |
| Base, model estimated on 2008-2025 only | 65.25 | 65.00 | 64.80 | 64.56 | 64.31 | 64.08 | 63.84 | 63.59 | 63.34 | 63.10 | 62.87 |
| Base, 2024-25 young shortfall persists | 65.25 | 65.01 | 64.84 | 64.71 | 64.57 | 64.45 | 64.32 | 64.18 | 64.04 | 63.91 | 63.79 |
| Base, JCHS main-immigration households | 65.25 | 65.02 | 64.86 | 64.74 | 64.62 | 64.51 | 64.40 | 64.27 | 64.14 | 64.03 | 63.93 |
| Base, zero-immigration households | 65.25 | 65.05 | 64.93 | 64.85 | 64.76 | 64.68 | 64.59 | 64.49 | 64.39 | 64.29 | 64.21 |
| Base, households not calibrated to JCHS | 65.25 | 65.02 | 64.86 | 64.74 | 64.62 | 64.51 | 64.39 | 64.26 | 64.13 | 64.01 | 63.90 |
| Ownership rates by age frozen at 2025 (no model) | 65.25 | 65.33 | 65.43 | 65.52 | 65.61 | 65.70 | 65.78 | 65.85 | 65.91 | 65.99 | 66.07 |

## 4. Households (millions)

| Scenario | 2025 | 2026 | 2027 | 2028 | 2029 | 2030 | 2031 | 2032 | 2033 | 2034 | 2035 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Base: mortgage from the market rate path** | 132.82 | 133.74 | 134.56 | 135.31 | 136.05 | 136.78 | 137.48 | 138.13 | 138.73 | 139.25 | 139.72 |
| Mortgage from the FOMC dots path | 132.82 | 133.74 | 134.56 | 135.31 | 136.05 | 136.78 | 137.48 | 138.13 | 138.73 | 139.25 | 139.72 |
| Mortgage 6.0% flat | 132.82 | 133.74 | 134.56 | 135.31 | 136.05 | 136.78 | 137.48 | 138.13 | 138.73 | 139.25 | 139.72 |
| Mortgage 6.5% flat | 132.82 | 133.74 | 134.56 | 135.31 | 136.05 | 136.78 | 137.48 | 138.13 | 138.73 | 139.25 | 139.72 |
| Mortgage 7.0% flat | 132.82 | 133.74 | 134.56 | 135.31 | 136.05 | 136.78 | 137.48 | 138.13 | 138.73 | 139.25 | 139.72 |
| Mortgage 7.5% flat | 132.82 | 133.74 | 134.56 | 135.31 | 136.05 | 136.78 | 137.48 | 138.13 | 138.73 | 139.25 | 139.72 |
| Mortgage 8.0% flat | 132.82 | 133.74 | 134.56 | 135.31 | 136.05 | 136.78 | 137.48 | 138.13 | 138.73 | 139.25 | 139.72 |
| Base, price/income stays at 2025 (no relief) | 132.82 | 133.74 | 134.56 | 135.31 | 136.05 | 136.78 | 137.48 | 138.13 | 138.73 | 139.25 | 139.72 |
| 8.0% flat, price/income stays at 2025 | 132.82 | 133.74 | 134.56 | 135.31 | 136.05 | 136.78 | 137.48 | 138.13 | 138.73 | 139.25 | 139.72 |
| Base, delinquency back to its 1991-2006 norm (2.2%) | 132.82 | 133.74 | 134.56 | 135.31 | 136.05 | 136.78 | 137.48 | 138.13 | 138.73 | 139.25 | 139.72 |
| Base, model estimated on 2008-2025 only | 132.82 | 133.74 | 134.56 | 135.31 | 136.05 | 136.78 | 137.48 | 138.13 | 138.73 | 139.25 | 139.72 |
| Base, 2024-25 young shortfall persists | 132.82 | 133.74 | 134.56 | 135.31 | 136.05 | 136.78 | 137.48 | 138.13 | 138.73 | 139.25 | 139.72 |
| Base, JCHS main-immigration households | 132.82 | 133.91 | 134.89 | 135.80 | 136.72 | 137.61 | 138.48 | 139.30 | 140.07 | 140.76 | 141.41 |
| Base, zero-immigration households | 132.82 | 133.38 | 133.83 | 134.22 | 134.59 | 134.95 | 135.29 | 135.57 | 135.79 | 135.94 | 136.03 |
| Base, households not calibrated to JCHS | 132.82 | 133.84 | 134.76 | 135.61 | 136.45 | 137.28 | 138.08 | 138.83 | 139.53 | 140.15 | 140.72 |
| Ownership rates by age frozen at 2025 (no model) | 132.82 | 133.74 | 134.56 | 135.31 | 136.05 | 136.78 | 137.48 | 138.13 | 138.73 | 139.25 | 139.72 |

## 5. Base case by age of householder

Ownership rate (%):

| Age group | 2025 | 2026 | 2031 | 2035 |
|---|---|---|---|---|
| <25 | 24.2 | 24.2 | 24.2 | 24.2 |
| 25-34 | 40.6 | 40.4 | 41.5 | 42.2 |
| 35-44 | 60.8 | 59.8 | 56.9 | 56.0 |
| 45-54 | 69.8 | 69.4 | 67.1 | 65.0 |
| 55-64 | 75.9 | 75.7 | 74.5 | 73.1 |
| 65-74 | 79.5 | 79.4 | 78.8 | 78.2 |
| 75+ | 77.4 | 77.5 | 77.5 | 77.3 |

Owner-occupied homes (thousand):

| Age group | 2025 | 2026 | 2031 | 2035 |
|---|---|---|---|---|
| <25 | 1,410 | 1,390 | 1,343 | 1,280 |
| 25-34 | 8,444 | 8,393 | 8,539 | 8,567 |
| 35-44 | 14,236 | 14,089 | 13,552 | 13,342 |
| 45-54 | 15,033 | 14,897 | 15,097 | 15,147 |
| 55-64 | 17,276 | 17,111 | 15,708 | 15,221 |
| 65-74 | 17,399 | 17,661 | 18,022 | 17,307 |
| 75+ | 12,862 | 13,430 | 16,353 | 18,572 |
| **Total** | 86,660 | 86,971 | 88,616 | 89,437 |

Households (thousand):

| Age group | 2025 | 2026 | 2031 | 2035 |
|---|---|---|---|---|
| <25 | 5,830 | 5,747 | 5,554 | 5,293 |
| 25-34 | 20,782 | 20,762 | 20,555 | 20,322 |
| 35-44 | 23,408 | 23,576 | 23,810 | 23,807 |
| 45-54 | 21,522 | 21,458 | 22,495 | 23,305 |
| 55-64 | 22,774 | 22,605 | 21,081 | 20,817 |
| 65-74 | 21,884 | 22,255 | 22,876 | 22,136 |
| 75+ | 16,618 | 17,337 | 21,108 | 24,038 |

**All of the net growth is in the 75+ group.** It adds 3.5m owners by 2031 as the baby boomers age,
while owners under 75 fall by 1.5m by 2031 and 2.9m by 2035. Anything that depends on home
purchases rather than the stock of owners (moves, sales, first-time buyers) grows more slowly than the headline:
75+ owners move least.

## 6. Base-case inputs

| Year | 2026 | 2027 | 2028 | 2029 | 2030 | 2031 | 2032 | 2033 | 2034 | 2035 |
|---|---|---|---|---|---|---|---|---|---|---|
| 30y mortgage rate (PMMS) % | 6.54 | 6.87 | 6.86 | 6.85 | 6.85 | 6.85 | 6.84 | 6.84 | 6.85 | 6.85 |
| Payment-to-income % | 23.67 | 23.68 | 23.66 | 23.63 | 23.62 | 23.61 | 23.61 | 23.61 | 23.61 | 23.61 |
| Delinquency % | 1.83 | 1.83 | 1.83 | 1.83 | 1.83 | 1.83 | 1.83 | 1.83 | 1.83 | 1.83 |

Price/income: 3.86 (2026), 3.73 (2027 on). The model reads last year's values, so the 2027 input moves 2028.

## 7. Uncertainty around the base case (millions)

2,000 simulations: coefficients drawn from their year-clustered covariance, plus one whole historical year's
residuals for each forecast year. Seed 7.

| Year | 10th percentile | Median | 90th percentile | Deterministic base |
|---|---|---|---|---|
| 2026 | 86.42 | 87.02 | 87.45 | 86.97 |
| 2027 | 86.60 | 87.34 | 88.03 | 87.31 |
| 2028 | 86.73 | 87.69 | 88.57 | 87.64 |
| 2029 | 86.94 | 88.01 | 89.08 | 87.97 |
| 2030 | 87.09 | 88.36 | 89.66 | 88.31 |
| 2031 | 87.22 | 88.69 | 90.12 | 88.62 |
| 2032 | 87.35 | 88.94 | 90.55 | 88.87 |
| 2033 | 87.39 | 89.16 | 90.98 | 89.09 |
| 2034 | 87.40 | 89.35 | 91.24 | 89.27 |
| 2035 | 87.39 | 89.48 | 91.61 | 89.44 |

## 8. Sensitivities at a glance (2031, millions)

| Change from the base | 2031 | vs base |
|---|---|---|
| Mortgage from the FOMC dots path | 88.65 | +0.04 |
| Mortgage 6.0% flat | 89.53 | +0.92 |
| Mortgage 6.5% flat | 89.00 | +0.38 |
| Mortgage 7.0% flat | 88.47 | -0.14 |
| Mortgage 7.5% flat | 87.97 | -0.65 |
| Mortgage 8.0% flat | 87.47 | -1.14 |
| Base, price/income stays at 2025 (no relief) | 87.69 | -0.93 |
| 8.0% flat, price/income stays at 2025 | 86.55 | -2.07 |
| Base, delinquency back to its 1991-2006 norm (2.2%) | 88.22 | -0.40 |
| Base, model estimated on 2008-2025 only | 87.77 | -0.84 |
| Base, 2024-25 young shortfall persists | 88.43 | -0.18 |
| Base, JCHS main-immigration households | 89.18 | +0.56 |
| Base, zero-immigration households | 87.38 | -1.23 |
| Base, households not calibrated to JCHS | 88.91 | +0.30 |
| Ownership rates by age frozen at 2025 (no model) | 90.44 | +1.82 |

Each 1pp on a flat mortgage rate moves 2031 by about 1.03m.

## 9. First look at 2026

Census Table 19 (quarterly ownership rates by age), first half of 2026 against the first half of 2025, beside the
model's full-year 2026 change:

| Age group | Model: 2026 minus 2025 (pp) | Census: H1-2026 minus H1-2025 (pp) | Census H1-2025 % | Census H1-2026 % |
|---|---|---|---|---|
| <35 | -0.13 | -0.50 | 36.50 | 36.00 |
| 35-44 | -1.06 | +0.35 | 60.65 | 61.00 |
| 45-54 | -0.43 | -0.45 | 69.90 | 69.45 |
| 55-64 | -0.17 | -0.15 | 75.50 | 75.35 |
| 65+ | -0.07 | -0.30 | 78.80 | 78.50 |

Census H1-2026 owner-occupied homes (FRED `EOWNOCCUSQ176N`) are 0.41m above the 2025 average; the model has +0.31m
for 2026 as a whole. The 35-44 gap is inside survey noise (about ±0.7pp per quarter) but matches the lock-in pattern
described in the methodology (section 3.4).

## 10. Comparison with JCHS

JCHS's projected owner-household growth for 2025-35 under the Census low-immigration series is +586k a year on its
average-homeownership-rate trajectory, +466k in its base scenario and +249k on its low-homeownership-rate
trajectory (JCHS, "Revised Projections Reflect Lower than Expected Immigration Levels", Figure 2:
https://www.jchs.harvard.edu/blog/revised-projections-reflect-lower-expected-immigration-levels). This model's
base case is
+278k a year over 2025-35 (+326k a year to 2031): just above JCHS's most pessimistic path. The 90th percentile of the uncertainty band
(+495k a year over 2025-35) is close to JCHS's middle path.
