from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .config import ART, DOCS_DIR, parse_tweet_date

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Análisis de Tweets - @JMilei</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f1419;
            color: #e7e9ea;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1100px;
            margin: 0 auto;
            padding: 2rem 1rem;
        }}
        h1 {{
            font-size: 2rem;
            margin-bottom: 0.5rem;
            color: #1da1f2;
        }}
        .subtitle {{
            color: #71767b;
            margin-bottom: 2rem;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .stat-card {{
            background: #16202a;
            border: 1px solid #2f3336;
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
        }}
        .stat-card .number {{
            font-size: 2rem;
            font-weight: bold;
            color: #1da1f2;
        }}
        .stat-card .label {{
            color: #71767b;
            font-size: 0.9rem;
        }}
        .section {{
            margin-bottom: 2rem;
        }}
        .section h2 {{
            font-size: 1.4rem;
            margin-bottom: 1rem;
            border-bottom: 1px solid #2f3336;
            padding-bottom: 0.5rem;
        }}
        .chart-container {{
            background: #16202a;
            border: 1px solid #2f3336;
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1rem;
        }}
        .chart-container img {{
            width: 100%;
            height: auto;
            border-radius: 8px;
        }}
        a {{
            color: #1da1f2;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .links {{
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            margin-top: 0.5rem;
        }}
        .btn {{
            display: inline-block;
            background: #1da1f2;
            color: #fff;
            padding: 0.6rem 1.2rem;
            border-radius: 9999px;
            font-weight: bold;
            font-size: 0.9rem;
        }}
        .btn:hover {{
            background: #1a91da;
            text-decoration: none;
        }}
        footer {{
            text-align: center;
            color: #71767b;
            margin-top: 3rem;
            font-size: 0.85rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Análisis de Tweets - @JMilei</h1>
        <p class="subtitle">Última actualización: {last_updated}</p>

        <div class="stats">
            <div class="stat-card">
                <div class="number">{total_tweets}</div>
                <div class="label">Total publicaciones</div>
            </div>
            <div class="stat-card">
                <div class="number">{total_posts}</div>
                <div class="label">Posts originales</div>
            </div>
            <div class="stat-card">
                <div class="number">{total_reposts}</div>
                <div class="label">Reposts</div>
            </div>
            <div class="stat-card">
                <div class="number">{date_range}</div>
                <div class="label">Período</div>
            </div>
        </div>

        <div class="section">
            <h2>Palabras más frecuentes por día</h2>
            <div class="chart-container">
                <img src="charts/words_per_day.png" alt="Palabras más frecuentes por día">
            </div>
            <div class="links">
                <a href="charts/words_per_day.html" class="btn">Ver gráfico interactivo</a>
            </div>
        </div>

        <div class="section">
            <h2>Publicaciones por hora del día</h2>
            <div class="chart-container">
                <img src="charts/posts_per_hour.png" alt="Publicaciones por hora">
            </div>
            <div class="links">
                <a href="charts/posts_per_hour.html" class="btn">Ver gráfico interactivo</a>
            </div>
        </div>

        <div class="section">
            <h2>Descargar datos</h2>
            <div class="links">
                <a href="data/milei_tweets.xlsx" class="btn">Descargar Excel (.xlsx)</a>
            </div>
        </div>

        <footer>
            <p>Datos recopilados desde el 20/04/2025 · Actualización automática 3 veces al día</p>
        </footer>
    </div>
</body>
</html>
"""


def generate_index_html(tweets: list[dict]):
    total = len(tweets)
    posts = sum(1 for t in tweets if not t.get("is_repost", False))
    reposts = total - posts

    if tweets:
        dates = []
        for t in tweets:
            try:
                dates.append(parse_tweet_date(t["created_at"]))
            except (ValueError, KeyError):
                pass
        if dates:
            min_d = min(dates)
            max_d = max(dates)
            date_range = f"{min_d.strftime('%d/%m')} - {max_d.strftime('%d/%m/%Y')}"
        else:
            date_range = "N/A"
    else:
        date_range = "Sin datos"

    now = datetime.now(ART)
    last_updated = now.strftime("%d/%m/%Y %H:%M ART")

    html = HTML_TEMPLATE.format(
        last_updated=last_updated,
        total_tweets=total,
        total_posts=posts,
        total_reposts=reposts,
        date_range=date_range,
    )

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    with open(DOCS_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Generated index.html ({total} tweets)")
