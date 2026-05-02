from __future__ import annotations

import re
from collections import Counter
from datetime import datetime, timedelta, timezone

import pandas as pd

from .config import SPANISH_STOP_WORDS

ART = timezone(timedelta(hours=-3))


def parse_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%a %b %d %H:%M:%S %z %Y").astimezone(ART)


def tokenize(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    tokens = re.findall(r"[a-záéíóúüñ]+", text)
    return [t for t in tokens if len(t) >= 3 and t not in SPANISH_STOP_WORDS]


def word_frequencies_by_day(tweets: list[dict], top_n: int = 15) -> pd.DataFrame:
    original_posts = [t for t in tweets if not t.get("is_repost", False)]

    rows = []
    by_day = {}
    for tweet in original_posts:
        dt = parse_date(tweet["created_at"])
        day = dt.strftime("%Y-%m-%d")
        by_day.setdefault(day, []).append(tweet["full_text"])

    for day, texts in sorted(by_day.items()):
        all_tokens = []
        for text in texts:
            all_tokens.extend(tokenize(text))
        counter = Counter(all_tokens)
        for word, count in counter.most_common(top_n):
            rows.append({"date": day, "word": word, "count": count})

    return pd.DataFrame(rows)


def posts_per_hour(tweets: list[dict]) -> pd.Series:
    hours = []
    for tweet in tweets:
        dt = parse_date(tweet["created_at"])
        hours.append(dt.hour)

    series = pd.Series(hours, name="hour").value_counts().sort_index()
    full_hours = pd.Series(0, index=range(24), name="count")
    full_hours.update(series)
    return full_hours
