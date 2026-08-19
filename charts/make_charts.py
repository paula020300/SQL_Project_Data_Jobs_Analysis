"""Build the README charts from the query result sets in charts/data/.

Run from the repository root:

    .venv/Scripts/python charts/make_charts.py     # Windows
    .venv/bin/python charts/make_charts.py         # macOS / Linux

Each CSV in charts/data/ is the result of the matching file in project_sql/,
exported from PostgreSQL. Every chart is written to assets/ as a PNG.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # no display needed; write straight to file
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "charts" / "data"
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

# Seaborn's whitegrid theme, shipped with matplotlib so it needs no extra
# dependency. It supplies the light background and recessive gridlines; the
# overrides below only set the colours and type.
plt.style.use("seaborn-v0_8-whitegrid")

SURFACE = "#ffffff"
INK = "#0b0b0b"
INK_MUTED = "#52514e"
SERIES = "#2a78d6"

plt.rcParams.update({
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "text.color": INK,
    "axes.labelcolor": INK_MUTED,
    "xtick.color": INK_MUTED,
    "ytick.color": INK_MUTED,
    "grid.linewidth": 0.8,
})


def titled(ax, title, subtitle):
    ax.set_title(title, loc="left", fontsize=13, fontweight="bold",
                 color=INK, pad=22)
    ax.text(0, 1.02, subtitle, transform=ax.transAxes, fontsize=9.5,
            color=INK_MUTED, va="bottom")


def save(fig, name):
    path = ASSETS / name
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {path.relative_to(ROOT)}")


def chart_1_top_paying_jobs():
    df = pd.read_csv(DATA / "query1_top_paying_jobs.csv")
    df = df.sort_values("salary_year_avg")

    labels = [
        f"{t[:38] + '...' if len(t) > 38 else t}\n{c}"
        for t, c in zip(df["job_title"], df["company_name"])
    ]

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(labels, df["salary_year_avg"], color=SERIES, height=0.62, zorder=3)
    for y, v in enumerate(df["salary_year_avg"]):
        ax.text(v + 8000, y, f"${v/1000:,.0f}k", va="center",
                fontsize=9, color=INK_MUTED)

    ax.set_xlim(0, df["salary_year_avg"].max() * 1.14)
    ax.grid(axis="y", visible=False)
    ax.set_xticks([])
    ax.tick_params(axis="y", labelsize=9)
    titled(ax, "Top 10 highest-paying Data Analyst postings",
           "Average yearly salary, postings with a disclosed salary")
    save(fig, "01_top_paying_jobs.png")


def chart_3_top_demanded_skills():
    df = pd.read_csv(DATA / "query3_top_demanded_skills.csv").sort_values("job_count")

    fig, ax = plt.subplots(figsize=(8, 3.6))
    ax.barh(df["skills"], df["job_count"], color=SERIES, height=0.6, zorder=3)
    for y, v in enumerate(df["job_count"]):
        ax.text(v + 1200, y, f"{v:,}", va="center", fontsize=9, color=INK_MUTED)

    ax.set_xlim(0, df["job_count"].max() * 1.14)
    ax.grid(axis="y", visible=False)
    ax.set_xticks([])
    titled(ax, "Top 5 most in-demand Data Analyst skills",
           "Postings requiring each skill, all Data Analyst postings")
    save(fig, "03_top_demanded_skills.png")


def chart_4_top_paying_skills():
    df = pd.read_csv(DATA / "query4_top_paying_skills.csv").sort_values("avg_salary")

    fig, ax = plt.subplots(figsize=(8.5, 8))
    y = range(len(df))
    ax.hlines(y, 104_000, df["avg_salary"], color="#d6d5d0", linewidth=1.4, zorder=2)
    ax.scatter(df["avg_salary"], y, s=64, color=SERIES, zorder=3)
    ax.set_yticks(list(y), df["skills"])

    for i, (v, n) in enumerate(zip(df["avg_salary"], df["postings_count"])):
        ax.text(v + 700, i, f"${v/1000:,.1f}k  ({n})", va="center",
                fontsize=8.5, color=INK_MUTED)

    ax.set_xlim(104_000, df["avg_salary"].max() * 1.055)
    ax.set_xticks([105_000, 110_000, 115_000, 120_000, 125_000, 130_000])
    ax.xaxis.set_major_formatter(lambda v, _: f"${v/1000:,.0f}k")
    ax.set_ylim(-0.8, len(df) - 0.2)
    ax.grid(axis="y", visible=False)
    titled(ax, "Top 25 highest-paying Data Analyst skills",
           "Average yearly salary; posting count in brackets; skills with 25+ postings")
    save(fig, "04_top_paying_skills.png")


def chart_5_optimal_skills():
    df = pd.read_csv(DATA / "query5_optimal_skills.csv")
    top_demand = df.nlargest(10, "demand_count").sort_values("demand_count")
    top_pay = df.nlargest(10, "avg_salary").sort_values("avg_salary")

    fig, (ax_d, ax_p) = plt.subplots(2, 1, figsize=(8.5, 9))

    y = range(10)
    ax_d.hlines(y, 0, top_demand["demand_count"], color="#d6d5d0",
                linewidth=1.4, zorder=2)
    ax_d.scatter(top_demand["demand_count"], y, s=64, color=SERIES, zorder=3)
    ax_d.set_yticks(list(y), top_demand["skills"])
    for i, (v, s) in enumerate(zip(top_demand["demand_count"],
                                   top_demand["avg_salary"])):
        ax_d.text(v + 110, i, f"{v:,}  (${s/1000:,.0f}k)", va="center",
                  fontsize=8.5, color=INK_MUTED)
    ax_d.set_xlim(0, top_demand["demand_count"].max() * 1.30)
    ax_d.set_xticks([])
    ax_d.grid(axis="y", visible=False)
    titled(ax_d, "Most in demand",
           "Postings requiring the skill; average salary in brackets; skills with 30+ postings")

    ax_p.hlines(y, 111_000, top_pay["avg_salary"], color="#d6d5d0",
                linewidth=1.4, zorder=2)
    ax_p.scatter(top_pay["avg_salary"], y, s=64, color=SERIES, zorder=3)
    ax_p.set_yticks(list(y), top_pay["skills"])
    for i, (v, n) in enumerate(zip(top_pay["avg_salary"],
                                   top_pay["demand_count"])):
        ax_p.text(v + 900, i, f"${v/1000:,.1f}k  ({n:,})", va="center",
                  fontsize=8.5, color=INK_MUTED)
    ax_p.set_xlim(111_000, top_pay["avg_salary"].max() * 1.06)
    ax_p.set_xticks([])
    ax_p.grid(axis="y", visible=False)
    titled(ax_p, "Best paid",
           "Average yearly salary; posting count in brackets; skills with 30+ postings")

    ax_d.set_ylim(-0.7, 9.6)
    ax_p.set_ylim(-0.7, 9.6)
    fig.subplots_adjust(hspace=0.34)
    save(fig, "05_optimal_skills.png")


if __name__ == "__main__":
    chart_1_top_paying_jobs()
    chart_3_top_demanded_skills()
    chart_4_top_paying_skills()
    chart_5_optimal_skills()
