# 📚 Book-Scraping

---

## 📖 Overview

---

**Book-Scraping** is a Python-based project designed to automatically scrapes popular lists, books, and books details from [Goodreads](https://www.goodreads.com/list/popular_lists?page=1) website.

## ⚙️ Features

---

- Asynchronously scrape popular lists, books, and their details (e.g., book title, author, genres, publication date, etc.):
  - Random rotation of request headers.
  - Handle pagination.
  - Rate-limit requests.
  - Control the maximum number of requests (attempts) per page.
  - Delays between requests.
  - Scraping in batches.
- Data processing using `ProcessPoolExecutor`.
- Compress raw and processed data using `gzip`.
- Save the processed data in the `parquet` files.
- Uploading the data to an S3 bucket using a `ThreadPoolExecutor` and saving it by date.
- Resource configuration using `Terraform`.
- Logging all steps.
- GitHub actions for CI/CD.

## 🧰 Tech Stack

---

- **Language**: Python.
- **Libraries**:
  - `beautifulsoup4` - for parsing and extracting data from HTML pages.
  - `black` & `ruff` - code formatting and linting/static analysis for clean, consistent code.
  - `boto3` - AWS SDK for Python to interact with S3 service.
  - `httpx` - for making asynchronous HTTP requests.
  - `pandas` - for data manipulation, cleaning, etc.
  - `pyarrow` - for efficient in-memory columnar data storage and interoperability (e.g., `parquet`).
  - `structlog` - structured logging for better observability and debugging.
  - `tenancity` - for retrying asynchronous requests.
- **Cloud Provider**: AWS.
- **AWS Services**:
  - `S3` - object storage for storing raw and processed data.
  - `ECR` - container registry to store, manage, and deploy project images.
  - `ECS` - container orchestration service to run and manage project containers.
  - `Lambda` - serverless compute service to trigger `ECS` tasks.
  - `Amazon EventBridge` - event bus service to create rules for triggering the `Lambda` handler.
  - `IAM` - Identity and Access Management for securely controlling access to AWS resources.

## 📂 Project Structure

---

```
book-scraping/
│
├── Dockerfile                 # Defines the container image and environment
├── pyproject.toml             # Project configuration and dependencies
├── README.md                  # Project documentation
├── src                        # Source code for scraping, parsing, and uploading
│   ├── common
│   │   ├── __init__.py
│   │   └── constants.py       # Shared constants used across the project
│   ├── data
│   │   ├── processed          # Folder for cleaned and structured data
│   │   └── raw                # Folder for raw scraped data
│   ├── main.py                # Entry point to run the project workflow
│   ├── parsers
│   │   ├── __init__.py
│   │   ├── base_parser.py         # Base parser class for all parsing logic
│   │   ├── book_parser.py         # Parses book summary data
│   │   ├── book_details_parser.py # Parses detailed book information
│   │   └── popular_list_parser.py # Parses popular book lists
│   ├── scrapers
│   │   ├── __init__.py
│   │   ├── base_scraper.py          # Base scraper class
│   │   ├── book_scraper.py          # Scrapes book summary data
│   │   ├── book_details_scraper.py  # Scrapes detailed book information
│   │   └── popular_list_scraper.py  # Scrapes popular book lists
│   └── uploader
│       ├── __init__.py
│       └── uploader.py           # Handles uploading data to object storage
├── terraform
│   ├── bootstrap
│   │   ├── main.tf                # Terraform script to provision resources
│   │   ├── terraform.tfstate      # Terraform state file
│   │   └── variables.tf           # Terraform variables for bootstrap resources
│   ├── lambda
│   │   └── lambda_func.py         # AWS Lambda function code
│   ├── main.tf                    # Main Terraform configuration
│   └── variables.tf               # Terraform variables for main configuration
└── uv.lock                        # Lock file for dependencies
```

## 🚀 Getting Started

---

1. Clone the Repository.

```bash
git clone https://github.com/Vasyl-Poremchuk/book-scraping
cd book-scraping
```

2. Run in Docker.

```bash
docker build -t book-scraping .
docker run book-scraping
```
