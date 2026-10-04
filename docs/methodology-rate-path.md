# Treasury and mortgage rate path: methodology

Code: `src/mortgage_path.py`. Output: `data/processed/mortgage_rate_path.csv` (base, annual),
`mortgage_rate_path_monthly.csv`, the FOMC-dots alternative in `mortgage_rate_path_dots*.csv`, and the Kim-Wright
decomposition in `kim_wright_expected_rates.csv`. Console output: `data/processed/mortgage_path_run.log`.

The homes model needs a 30-year mortgage rate for every year to 2035. Rather than assume one, the path is built
from what the Treasury market prices today. Yields are as of 28-Sep-2026; the Kim-Wright fit is of 25-Sep-2026.
The same build also produces a 10-year Treasury path, which the homes model does not use.

## Step 1. Expected one-year rates from the market

The Kim-Wright model (Federal Reserve Board; FRED `THREEFYn` and `THREEFYTPn`, n = 1 to 10) splits each
zero-coupon Treasury yield into the expected average short rate over the next n years, `a(n)`, and a term
premium:

`a(n) = fitted zero-coupon yield(n) - term premium(n)`

The expected one-year rate in year n is the forward implied by successive averages:

`y(n) = n * a(n) - (n - 1) * a(n - 1)`

| Year from now | Fitted yield % | Term premium (pp) | Expected average short rate a(n) % | Expected 1-year rate y(n) % |
|---|---|---|---|---|
| 1 | 4.57 | 0.36 | 4.22 | 4.22 |
| 2 | 4.83 | 0.53 | 4.30 | 4.38 |
| 3 | 4.91 | 0.62 | 4.29 | 4.28 |
| 4 | 4.94 | 0.68 | 4.26 | 4.16 |
| 5 | 4.95 | 0.73 | 4.23 | 4.08 |
| 6 | 4.97 | 0.78 | 4.19 | 4.03 |
| 7 | 5.00 | 0.83 | 4.17 | 4.01 |
| 8 | 5.04 | 0.89 | 4.15 | 4.01 |
| 9 | 5.09 | 0.95 | 4.13 | 4.01 |
| 10 | 5.14 | 1.02 | 4.12 | 4.02 |

After year 10 the expected one-year rate is held at the year-10 value (4.02%). Monthly, each 12-month block from
today carries that year's expected rate.

## Step 2. Treasury yields: compounded expectations plus a maturity premium

In any month, the n-year Treasury yield is the compounded average of the next n expected one-year rates plus a
maturity premium:

`Treasury(n) = [(1 + y1)(1 + y2)...(1 + yn)]^(1/n) - 1 + MP(n)`, with n = 30 and n = 10.

Each premium is backed out today, as the actual yield minus today's compounded expectation, and then held
constant:

| | Actual yield, 28-Sep-2026 | Compounded expectation | Maturity premium |
|---|---|---|---|
| 30-year | 5.56% | 4.05% | 1.51pp |
| 10-year | 5.24% | 4.12% | 1.12pp |

Kim-Wright's own 10-year term premium is 1.02pp, close to the 1.12pp backed out here.

Each path therefore starts exactly at today's yield and then rolls: as the window moves forward, near-term years
drop out and more long-run years come in. Long run: 30-year = 4.02 + 1.51 = 5.53%; 10-year = 4.02 + 1.12 = 5.14%.

Cross-check on the long end (`curve_slope_check()`): the 30-20 year slope is -0.4bp per year of maturity against
a 30-year median of +0.3, and the 20-10 slope 3.6 against 4.6. The long end is slightly flatter than usual, so
nothing points to an unusually steep curve inflating the premium.

## Step 3. Mortgage rate

`30-year mortgage rate = 30-year Treasury + 1.32pp`

1.32pp is the median weekly spread between the Freddie Mac PMMS 30-year fixed rate and the 30-year Treasury
(FRED graph `MORTGAGE30US - DGS30`), February 1977 to September 2026: 2,581 weeks, mean 1.44, latest 1.56. Using
the median rather than today's spread takes about 0.24pp off the mortgage rate from the start; it assumes the
spread returns to normal.

## Step 4. The current year

2026 is mostly history. Each 2026 value is the actual year-to-date average (38 weeks of PMMS to 24-Sep-2026:
6.41%) blended with the path for the remaining weeks (6.88%), giving 6.54%. The homes model receives the
rest-of-year value separately, so flat-rate scenarios can be applied to the remaining weeks only.

## Result

| Year | Expected short rate (year average) % | 30y: compounded expectation % | 30y Treasury % | 10y: compounded expectation % | 10y Treasury % | 30y mortgage % |
|---|---|---|---|---|---|---|
| 2026 | 3.80 | 4.05 | 5.15 | 4.12 | 4.66 | 6.54 |
| 2027 | 4.27 | 4.05 | 5.55 | 4.10 | 5.22 | 6.87 |
| 2028 | 4.35 | 4.04 | 5.54 | 4.07 | 5.19 | 6.86 |
| 2029 | 4.24 | 4.03 | 5.53 | 4.04 | 5.16 | 6.85 |
| 2030 | 4.14 | 4.02 | 5.53 | 4.03 | 5.15 | 6.85 |
| 2031 | 4.07 | 4.02 | 5.53 | 4.02 | 5.14 | 6.85 |
| 2032-35 | 4.01-4.03 | 4.02 | 5.52-5.53 | 4.02 | 5.13-5.14 | 6.84-6.85 |

2026 columns for the Treasuries and the mortgage rate are year averages including the actual year to date.

## The FOMC dots alternative

The same build, with the expected short rates taken from the Fed instead of the market: today's effective fed
funds rate (3.88%) moves in straight lines to the FOMC median dots of 16-Sep-2026 at each year-end (4.1% for 2026,
4.1% for 2027, 3.9% for 2028, 3.6% for 2029) and to the longer-run dot (3.2%) by end-2030, flat after. y1 is the
average of that monthly path over the next 12 months, y2 over the 12 after, and so on.

| Year | 30y: market % | 30y: dots % | 10y: market % | 10y: dots % | Mortgage: market % | Mortgage: dots % |
|---|---|---|---|---|---|---|
| 2027 | 5.55 | 5.54 | 5.22 | 5.17 | 6.87 | 6.86 |
| 2029 | 5.53 | 5.49 | 5.16 | 5.02 | 6.85 | 6.81 |
| 2031 on | 5.53 | 5.47 | 5.14 | 4.97 | 6.85 | 6.79 |

**Why the market path is the base.** From year 5 on, the dots' expected rates sit about 0.8pp below the market's,
mostly the 3.2% longer-run dot against about 4.0% priced. Backed out of today's yields, that gap ends up inside the
"premium": 2.27pp at 30 years and 1.77pp at 10 years, far above Kim-Wright's 1.02pp term premium. The market path
keeps expectations and premium consistent with each other; the dots path is kept as a scenario. For the homes
forecast the difference is small (88.62m vs 88.65m in 2031).

## Limits

- The maturity premium is held at today's level. A fall in term premia would lower the whole path.
- The mortgage spread is assumed to return to its long-run median at once.
- Kim-Wright is a model estimate of expectations, not a survey; it is refitted daily and moves with the market.
