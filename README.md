# CodeAlpha Web Scraping

This project collects quote text and author names from [Quotes to Scrape](https://quotes.toscrape.com/), a website intended for scraping practice. It follows the site's pagination and saves one row per unique quote.

## Run

From this folder, install the dependencies listed in `requirements.txt` and run the script:

```powershell
python -m pip install -r requirements.txt
python web_scraper.py
```

The script writes `scraped_quotes.csv` beside `web_scraper.py`. It checks HTTP responses, uses a request timeout, pauses briefly between pages, and reports unexpected page structure instead of silently saving incomplete data.

To run the Streamlit app locally:

```powershell
streamlit run streamlit_app.py
```

For Streamlit Community Cloud, set the app's main file path to `streamlit_app.py`. The app shows saved quotes on startup in a searchable table with quote, author, and image columns, and includes a button to scrape the latest quotes.

To run the offline tests:

```powershell
python -m unittest -v
```

## Output

The CSV contains:

| Column | Description |
| --- | --- |
| `quote` | Quote text as displayed on the site |
| `author` | Author name as displayed on the site |
| `image_url` | Deterministic generic image URL displayed beneath the quote |

The source site does not provide quote images. The scraper assigns each quote a stable, seeded placeholder image from Picsum Photos; these are decorative images, not author portraits or images from the source site. They require an internet connection to load.

```python
import csv
from web_scraper import display_quotes

with open("scraped_quotes.csv", encoding="utf-8", newline="") as csv_file:
    display_quotes(list(csv.DictReader(csv_file)))
```

In the notebook, each quote and author are displayed first, followed by its image.

The website can change, so the number of records may vary between runs. The checked-in CSV is a sample snapshot; rerun the scraper to refresh it.

## Files

- `web_scraper.py` — paginated scraper and CSV writer
- `streamlit_app.py` — Streamlit interface for displaying and scraping quotes
- `scraped_quotes.csv` — sample output
- `test_web_scraper.py` — offline tests for scraping and notebook display order
