from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import httpx

from .config import (
    DATA_DIR,
    LAST_RUN_PATH,
    RAW_TWEETS_PATH,
    SCRAPE_START_DATE,
    TARGET_USER,
    parse_tweet_date,
)

GRAPHQL_USER_BY_SCREEN_NAME = "https://x.com/i/api/graphql/sLVLhk0bGj3MVFEKTdax1w/UserByScreenName"
GRAPHQL_USER_TWEETS = "https://x.com/i/api/graphql/HuTx74BxAnezK1gWvYY7zg/UserTweets"

FEATURES = {
    "rweb_tipjar_consumption_enabled": True,
    "responsive_web_graphql_exclude_directive_enabled": True,
    "verified_phone_label_enabled": False,
    "creator_subscriptions_tweet_preview_api_enabled": True,
    "responsive_web_graphql_timeline_navigation_enabled": True,
    "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
    "communities_web_enable_tweet_community_results_fetch": True,
    "c9s_tweet_anatomy_moderator_badge_enabled": True,
    "articles_preview_enabled": True,
    "responsive_web_edit_tweet_api_enabled": True,
    "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
    "view_counts_everywhere_api_enabled": True,
    "longform_notetweets_consumption_enabled": True,
    "responsive_web_twitter_article_tweet_consumption_enabled": True,
    "tweet_awards_web_tipping_enabled": False,
    "creator_subscriptions_quote_tweet_preview_enabled": False,
    "freedom_of_speech_not_reach_fetch_enabled": True,
    "standardized_nudges_misinfo": True,
    "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
    "rweb_video_timestamps_enabled": True,
    "longform_notetweets_rich_text_read_enabled": True,
    "longform_notetweets_inline_media_enabled": True,
    "responsive_web_enhance_cards_enabled": False,
    "tweetypie_unmention_optimization_enabled": True,
    "responsive_web_text_conversations_enabled": False,
    "interactive_text_enabled": True,
    "responsive_web_media_download_video_enabled": False,
    "premium_content_api_read_enabled": False,
}


def _build_headers() -> dict:
    auth_token = os.environ.get("X_AUTH_TOKEN")
    ct0 = os.environ.get("X_CT0")
    if not auth_token or not ct0:
        raise RuntimeError("Missing X_AUTH_TOKEN or X_CT0 env vars. Extract from browser DevTools > Application > Cookies > x.com")
    return {
        # Public bearer token shared by all Twitter web clients (not a secret)
        "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
        "cookie": f"auth_token={auth_token}; ct0={ct0}",
        "x-csrf-token": ct0,
        "x-twitter-active-user": "yes",
        "x-twitter-auth-type": "OAuth2Session",
        "x-twitter-client-language": "en",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    }


async def _get_user_id(client: httpx.AsyncClient, screen_name: str) -> str:
    variables = {
        "screen_name": screen_name,
        "withSafetyModeUserFields": True,
    }
    params = {
        "variables": json.dumps(variables),
        "features": json.dumps(FEATURES),
    }
    resp = await client.get(GRAPHQL_USER_BY_SCREEN_NAME, params=params)
    resp.raise_for_status()
    data = resp.json()
    return data["data"]["user"]["result"]["rest_id"]


def _extract_tweets_from_timeline(data: dict) -> tuple[list[dict], str | None]:
    tweets = []
    cursor = None
    instructions = data["data"]["user"]["result"]["timeline_v2"]["timeline"]["instructions"]

    for instruction in instructions:
        if instruction.get("type") == "TimelineAddEntries":
            entries = instruction.get("entries", [])
        elif instruction.get("type") == "TimelineAddToModule":
            entries = instruction.get("moduleItems", [])
        else:
            continue

        for entry in entries:
            entry_id = entry.get("entryId", "")

            if entry_id.startswith("cursor-bottom"):
                cursor = entry["content"]["value"]
                continue

            content = entry.get("content", {})
            if content.get("entryType") != "TimelineTimelineItem":
                continue

            tweet_result = content.get("itemContent", {}).get("tweet_results", {}).get("result", {})
            if not tweet_result:
                continue

            typename = tweet_result.get("__typename", "")
            if typename == "TweetWithVisibilityResults":
                tweet_result = tweet_result.get("tweet", {})

            legacy = tweet_result.get("legacy", {})
            if not legacy:
                continue

            is_repost = "retweeted_status_result" in legacy
            full_text = legacy.get("full_text", "")
            created_at = legacy.get("created_at", "")
            tweet_id = legacy.get("id_str", tweet_result.get("rest_id", ""))

            tweets.append({
                "id": tweet_id,
                "created_at": created_at,
                "full_text": full_text,
                "is_repost": is_repost,
                "type": "Repost" if is_repost else "Post",
            })

    return tweets, cursor


async def scrape_tweets(since_date: datetime) -> list[dict]:
    headers = _build_headers()
    all_tweets = []

    async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
        user_id = await _get_user_id(client, TARGET_USER)
        print(f"User ID for @{TARGET_USER}: {user_id}")

        cursor = None
        page = 0

        while True:
            page += 1
            variables = {
                "userId": user_id,
                "count": 40,
                "includePromotedContent": False,
                "withQuickPromoteEligibilityTweetFields": True,
                "withVoice": True,
                "withV2Timeline": True,
            }
            if cursor:
                variables["cursor"] = cursor

            params = {
                "variables": json.dumps(variables),
                "features": json.dumps(FEATURES),
            }

            resp = await client.get(GRAPHQL_USER_TWEETS, params=params)
            if resp.status_code == 429:
                print("Rate limited, waiting 60s...")
                await asyncio.sleep(60)
                continue
            resp.raise_for_status()

            data = resp.json()
            tweets, cursor = _extract_tweets_from_timeline(data)

            stop = False
            for tweet in tweets:
                if not tweet["created_at"]:
                    continue
                tweet_date = parse_tweet_date(tweet["created_at"])
                if tweet_date < since_date:
                    stop = True
                    break
                all_tweets.append(tweet)

            print(f"Page {page}: got {len(tweets)} tweets (total: {len(all_tweets)})")

            if stop or not cursor or not tweets:
                break

            await asyncio.sleep(2)

    print(f"Scraped {len(all_tweets)} tweets since {since_date.isoformat()}")
    return all_tweets


def load_existing_tweets() -> list[dict]:
    if RAW_TWEETS_PATH.exists():
        with open(RAW_TWEETS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def merge_tweets(existing: list[dict], new: list[dict]) -> list[dict]:
    by_id = {t["id"]: t for t in existing}
    for t in new:
        by_id[t["id"]] = t
    merged = sorted(
        (t for t in by_id.values() if t.get("created_at")),
        key=lambda t: parse_tweet_date(t["created_at"]),
        reverse=True,
    )
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
