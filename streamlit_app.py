import csv

import requests
import streamlit as st

from web_scraper import OUTPUT_FILE, scrape_quotes


def load_saved_quotes():
    if not OUTPUT_FILE.exists():
        return []

    with OUTPUT_FILE.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        if not reader.fieldnames or not {"quote", "author"}.issubset(
            reader.fieldnames
        ):
            raise ValueError("The CSV must contain quote and author columns.")

        return [
            {
                "quote": row["quote"],
                "author": row["author"],
                "image_url": row.get("image_url", ""),
            }
            for row in reader
        ]


st.set_page_config(page_title="Quote Scraper", layout="wide")
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%);
    }
    [data-testid="stHeader"] {
        background: transparent;
    }
    .main .block-container {
        max-width: 1120px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }
    .hero {
        padding: 2.3rem 2.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 24px;
        color: #f8fafc;
        background:
            radial-gradient(circle at 88% 18%, rgba(45, 212, 191, 0.3), transparent 28%),
            linear-gradient(120deg, #172554 0%, #164e63 100%);
        box-shadow: 0 18px 45px rgba(23, 37, 84, 0.16);
    }
    .hero-kicker {
        margin: 0 0 0.6rem;
        color: #99f6e4;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.15em;
        text-transform: uppercase;
    }
    .hero h1 {
        margin: 0;
        color: #ffffff;
        font-size: clamp(2rem, 5vw, 3.2rem);
        line-height: 1.1;
    }
    .hero-copy {
        max-width: 650px;
        margin: 0.8rem 0 0;
        color: #dbeafe;
        font-size: 1.05rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    """
    <div class="hero">
        <p class="hero-kicker">CodeAlpha / Web scraping</p>
        <h1>Words worth keeping.</h1>
        <p class="hero-copy">
            Explore memorable quotes, discover their authors, and see a
            complementary image alongside each quote.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption("Each row contains a quote, its author, and a generic placeholder image.")

if "quotes" not in st.session_state:
    try:
        st.session_state["quotes"] = load_saved_quotes()
    except (OSError, UnicodeError, csv.Error, ValueError) as error:
        st.session_state["quotes"] = []
        st.error(f"Could not load scraped_quotes.csv: {error}")

if st.button("Scrape latest quotes"):
    try:
        quotes = scrape_quotes()
    except (requests.RequestException, RuntimeError, ValueError) as error:
        st.error(f"Scraping failed: {error}")
    else:
        existing_image_urls = {
            (quote["quote"], quote["author"]): quote.get("image_url", "")
            for quote in st.session_state["quotes"]
        }
        for quote in quotes:
            quote["image_url"] = existing_image_urls.get(
                (quote["quote"], quote["author"]), ""
            )
        st.session_state["quotes"] = quotes
        st.success(f"Scraped {len(quotes)} unique quotes.")

quotes = st.session_state["quotes"]
if not quotes:
    st.info("Click 'Scrape latest quotes' to load quotes.")
else:
    image_count = sum(
        bool((quote.get("image_url") or "").strip()) for quote in quotes
    )
    metric_quotes, metric_authors, metric_images = st.columns(3)
    metric_quotes.metric("Quotes", len(quotes))
    metric_authors.metric(
        "Authors", len({quote["author"] for quote in quotes})
    )
    metric_images.metric("Images", image_count)

    search = st.text_input(
        "Find a quote or author",
        placeholder="Search the collection...",
    ).casefold()
    visible_quotes = [
        quote
        for quote in quotes
        if search in quote["quote"].casefold()
        or search in quote["author"].casefold()
    ]
    st.caption(f"Showing {len(visible_quotes)} of {len(quotes)} quotes")

    table_rows = [
        {
            "Quote": quote["quote"],
            "Author": quote["author"],
            "Image": quote.get("image_url", ""),
        }
        for quote in visible_quotes
    ]
    st.dataframe(
        table_rows,
        column_config={
            "Quote": st.column_config.TextColumn("Quote", width="large"),
            "Author": st.column_config.TextColumn("Author", width="medium"),
            "Image": st.column_config.ImageColumn("Image", width="small"),
        },
        hide_index=True,
        use_container_width=True,
    )
