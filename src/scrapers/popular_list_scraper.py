import time

from common.constants import PopularListConstants
from scrapers.base_scraper import BaseScraper


class PopularListScraper(BaseScraper):
    def __init__(self) -> None:
        super().__init__()

    async def save_popular_lists(self) -> None:
        """Save the HTML data from the popular lists pages.

        :return: None.
        """
        popular_lists_urls = self._generate_urls(
            path_parameter=PopularListConstants.PATH_PARAMETER
        )
        grouped_popular_lists_urls = self._group_urls(urls=popular_lists_urls)

        for (
            batch,
            urls,
        ) in enumerate(grouped_popular_lists_urls, start=1):
            start = time.perf_counter()
            self._logger.info(
                f"Scraping popular lists for batch '{batch}' of "
                f"'{len(urls)}' items have been started"
            )

            await self.save_data(
                urls=urls,
                batch=batch,
                file_prefix=PopularListConstants.FILE_PREFIX,
            )

            end = time.perf_counter()
            self._logger.info(
                f"Scraping popular lists for batch '{batch}' "
                f"took {end - start:.3f} seconds"
            )
