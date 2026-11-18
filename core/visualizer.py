"""
Visualizer module for Student Result Management System.
Uses Matplotlib to generate clean charts for computational analysis:
1. Subject-wise average performance bar chart
2. Grade distribution pie/donut chart
3. Score spread histogram
"""

import os
from typing import List, Dict, Any
import matplotlib
# Use Agg backend for non-GUI headless image generation
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def generate_all_charts(students: List[Dict[str, Any]], stats: Dict[str, Any], output_dir: str) -> Dict[str, str]:
    """
    Generates all analytical charts and saves them as PNG files.
    Returns a dictionary of chart names to file paths.
    """
    os.makedirs(output_dir, exist_ok=True)
    chart_paths = {}

    if not students:
        return chart_paths

    # Set aesthetic styles
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.size"] = 10

    # 1. Subject-wise Average Bar Chart
    subj_stats = stats.get("subject_stats", {})
    if subj_stats:
        subjects = list(subj_stats.keys())
        averages = [subj_stats[s]["average"] for s in subjects]
        highests = [subj_stats[s]["highest"] for s in subjects]
        lowests = [subj_stats[s]["lowest"] for s in subjects]

        # Shorten subject names for clean horizontal label display if needed
        short_names = [s.replace("Programming", "Prog.").replace("Professional Communication", "Prof. Comm.") for s in subjects]

        fig, ax = plt.subplots(figsize=(9, 5))
        x = np.arange(len(short_names))
        width = 0.55

        bars = ax.bar(x, averages, width, color="#2563eb", alpha=0.85, edgecolor="#1e40af", label="Class Average")
        ax.axhline(40, color="#dc2626", linestyle="--", linewidth=1.5, label="Passing Threshold (40%)")

        # Add values on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f"{height:.1f}%",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontweight="bold",
                color="#1e293b",
            )

        ax.set_ylabel("Average Marks (out of 100)", fontweight="bold")
        ax.set_title("Subject-wise Academic Performance Analysis", fontsize=14, fontweight="bold", pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels(short_names, rotation=15, ha="right", fontweight="medium")
        ax.set_ylim(0, 110)
        ax.legend(loc="upper right", frameon=True)
        plt.tight_layout()

        chart1_path = os.path.join(output_dir, "subject_averages.png")
        fig.savefig(chart1_path, dpi=200)
        plt.close(fig)
        chart_paths["subject_averages"] = chart1_path

    # 2. Grade Distribution Donut Chart
    grade_dist = stats.get("grade_distribution", {})
    if grade_dist and any(count > 0 for count in grade_dist.values()):
        labels = [g for g, count in grade_dist.items() if count > 0]
        counts = [grade_dist[g] for g in labels]

        color_palette = {
            "A+": "#10b981",  # emerald
            "A": "#06b6d4",   # cyan
            "B+": "#3b82f6",  # blue
            "B": "#6366f1",   # indigo
            "C": "#f59e0b",   # amber
            "D": "#f97316",   # orange
            "F": "#ef4444",   # red
        }
        colors = [color_palette.get(g, "#94a3b8") for g in labels]

        fig, ax = plt.subplots(figsize=(7, 5))
        wedges, texts, autotexts = ax.pie(
            counts,
            labels=labels,
            autopct="%1.1f%%",
            startangle=140,
            colors=colors,
            pctdistance=0.75,
            wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2),
        )

        for text in texts:
            text.set_color("#1e293b")
            text.set_fontweight("bold")
        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontweight("bold")

        ax.set_title("Overall Class Grade Distribution", fontsize=14, fontweight="bold", pad=15)
        plt.tight_layout()

        chart2_path = os.path.join(output_dir, "grade_distribution.png")
        fig.savefig(chart2_path, dpi=200)
        plt.close(fig)
        chart_paths["grade_distribution"] = chart2_path

    # 3. Score Distribution Histogram
    percentages = [s["percentage"] for s in students]
    if percentages:
        fig, ax = plt.subplots(figsize=(8, 4.8))
        bins = [0, 40, 50, 60, 70, 80, 90, 100]
        n, _, patches = ax.hist(percentages, bins=bins, edgecolor="#1e293b", linewidth=1.2, color="#0ea5e9", alpha=0.8)

        # Highlight failing bracket in red
        if len(patches) > 0:
            patches[0].set_facecolor("#ef4444")

        ax.axvline(stats["class_average"], color="#e11d48", linestyle="-", linewidth=2, label=f"Class Mean ({stats['class_average']:.1f}%)")
        ax.axvline(stats["median_percentage"], color="#8b5cf6", linestyle=":", linewidth=2, label=f"Median ({stats['median_percentage']:.1f}%)")

        ax.set_xlabel("Percentage (%)", fontweight="bold")
        ax.set_ylabel("Number of Students", fontweight="bold")
        ax.set_title("Student Percentage Distribution & Centroids", fontsize=14, fontweight="bold", pad=15)
        ax.set_xticks(bins)
        ax.legend(loc="upper left", frameon=True)
        plt.tight_layout()

        chart3_path = os.path.join(output_dir, "score_distribution.png")
        fig.savefig(chart3_path, dpi=200)
        plt.close(fig)
        chart_paths["score_distribution"] = chart3_path

    return chart_paths
