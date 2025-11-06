import time

from common.constants import BaseConstants, BookDetailsConstants
from scrapers.base_scraper import BaseScraper


class BookDetailsScraper(BaseScraper):
    def __init__(self) -> None:
        super().__init__()

    def get_books_urls(self) -> list[str]:
        """Get a list of books URLs.

        :return: List of URLs.
        """
        filepath = BaseConstants.PROCESSED_DATA_DIR.joinpath(
            BaseConstants.CURRENT_DATE, "books.parquet.gz"
        )
        books_df = self._read_to_df(filepath=filepath)

        books_urls = books_df["book_url"].unique()

        return books_urls

    async def save_books_details(self) -> None:
        """Save the HTML data from the books details pages.

        :return: None.
        """
        books_urls = self.get_books_urls()
        grouped_books_urls = self._group_urls(urls=books_urls)

        for batch, urls in enumerate(grouped_books_urls, start=1):
            start = time.perf_counter()
            self._logger.info(
                f"Scraping books details for batch '{batch}' of "
                f"'{len(urls)}' items have been started"
            )

            await self.save_data(
                urls=urls,
                batch=batch,
                file_prefix=BookDetailsConstants.FILE_PREFIX,
            )

            end = time.perf_counter()
            self._logger.info(
                f"Scraping books details for batch '{batch}' "
                f"took {end - start:.3f} seconds"
            )
