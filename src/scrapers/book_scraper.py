import time

from common.constants import BaseConstants, BookConstants
from scrapers.base_scraper import BaseScraper


class BookScraper(BaseScraper):
    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def _get_total_books(books: str) -> int:
        """Get the numeric value of the total number of books.

        :param books: Number of books as a string.
        :return: Total number of books.
        """
        total_books = int(books.replace(" books", "").replace(",", ""))

        return total_books

    def _get_number_of_pages(self, total_books: int) -> int:
        """Get the number of pages per book list.

        :param total_books: Total number of books per book list.
        :return: Number of pages per book list.
        """
        number_of_pages = int((total_books + 1) / self._pages)

        if number_of_pages >= self._pages:
            return self._pages

        return number_of_pages

    def get_book_lists_urls(self) -> list[str]:
        """Get a list of URLs for book lists.

        :return: A list of URLs.
        """
        filepath = BaseConstants.PROCESSED_DATA_DIR.joinpath(
            "popular_lists.parquet.gz"
        )
        popular_lists_df = self._read_to_df(filepath=filepath)

        book_lists_urls = []

        for _, row in popular_lists_df.iterrows():
            book_list_url = row["book_list_url"]
            books = row["books"]

            total_books = self._get_total_books(books=books)
            number_of_pages = self._get_number_of_pages(
                total_books=total_books
            )

            urls = [
                f"{book_list_url}?page={page}"
                for page in range(1, number_of_pages + 1)
            ]

            book_lists_urls.extend(urls)

        return book_lists_urls

    async def save_books(self) -> None:
        """Save the HTML data from the books pages.

        :return: None.
        """
        book_lists_urls = self.get_book_lists_urls()
        grouped_book_lists_urls = self._group_urls(urls=book_lists_urls)

        for batch, urls in enumerate(grouped_book_lists_urls, start=1):
            start = time.perf_counter()
            self._logger.info(
                f"Scraping book lists for batch '{batch}' of "
                f"'{len(urls)}' items have been started"
            )

            await self.save_data(
                urls=book_lists_urls,
                batch=batch,
                file_prefix=BookConstants.FILE_PREFIX,
            )

            end = time.perf_counter()
            self._logger.info(
                f"Scraping book lists for batch '{batch}' "
                f"took {end - start:.3f} seconds"
            )
