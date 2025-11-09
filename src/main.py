import asyncio

from common.constants import (
    BaseConstants,
    BookConstants,
    BookDetailsConstants,
    PopularListConstants,
)
from parsers.book_details_parser import BookDetailsParser
from parsers.book_parser import BookParser
from parsers.popular_list_parser import PopularListParser
from scrapers.book_details_scraper import BookDetailsScraper
from scrapers.book_scraper import BookScraper
from scrapers.popular_list_scraper import PopularListScraper
from uploader.uploader import Uploader


def scrape_popular_lists() -> None:
    """Initialize the process of scraping popular lists.

    :return: None.
    """
    popular_list_scraper = PopularListScraper()

    asyncio.run(popular_list_scraper.save_popular_lists())


def upload_scraped_popular_lists(upl: Uploader) -> None:
    """Upload the scraped popular lists data to an S3 bucket.

    :param upl: An uploader to use.
    :return: None.
    """
    popular_lists_file_keys = upl.get_file_keys(
        base_dir=BaseConstants.RAW_DATA_DIR,
        file_prefix=PopularListConstants.FILE_PREFIX,
    )

    uploader.upload_files(file_keys=popular_lists_file_keys)


def parse_popular_lists() -> None:
    """Initialize the process of parsing popular lists.

    :return: None.
    """
    popular_list_parser = PopularListParser()

    popular_list_parser.save_popular_lists()


def upload_parsed_popular_lists(upl: Uploader) -> None:
    """Upload the parsed popular lists data to an S3 bucket.

    :param upl: An uploader to use.
    :return: None.
    """
    popular_lists_file_keys = upl.get_file_keys(
        base_dir=BaseConstants.PROCESSED_DATA_DIR,
        file_prefix=PopularListConstants.FILE_PREFIX,
    )

    uploader.upload_files(file_keys=popular_lists_file_keys)


def scrape_books() -> None:
    """Initialize the process of scraping books.

    :return: None.
    """
    book_scraper = BookScraper()

    asyncio.run(book_scraper.save_books())


def upload_scraped_books(upl: Uploader) -> None:
    """Upload the scraped books data to an S3 bucket.

    :param upl: An uploader to use.
    :return: None.
    """
    books_file_keys = upl.get_file_keys(
        base_dir=BaseConstants.RAW_DATA_DIR,
        file_prefix=BookConstants.FILE_PREFIX,
    )

    uploader.upload_files(file_keys=books_file_keys)


def parse_books() -> None:
    """Initialize the process of parsing books.

    :return: None.
    """
    book_parser = BookParser()

    book_parser.save_books()


def upload_parsed_books(upl: Uploader) -> None:
    """Upload the parsed books data to an S3 bucket.

    :param upl: An uploader to use.
    :return: None.
    """
    books_file_keys = upl.get_file_keys(
        base_dir=BaseConstants.PROCESSED_DATA_DIR,
        file_prefix=BookConstants.FILE_PREFIX,
    )

    uploader.upload_files(file_keys=books_file_keys)


def scrape_books_details() -> None:
    """Initialize the process of scraping books details.

    :return: None.
    """
    book_details_scraper = BookDetailsScraper()

    asyncio.run(book_details_scraper.save_books_details())


def upload_scraped_books_details(upl: Uploader) -> None:
    """Upload the scraped books details data to an S3 bucket.

    :param upl: An uploader to use.
    :return: None.
    """
    books_details_file_keys = upl.get_file_keys(
        base_dir=BaseConstants.RAW_DATA_DIR,
        file_prefix=BookDetailsConstants.FILE_PREFIX,
    )

    uploader.upload_files(file_keys=books_details_file_keys)


def parse_books_details() -> None:
    """Initialize the process of parsing books details.

    :return: None.
    """
    book_details_parser = BookDetailsParser()

    book_details_parser.save_books_details()


def upload_parsed_books_details(upl: Uploader) -> None:
    """Upload the parsed books details data to an S3 bucket.

    :param upl: An uploader to use.
    :return: None.
    """
    books_details_file_keys = upl.get_file_keys(
        base_dir=BaseConstants.PROCESSED_DATA_DIR,
        file_prefix=BookDetailsConstants.FILE_PREFIX,
    )

    uploader.upload_files(file_keys=books_details_file_keys)


if __name__ == "__main__":
    uploader = Uploader()

    scrape_popular_lists()
    upload_scraped_popular_lists(upl=uploader)

    parse_popular_lists()
    upload_parsed_popular_lists(upl=uploader)

    scrape_books()
    upload_scraped_books(upl=uploader)

    parse_books()
    upload_parsed_books(upl=uploader)

    scrape_books_details()
    upload_scraped_books_details(upl=uploader)

    parse_books_details()
    upload_parsed_books_details(upl=uploader)
