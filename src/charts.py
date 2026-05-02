from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .config import CHARTS_DIR


def chart_words_per_day(df: pd.DataFrame, output_dir: Path | None = None):
    if output_dir is None:
        output_dir = CHARTS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    if df.empty:
        print("No word frequency data to chart.")
        return

    pivot = df.pivot_table(index="word", columns="date", values="count", fill_value=0)

    top_words = df.groupby("word")["count"].sum().nlargest(20).index
    pivot = pivot.loc[pivot.index.isin(top_words)]

    # Matplotlib heatmap
    fig, ax = plt.subplots(figsize=(max(12, len(pivot.columns) * 0.8), 8))
    im = ax.imshow(pivot.values, aspect="auto", cmap="YlOrRd")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=45, ha="right", fontsize=7)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=9)
    ax.set_title("Palabras más frecuentes por día - @JMilei", fontsize=14)
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Palabra")
    plt.colorbar(im, ax=ax, label="Frecuencia")
    plt.tight_layout()
    plt.savefig(output_dir / "words_per_day.png", dpi=150)
    plt.close()

    # Plotly interactive
    fig = px.imshow(
        pivot.values,
        x=list(pivot.columns),
        y=list(pivot.index),
        color_continuous_scale="YlOrRd",
        labels={"x": "Fecha", "y": "Palabra", "color": "Frecuencia"},
        title="Palabras más frecuentes por día - @JMilei",
        aspect="auto",
    )
    fig.update_xaxes(tickangle=45)
    fig.write_html(output_dir / "words_per_day.html", full_html=True, include_plotlyjs="cdn")

    print("Generated words_per_day charts.")


def chart_posts_per_hour(series: pd.Series, output_dir: Path | None = None):
    if output_dir is None:
        output_dir = CHARTS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    hours = list(range(24))
    counts = [series.get(h, 0) for h in hours]
    labels = [f"{h:02d}:00" for h in hours]

    # Matplotlib bar chart
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(hours, counts, color="#1DA1F2", edgecolor="white")
    ax.set_xticks(hours)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_xlabel("Hora (ART, UTC-3)")
    ax.set_ylabel("Cantidad de publicaciones")
    ax.set_title("Publicaciones por hora del día - @JMilei", fontsize=14)

    for bar, count in zip(bars, counts):
        if count > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                    str(count), ha="center", va="bottom", fontsize=8)

    plt.tight_layout()
    plt.savefig(output_dir / "posts_per_hour.png", dpi=150)
    plt.close()

    # Plotly interactive
    fig = px.bar(
        x=labels,
        y=counts,
        labels={"x": "Hora (ART, UTC-3)", "y": "Cantidad de publicaciones"},
        title="Publicaciones por hora del día - @JMilei",
    )
    fig.update_traces(marker_color="#1DA1F2")
    fig.write_html(output_dir / "posts_per_hour.html", full_html=True, include_plotlyjs="cdn")

    print("Generated posts_per_hour charts.")
