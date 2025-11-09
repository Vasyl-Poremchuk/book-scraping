import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import boto3
from botocore.client import BaseClient
from structlog import get_logger

from common.constants import BaseConstants


class Uploader:
    def __init__(self) -> None:
        self._client_name = "s3"
        self._bucket = BaseConstants.S3_BUCKET
        self._logger = get_logger(__name__)

    def _init_client(self) -> BaseClient:
        """Initialize an S3 client.

        :return: S3 client.
        """
        s3_client = boto3.client(self._client_name)

        return s3_client

    @staticmethod
    def get_file_keys(base_dir: Path, file_prefix: str) -> list[dict]:
        """Get file keys for uploading to an S3 bucket.

        :param base_dir: Base directory from which to get file keys.
        :param file_prefix: The prefix of file to upload.
        :return: List of file keys.
        """
        filenames = os.listdir(base_dir)

        file_keys = []

        for filename in filenames:
            if not filename.startswith(file_prefix):
                continue

            filepath = base_dir.joinpath(filename)

            s3_inner_dir = filepath.parent
            s3_dir = s3_inner_dir.parent

            file_key = f"{s3_dir.name}/{s3_inner_dir.name}/{filename}"

            file_keys.append({"filepath": filepath, "file_key": file_key})

        return file_keys

    def upload_file(self, obj: dict[str, str]) -> None:
        """Upload a file to an S3 bucket.

        :param obj: An object that contains a path
            to the file and an S3 key.
        :return: None.
        """
        s3_client = self._init_client()

        filepath = obj.get("filepath")
        file_key = obj.get("file_key")

        s3_client.upload_file(
            Filename=filepath, Bucket=self._bucket, Key=file_key
        )

    def upload_files(self, file_keys: list[dict]) -> None:
        """Upload multiple files to an S3 bucket.

        :param file_keys: List of file keys.
        :return: None.
        """
        start = time.perf_counter()
        self._logger.info(
            f"Uploading '{len(file_keys)}' files to '{self._bucket}' "
            f"bucket have been started"
        )

        with ThreadPoolExecutor(
            max_workers=BaseConstants.MAX_WORKERS
        ) as executor:
            futures = {
                executor.submit(self.upload_file, obj): obj
                for obj in file_keys
            }

            for future in as_completed(futures):
                file_key = futures.get(future)
                filepath = file_key.get("filepath")
                filename = filepath.name

                try:
                    future.result()
                except Exception as exc:
                    self._logger.error(
                        f"An exception occurred while uploading '{filename}'"
                        f"due to '{exc}'"
                    )

        end = time.perf_counter()
        self._logger.info(f"Uploading files took {end - start:.3f} seconds")
