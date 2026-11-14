from __future__ import annotations

from collections import Counter
from datetime import date, timedelta
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "assets" / "repository-streak.svg"
WINDOW_DAYS = 30 * 7


def commit_dates() -> list[date]:
    result = subprocess.run(
        ["git", "log", "--format=%ae%x09%ad", "--date=short", "--no-merges"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    dates = []
    for line in result.stdout.splitlines():
        email, value = line.split("\t", maxsplit=1)
        if email != "41898282+github-actions[bot]@users.noreply.github.com":
            dates.append(date.fromisoformat(value))
    return dates


def streak_lengths(days: set[date]) -> tuple[int, int]:
    if not days:
        return 0, 0

    ordered = sorted(days)
    longest = current = 1
    for previous, following in zip(ordered, ordered[1:]):
        if following == previous + timedelta(days=1):
            current += 1
            longest = max(longest, current)
        else:
            current = 1

    anchor = date.today()
    if anchor not in days:
        anchor -= timedelta(days=1)
    current = 0
    while anchor in days:
        current += 1
        anchor -= timedelta(days=1)
    return current, longest


def activity_grid(days: Counter[date]) -> str:
    today = date.today()
    start = today - timedelta(days=WINDOW_DAYS - 1)
    cells: list[str] = []
    colors = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

    for column in range(30):
        for row in range(7):
            current = start + timedelta(days=column * 7 + row)
            level = min(days[current], 4)
            x = 78 + column * 23
            y = 282 + row * 19
            cells.append(
                f'<rect x="{x}" y="{y}" width="13" height="13" rx="2" '
                f'fill="{colors[level]}"/>'
            )
    return "".join(cells)


def render(total: int, current: int, longest: int, grid: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="430" viewBox="0 0 900 430" role="img" aria-labelledby="title desc">
  <title id="title">Practice streak board for this DSA repository</title>
  <desc id="desc">Repository-only contribution streak dashboard</desc>
  <defs>
    <linearGradient id="card" x1="0" x2="1">
      <stop offset="0" stop-color="#111827"/>
      <stop offset="1" stop-color="#172554"/>
    </linearGradient>
  </defs>
  <rect width="900" height="430" rx="14" fill="#0d1117"/>
  <text x="34" y="46" fill="#f8fafc" font-family="Arial,sans-serif" font-size="28" font-weight="700">Practice Streak Board</text>
  <text x="34" y="77" fill="#cbd5e1" font-family="Arial,sans-serif" font-size="16">Progress recorded from meaningful commits to this repository only.</text>
  <rect x="34" y="102" width="832" height="128" rx="9" fill="url(#card)" stroke="#1f2937"/>
  <line x1="311" y1="122" x2="311" y2="210" stroke="#64748b"/>
  <line x1="589" y1="122" x2="589" y2="210" stroke="#64748b"/>
  <text x="172" y="146" text-anchor="middle" fill="#7dd3fc" font-family="Arial,sans-serif" font-size="16">PROBLEMS SOLVED</text>
  <text x="172" y="187" text-anchor="middle" fill="#f8fafc" font-family="Arial,sans-serif" font-size="38" font-weight="700">0</text>
  <text x="172" y="211" text-anchor="middle" fill="#94a3b8" font-family="Arial,sans-serif" font-size="14">out of 385</text>
  <text x="450" y="146" text-anchor="middle" fill="#7dd3fc" font-family="Arial,sans-serif" font-size="16">CURRENT STREAK</text>
  <circle cx="450" cy="181" r="26" fill="none" stroke="#7c3aed" stroke-width="6" stroke-dasharray="120 44">
    <animateTransform attributeName="transform" type="rotate" from="0 450 181" to="360 450 181" dur="6s" repeatCount="indefinite"/>
  </circle>
  <text x="450" y="190" text-anchor="middle" fill="#f8fafc" font-family="Arial,sans-serif" font-size="25" font-weight="700">{current}</text>
  <text x="450" y="211" text-anchor="middle" fill="#94a3b8" font-family="Arial,sans-serif" font-size="14">practice days</text>
  <text x="728" y="146" text-anchor="middle" fill="#7dd3fc" font-family="Arial,sans-serif" font-size="16">LONGEST STREAK</text>
  <text x="728" y="187" text-anchor="middle" fill="#f8fafc" font-family="Arial,sans-serif" font-size="38" font-weight="700">{longest}</text>
  <text x="728" y="211" text-anchor="middle" fill="#94a3b8" font-family="Arial,sans-serif" font-size="14">days in a row</text>
  <text x="34" y="270" fill="#cbd5e1" font-family="Arial,sans-serif" font-size="15">Activity in this repository</text>
  <text x="34" y="294" fill="#64748b" font-family="Arial,sans-serif" font-size="11">Mon</text>
  <text x="34" y="319" fill="#64748b" font-family="Arial,sans-serif" font-size="11">Wed</text>
  <text x="34" y="344" fill="#64748b" font-family="Arial,sans-serif" font-size="11">Fri</text>
  <g>{grid}</g>
  <text x="34" y="392" fill="#64748b" font-family="Arial,sans-serif" font-size="13">Updated automatically from repository commits.</text>
</svg>
"""


def main() -> None:
    dates = commit_dates()
    counts = Counter(dates)
    current, longest = streak_lengths(set(dates))
    OUTPUT.write_text(
        render(len(dates), current, longest, activity_grid(counts)),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
