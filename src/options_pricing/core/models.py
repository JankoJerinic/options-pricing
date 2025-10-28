"""
Core data models for the Market Data System.

This module defines the primary data structures for storing and validating
market data across multiple tickers and timeframes.
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Optional, Tuple
import pandas as pd


@dataclass
class DailyPrice:
    """Daily OHLCV price data for any ticker symbol."""

    ticker: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    vwap: float  # Volume-weighted average price

    def __post_init__(self):
        """Validate daily price data after initialization."""
        self._validate_ticker()
        self._validate_ohlc_consistency()
        self._validate_volume()
        self._validate_vwap()

    def _validate_ticker(self):
        """Validate ticker symbol format."""
        if not self.ticker or not isinstance(self.ticker, str):
            raise ValueError("Ticker must be a non-empty string")
        if len(self.ticker.strip()) == 0:
            raise ValueError("Ticker cannot be empty or whitespace")

    def _validate_ohlc_consistency(self):
        """Validate OHLC price relationships."""
        if not all(
            isinstance(price, (int, float)) and price >= 0
            for price in [self.open, self.high, self.low, self.close]
        ):
            raise ValueError("All OHLC prices must be non-negative numbers")

        if self.high < self.low:
            raise ValueError("High price cannot be less than low price")

        if not (self.low <= self.open <= self.high):
            raise ValueError("Open price must be between low and high")

        if not (self.low <= self.close <= self.high):
            raise ValueError("Close price must be between low and high")

    def _validate_volume(self):
        """Validate volume data."""
        if not isinstance(self.volume, int) or self.volume < 0:
            raise ValueError("Volume must be a non-negative integer")

    def _validate_vwap(self):
        """Validate VWAP data."""
        if not isinstance(self.vwap, (int, float)) or self.vwap < 0:
            raise ValueError("VWAP must be a non-negative number")

        # VWAP should be within the day's trading range
        if not (self.low <= self.vwap <= self.high):
            raise ValueError("VWAP must be between low and high prices")


@dataclass
class MinutePrice:
    """Minute-level OHLCV price data for any ticker symbol."""

    ticker: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    vwap: float  # Volume-weighted average price

    def __post_init__(self):
        """Validate minute price data after initialization."""
        self._validate_ticker()
        self._validate_timestamp()
        self._validate_ohlc_consistency()
        self._validate_volume()
        self._validate_vwap()

    def _validate_ticker(self):
        """Validate ticker symbol format."""
        if not self.ticker or not isinstance(self.ticker, str):
            raise ValueError("Ticker must be a non-empty string")
        if len(self.ticker.strip()) == 0:
            raise ValueError("Ticker cannot be empty or whitespace")

    def _validate_timestamp(self):
        """Validate timestamp format and market hours."""
        if not isinstance(self.timestamp, datetime):
            raise ValueError("Timestamp must be a datetime object")

        # Check if timestamp is within market hours (9:30 AM - 4:00 PM ET)
        # Note: This is a basic check - full implementation would handle holidays and timezone conversion
        time = self.timestamp.time()
        market_open = datetime.strptime("09:30", "%H:%M").time()
        market_close = datetime.strptime("16:00", "%H:%M").time()

        if not (market_open <= time <= market_close):
            raise ValueError(
                f"Timestamp {self.timestamp} is outside market hours (9:30 AM - 4:00 PM ET)"
            )

    def _validate_ohlc_consistency(self):
        """Validate OHLC price relationships."""
        if not all(
            isinstance(price, (int, float)) and price >= 0
            for price in [self.open, self.high, self.low, self.close]
        ):
            raise ValueError("All OHLC prices must be non-negative numbers")

        if self.high < self.low:
            raise ValueError("High price cannot be less than low price")

        if not (self.low <= self.open <= self.high):
            raise ValueError("Open price must be between low and high")

        if not (self.low <= self.close <= self.high):
            raise ValueError("Close price must be between low and high")

    def _validate_volume(self):
        """Validate volume data."""
        if not isinstance(self.volume, int) or self.volume < 0:
            raise ValueError("Volume must be a non-negative integer")

    def _validate_vwap(self):
        """Validate VWAP data."""
        if not isinstance(self.vwap, (int, float)) or self.vwap < 0:
            raise ValueError("VWAP must be a non-negative number")

        # VWAP should be within the minute's trading range
        if not (self.low <= self.vwap <= self.high):
            raise ValueError("VWAP must be between low and high prices")


@dataclass
class DataQualityReport:
    """Data quality assessment report for ticker and timeframe combinations."""

    ticker: str
    data_type: str  # 'daily', 'minute', 'options'
    date_range: Tuple[date, date]
    total_records: int
    missing_dates: List[date]
    anomalies: List[str]
    quality_score: float  # 0.0 to 1.0

    def __post_init__(self):
        """Validate data quality report after initialization."""
        self._validate_ticker()
        self._validate_data_type()
        self._validate_date_range()
        self._validate_counts()
        self._validate_quality_score()

    def _validate_ticker(self):
        """Validate ticker symbol format."""
        if not self.ticker or not isinstance(self.ticker, str):
            raise ValueError("Ticker must be a non-empty string")
        if len(self.ticker.strip()) == 0:
            raise ValueError("Ticker cannot be empty or whitespace")

    def _validate_data_type(self):
        """Validate data type."""
        valid_types = {"daily", "minute", "options"}
        if self.data_type not in valid_types:
            raise ValueError(f"Data type must be one of {valid_types}")

    def _validate_date_range(self):
        """Validate date range."""
        if not isinstance(self.date_range, tuple) or len(self.date_range) != 2:
            raise ValueError("Date range must be a tuple of two dates")

        start_date, end_date = self.date_range
        if not isinstance(start_date, date) or not isinstance(end_date, date):
            raise ValueError("Date range must contain date objects")

        if start_date > end_date:
            raise ValueError("Start date cannot be after end date")

    def _validate_counts(self):
        """Validate record counts."""
        if not isinstance(self.total_records, int) or self.total_records < 0:
            raise ValueError("Total records must be a non-negative integer")

        if not isinstance(self.missing_dates, list):
            raise ValueError("Missing dates must be a list")

        if not isinstance(self.anomalies, list):
            raise ValueError("Anomalies must be a list")

        # Validate that missing_dates contains date objects
        for missing_date in self.missing_dates:
            if not isinstance(missing_date, date):
                raise ValueError("All missing dates must be date objects")

    def _validate_quality_score(self):
        """Validate quality score."""
        if not isinstance(self.quality_score, (int, float)):
            raise ValueError("Quality score must be a number")

        if not (0.0 <= self.quality_score <= 1.0):
            raise ValueError("Quality score must be between 0.0 and 1.0")

    def add_anomaly(self, anomaly: str):
        """Add an anomaly to the report."""
        if not isinstance(anomaly, str):
            raise ValueError("Anomaly must be a string")
        self.anomalies.append(anomaly)

    def add_missing_date(self, missing_date: date):
        """Add a missing date to the report."""
        if not isinstance(missing_date, date):
            raise ValueError("Missing date must be a date object")
        if missing_date not in self.missing_dates:
            self.missing_dates.append(missing_date)

    def calculate_quality_score(self) -> float:
        """
        Calculate quality score based on missing data and anomalies.

        Returns:
            float: Quality score between 0.0 and 1.0
        """
        # Start with perfect score
        score = 1.0

        # Deduct for missing dates (-0.1 per missing day)
        score -= len(self.missing_dates) * 0.1

        # Deduct for anomalies (-0.05 per anomaly)
        score -= len(self.anomalies) * 0.05

        # Ensure score doesn't go below 0
        score = max(0.0, score)

        # Update the stored quality score
        self.quality_score = score

        return score

    def is_high_quality(self, threshold: float = 0.8) -> bool:
        """
        Check if data quality meets the specified threshold.

        Args:
            threshold: Minimum quality score threshold (default: 0.8)

        Returns:
            bool: True if quality score meets or exceeds threshold
        """
        return self.quality_score >= threshold

    def get_summary(self) -> str:
        """
        Get a human-readable summary of the data quality report.

        Returns:
            str: Formatted summary string
        """
        start_date, end_date = self.date_range
        return (
            f"Data Quality Report for {self.ticker} ({self.data_type})\n"
            f"Date Range: {start_date} to {end_date}\n"
            f"Total Records: {self.total_records:,}\n"
            f"Missing Dates: {len(self.missing_dates)}\n"
            f"Anomalies: {len(self.anomalies)}\n"
            f"Quality Score: {self.quality_score:.2f}"
        )
