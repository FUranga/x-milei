from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from twikit import Client

from .config import (
    DATA_DIR,
    LAST_RUN_PATH,
    RAW_TWEETS_PATH,
    SCRAPE_START_DATE,
    TARGET_USER,
)

COOKIES_PATH = Path("cookies.json")


async def get_client() -> Client:
    client = Client("en-US")
    if COOKIES_PATH.exists():
        client.load_cookies(str(COOKIES_PATH))
    else:
        await client.login(
            auth_info_1=os.environ["X_USERNAME"],
            auth_info_2=os.environ["X_EMAIL"],
            password=os.environ["X_PASSWORD"],
        )
        client.save_cookies(str(COOKIES_PATH))
    return client


def parse_tweet_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%a %b %d %H:%M:%S %z %Y")


def tweet_to_dict(tweet) -> dict:
    is_repost = tweet.retweeted_tweet is not None
    return {
        "id": tweet.id,
        "created_at": tweet.created_at,
        "full_text": tweet.full_text,
        "is_repost": is_repost,
        "type": "Repost" if is_repost else "Post",
    }


async def scrape_tweets(since_date: datetime, client: Client) -> list[dict]:
    user = await client.get_user_by_screen_name(TARGET_USER)
    tweets = []

    results = await client.get_user_tweets(user.id, "Tweets", count=40)

    while results:
        stop = False
        for tweet in results:
            tweet_date = parse_tweet_date(tweet.created_at)
            if tweet_date < since_date:
                stop = True
                break
            tweets.append(tweet_to_dict(tweet))

        if stop:
            break

        await asyncio.sleep(2)
        try:
            results = await results.next()
        except Exception:
            break

    print(f"Scraped {len(tweets)} tweets since {since_date.isoformat()}")
    return tweets


def load_existing_tweets() -> list[dict]:
    if RAW_TWEETS_PATH.exists():
        with open(RAW_TWEETS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def merge_tweets(existing: list[dict], new: list[dict]) -> list[dict]:
    by_id = {t["id"]: t for t in existing}
    for t in new:
        by_id[t["id"]] = t
    merged = sorted(by_id.values(), key=lambda t: t["created_at"], reverse=True)
    return merged


def save_tweets(tweets: list[dict]):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(RAW_TWEETS_PATH, "w", encoding="utf-8") as f:
        json.dump(tweets, f, ensure_ascii=False, indent=2)


def get_since_date() -> datetime:
    if LAST_RUN_PATH.exists():
        with open(LAST_RUN_PATH, "r") as f:
            data = json.load(f)
        return datetime.fromisoformat(data["last_scrape_at"])
    return SCRAPE_START_DATE


def save_last_run():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(LAST_RUN_PATH, "w") as f:
        json.dump({"last_scrape_at": datetime.now(timezone.utc).isoformat()}, f)
