"""Build the README charts from the query result sets in charts/data/.

Run from the repository root:

    .venv/Scripts/python charts/make_charts.py     # Windows
    .venv/bin/python charts/make_charts.py         # macOS / Linux

Each CSV in charts/data/ is the result of the matching file in project_sql/,
exported from PostgreSQL. Every chart is written to assets/ as a PNG.

All figures share one width so they render at the same size in the README, and
the type is sized to match the body text of the page at GitHub's content width.
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

# Every figure is this wide, and is saved without a tight bounding box, so all
# four PNGs come out at exactly the same pixel width and GitHub scales them
# identically. Only the height varies.
FIG_W = 9.0
DPI = 200
FS_BODY = 12.5
FS_TITLE = 16
FS_SUB = 12
FS_LABEL = 11.5

# Seaborn's whitegrid theme supplies the base; the overrides set colour and type.
plt.style.use("seaborn-v0_8-whitegrid")

SURFACE = "#ffffff"
INK = "#111111"
INK_MUTED = "#4a4a48"
SERIES = "#2a78d6"
TRACK = "#f0efec"
STEM = "#dedcd7"

plt.rcParams.update({
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "font.family": "DejaVu Sans",
    "font.size": FS_BODY,
    "text.color": INK,
    "axes.labelcolor": INK_MUTED,
    "axes.labelsize": FS_LABEL,
    "xtick.color": INK_MUTED,
    "ytick.color": INK_MUTED,
    "xtick.labelsize": FS_LABEL,
    "ytick.labelsize": FS_LABEL,
    "grid.color": "#eceae5",
    "grid.linewidth": 1.0,
})


def new_figure(height):
    """A figure of the shared width, with room reserved for the title block."""
    fig, ax = plt.subplots(figsize=(FIG_W, height), layout="constrained")
    # Reserve space in inches, converted to figure fractions, so the title block
    # and footnote occupy the same absolute space on every chart.
    fig.get_layout_engine().set(
        rect=(0.012, 0.25 / height, 0.976, 1 - (1.05 + 0.25) / height)
    )
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)
    ax.tick_params(length=0)
    return fig, ax


def titled(fig, height, title, subtitle):
    """Title block above the plot."""
    fig.text(0.012, 1 - 0.30 / height, title, fontsize=FS_TITLE,
             fontweight="bold", color=INK, va="top")
    fig.text(0.012, 1 - 0.66 / height, subtitle, fontsize=FS_SUB,
             color=INK_MUTED, va="top")


def save(fig, name):
    path = ASSETS / name
    fig.savefig(path, dpi=DPI)
    plt.close(fig)
    print(f"wrote {path.relative_to(ROOT)}")


def chart_1_top_paying_jobs():
    df = pd.read_csv(DATA / "query1_top_paying_jobs.csv").sort_values("salary_year_avg")
    height = 7.4

    labels = [
        f"{title[:34] + '...' if len(title) > 34 else title}\n{company}"
        for title, company in zip(df["job_title"], df["company_name"])
    ]
    top = df["salary_year_avg"].max()

    fig, ax = new_figure(height)
    rows = range(len(df))
    # A faint full-width track behind each bar carries the scale.
    ax.barh(rows, top * 1.16, color=TRACK, height=0.66, zorder=1)
    ax.barh(rows, df["salary_year_avg"], color=SERIES, height=0.66, zorder=3)
    ax.set_yticks(list(rows), labels)

    for row, salary in enumerate(df["salary_year_avg"]):
        ax.text(salary + top * 0.015, row, f"${salary/1000:,.0f}k", va="center",
                fontsize=FS_LABEL, color=INK_MUTED)

    ax.set_xlim(0, top * 1.16)
    ax.set_ylim(-0.7, len(df) - 0.3)
    ax.set_xticks([])
    ax.grid(visible=False)
    titled(fig, height, "Top 10 highest-paying Data Analyst postings",
           "Average yearly salary, postings with a disclosed salary")
    save(fig, "01_top_paying_jobs.png")


def chart_3_top_demanded_skills():
    df = pd.read_csv(DATA / "query3_top_demanded_skills.csv").sort_values("job_count")
    height = 4.8

    top = df["job_count"].max()

    fig, ax = new_figure(height)
    rows = range(len(df))
    ax.barh(rows, top * 1.18, color=TRACK, height=0.62, zorder=1)
    ax.barh(rows, df["job_count"], color=SERIES, height=0.62, zorder=3)
    ax.set_yticks(list(rows), df["skills"])

    for row, postings in enumerate(df["job_count"]):
        ax.text(postings + top * 0.018, row, f"{postings:,}", va="center",
                fontsize=FS_LABEL, color=INK_MUTED)

    ax.set_xlim(0, top * 1.18)
    ax.set_ylim(-0.7, len(df) - 0.3)
    ax.set_xticks([])
    ax.grid(visible=False)
    titled(fig, height, "Top 5 most in-demand Data Analyst skills",
           "Postings requiring each skill, all Data Analyst postings")
    save(fig, "03_top_demanded_skills.png")


def chart_4_top_paying_skills():
    df = pd.read_csv(DATA / "query4_top_paying_skills.csv").sort_values("avg_salary")
    height = 10.4
    top = df["avg_salary"].max()

    fig, ax = new_figure(height)
    rows = range(len(df))
    ax.hlines(rows, 104_000, df["avg_salary"], color=STEM, linewidth=1.6, zorder=2)
    ax.scatter(df["avg_salary"], rows, s=90, color=SERIES, zorder=3)
    ax.set_yticks(list(rows), df["skills"])

    for row, (salary, postings) in enumerate(zip(df["avg_salary"],
                                                 df["postings_count"])):
        ax.text(salary + 800, row, f"${salary/1000:,.1f}k  ({postings})",
                va="center", fontsize=FS_LABEL, color=INK_MUTED)

    ax.set_xlim(104_000, top * 1.07)
    ax.set_xticks([105_000, 110_000, 115_000, 120_000, 125_000, 130_000])
    ax.xaxis.set_major_formatter(lambda salary, _: f"${salary/1000:,.0f}k")
    ax.set_ylim(-0.8, len(df) - 0.2)
    ax.grid(axis="y", visible=False)
    titled(fig, height, "Top 25 highest-paying Data Analyst skills",
           "Average yearly salary; posting count in brackets")
    save(fig, "04_top_paying_skills.png")


def chart_5_optimal_skills():
    df = pd.read_csv(DATA / "query5_optimal_skills.csv")
    height = 7.2

    fig, ax = new_figure(height)
    ax.scatter(df["demand_count"], df["avg_salary"], s=95, color=SERIES,
               edgecolor=SURFACE, linewidth=1.4, zorder=3)

    # Hand-placed offsets where neighbouring points would collide.
    offsets = {"azure": (-16, -19), "oracle": (-19, -19), "qlik": (-14, -19),
               "hadoop": (-56, -4), "databricks": (13, 11), "python": (-48, 12),
               "looker": (-62, -4),
               "snowflake": (11, 6)}
    for skill, postings, salary in zip(df["skills"], df["demand_count"],
                                       df["avg_salary"]):
        ax.annotate(skill, (postings, salary), textcoords="offset points",
                    xytext=offsets.get(skill, (11, 5)),
                    fontsize=FS_LABEL, color=INK_MUTED)

    ax.set_xscale("log")
    ax.set_xlim(85, 2700)
    ax.set_ylim(98_500, 115_800)
    ax.set_xticks([100, 200, 500, 1000, 2000])
    ax.xaxis.set_major_formatter(lambda postings, _: f"{postings:,.0f}")
    ax.yaxis.set_major_formatter(lambda salary, _: f"${salary/1000:,.0f}k")
    ax.set_xlabel("Postings requiring the skill (log scale)")
    ax.set_ylabel("Average yearly salary")
    titled(fig, height, "Skills that are both in demand and well paid",
           "Skills with 100+ postings and a $100,000+ average")
    save(fig, "05_optimal_skills.png")


if __name__ == "__main__":
    chart_1_top_paying_jobs()
    chart_3_top_demanded_skills()
    chart_4_top_paying_skills()
    chart_5_optimal_skills()
