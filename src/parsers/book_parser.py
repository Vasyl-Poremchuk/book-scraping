import re
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path


from common.constants import BaseConstants, BookConstants
from parsers.base_parser import BaseParser


class BookParser(BaseParser):
    def __init__(self) -> None:
        super().__init__(file_prefix=BookConstants.FILE_PREFIX)

    def parse_books(self, raw_filepath: Path) -> list[dict]:
        """Parse the books from the specified file.

        :param raw_filepath: Path to the file to parse.
        :return: List of books.
        """
        html_data = self._read_html_data(filepath=raw_filepath)
        soup = self.get_soup(html_data=html_data)

        tr_tags = soup.find_all(name="tr", attrs={"itemscope": ""})

        books_data = []

        for tr_tag in tr_tags:
            book_title_tag = tr_tag.find(
                name="a", attrs={"class": "bookTitle"}
            )
            book_title = book_title_tag.text.strip()
            book_url = f"{BaseConstants.BASE_URL}{book_title_tag.get('href')}"

            author_name_tag = tr_tag.find(
                name="a", attrs={"class": "authorName"}
            )
            author_name = author_name_tag.text.strip()

            mini_rating_tag = tr_tag.find(
                name="span", attrs={"class": "minirating"}
            )
            mini_rating = mini_rating_tag.text.strip()
            avg_rating, ratings = mini_rating.split("—")

            score, people_voted = None, None

            score_tag = tr_tag.find(name="a", string=re.compile(r"^score:"))  # type: ignore[arg-type]

            if score_tag:
                score = score_tag.text.strip()

            people_voted_tag = (
                tr_tag.find(name="a", string=re.compile(r"people voted$"))  # type: ignore[arg-type]
            )

            if people_voted_tag:
                people_voted = people_voted_tag.text.strip()

            data = {
                "book_title": book_title,
                "book_url": book_url,
                "author_name": author_name,
                "avg_rating": avg_rating,
                "ratings": ratings,
                "score": score,
                "people_voted": people_voted,
            }

            books_data.append(data)

        return books_data

    def parse_list_of_books(self) -> list[dict]:
        """Parse the books from the specified files.

        :return: List of books.
        """
        raw_filepaths = self._get_filepaths(
            data_dir=BaseConstants.RAW_DATA_DIR
        )
        parsed_list_of_books = []

        start = time.perf_counter()
        self._logger.info(
            f"Parsing book lists of '{len(raw_filepaths)}' items "
            f"have been started"
        )

        with ProcessPoolExecutor(
            max_workers=BaseConstants.MAX_WORKERS
        ) as executor:
            futures = {
                executor.submit(self.parse_books, raw_filepath): raw_filepath
                for raw_filepath in raw_filepaths
            }

            for future in as_completed(futures):
                raw_filepath = futures.get(future)
                filename = raw_filepath.name

                try:
                    parsed_books = future.result()

                    parsed_list_of_books.extend(parsed_books)
                except Exception as exc:
                    self._logger.error(
                        f"An exception occurred while parsing '{filename}' "
                        f"due to '{exc}'"
                    )

        end = time.perf_counter()
        self._logger.info(f"Parsing book lists took {end - start:.3f} seconds")

        return parsed_list_of_books

    def save_books(self) -> None:
        """Save the books to the specified file.

        :return: None.
        """
        parsed_list_of_books = self.parse_list_of_books()
        processed_filepath = self._get_processed_filepath()

        self._save_to_parquet(
            data=parsed_list_of_books, filepath=processed_filepath
        )
