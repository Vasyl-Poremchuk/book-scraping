import json
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from string import punctuation
from typing import Any


from common.constants import BaseConstants, BookDetailsConstants
from parsers.base_parser import BaseParser


class BookDetailsParser(BaseParser):
    def __init__(self) -> None:
        super().__init__(file_prefix=BookDetailsConstants.FILE_PREFIX)

    @staticmethod
    def extract_data(json_data: dict[str, Any], key_prefix: str) -> list[Any]:
        """Extract data from JSON by specified key prefix.

        :param json_data: JSON data from which to extract data.
        :param key_prefix: Key prefix to use.
        :return: List of extracted data.
        """
        extracted_data = []

        for key, value in json_data.items():
            if key.startswith(key_prefix) and isinstance(value, dict):
                extracted_data.append(value)
            elif key.startswith(key_prefix) and isinstance(value, list):
                extracted_data += value

        return extracted_data

    @staticmethod
    def normalize_attr(attr: str, attrs_map: dict[str, str] = None) -> str:
        """Normalize the attribute by converting it to snake case
        and removing punctuation characters.

        :param attr: The attribute to normalize.
        :param attrs_map: Attribute mapping for complex cases.
        :return: Normalized attribute.
        """
        if attrs_map and (normalized_attr := attrs_map.get(attr)):
            return normalized_attr

        normalized_attr = ""

        for char in attr:
            if char in punctuation:
                continue

            if char.isupper():
                normalized_attr += f"_{char.lower()}"
            else:
                normalized_attr += char

        return normalized_attr

    def normalize_data(
        self,
        data: list[dict] | dict[str, Any],
        attrs_to_skip: list[str] = None,
        attrs_map: dict[str, str] = None,
    ) -> list[dict]:
        """Normalize data by removing unnecessary attribute values.

        :param data: Data to normalize.
        :param attrs_to_skip: List of attributes to skip.
        :param attrs_map: Attribute mapping for complex cases.
        :return: Normalized data.
        """
        if not data:
            return []

        if isinstance(data, dict):
            data = [data]

        if attrs_to_skip is None:
            attrs_to_skip = []

        normalized_data = []

        for value in data:
            if not isinstance(value, dict):
                normalized_data.append(value)
            else:
                normalized_value = {}

                for attr, attr_value in value.items():
                    if attr in attrs_to_skip:
                        continue

                    normalized_attr = self.normalize_attr(
                        attr=attr, attrs_map=attrs_map
                    )

                    if isinstance(attr_value, dict):
                        normalized_value[normalized_attr] = (
                            self.normalize_data(
                                data=attr_value,
                                attrs_to_skip=attrs_to_skip,
                                attrs_map=attrs_map,
                            )[0]
                        )
                    elif isinstance(attr_value, list):
                        normalized_value[normalized_attr] = (
                            self.normalize_data(
                                data=attr_value,
                                attrs_to_skip=attrs_to_skip,
                                attrs_map=attrs_map,
                            )
                        )
                    else:
                        normalized_value[normalized_attr] = attr_value

                normalized_data.append(normalized_value)

        return normalized_data

    @staticmethod
    def filter_by_genres(data: list[dict], genre_prefix: str = "rus") -> bool:
        """Filter data by unwanted genres.

        :param data: Data to filter.
        :param genre_prefix: The genre prefix filter by.
        :return: True if data needs to be filtered,
            otherwise False if not.
        """
        for value in data:
            book_genres = value.get("book_genres")

            if not book_genres:
                return True

            for inner_value in book_genres:
                genre_name = inner_value.get("genre", {}).get("name")

                if genre_name.lower().startswith(genre_prefix):
                    return True

        return False

    def parse_book_details(self, raw_filepath: Path) -> dict[str, Any]:
        """Parse a book details from the specified files.

        :param raw_filepath: Path to the file to parse.
        :return: Book details.
        """
        html_data = self._read_html_data(filepath=raw_filepath)
        soup = self.get_soup(html_data=html_data)

        book_title_tag = soup.find(
            name="h1", attrs={"data-testid": "bookTitle"}
        )
        book_title = None

        if book_title_tag:
            book_title = book_title_tag.text.strip()

        name_tag = soup.find(name="span", attrs={"data-testid": "name"})
        name = None

        if name_tag:
            name = name_tag.text.strip()

        next_data_tag = soup.find(
            name="script",
            attrs={"id": "__NEXT_DATA__", "type": "application/json"},
        )
        next_data_json = json.loads(next_data_tag.text)
        props = next_data_json.get("props")
        page_props = props.get("pageProps")
        apollo_state = page_props.get("apolloState")
        root_query = apollo_state.get("ROOT_QUERY")

        extracted_social_signals = self.extract_data(
            json_data=root_query, key_prefix="getSocialSignals"
        )
        normalized_social_signals = self.normalize_data(
            data=extracted_social_signals, attrs_to_skip=["imageUrlSquare"]
        )

        extracted_contributors = self.extract_data(
            json_data=apollo_state, key_prefix="Contributor"
        )
        normalized_contributors = self.normalize_data(
            data=extracted_contributors, attrs_to_skip=["profileImageUrl"]
        )

        extracted_series = self.extract_data(
            json_data=apollo_state, key_prefix="Series"
        )
        normalized_series = self.normalize_data(data=extracted_series)

        extracted_book = self.extract_data(
            json_data=apollo_state, key_prefix="Book"
        )
        normalized_book = self.normalize_data(
            data=extracted_book,
            attrs_to_skip=[
                'description({"stripped":true})',
                "featureFlags",
                "imageUrl",
            ],
            attrs_map={"links({})": "links"},
        )

        need_to_filter = self.filter_by_genres(data=normalized_book)

        if need_to_filter:
            return {}

        extracted_work = self.extract_data(
            json_data=apollo_state, key_prefix="Work"
        )
        normalized_work = self.normalize_data(
            data=extracted_work,
            attrs_map={
                'questions({"pagination":{"limit":1}})': "questions",
                'quotes({"pagination":{"limit":1}})': "quotes",
                'topics({"pagination":{"limit":1}})': "topics",
            },
        )

        extracted_users = self.extract_data(
            json_data=apollo_state, key_prefix="User"
        )
        normalized_users = self.normalize_data(
            data=extracted_users, attrs_to_skip=["imageUrlSquare"]
        )

        extracted_reviews = self.extract_data(
            json_data=apollo_state, key_prefix="Review"
        )
        normalized_reviews = self.normalize_data(data=extracted_reviews)

        book_details = {
            "book_title": book_title,
            "name": name,
            "social_signals": normalized_social_signals,
            "contributors": normalized_contributors,
            "series": normalized_series,
            "book": normalized_book,
            "work": normalized_work,
            "users": normalized_users,
            "reviews": normalized_reviews,
        }

        return book_details

    def parse_books_details(self) -> list[dict]:
        """Parse books details from the specified files.

        :return: List of books details.
        """
        raw_filepaths = self._get_filepaths(
            data_dir=BaseConstants.RAW_DATA_DIR
        )
        parsed_books_details = []

        start = time.perf_counter()
        self._logger.info(
            f"Parsing books details of '{len(raw_filepaths)}' items "
            f"have been started"
        )

        with ProcessPoolExecutor(
            max_workers=BaseConstants.MAX_WORKERS
        ) as executor:
            futures = {
                executor.submit(
                    self.parse_book_details, raw_filepath
                ): raw_filepath
                for raw_filepath in raw_filepaths
            }

            for future in as_completed(futures):
                raw_filepath = futures.get(future)
                filename = raw_filepath.name

                try:
                    parsed_book_details = future.result()

                    if not parsed_book_details:
                        continue

                    parsed_books_details.append(parsed_book_details)
                except Exception as exc:
                    self._logger.error(
                        f"An exception occurred while parsing '{filename}' "
                        f"due to '{exc}'"
                    )

        end = time.perf_counter()
        self._logger.info(
            f"Parsing books details took {end - start:.3f} seconds"
        )

        return parsed_books_details

    def save_books_details(self) -> None:
        """Save the books details to the specified file.

        :return: None.
        """
        parsed_books_details = self.parse_books_details()
        processed_filepath = self._get_processed_filepath()

        self._save_to_parquet(
            data=parsed_books_details, filepath=processed_filepath
        )
