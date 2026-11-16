# CodeAlpha Web Scraping

This project collects quote text and author names from [Quotes to Scrape](https://quotes.toscrape.com/), a website intended for scraping practice. It follows the site's pagination and saves one row per unique quote.

## Run

From this folder, install the dependencies listed in `requirements.txt` and run the script:

```powershell
python -m pip install -r requirements.txt
python web_scraper.py
```

The script writes `scraped_quotes.csv` beside `web_scraper.py`. It checks HTTP responses, uses a request timeout, pauses briefly between pages, and reports unexpected page structure instead of silently saving incomplete data.

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

The website can change, so the number of records may vary between runs. The checked-in CSV is a sample snapshot; rerun the scraper to refresh it.

## Files

- `web_scraper.py` — paginated scraper and CSV writer
- `scraped_quotes.csv` — sample output
- `test_web_scraper.py` — offline tests for pagination and HTTP failures
