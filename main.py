from __future__ import annotations

import asyncio

from src.scraper import (
    get_since_date,
    load_existing_tweets,
    merge_tweets,
    save_last_run,
    save_tweets,
    scrape_tweets,
)
from src.exporter import export_to_excel
from src.analyzer import word_frequencies_by_day, posts_per_hour
from src.charts import chart_words_per_day, chart_posts_per_hour
from src.site import generate_index_html


async def main():
    # Stage 1: Scrape
    print("=== Stage 1: Scraping tweets ===")
    since = get_since_date()
    new_tweets = await scrape_tweets(since)
    existing = load_existing_tweets()
    all_tweets = merge_tweets(existing, new_tweets)
    save_tweets(all_tweets)
    save_last_run()

    # Stage 2: Export to Excel
    print("=== Stage 2: Exporting to Excel ===")
    export_to_excel(all_tweets)

    # Stage 3: Analysis
    print("=== Stage 3: Analyzing data ===")
    word_freq_df = word_frequencies_by_day(all_tweets)
    hourly = posts_per_hour(all_tweets)

    # Stage 4: Charts
    print("=== Stage 4: Generating charts ===")
    chart_words_per_day(word_freq_df)
    chart_posts_per_hour(hourly)

    # Generate site
    print("=== Generating site ===")
    generate_index_html(all_tweets)

    print(f"\nDone. {len(new_tweets)} new tweets scraped, {len(all_tweets)} total.")


if __name__ == "__main__":
    asyncio.run(main())
