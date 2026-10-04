"""Chart for the owner-occupied-homes forecast: history 2000-2025, rate scenarios and the base
scenario's 80% band to 2035. Reads the CSVs tenure_model.py writes. History starts in 2000
because earlier years sit on older Census population controls: their rates splice cleanly,
their levels do not (a false 0.9m dip at 1999-2000)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "data" / "processed"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

hist = pd.read_csv(D / "tenure_by_age.csv").groupby("year").owners_k.sum() / 1000
fc = pd.read_csv(D / "owner_occupied_forecast.csv")
fan = pd.read_csv(D / "owner_occupied_fan_base.csv", index_col=0)
fan.index = fan.index.astype(int)

# one hue, light -> dark with the rate: magnitude, not identity
shades = {"PMMS 6.0%": "#9ecae1", "Market path": "#2171b5", "PMMS 8.0%": "#08306b"}
ink, muted, grid = "#1f2328", "#6e7781", "#e6e8eb"

fig, ax = plt.subplots(figsize=(9, 5.2), dpi=150)
h = hist.loc[2000:]
h_ok = h.drop(2020)
ax.plot(h_ok.index, h_ok.values, color=ink, lw=2, label="Actual (Census CPS/HVS)")
ax.plot([2020], [h.loc[2020]], "o", ms=4, mfc="white", mec=muted, label="2020 (survey problems)")
ax.fill_between(fan.index, fan["0.1"], fan["0.9"], color="#2171b5", alpha=0.12, lw=0,
                label="Base: 80% range")
for name, col in shades.items():
    s = fc[fc.scenario == name].set_index("year").owners_k / 1000
    base = name == "Market path"
    lab = "Base: mortgage from market rate path (~6.85%)" if base else f"Mortgage {name.split()[1]} flat"
    ax.plot(s.index, s.values, color=col, lw=2.6 if base else 1.8, label=lab)
    ax.annotate(f"{'Market' if base else name.split()[1]}: {s.loc[2031]:.1f}m in 2031, {s.loc[2035]:.1f}m in 2035", (2035, s.loc[2035]),
                xytext=(6, 0), textcoords="offset points", va="center", fontsize=8, color=ink)
ax.axvline(2025.5, color=muted, lw=0.8, ls=(0, (3, 3)))
ax.set_title("US owner-occupied homes, millions: actual and forecast by mortgage-rate path",
             loc="left", fontsize=11, color=ink)
ax.set_xlim(2000, 2044)
ax.set_xticks(range(2000, 2036, 5))
ax.text(2025.7, h.loc[2000:].min(), "forecast", color=muted, fontsize=8.5)
ax.grid(axis="y", color=grid, lw=0.8)
ax.set_axisbelow(True)
for sp in ["top", "right"]:
    ax.spines[sp].set_visible(False)
for sp in ["left", "bottom"]:
    ax.spines[sp].set_color(grid)
ax.tick_params(colors=muted, labelsize=9)
ax.legend(loc="upper left", frameon=False, fontsize=8.5, labelcolor=ink)
fig.text(0.01, 0.01, "Low-immigration households calibrated to JCHS; price/income per Fannie Mae HPI to 2027.\n"
         "Sources: Census HVS Tables 12/12a, NAR, Freddie Mac PMMS, Federal Reserve, Census 2023 projections, JCHS.",
         fontsize=7, color=muted)
fig.tight_layout(rect=(0, 0.05, 1, 1))
fig.savefig(OUT / "owner_occupied_forecast.png")
print(OUT / "owner_occupied_forecast.png")
