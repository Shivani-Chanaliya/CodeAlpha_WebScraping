import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

import requests

from web_scraper import display_quotes, scrape_quotes, save_quotes


class FakeResponse:
    def __init__(self, url, text, error=None):
        self.url = url
        self.text = text
        self.error = error

    def raise_for_status(self):
        if self.error:
            raise self.error


class ScrapeQuotesTests(unittest.TestCase):
    def test_scrapes_all_pages_and_deduplicates_quotes(self):
        first_page = """
        <div class="quote"><span class="text">First quote</span>
        <small class="author">Writer A</small></div>
        <li class="next"><a href="/page/2/">next</a></li>
        """
        second_page = """
        <div class="quote"><span class="text">First quote</span>
        <small class="author">Writer A</small></div>
        <div class="quote"><span class="text">Second quote</span>
        <small class="author">Writer B</small></div>
        """
        responses = [
            FakeResponse("https://quotes.toscrape.com/", first_page),
            FakeResponse("https://quotes.toscrape.com/page/2/", second_page),
        ]

        with patch("web_scraper.requests.get", side_effect=responses) as get:
            with patch("web_scraper.time.sleep"):
                quotes = scrape_quotes()

        self.assertEqual(
            [(quote["quote"], quote["author"]) for quote in quotes],
            [("First quote", "Writer A"), ("Second quote", "Writer B")],
        )
        self.assertTrue(
            all(
                quote["image_url"].startswith("https://picsum.photos/seed/")
                for quote in quotes
            )
        )
        self.assertNotEqual(quotes[0]["image_url"], quotes[1]["image_url"])
        self.assertEqual(get.call_count, 2)
        self.assertEqual(get.call_args.kwargs["timeout"], 15)

    def test_http_failure_is_reported(self):
        response = FakeResponse(
            "https://quotes.toscrape.com/",
            "",
            error=requests.HTTPError("server error"),
        )
        with patch("web_scraper.requests.get", return_value=response):
            with self.assertRaises(requests.HTTPError):
                scrape_quotes()

    def test_unexpected_page_structure_is_reported(self):
        response = FakeResponse("https://quotes.toscrape.com/", "<html></html>")
        with patch("web_scraper.requests.get", return_value=response):
            with self.assertRaisesRegex(ValueError, "No quote cards"):
                scrape_quotes()

    def test_notebook_displays_text_before_image(self):
        display_module = ModuleType("IPython.display")
        display_module.HTML = lambda content: ("html", content)
        display_module.Image = lambda url: ("image", url)
        display_module.display = lambda output: outputs.append(output)
        ipython_module = ModuleType("IPython")
        ipython_module.display = display_module
        outputs = []
        quotes = [
            {
                "quote": "A <quote>",
                "author": "Writer",
                "image_url": "https://example.com/image.jpg",
            }
        ]

        with patch.dict(
            sys.modules,
            {"IPython": ipython_module, "IPython.display": display_module},
        ):
            display_quotes(quotes)

        self.assertEqual(
            outputs,
            [
                ("html", "<p>A &lt;quote&gt;<br><strong>Writer</strong></p>"),
                ("image", "https://example.com/image.jpg"),
            ],
        )

    def test_csv_includes_column_for_supplied_image_urls(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "quotes.csv"
            save_quotes([{"quote": "Text", "author": "Writer"}], output_file)

            with output_file.open(encoding="utf-8", newline="") as csv_file:
                header = csv_file.readline().strip()

        self.assertEqual(header, "quote,author,image_url")


if __name__ == "__main__":
    unittest.main()
