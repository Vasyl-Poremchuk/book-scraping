import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from common.constants import BaseConstants, PopularListConstants
from parsers.base_parser import BaseParser


class PopularListParser(BaseParser):
    def __init__(self) -> None:
        super().__init__(file_prefix=PopularListConstants.FILE_PREFIX)

    def parse_popular_lists(self, raw_filepath: Path) -> list[dict]:
        """Parse the popular lists from the specified files.

        :param raw_filepath: Path to the file to parse.
        :return: List of popular lists.
        """
        popular_lists_data = []

        filename = raw_filepath.name
        html_data = self._read_html_data(filepath=raw_filepath)

        if html_data is None:
            return []

        soup = self.get_soup(html_data=html_data)

        cells = soup.find_all(name="div", attrs={"class": "cell"})

        for cell in cells:
            list_title_tag = cell.find(name="a", attrs={"class": "listTitle"})

            book_list = list_title_tag.text.strip()
            book_list_url = (
                f"{BaseConstants.BASE_URL}{list_title_tag.get('href')}"
            )

            list_full_details = cell.find(
                name="div", attrs={"class": "listFullDetails"}
            ).text.strip()
            books, voters = list_full_details.split("—")

            data = {
                "book_list": book_list,
                "book_list_url": book_list_url,
                "books": books,
                "voters": voters,
            }

            popular_lists_data.append(data)

        return popular_lists_data

    def parse_list_of_popular_lists(self) -> list[dict]:
        """Parse the popular lists from the specified files.

        :return: List of popular lists.
        """
        raw_filepaths = self._get_filepaths(
            data_dir=BaseConstants.RAW_DATA_DIR.joinpath(
                BaseConstants.CURRENT_DATE
            )
        )
        parsed_list_of_popular_lists = []

        start = time.perf_counter()
        self._logger.info(
            f"Parsing popular lists of '{len(raw_filepaths)}' items "
            f"have been started"
        )

        with ProcessPoolExecutor(
            max_workers=BaseConstants.MAX_WORKERS
        ) as executor:
            futures = {
                executor.submit(
                    self.parse_popular_lists, raw_filepath
                ): raw_filepath
                for raw_filepath in raw_filepaths
            }

            for future in as_completed(futures):
                raw_filepath = futures.get(future)
                filename = raw_filepath.name

                try:
                    parsed_popular_lists = future.result()

                    parsed_list_of_popular_lists.extend(parsed_popular_lists)
                except Exception as exc:
                    self._logger.error(
                        f"An exception occurred while parsing '{filename}', due to '{exc}'"
                    )

        end = time.perf_counter()
        self._logger.info(
            f"Parsing popular lists took {end - start:.3f} seconds"
        )

        return parsed_list_of_popular_lists

    def save_popular_lists(self) -> None:
        """Save the popular lists to the specified file.

        :return: None.
        """
        parsed_list_of_popular_lists = self.parse_list_of_popular_lists()
        processed_filepath = self._get_processed_filepath()

        self._save_to_parquet(
            data=parsed_list_of_popular_lists, filepath=processed_filepath
        )
