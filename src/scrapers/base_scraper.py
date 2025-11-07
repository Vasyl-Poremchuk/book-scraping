import asyncio
import gzip
import os
from asyncio import TaskGroup
from pathlib import Path
from random import choice

import pandas as pd
from httpx import AsyncClient, Limits
from structlog import get_logger
from tenacity import (
    AsyncRetrying,
    RetryError,
    stop_after_attempt,
    wait_random,
)

from common.constants import BaseConstants


class BaseScraper:
    def __init__(self) -> None:
        self._base_url = BaseConstants.BASE_URL
        self._pages = BaseConstants.PAGES
        self._batch_size = BaseConstants.BATCH_SIZE
        self._logger = get_logger(__name__)

    @staticmethod
    def _make_current_date_dir(base_dir: Path) -> None:
        """Create a current date directory in the raw data path.

        :param base_dir: Base directory of the current date.
        :return: None.
        """
        os.makedirs(base_dir, exist_ok=True)

    def _generate_urls(self, path_parameter: str) -> list[str]:
        """Generate a list of source URLs.

        :param path_parameter: Path parameter of the source URL.
        :return: List of urls to scrape.
        """
        urls = [
            f"{self._base_url}/{path_parameter}?page={page}"
            for page in range(1, self._pages + 1)
        ]

        return urls

    @staticmethod
    def _rotate_header(headers: list[dict[str, str]]) -> dict[str, str]:
        """Rotate the header to use a different 'User-Agent' for each
        request.

        :param headers: List of 'User-Agent' dictionaries to rotate.
        :return: Rotated header.
        """
        header = choice(headers)

        return header

    def _save_html_data(
        self, html_data: str | None, *, filepath: Path
    ) -> None:
        """Save the HTML data to appropriate filepath.

        :param html_data: HTML data to save.
        :param filepath: Path to save the HTML data to.
        :return: None.
        """
        if html_data is None:
            self._logger.info("No HTML data to save")
            return

        with gzip.open(filename=filepath, mode="wb") as f:
            f.write(html_data.encode("utf-8"))

    @staticmethod
    def _get_filepath(
        base_path: Path, *, file_prefix: str, batch: int, idx: int
    ) -> Path:
        """Get path to the file where to store the data.

        :param base_path: Base path of the file.
        :param file_prefix: Prefix of the file.
        :param batch: Batch size.
        :param idx: Index of the file.
        :return: Path to the file.
        """
        filepath = base_path.joinpath(f"{file_prefix}_{batch}_{idx}.html.gz")

        return filepath

    async def get_html_data(self, url: str, client: AsyncClient) -> str | None:
        """Make an asynchronous request to the source and get
        the HTML data.

        :param url: A URL of the source.
        :param client: An asynchronous HTTP client.
        :return: HTML data.
        """
        header = self._rotate_header(BaseConstants.HEADERS)

        try:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(max_attempt_number=3),
                wait=wait_random(min=5, max=20),
            ):
                with attempt:
                    response = await client.get(url=url, headers=header)
                    response.raise_for_status()
                    html_data = response.text

                    return html_data
        except RetryError as exc:
            self._logger.error(
                f"Failed to get data after multiple retries for '{url}' "
                f"due to '{exc}'"
            )
        except Exception as exc:
            self._logger.error(
                f"An unexpected exception for '{url}' due to '{exc}'"
            )

    async def make_requests(
        self, urls: list[str], client: AsyncClient
    ) -> list:
        """Make a group of asynchronous requests to appropriate sources.

        :param urls: List of URLs to scrape.
        :param client: Asynchronous HTTP client.
        :return: List of groups of tasks.
        """
        tasks = []

        async with TaskGroup() as tg:
            for url in urls:
                task = tg.create_task(
                    coro=self.get_html_data(url=url, client=client)
                )

                tasks.append(task)

                await asyncio.sleep(delay=0.1)

        return tasks

    async def save_data(
        self, urls: list[str], *, batch: int, file_prefix: str
    ) -> None:
        """Save the retrieved data to appropriate filepaths.

        :param urls: List of URLs to scrape.
        :param batch: Batch size.
        :param file_prefix: Prefix of the file.
        :return: None.
        """
        limits = Limits(
            max_connections=BaseConstants.MAX_CONNECTIONS,
            max_keepalive_connections=BaseConstants.MAX_KEEPALIVE_CONNECTIONS,
        )
        self._make_current_date_dir(base_dir=BaseConstants.RAW_DATA_DIR)

        async with AsyncClient(limits=limits) as client:
            tasks = await self.make_requests(urls=urls, client=client)

        for idx, task in enumerate(tasks, start=1):
            filepath = self._get_filepath(
                base_path=BaseConstants.RAW_DATA_DIR,
                file_prefix=file_prefix,
                batch=batch,
                idx=idx,
            )

            html_data = task.result()

            self._save_html_data(html_data=html_data, filepath=filepath)

    @staticmethod
    def _read_to_df(filepath: Path) -> pd.DataFrame:
        """Read the data from a file into a dataframe.

        :param filepath: Path to the file.
        :return: Dataframe.
        """
        df = pd.read_parquet(filepath, engine="pyarrow")

        return df

    def _group_urls(self, urls: list[str]) -> list[list[str]]:
        """Group a list of URLs into a list of batches.

        :param urls: List of URLs to group.
        :return: Grouped list of URLs.
        """
        grouped_urls = [
            urls[idx : idx + self._batch_size]
            for idx in range(0, len(urls), self._batch_size)
        ]

        return grouped_urls
