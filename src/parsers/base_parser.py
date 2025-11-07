import gzip
import os
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup
from structlog import get_logger

from common.constants import BaseConstants


class BaseParser:
    def __init__(self, file_prefix: str) -> None:
        self.file_prefix = file_prefix
        self._pages = BaseConstants.PAGES
        self._logger = get_logger(__name__)

    @staticmethod
    def _make_current_date_dir(base_dir: Path) -> None:
        """Create a current date directory in the processed data path.

        :param base_dir: Base directory of the current date.
        :return: None.
        """
        os.makedirs(base_dir, exist_ok=True)

    def _get_raw_filepath(self, page: int) -> Path:
        """Get a path to the file to parse.

        :param page: Page number of the file.
        :return: Path to the file.
        """
        raw_filepath = BaseConstants.RAW_DATA_DIR.joinpath(
            f"{self.file_prefix}_{page}.html.gz"
        )

        return raw_filepath

    def _get_processed_filepath(self) -> Path:
        """Get a path to the file to save data.

        :return: Path to the file.
        """
        self._make_current_date_dir(base_dir=BaseConstants.PROCESSED_DATA_DIR)

        processed_filepath = BaseConstants.PROCESSED_DATA_DIR.joinpath(
            f"{self.file_prefix}.parquet.gz"
        )

        return processed_filepath

    def _get_filepaths(self, data_dir: Path) -> list[Path]:
        """Get a list of filepaths from the specified directory.

        :param data_dir: Path to the base directory to use.
        :return: List of filepaths.
        """
        filenames = os.listdir(data_dir)

        filepaths = [
            data_dir.joinpath(filename)
            for filename in filenames
            if filename.startswith(self.file_prefix)
        ]

        return filepaths

    @staticmethod
    def _read_html_data(filepath: Path) -> str | None:
        """Read the HTML data from the specified filepath.

        :param filepath: Path to read the HTML data from.
        :return: HTML data.
        """
        if not filepath.exists():
            return None

        with gzip.open(filename=filepath, mode="rt") as f:
            html_data = f.read()

        return html_data

    @staticmethod
    def get_soup(html_data: str) -> BeautifulSoup:
        """Get the BeautifulSoup object from the HTML data.

        :param html_data: HTML data.
        :return: BeautifulSoup object.
        """
        soup = BeautifulSoup(markup=html_data, features="html.parser")

        return soup

    @staticmethod
    def _save_to_parquet(data: list[dict], filepath: Path) -> None:
        """Save the parsed data into a parquet file.

        :param data: Data to save.
        :param filepath: Path to save the data to.
        :return: None.
        """
        df = pd.DataFrame(data=data)

        df.to_parquet(filepath, engine="pyarrow", compression="gzip")
