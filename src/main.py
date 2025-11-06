import asyncio

from parsers.book_details_parser import BookDetailsParser
from parsers.book_parser import BookParser
from parsers.popular_list_parser import PopularListParser
from scrapers.book_details_scraper import BookDetailsScraper
from scrapers.book_scraper import BookScraper
from scrapers.popular_list_scraper import PopularListScraper


def scrape_popular_lists() -> None:
    """Initialize the process of scraping popular lists.

    :return: None.
    """
    popular_list_scraper = PopularListScraper()

    asyncio.run(popular_list_scraper.save_popular_lists())


def parse_popular_lists() -> None:
    """Initialize the process of parsing popular lists.

    :return: None.
    """
    popular_list_parser = PopularListParser()

    popular_list_parser.save_popular_lists()


def scrape_books() -> None:
    """Initialize the process of scraping books.

    :return: None.
    """
    book_scraper = BookScraper()

    asyncio.run(book_scraper.save_books())


def parse_books() -> None:
    """Initialize the process of parsing books.

    :return: None.
    """
    book_parser = BookParser()

    book_parser.save_books()


def scrape_books_details() -> None:
    """Initialize the process of scraping books details.

    :return: None.
    """
    book_details_scraper = BookDetailsScraper()

    asyncio.run(book_details_scraper.save_books_details())


def parse_books_details() -> None:
    """Initialize the process of parsing books details.

    :return: None.
    """
    book_details_parser = BookDetailsParser()

    book_details_parser.save_books_details()


if __name__ == "__main__":
    scrape_popular_lists()
    parse_popular_lists()

    scrape_books()
    parse_books()

    scrape_books_details()
    parse_books_details()
