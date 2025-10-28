"""
Unit tests for configuration module.

Tests the configuration system including directory management,
ticker validation, and asset class configuration.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from options_pricing import config


class TestConfigurationConstants:
    """Test configuration constants and basic setup."""

    def test_data_directories_exist(self):
        """Test that all required data directories are defined."""
        assert hasattr(config, "DATA_DIR")
        assert hasattr(config, "DAILY_DATA_DIR")
        assert hasattr(config, "MINUTE_DATA_DIR")
        assert hasattr(config, "OPTIONS_DATA_DIR")
        assert hasattr(config, "METADATA_DIR")
        assert hasattr(config, "LOGS_DIR")
        assert hasattr(config, "CACHE_DIR")

    def test_api_configuration_exists(self):
        """Test that API configuration constants are defined."""
        assert hasattr(config, "API_RATE_LIMIT")
        assert hasattr(config, "API_TIMEOUT")
        assert hasattr(config, "MAX_RETRIES")
        assert isinstance(config.API_RATE_LIMIT, int)
        assert isinstance(config.API_TIMEOUT, int)
        assert isinstance(config.MAX_RETRIES, int)

    def test_quality_configuration_exists(self):
        """Test that data quality configuration constants are defined."""
        assert hasattr(config, "QUALITY_SCORE_THRESHOLD")
        assert hasattr(config, "MAX_MISSING_DAYS_PERCENT")
        assert isinstance(config.QUALITY_SCORE_THRESHOLD, float)
        assert isinstance(config.MAX_MISSING_DAYS_PERCENT, float)

    def test_default_tickers_list(self):
        """Test that default tickers list is properly defined."""
        assert hasattr(config, "DEFAULT_TICKERS")
        assert isinstance(config.DEFAULT_TICKERS, list)
        assert len(config.DEFAULT_TICKERS) > 0
        assert "SPY" in config.DEFAULT_TICKERS
        assert "SPX" in config.DEFAULT_TICKERS

    def test_asset_class_config_structure(self):
        """Test that asset class configuration has proper structure."""
        assert hasattr(config, "ASSET_CLASS_CONFIG")
        assert isinstance(config.ASSET_CLASS_CONFIG, dict)

        required_classes = ["stock", "etf", "index"]
        for asset_class in required_classes:
            assert asset_class in config.ASSET_CLASS_CONFIG

            class_config = config.ASSET_CLASS_CONFIG[asset_class]
            assert "min_price" in class_config
            assert "max_price" in class_config
            assert "max_daily_change_percent" in class_config


class TestDirectoryManagement:
    """Test directory creation and management functions."""

    def test_get_ticker_data_dir_daily(self):
        """Test getting daily data directory for a ticker."""
        ticker_dir = config.get_ticker_data_dir("AAPL", "daily")

        assert isinstance(ticker_dir, Path)
        assert ticker_dir.name == "AAPL"
        assert "daily" in str(ticker_dir)
        assert ticker_dir.exists()

    def test_get_ticker_data_dir_minute(self):
        """Test getting minute data directory for a ticker."""
        ticker_dir = config.get_ticker_data_dir("MSFT", "minute")

        assert isinstance(ticker_dir, Path)
        assert ticker_dir.name == "MSFT"
        assert "minute" in str(ticker_dir)
        assert ticker_dir.exists()

    def test_get_ticker_data_dir_options(self):
        """Test getting options data directory for a ticker."""
        ticker_dir = config.get_ticker_data_dir("GOOGL", "options")

        assert isinstance(ticker_dir, Path)
        assert ticker_dir.name == "GOOGL"
        assert "options" in str(ticker_dir)
        assert ticker_dir.exists()

    def test_get_ticker_data_dir_invalid_timeframe(self):
        """Test that invalid timeframe raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported timeframe"):
            config.get_ticker_data_dir("AAPL", "invalid")

    def test_get_ticker_data_dir_case_insensitive(self):
        """Test that ticker symbols are converted to uppercase."""
        ticker_dir_lower = config.get_ticker_data_dir("aapl", "daily")
        ticker_dir_upper = config.get_ticker_data_dir("AAPL", "daily")

        assert ticker_dir_lower == ticker_dir_upper
        assert ticker_dir_lower.name == "AAPL"

    def test_get_ticker_metadata_dir(self):
        """Test getting metadata directory for a ticker."""
        metadata_dir = config.get_ticker_metadata_dir("AAPL")

        assert isinstance(metadata_dir, Path)
        assert metadata_dir.name == "AAPL"
        assert "metadata" in str(metadata_dir)
        assert metadata_dir.exists()

    def test_get_ticker_metadata_dir_case_insensitive(self):
        """Test that metadata directory handles case insensitive tickers."""
        metadata_dir_lower = config.get_ticker_metadata_dir("aapl")
        metadata_dir_upper = config.get_ticker_metadata_dir("AAPL")

        assert metadata_dir_lower == metadata_dir_upper
        assert metadata_dir_lower.name == "AAPL"


class TestAssetClassConfiguration:
    """Test asset class configuration and detection."""

    def test_get_asset_class_config_index(self):
        """Test getting asset class config for index tickers."""
        spx_config = config.get_asset_class_config("SPX")
        ndx_config = config.get_asset_class_config("NDX")
        rut_config = config.get_asset_class_config("RUT")

        expected_config = config.ASSET_CLASS_CONFIG["index"]

        assert spx_config == expected_config
        assert ndx_config == expected_config
        assert rut_config == expected_config

    def test_get_asset_class_config_etf(self):
        """Test getting asset class config for ETF tickers."""
        spy_config = config.get_asset_class_config("SPY")
        qqq_config = config.get_asset_class_config("QQQ")
        iwm_config = config.get_asset_class_config("IWM")

        expected_config = config.ASSET_CLASS_CONFIG["etf"]

        assert spy_config == expected_config
        assert qqq_config == expected_config
        assert iwm_config == expected_config

    def test_get_asset_class_config_stock(self):
        """Test getting asset class config for stock tickers."""
        aapl_config = config.get_asset_class_config("AAPL")
        msft_config = config.get_asset_class_config("MSFT")
        googl_config = config.get_asset_class_config("GOOGL")

        expected_config = config.ASSET_CLASS_CONFIG["stock"]

        assert aapl_config == expected_config
        assert msft_config == expected_config
        assert googl_config == expected_config

    def test_get_asset_class_config_case_insensitive(self):
        """Test that asset class config handles case insensitive tickers."""
        lower_config = config.get_asset_class_config("aapl")
        upper_config = config.get_asset_class_config("AAPL")

        assert lower_config == upper_config


class TestTickerValidation:
    """Test ticker symbol validation."""

    def test_validate_ticker_valid_symbols(self):
        """Test validation of valid ticker symbols."""
        valid_tickers = ["AAPL", "MSFT", "GOOGL", "SPY", "SPX", "A", "AMZN"]

        for ticker in valid_tickers:
            assert config.validate_ticker(ticker) is True

    def test_validate_ticker_case_insensitive(self):
        """Test that ticker validation is case insensitive."""
        assert config.validate_ticker("aapl") is True
        assert config.validate_ticker("AAPL") is True
        assert config.validate_ticker("AaPl") is True

    def test_validate_ticker_empty_string(self):
        """Test that empty string is invalid."""
        assert config.validate_ticker("") is False
        assert config.validate_ticker("   ") is False

    def test_validate_ticker_none(self):
        """Test that None is invalid."""
        assert config.validate_ticker(None) is False

    def test_validate_ticker_non_string(self):
        """Test that non-string types are invalid."""
        assert config.validate_ticker(123) is False
        assert config.validate_ticker(["AAPL"]) is False
        assert config.validate_ticker({"ticker": "AAPL"}) is False

    def test_validate_ticker_too_long(self):
        """Test that tickers longer than 5 characters are invalid."""
        assert config.validate_ticker("TOOLONG") is False
        assert config.validate_ticker("ABCDEF") is False

    def test_validate_ticker_special_characters(self):
        """Test that tickers with special characters are invalid."""
        assert config.validate_ticker("AAP-L") is False
        assert config.validate_ticker("AAP.L") is False
        assert config.validate_ticker("AAP_L") is False
        assert config.validate_ticker("AAP L") is False

    def test_validate_ticker_numbers_only(self):
        """Test that numeric-only tickers are valid (edge case)."""
        assert config.validate_ticker("123") is True
        assert config.validate_ticker("12345") is True

    def test_validate_ticker_alphanumeric(self):
        """Test that alphanumeric tickers are valid."""
        assert config.validate_ticker("A1B2") is True
        assert config.validate_ticker("SPY1") is True


class TestSetupDataDirectories:
    """Test the setup_data_directories function."""

    def test_setup_data_directories_function_exists(self):
        """Test that setup_data_directories function exists and is callable."""
        assert hasattr(config, "setup_data_directories")
        assert callable(config.setup_data_directories)

        # Test that it runs without error (directories are created in integration tests)
        try:
            config.setup_data_directories()
        except Exception as e:
            pytest.fail(f"setup_data_directories() raised an exception: {e}")


class TestIntegration:
    """Integration tests for configuration module."""

    def test_directory_creation_integration(self):
        """Test that directory creation works end-to-end."""
        # Test creating directories for multiple tickers and timeframes
        tickers = ["AAPL", "MSFT", "GOOGL"]
        timeframes = ["daily", "minute", "options"]

        for ticker in tickers:
            for timeframe in timeframes:
                ticker_dir = config.get_ticker_data_dir(ticker, timeframe)
                assert ticker_dir.exists()
                assert ticker_dir.is_dir()
                assert ticker_dir.name == ticker.upper()

            # Test metadata directory
            metadata_dir = config.get_ticker_metadata_dir(ticker)
            assert metadata_dir.exists()
            assert metadata_dir.is_dir()
            assert metadata_dir.name == ticker.upper()

    def test_configuration_consistency(self):
        """Test that configuration values are consistent and reasonable."""
        # Test that quality threshold is reasonable
        assert 0.0 <= config.QUALITY_SCORE_THRESHOLD <= 1.0

        # Test that missing days percent is reasonable
        assert 0.0 <= config.MAX_MISSING_DAYS_PERCENT <= 1.0

        # Test that API limits are positive
        assert config.API_RATE_LIMIT > 0
        assert config.API_TIMEOUT > 0
        assert config.MAX_RETRIES >= 0

        # Test that asset class configs have reasonable values
        for asset_class, class_config in config.ASSET_CLASS_CONFIG.items():
            assert class_config["min_price"] >= 0
            assert class_config["max_price"] > class_config["min_price"]
            assert class_config["max_daily_change_percent"] > 0
