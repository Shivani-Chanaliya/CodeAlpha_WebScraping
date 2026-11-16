import unittest
from unittest.mock import patch

import requests

from web_scraper import scrape_quotes


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
            quotes,
            [
                {"quote": "First quote", "author": "Writer A"},
                {"quote": "Second quote", "author": "Writer B"},
            ],
        )
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


if __name__ == "__main__":
    unittest.main()
