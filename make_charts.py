"""Generates the two charts by executing the queries in answer.sql (so graphs and SQL always agree).
Usage: python3 make_charts.py   (needs matplotlib)"""
import re, sqlite3
from datetime import date
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

RELEASE = date(2018, 6, 2)
GREY, BLUE, GREEN, ORANGE = "#8a8f98", "#2f7bd9", "#2e9e5b", "#e07b39"

conn = sqlite3.connect("shiptivity.db")
sql = open("answer.sql").read()
body = "\n".join(l for l in sql.splitlines() if not l.strip().startswith("--"))
stmts = [s.strip() for s in re.split(r";\s*(?:--[^\n]*)?\n", body + "\n") if s.strip()]
q = lambda i: conn.execute(stmts[i]).fetchall()
d = lambda s: date.fromisoformat(s)

# ---------- Chart 1: daily active users before vs after ----------
daily = q(0)
days = [d(r[0]) for r in daily]
dau = [r[2] for r in daily]
before = {r[0]: r for r in q(1)}
b_avg, a_avg = before["before"][2], before["after"][2]
lift = (a_avg / b_avg - 1) * 100
roll = [sum(dau[max(0, i - 6):i + 1]) / len(dau[max(0, i - 6):i + 1]) for i in range(len(dau))]

fig, (ax, ax2) = plt.subplots(1, 2, figsize=(13, 5), gridspec_kw={"width_ratios": [3, 1]})
ax.bar(days, dau, width=1.0, color="#cfd6df", label="Daily active users")
ax.plot(days, roll, color=BLUE, lw=2, label="7-day average")
ax.axvline(RELEASE, color=ORANGE, ls="--", lw=1.8)
ax.text(RELEASE, max(dau) * 1.02, " Kanban Board released\n 2018-06-02", color=ORANGE, va="bottom", fontsize=9)
ax.hlines(b_avg, days[0], RELEASE, color=GREY, lw=2.5)
ax.hlines(a_avg, RELEASE, days[-1], color=GREEN, lw=2.5)
ax.set_ylim(0, max(dau) * 1.25)
ax.set_title("Daily active users, Feb 2018 - Feb 2019")
ax.set_ylabel("Distinct users who logged in")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))
ax.legend(loc="upper left", frameon=False)
for s in ("top", "right"): ax.spines[s].set_visible(False)

bars = ax2.bar(["Before\n(%d days)" % before["before"][1], "After\n(%d days)" % before["after"][1]],
               [b_avg, a_avg], color=[GREY, GREEN], width=0.6)
for b_, v in zip(bars, [b_avg, a_avg]):
    ax2.text(b_.get_x() + b_.get_width() / 2, v + 0.2, f"{v:.2f}", ha="center", fontweight="bold")
ax2.set_title(f"Average DAU ({lift:+.0f}%)")
ax2.set_ylim(0, a_avg * 1.2)
for s in ("top", "right"): ax2.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig("chart_daily_active_users.png", dpi=160)

# ---------- Chart 2: status changes by card ----------
per_card = q(2)              # (id, name, n) sorted desc
dist = q(3)                  # (n, cards)
daily_ch = q(4)              # (day, changes, cards_moved)
fig = plt.figure(figsize=(13, 8))
gs = fig.add_gridspec(2, 2, height_ratios=[1.1, 1])
a1 = fig.add_subplot(gs[0, 0]); a2 = fig.add_subplot(gs[0, 1]); a3 = fig.add_subplot(gs[1, :])

vals = [r[2] for r in per_card]
a1.bar(range(len(vals)), vals, width=1.0, color=[BLUE if v else "#cfd6df" for v in vals])
a1.set_title("Status changes per card (all %d cards, sorted)" % len(vals))
a1.set_xlabel("Cards, ranked by number of status changes"); a1.set_ylabel("Status changes")
a1.set_xticks([])
a1.text(len(vals) * 0.98, max(vals) * 0.9, "%d cards never moved" % sum(1 for v in vals if v == 0), ha="right", color=GREY)

xs = [r[0] for r in dist]; ys = [r[1] for r in dist]
a2.bar(xs, ys, color=BLUE)
for x, y in zip(xs, ys): a2.text(x, y + 1.5, str(y), ha="center", fontweight="bold")
a2.set_title("How many cards had N status changes"); a2.set_xlabel("Status changes on the card"); a2.set_ylabel("Number of cards")
a2.set_ylim(0, max(ys) * 1.15)

a3.bar([d(r[0]) for r in daily_ch], [r[1] for r in daily_ch], width=1.0, color=GREEN)
a3.set_title("Daily status changes (total %d, on %d active days)" % (sum(r[1] for r in daily_ch), len(daily_ch)))
a3.set_ylabel("Status changes per day")
a3.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))
for a in (a1, a2, a3):
    for s in ("top", "right"): a.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig("chart_status_changes_by_card.png", dpi=160)
print("lift %.1f%%" % lift, b_avg, a_avg)
