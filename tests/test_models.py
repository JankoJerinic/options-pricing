"""
Unit tests for core data models.

Tests the DailyPrice, MinutePrice, and DataQualityReport models
including validation logic and edge cases.
"""

import pytest
from datetime import date, datetime
from options_pricing.core import DailyPrice, MinutePrice, DataQualityReport


class TestDailyPrice:
    """Test cases for DailyPrice model."""

    def test_valid_daily_price_creation(self):
        """Test creating a valid DailyPrice instance."""
        daily_price = DailyPrice(
            ticker="AAPL",
            date=date(2024, 1, 15),
            open=150.0,
            high=155.0,
            low=149.0,
            close=154.0,
            volume=1000000,
            vwap=152.5,
        )

        assert daily_price.ticker == "AAPL"
        assert daily_price.date == date(2024, 1, 15)
        assert daily_price.open == 150.0
        assert daily_price.high == 155.0
        assert daily_price.low == 149.0
        assert daily_price.close == 154.0
        assert daily_price.volume == 1000000
        assert daily_price.vwap == 152.5

    def test_empty_ticker_validation(self):
        """Test that empty ticker raises ValueError."""
        with pytest.raises(ValueError, match="Ticker must be a non-empty string"):
            DailyPrice(
                ticker="",
                date=date(2024, 1, 15),
                open=150.0,
                high=155.0,
                low=149.0,
                close=154.0,
                volume=1000000,
                vwap=152.5,
            )

    def test_none_ticker_validation(self):
        """Test that None ticker raises ValueError."""
        with pytest.raises(ValueError, match="Ticker must be a non-empty string"):
            DailyPrice(
                ticker=None,
                date=date(2024, 1, 15),
                open=150.0,
                high=155.0,
                low=149.0,
                close=154.0,
                volume=1000000,
                vwap=152.5,
            )

    def test_high_less_than_low_validation(self):
        """Test that high < low raises ValueError."""
        with pytest.raises(
            ValueError, match="High price cannot be less than low price"
        ):
            DailyPrice(
                ticker="AAPL",
                date=date(2024, 1, 15),
                open=150.0,
                high=148.0,  # High less than low
                low=149.0,
                close=154.0,
                volume=1000000,
                vwap=152.5,
            )

    def test_open_outside_range_validation(self):
        """Test that open price outside high-low range raises ValueError."""
        with pytest.raises(ValueError, match="Open price must be between low and high"):
            DailyPrice(
                ticker="AAPL",
                date=date(2024, 1, 15),
                open=160.0,  # Open above high
                high=155.0,
                low=149.0,
                close=154.0,
                volume=1000000,
                vwap=152.5,
            )

    def test_close_outside_range_validation(self):
        """Test that close price outside high-low range raises ValueError."""
        with pytest.raises(
            ValueError, match="Close price must be between low and high"
        ):
            DailyPrice(
                ticker="AAPL",
                date=date(2024, 1, 15),
                open=150.0,
                high=155.0,
                low=149.0,
                close=148.0,  # Close below low
                volume=1000000,
                vwap=152.5,
            )

    def test_negative_price_validation(self):
        """Test that negative prices raise ValueError."""
        with pytest.raises(
            ValueError, match="All OHLC prices must be non-negative numbers"
        ):
            DailyPrice(
                ticker="AAPL",
                date=date(2024, 1, 15),
                open=-150.0,  # Negative price
                high=155.0,
                low=149.0,
                close=154.0,
                volume=1000000,
                vwap=152.5,
            )

    def test_negative_volume_validation(self):
        """Test that negative volume raises ValueError."""
        with pytest.raises(ValueError, match="Volume must be a non-negative integer"):
            DailyPrice(
                ticker="AAPL",
                date=date(2024, 1, 15),
                open=150.0,
                high=155.0,
                low=149.0,
                close=154.0,
                volume=-1000,  # Negative volume
                vwap=152.5,
            )

    def test_vwap_outside_range_validation(self):
        """Test that VWAP outside high-low range raises ValueError."""
        with pytest.raises(
            ValueError, match="VWAP must be between low and high prices"
        ):
            DailyPrice(
                ticker="AAPL",
                date=date(2024, 1, 15),
                open=150.0,
                high=155.0,
                low=149.0,
                close=154.0,
                volume=1000000,
                vwap=160.0,  # VWAP above high
            )

    def test_edge_case_equal_prices(self):
        """Test edge case where all prices are equal."""
        daily_price = DailyPrice(
            ticker="AAPL",
            date=date(2024, 1, 15),
            open=150.0,
            high=150.0,
            low=150.0,
            close=150.0,
            volume=1000000,
            vwap=150.0,
        )

        assert (
            daily_price.open
            == daily_price.high
            == daily_price.low
            == daily_price.close
            == daily_price.vwap
        )


class TestMinutePrice:
    """Test cases for MinutePrice model."""

    def test_valid_minute_price_creation(self):
        """Test creating a valid MinutePrice instance."""
        minute_price = MinutePrice(
            ticker="AAPL",
            timestamp=datetime(2024, 1, 15, 10, 30),
            open=150.0,
            high=150.5,
            low=149.8,
            close=150.2,
            volume=1000,
            vwap=150.1,
        )

        assert minute_price.ticker == "AAPL"
        assert minute_price.timestamp == datetime(2024, 1, 15, 10, 30)
        assert minute_price.open == 150.0
        assert minute_price.high == 150.5
        assert minute_price.low == 149.8
        assert minute_price.close == 150.2
        assert minute_price.volume == 1000
        assert minute_price.vwap == 150.1

    def test_market_hours_validation_before_open(self):
        """Test that timestamp before market open raises ValueError."""
        with pytest.raises(ValueError, match="is outside market hours"):
            MinutePrice(
                ticker="AAPL",
                timestamp=datetime(2024, 1, 15, 8, 30),  # Before 9:30 AM
                open=150.0,
                high=150.5,
                low=149.8,
                close=150.2,
                volume=1000,
                vwap=150.1,
            )

    def test_market_hours_validation_after_close(self):
        """Test that timestamp after market close raises ValueError."""
        with pytest.raises(ValueError, match="is outside market hours"):
            MinutePrice(
                ticker="AAPL",
                timestamp=datetime(2024, 1, 15, 17, 30),  # After 4:00 PM
                open=150.0,
                high=150.5,
                low=149.8,
                close=150.2,
                volume=1000,
                vwap=150.1,
            )

    def test_market_hours_validation_at_open(self):
        """Test that timestamp exactly at market open is valid."""
        minute_price = MinutePrice(
            ticker="AAPL",
            timestamp=datetime(2024, 1, 15, 9, 30),  # Exactly 9:30 AM
            open=150.0,
            high=150.5,
            low=149.8,
            close=150.2,
            volume=1000,
            vwap=150.1,
        )

        assert minute_price.timestamp.time().hour == 9
        assert minute_price.timestamp.time().minute == 30

    def test_market_hours_validation_at_close(self):
        """Test that timestamp exactly at market close is valid."""
        minute_price = MinutePrice(
            ticker="AAPL",
            timestamp=datetime(2024, 1, 15, 16, 0),  # Exactly 4:00 PM
            open=150.0,
            high=150.5,
            low=149.8,
            close=150.2,
            volume=1000,
            vwap=150.1,
        )

        assert minute_price.timestamp.time().hour == 16
        assert minute_price.timestamp.time().minute == 0

    def test_invalid_timestamp_type(self):
        """Test that non-datetime timestamp raises ValueError."""
        with pytest.raises(ValueError, match="Timestamp must be a datetime object"):
            MinutePrice(
                ticker="AAPL",
                timestamp="2024-01-15 10:30:00",  # String instead of datetime
                open=150.0,
                high=150.5,
                low=149.8,
                close=150.2,
                volume=1000,
                vwap=150.1,
            )


class TestDataQualityReport:
    """Test cases for DataQualityReport model."""

    def test_valid_quality_report_creation(self):
        """Test creating a valid DataQualityReport instance."""
        report = DataQualityReport(
            ticker="AAPL",
            data_type="daily",
            date_range=(date(2024, 1, 1), date(2024, 1, 31)),
            total_records=21,
            missing_dates=[],
            anomalies=[],
            quality_score=1.0,
        )

        assert report.ticker == "AAPL"
        assert report.data_type == "daily"
        assert report.date_range == (date(2024, 1, 1), date(2024, 1, 31))
        assert report.total_records == 21
        assert report.missing_dates == []
        assert report.anomalies == []
        assert report.quality_score == 1.0

    def test_invalid_data_type_validation(self):
        """Test that invalid data type raises ValueError."""
        with pytest.raises(ValueError, match="Data type must be one of"):
            DataQualityReport(
                ticker="AAPL",
                data_type="invalid",  # Invalid data type
                date_range=(date(2024, 1, 1), date(2024, 1, 31)),
                total_records=21,
                missing_dates=[],
                anomalies=[],
                quality_score=1.0,
            )

    def test_invalid_date_range_order(self):
        """Test that start date after end date raises ValueError."""
        with pytest.raises(ValueError, match="Start date cannot be after end date"):
            DataQualityReport(
                ticker="AAPL",
                data_type="daily",
                date_range=(date(2024, 1, 31), date(2024, 1, 1)),  # Reversed dates
                total_records=21,
                missing_dates=[],
                anomalies=[],
                quality_score=1.0,
            )

    def test_invalid_quality_score_range(self):
        """Test that quality score outside 0-1 range raises ValueError."""
        with pytest.raises(
            ValueError, match="Quality score must be between 0.0 and 1.0"
        ):
            DataQualityReport(
                ticker="AAPL",
                data_type="daily",
                date_range=(date(2024, 1, 1), date(2024, 1, 31)),
                total_records=21,
                missing_dates=[],
                anomalies=[],
                quality_score=1.5,  # Above 1.0
            )

    def test_negative_total_records(self):
        """Test that negative total records raises ValueError."""
        with pytest.raises(
            ValueError, match="Total records must be a non-negative integer"
        ):
            DataQualityReport(
                ticker="AAPL",
                data_type="daily",
                date_range=(date(2024, 1, 1), date(2024, 1, 31)),
                total_records=-1,  # Negative records
                missing_dates=[],
                anomalies=[],
                quality_score=1.0,
            )

    def test_add_anomaly_method(self):
        """Test adding anomalies to the report."""
        report = DataQualityReport(
            ticker="AAPL",
            data_type="daily",
            date_range=(date(2024, 1, 1), date(2024, 1, 31)),
            total_records=21,
            missing_dates=[],
            anomalies=[],
            quality_score=1.0,
        )

        report.add_anomaly("Price gap detected")
        report.add_anomaly("Volume spike")

        assert len(report.anomalies) == 2
        assert "Price gap detected" in report.anomalies
        assert "Volume spike" in report.anomalies

    def test_add_missing_date_method(self):
        """Test adding missing dates to the report."""
        report = DataQualityReport(
            ticker="AAPL",
            data_type="daily",
            date_range=(date(2024, 1, 1), date(2024, 1, 31)),
            total_records=21,
            missing_dates=[],
            anomalies=[],
            quality_score=1.0,
        )

        report.add_missing_date(date(2024, 1, 15))
        report.add_missing_date(date(2024, 1, 16))

        assert len(report.missing_dates) == 2
        assert date(2024, 1, 15) in report.missing_dates
        assert date(2024, 1, 16) in report.missing_dates

    def test_add_duplicate_missing_date(self):
        """Test that duplicate missing dates are not added."""
        report = DataQualityReport(
            ticker="AAPL",
            data_type="daily",
            date_range=(date(2024, 1, 1), date(2024, 1, 31)),
            total_records=21,
            missing_dates=[],
            anomalies=[],
            quality_score=1.0,
        )

        report.add_missing_date(date(2024, 1, 15))
        report.add_missing_date(date(2024, 1, 15))  # Duplicate

        assert len(report.missing_dates) == 1
        assert date(2024, 1, 15) in report.missing_dates

    def test_calculate_quality_score(self):
        """Test quality score calculation."""
        report = DataQualityReport(
            ticker="AAPL",
            data_type="daily",
            date_range=(date(2024, 1, 1), date(2024, 1, 31)),
            total_records=21,
            missing_dates=[date(2024, 1, 15)],  # 1 missing date
            anomalies=["Price gap"],  # 1 anomaly
            quality_score=1.0,
        )

        calculated_score = report.calculate_quality_score()
        expected_score = 1.0 - (1 * 0.1) - (1 * 0.05)  # 1.0 - 0.1 - 0.05 = 0.85

        assert calculated_score == expected_score
        assert report.quality_score == expected_score

    def test_is_high_quality_method(self):
        """Test high quality threshold checking."""
        high_quality_report = DataQualityReport(
            ticker="AAPL",
            data_type="daily",
            date_range=(date(2024, 1, 1), date(2024, 1, 31)),
            total_records=21,
            missing_dates=[],
            anomalies=[],
            quality_score=0.9,
        )

        low_quality_report = DataQualityReport(
            ticker="AAPL",
            data_type="daily",
            date_range=(date(2024, 1, 1), date(2024, 1, 31)),
            total_records=21,
            missing_dates=[],
            anomalies=[],
            quality_score=0.7,
        )

        assert high_quality_report.is_high_quality() is True
        assert low_quality_report.is_high_quality() is False
        assert low_quality_report.is_high_quality(threshold=0.6) is True

    def test_get_summary_method(self):
        """Test summary string generation."""
        report = DataQualityReport(
            ticker="AAPL",
            data_type="daily",
            date_range=(date(2024, 1, 1), date(2024, 1, 31)),
            total_records=21,
            missing_dates=[date(2024, 1, 15)],
            anomalies=["Price gap"],
            quality_score=0.85,
        )

        summary = report.get_summary()

        assert "AAPL" in summary
        assert "daily" in summary
        assert "2024-01-01" in summary
        assert "2024-01-31" in summary
        assert "21" in summary
        assert "1" in summary  # Missing dates count
        assert "1" in summary  # Anomalies count
        assert "0.85" in summary
