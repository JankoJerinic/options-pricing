import os
from dotenv import load_dotenv
from pathlib import Path
from typing import List, Dict, Any

load_dotenv()

# Base data directory configuration
DATA_DIR = Path(os.getenv("DATA_DIR", "./data")).resolve()

# Legacy directories (maintained for backward compatibility)
RAW_DIR = DATA_DIR / "raw"
QA_DIR = DATA_DIR / "qa"

# Multi-ticker, multi-timeframe directory structure
DAILY_DATA_DIR = DATA_DIR / "daily"
MINUTE_DATA_DIR = DATA_DIR / "minute"
OPTIONS_DATA_DIR = DATA_DIR / "options"
METADATA_DIR = DATA_DIR / "metadata"
LOGS_DIR = DATA_DIR / "logs"
CACHE_DIR = DATA_DIR / "cache"

# API Configuration
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
if not POLYGON_API_KEY:
    raise RuntimeError("POLYGON_API_KEY missing. Put it in .env")

# Rate limiting configuration
API_RATE_LIMIT = int(os.getenv("API_RATE_LIMIT", "5"))  # calls per minute
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))  # seconds
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# Data validation configuration
QUALITY_SCORE_THRESHOLD = float(os.getenv("QUALITY_SCORE_THRESHOLD", "0.8"))
MAX_MISSING_DAYS_PERCENT = float(os.getenv("MAX_MISSING_DAYS_PERCENT", "0.05"))  # 5%

# File format configuration
PARQUET_COMPRESSION = os.getenv("PARQUET_COMPRESSION", "snappy")
PARQUET_ENGINE = os.getenv("PARQUET_ENGINE", "pyarrow")

# Market hours configuration (ET)
MARKET_OPEN_TIME = "09:30"
MARKET_CLOSE_TIME = "16:00"

# Supported tickers configuration
DEFAULT_TICKERS = [
    "SPY",  # SPDR S&P 500 ETF
    "SPX",  # S&P 500 Index
    "AAPL",  # Apple Inc.
    "MSFT",  # Microsoft Corporation
    "GOOGL",  # Alphabet Inc.
    "AMZN",  # Amazon.com Inc.
    "TSLA",  # Tesla Inc.
    "NVDA",  # NVIDIA Corporation
]

# Asset class configuration for validation
ASSET_CLASS_CONFIG = {
    "stock": {
        "min_price": 0.01,
        "max_price": 10000.0,
        "max_daily_change_percent": 50.0,
    },
    "etf": {
        "min_price": 1.0,
        "max_price": 1000.0,
        "max_daily_change_percent": 20.0,
    },
    "index": {
        "min_price": 100.0,
        "max_price": 10000.0,
        "max_daily_change_percent": 10.0,
    },
}


def setup_data_directories():
    """
    Create the complete directory structure for multi-ticker data storage.

    This function sets up all necessary directories for storing market data
    organized by ticker and timeframe as specified in the design document.
    """
    # Create base directories
    directories_to_create = [
        DATA_DIR,
        DAILY_DATA_DIR,
        MINUTE_DATA_DIR,
        OPTIONS_DATA_DIR,
        METADATA_DIR,
        LOGS_DIR,
        CACHE_DIR,
        # Legacy directories for backward compatibility
        RAW_DIR,
        QA_DIR,
        RAW_DIR / "indices",
        RAW_DIR / "options",
        RAW_DIR / "treasury",
        QA_DIR / "indices",
        QA_DIR / "options",
        QA_DIR / "treasury",
    ]

    for directory in directories_to_create:
        directory.mkdir(parents=True, exist_ok=True)


def get_ticker_data_dir(ticker: str, timeframe: str) -> Path:
    """
    Get the data directory path for a specific ticker and timeframe.

    Args:
        ticker: Ticker symbol (e.g., 'AAPL', 'SPY')
        timeframe: Data timeframe ('daily', 'minute', 'options')

    Returns:
        Path: Directory path for the ticker's data

    Raises:
        ValueError: If timeframe is not supported
    """
    ticker = ticker.upper()

    if timeframe == "daily":
        base_dir = DAILY_DATA_DIR
    elif timeframe == "minute":
        base_dir = MINUTE_DATA_DIR
    elif timeframe == "options":
        base_dir = OPTIONS_DATA_DIR
    else:
        raise ValueError(f"Unsupported timeframe: {timeframe}")

    ticker_dir = base_dir / ticker
    ticker_dir.mkdir(parents=True, exist_ok=True)

    return ticker_dir


def get_ticker_metadata_dir(ticker: str) -> Path:
    """
    Get the metadata directory path for a specific ticker.

    Args:
        ticker: Ticker symbol (e.g., 'AAPL', 'SPY')

    Returns:
        Path: Metadata directory path for the ticker
    """
    ticker = ticker.upper()
    metadata_dir = METADATA_DIR / ticker
    metadata_dir.mkdir(parents=True, exist_ok=True)

    return metadata_dir


def get_asset_class_config(ticker: str) -> Dict[str, Any]:
    """
    Get asset class configuration for validation based on ticker.

    Args:
        ticker: Ticker symbol

    Returns:
        Dict: Asset class configuration parameters
    """
    ticker = ticker.upper()

    # Simple heuristic for asset class detection
    # In a production system, this would be looked up from a database
    if ticker in ["SPX", "NDX", "RUT"]:
        return ASSET_CLASS_CONFIG["index"]
    elif ticker in ["SPY", "QQQ", "IWM", "VTI", "VOO"]:
        return ASSET_CLASS_CONFIG["etf"]
    else:
        return ASSET_CLASS_CONFIG["stock"]


def validate_ticker(ticker: str) -> bool:
    """
    Validate ticker symbol format.

    Args:
        ticker: Ticker symbol to validate

    Returns:
        bool: True if ticker is valid format
    """
    if not ticker or not isinstance(ticker, str):
        return False

    ticker = ticker.strip().upper()

    # Basic validation: 1-5 characters, alphanumeric
    if not (1 <= len(ticker) <= 5):
        return False

    if not ticker.isalnum():
        return False

    return True


# Initialize directory structure on import
setup_data_directories()
