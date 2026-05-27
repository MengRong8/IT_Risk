from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any


def _truthy(value: Any) -> bool:
    return value in (True, "True", "true", "1", 1)


def create_detection_rate_chart(rows: list[dict[str, Any]], output_path: Path) -> None:
    """Create a detection/accuracy rate chart by email category."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    stats: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "correct": 0})
    for row in rows:
        category = str(row["category"])
        stats[category]["total"] += 1
        if _truthy(row["is_correct"]):
            stats[category]["correct"] += 1

    categories = ["normal", "traditional_phishing", "ai_phishing"]
    labels = ["Normal", "Traditional\nphishing", "AI-style\nphishing"]
    rates = [
        (stats[cat]["correct"] / stats[cat]["total"] * 100) if stats[cat]["total"] else 0
        for cat in categories
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, rates, color=["#70AD47", "#ED7D31", "#5B9BD5"])
    ax.set_ylim(0, 100)
    ax.set_ylabel("Correct detection rate (%)")
    ax.set_title("Rule-based detector accuracy by email category")
    ax.grid(axis="y", linestyle="--", alpha=0.35)

    for bar, rate in zip(bars, rates):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            min(rate + 2, 98),
            f"{rate:.0f}%",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def main() -> None:
    import argparse
    import csv

    parser = argparse.ArgumentParser(description="Create experiment charts")
    parser.add_argument("--input-csv", type=Path, default=Path("results/email_results.csv"))
    parser.add_argument(
        "--output", type=Path, default=Path("results/charts/detection_rate_by_category.png")
    )
    args = parser.parse_args()

    with args.input_csv.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    create_detection_rate_chart(rows, args.output)
    print(args.output)


if __name__ == "__main__":
    main()
