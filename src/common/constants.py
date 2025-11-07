from datetime import datetime, timezone
from pathlib import Path


class BaseConstants:
    BASE_URL = "https://www.goodreads.com"
    BASE_DIR = Path(__file__).parents[1]
    DATA_DIR = BASE_DIR.joinpath("data")
    CURRENT_DATE = datetime.now(tz=timezone.utc).strftime(format="%Y-%m-%d")
    RAW_DATA_DIR = DATA_DIR.joinpath("raw", CURRENT_DATE)
    PROCESSED_DATA_DIR = DATA_DIR.joinpath("processed", CURRENT_DATE)
    MAX_CONNECTIONS = 10
    MAX_KEEPALIVE_CONNECTIONS = 10
    PAGES = 100
    BATCH_SIZE = 1000
    MAX_WORKERS = 10
    HEADERS = [
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/130.0.0.0 Safari/537.36"
        },
        {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0_0) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/18.0 Safari/605.1.15"
        },
        {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/129.0.6668.71 Safari/537.36"
        },
        {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone "
            "OS 18_0 like Mac OS X) AppleWebKit/605.1.15 "
            "(KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1"
        },
        {
            "User-Agent": "Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/17.4 Mobile/15E148 Safari/604.1"
        },
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; "
            "x64; rv:131.0) Gecko/20100101 Firefox/131.0"
        },
        {
            "User-Agent": "Mozilla/5.0 (Linux; Android 14; SM-G998B) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/129.0.6668.89 Mobile Safari/537.36"
        },
        {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:132.0) "
            "Gecko/20100101 Firefox/132.0"
        },
        {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_1) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/128.0.6613.120 Safari/537.36"
        },
        {
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/127.0.6533.72 Mobile Safari/537.36"
        },
    ]


class PopularListConstants:
    FILE_PREFIX = "popular_lists"
    PATH_PARAMETER = f"list/{FILE_PREFIX}"


class BookConstants:
    FILE_PREFIX = "books"


class BookDetailsConstants:
    FILE_PREFIX = "book_details"
