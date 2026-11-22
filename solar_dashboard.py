"""
Solar Energy Optimization & Procurement Savings Dashboard (recreation)

Recreates the dashboard I built at Adani Wilmar, Firozpur for a 0.498 MWp
rooftop solar system (commissioned with Adani Green & Waaree).
The original used plant data and is internal, so this version runs on
SAMPLE DATA generated below. Run:  python solar_dashboard.py
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

rng = np.random.default_rng(42)
CAPACITY_KWP = 498          # 0.498 MWp rooftop system
DAYS = 30

# ---------- sample daily generation (kWh) ----------
day = np.arange(1, DAYS + 1)
irradiance = 4.6 + 0.6 * np.sin(day / 5) + rng.normal(0, 0.35, DAYS)   # kWh/m2/day
cloudy = rng.random(DAYS) < 0.12
irradiance[cloudy] *= rng.uniform(0.45, 0.7, cloudy.sum())
actual = CAPACITY_KWP * irradiance * 0.80                               # 80% performance ratio

# ---------- simple forecast: 3-day moving average of irradiance x capacity x PR ----------
irr_forecast = pd.Series(irradiance).shift(1).rolling(3, min_periods=1).mean().fillna(irradiance[0]).to_numpy()
forecast = CAPACITY_KWP * irr_forecast * 0.80
mape = np.mean(np.abs(actual - forecast) / actual) * 100

# ---------- average hourly profile ----------
hours = np.arange(6, 20)
profile = np.clip(np.sin((hours - 6) / 13 * np.pi), 0, None)
profile = profile / profile.sum() * actual.mean()

# ---------- monthly energy mix (MWh): grid vs solar ----------
months = ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]
demand = 520 + 40 * np.sin(np.arange(12) / 2) + rng.normal(0, 10, 12)
solar = np.array([0, 0, 0, 58, 61, 64, 62, 55, 49, 47, 53, 60], float)   # live from Jul
grid = demand - solar

# ---------- dashboard ----------
BG, PANEL, INK, MUTED, SUN, GRID_C, ACC = "#1E2533", "#262F40", "#F2EEE6", "#9AA4B5", "#F2A33A", "#5B8DB8", "#4C9A7C"
plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": INK, "axes.labelcolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.edgecolor": "#3A4559"})
fig = plt.figure(figsize=(16, 10), facecolor=BG)
gs = GridSpec(3, 4, figure=fig, height_ratios=[0.55, 1.4, 1.4], hspace=0.55, wspace=0.35,
              left=0.05, right=0.97, top=0.86, bottom=0.08)
fig.text(0.05, 0.94, "SOLAR GENERATION & POWER PROCUREMENT", fontsize=22, weight="bold")
fig.text(0.05, 0.905, "0.498 MWp rooftop system  ·  Python forecast + dashboard  ·  RECREATED WITH SAMPLE DATA",
         fontsize=11, color=SUN)

kpis = [("Installed capacity", f"{CAPACITY_KWP/1000:.3f} MWp"),
        ("Generation this month", f"{actual.sum()/1000:.1f} MWh"),
        ("Forecast error (MAPE)", f"{mape:.1f}%"),
        ("Solar share of demand", f"{solar[-1]/demand[-1]*100:.0f}%")]
for i, (lab, val) in enumerate(kpis):
    ax = fig.add_subplot(gs[0, i]); ax.set_facecolor(PANEL)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)
    ax.text(0.06, 0.62, val, fontsize=20, weight="bold", color=SUN if i == 0 else INK, transform=ax.transAxes)
    ax.text(0.06, 0.2, lab.upper(), fontsize=9, color=MUTED, transform=ax.transAxes)

def style(ax, title):
    ax.set_facecolor(PANEL); ax.set_title(title, loc="left", fontsize=12, color=INK, pad=10)
    ax.grid(axis="y", color="#33405A", lw=0.6); ax.set_axisbelow(True)
    for s in ["top", "right"]: ax.spines[s].set_visible(False)

ax = fig.add_subplot(gs[1, :3]); style(ax, "Daily generation: actual vs forecast (kWh)")
ax.bar(day, actual, color=SUN, alpha=0.85, label="Actual")
ax.plot(day, forecast, color=GRID_C, lw=2.2, marker="o", ms=3, label="Forecast")
ax.set_xlabel("Day of month"); ax.legend(frameon=False, loc="upper right")

ax = fig.add_subplot(gs[1, 3]); style(ax, "Average day profile (kWh)")
ax.fill_between(hours, profile, color=SUN, alpha=0.35); ax.plot(hours, profile, color=SUN, lw=2)
ax.set_xticks(hours[::2]); ax.set_xticklabels([f"{h}:00" for h in hours[::2]], rotation=45)

ax = fig.add_subplot(gs[2, :3]); style(ax, "Monthly energy mix: grid procurement vs solar (MWh)")
ax.bar(months, grid, color=GRID_C, label="Grid procurement")
ax.bar(months, solar, bottom=grid, color=SUN, label="Rooftop solar")
ax.annotate("Solar live", xy=(3, demand[3]), xytext=(1.2, demand.max() + 25),
            color=INK, fontsize=9, arrowprops=dict(arrowstyle="->", color=MUTED))
ax.set_ylim(0, demand.max() + 70); ax.legend(frameon=False, ncol=2, loc="upper right")

ax = fig.add_subplot(gs[2, 3]); style(ax, "Forecast vs actual (kWh)")
ax.scatter(forecast, actual, color=ACC, s=22)
lim = [actual.min() * 0.95, actual.max() * 1.05]; ax.plot(lim, lim, color=MUTED, ls="--", lw=1)
ax.set_xlabel("Forecast"); ax.set_ylabel("Actual")

fig.text(0.05, 0.025, "Recreation of a dashboard built at Adani Wilmar, Firozpur. Original plant data is internal; "
         "all figures here are sample data except the 0.498 MWp capacity.", fontsize=9, color=MUTED)
fig.savefig("solar-dashboard.png", dpi=110, facecolor=BG)
print(f"Saved solar-dashboard.png  |  month generation {actual.sum()/1000:.1f} MWh, MAPE {mape:.1f}%")
