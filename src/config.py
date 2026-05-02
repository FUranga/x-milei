from pathlib import Path
from datetime import datetime, timezone

TARGET_USER = "JMilei"
SCRAPE_START_DATE = datetime(2025, 4, 20, tzinfo=timezone.utc)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DIR = PROJECT_ROOT / "docs"
CHARTS_DIR = DOCS_DIR / "charts"
DOCS_DATA_DIR = DOCS_DIR / "data"

RAW_TWEETS_PATH = DATA_DIR / "raw_tweets.json"
LAST_RUN_PATH = DATA_DIR / "last_run.json"
EXCEL_PATH = DATA_DIR / "milei_tweets.xlsx"
EXCEL_DOCS_PATH = DOCS_DATA_DIR / "milei_tweets.xlsx"

SPANISH_STOP_WORDS = {
    # Articles
    "el", "la", "los", "las", "un", "una", "unos", "unas", "lo",
    # Demonstratives
    "este", "esta", "estos", "estas", "ese", "esa", "esos", "esas",
    "aquel", "aquella", "aquellos", "aquellas", "esto", "eso", "aquello",
    # Personal pronouns
    "yo", "tu", "tú", "usted", "él", "ella", "nosotros", "nosotras",
    "vosotros", "vosotras", "ustedes", "ellos", "ellas",
    # Object pronouns
    "me", "te", "se", "nos", "os", "le", "les", "lo", "la", "los", "las",
    # Possessives
    "mi", "mis", "tu", "tus", "su", "sus", "nuestro", "nuestra",
    "nuestros", "nuestras", "vuestro", "vuestra", "vuestros", "vuestras",
    "mí", "ti", "sí", "conmigo", "contigo", "consigo",
    # Prepositions
    "a", "ante", "bajo", "cabe", "con", "contra", "de", "desde",
    "durante", "en", "entre", "hacia", "hasta", "mediante", "para",
    "por", "según", "sin", "so", "sobre", "tras",
    # Conjunctions
    "y", "e", "ni", "o", "u", "pero", "mas", "sino", "aunque",
    "porque", "pues", "que", "si", "como", "cuando", "donde",
    "mientras", "apenas", "luego",
    # Common verbs (ser, estar, haber, ir, tener, hacer, poder, decir)
    "es", "son", "fue", "era", "ser", "sido", "siendo", "soy", "eres",
    "somos", "sois", "sean", "sea", "fuera", "fuese", "será", "serán",
    "estar", "está", "están", "estoy", "estamos", "esté", "estén",
    "estaba", "estaban", "estado", "estando",
    "ha", "han", "hay", "he", "has", "hemos", "haber", "había",
    "habían", "habido", "habiendo", "habrá",
    "ir", "va", "van", "voy", "vamos", "fue", "ido", "yendo",
    "tiene", "tienen", "tengo", "tener", "tenía", "tenido", "teniendo",
    "hace", "hacen", "hago", "hacer", "hizo", "hecho", "haciendo",
    "puede", "pueden", "puedo", "poder", "pudo", "podido", "pudiendo",
    "dice", "dicen", "digo", "decir", "dijo", "dicho", "diciendo",
    # Adverbs and common words
    "no", "sí", "ya", "más", "menos", "muy", "mucho", "mucha",
    "muchos", "muchas", "poco", "poca", "pocos", "pocas",
    "todo", "toda", "todos", "todas", "cada", "otro", "otra",
    "otros", "otras", "mismo", "misma", "mismos", "mismas",
    "tan", "tanto", "tanta", "tantos", "tantas",
    "aquí", "ahí", "allí", "acá", "allá",
    "bien", "mal", "mejor", "peor",
    "también", "tampoco", "además", "solo", "sólo",
    "antes", "después", "ahora", "hoy", "ayer", "mañana",
    "siempre", "nunca", "jamás",
    # Contractions and relative pronouns
    "al", "del", "cual", "cuales", "quien", "quienes",
    "cuyo", "cuya", "cuyos", "cuyas",
    # Question words (without accents, as they appear in tweets)
    "que", "quien", "como", "donde", "cuando", "cuanto", "cuanta",
    # Misc
    "ser", "ver", "dar", "así", "aún", "aun", "sino",
    "entre", "sin", "sobre", "bajo",
    # Common tweet artifacts
    "rt", "https", "http", "co",
}
