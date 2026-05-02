from __future__ import annotations

import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

from .config import DOCS_DATA_DIR, EXCEL_DOCS_PATH, EXCEL_PATH, RAW_TWEETS_PATH

ART = timezone(timedelta(hours=-3))


def parse_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%a %b %d %H:%M:%S %z %Y").astimezone(ART)


def export_to_excel(tweets: list[dict], output_path: Path | None = None):
    if output_path is None:
        output_path = EXCEL_PATH

    df = pd.DataFrame(tweets)
    df["parsed_dt"] = df["created_at"].apply(parse_date)
    df["Fecha"] = df["parsed_dt"].dt.strftime("%d/%m/%Y")
    df["Hora"] = df["parsed_dt"].dt.strftime("%H:%M:%S")
    df["Texto"] = df["full_text"]
    df["Tipo"] = df["type"]

    df = df.sort_values(by="parsed_dt", ascending=False).reset_index(drop=True)
    export_df = df[["Fecha", "Hora", "Texto", "Tipo"]].copy()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    export_df.to_excel(output_path, index=False, engine="openpyxl")

    DOCS_DATA_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(output_path, EXCEL_DOCS_PATH)

    print(f"Exported {len(export_df)} tweets to {output_path}")
