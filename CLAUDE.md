# x-milei

Automated pipeline that scrapes @JMilei tweets from X/Twitter, analyzes word frequency and posting patterns, and publishes results to GitHub Pages.

## Tech Stack

- Python 3.11 (GitHub Actions) / 3.8+ (local)
- httpx for direct GraphQL API calls to Twitter (no third-party scraping library)
- pandas + openpyxl for data processing and Excel export
- matplotlib (static PNGs) + plotly (interactive HTML) for charts
- GitHub Actions for cron scheduling (8am, 4pm, midnight ART)
- GitHub Pages for deployment

## Project Structure

```
src/config.py    - Constants, paths, Spanish stop words (~120 words)
src/scraper.py   - Twitter GraphQL API scraping with browser cookies
src/exporter.py  - JSON → Excel export (Date dd/mm/yyyy, Time, Text, Type)
src/analyzer.py  - Word frequency by day + posts per hour (ART timezone)
src/charts.py    - Heatmap (words/day) + bar chart (posts/hour)
src/site.py      - GitHub Pages index.html generation
main.py          - Orchestrator: runs all stages sequentially
```

## Authentication

Uses browser cookies (`auth_token` and `ct0`) instead of username/password login. Stored as GitHub secrets `X_AUTH_TOKEN` and `X_CT0`. If cookies expire, extract new ones from browser DevTools > Application > Cookies > x.com.

## GraphQL Query IDs

Twitter rotates GraphQL query IDs periodically. Current IDs are in `src/scraper.py`. If scraping returns 404, these need updating from https://github.com/trevorhobenshield/twitter-api-client/blob/main/twitter/constants.py

## Commands

```bash
# Run locally (requires X_AUTH_TOKEN and X_CT0 env vars)
export X_AUTH_TOKEN=xxx X_CT0=xxx
python main.py

# Install dependencies
pip install -r requirements.txt
```

## Key Decisions

- Stop words are hardcoded (no NLTK dependency) in src/config.py
- All timestamps converted to ART (UTC-3) for analysis
- Incremental scraping via data/last_run.json
- Deduplication by tweet ID on merge
- `from __future__ import annotations` needed in all src/ files for Python 3.8 compat

## GitHub

- Repo: github.com/FUranga/x-milei
- Pages: furanga.github.io/x-milei
- Remote: SSH (git@github.com:FUranga/x-milei.git)
