# Market Data System Design

## Overview

The Market Data System is a comprehensive, scalable data management platform designed to collect, store, and serve market data for any ticker symbol across multiple timeframes. The system emphasizes simplicity, reliability, and performance, providing a solid foundation for quantitative analysis and trading strategies across diverse market instruments.

## Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Tools     │    │   Data API      │    │  Polygon API    │
│                 │    │                 │    │                 │
│ • fetch-data    │───▶│ • DataManager   │───▶│ • Daily OHLCV   │
│ • validate-data │    │ • DataValidator │    │ • Minute OHLCV  │
│ • data-status   │    │ • DataStorage   │    │ • Options Chain │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Local Storage   │
                       │                 │
                       │ • Parquet Files │
                       │ • Metadata      │
                       │ • Checksums     │
                       └─────────────────┘
```

### Data Flow

1. **Data Fetching**: CLI tools request data for specific tickers and timeframes through DataManager
2. **API Integration**: DataManager calls Polygon API with proper rate limiting and ticker-specific requests
3. **Data Processing**: Raw data is cleaned, validated, and formatted by ticker and timeframe
4. **Storage**: Processed data is stored in organized Parquet files by ticker, timeframe, and time period
5. **Retrieval**: Local data is served quickly for analysis requests with efficient file concatenation

## Components and Interfaces

### Core Components

#### DataManager

- **Purpose**: Central coordinator for all data operations across tickers and timeframes
- **Responsibilities**:
  - Orchestrate data fetching from Polygon API for multiple tickers
  - Coordinate storage and retrieval operations across timeframes
  - Handle error recovery and retry logic per ticker
  - Manage API rate limiting across concurrent requests

#### PolygonDataProvider

- **Purpose**: Interface to Polygon API for all market data types
- **Responsibilities**:
  - Fetch daily OHLCV data for any ticker
  - Fetch minute OHLCV data for any ticker
  - Fetch options chain data for optionable tickers
  - Handle API authentication and rate limits
  - Implement retry logic with exponential backoff

#### DataStorage

- **Purpose**: Multi-ticker, multi-timeframe data persistence layer
- **Responsibilities**:
  - Store data in organized Parquet files by ticker and timeframe
  - Implement efficient data retrieval with file concatenation
  - Maintain data integrity with checksums per ticker
  - Organize data hierarchically by ticker, timeframe, and time period

#### DataValidator

- **Purpose**: Data quality assurance across all tickers and timeframes
- **Responsibilities**:
  - Validate data completeness and format per ticker
  - Check for reasonable data ranges across different asset classes
  - Generate comprehensive data quality reports by ticker
  - Identify and flag data anomalies with ticker context

### Data Models

#### DailyPrice

```python
@dataclass
class DailyPrice:
    ticker: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    vwap: float  # Volume-weighted average price
```

#### MinutePrice

```python
@dataclass
class MinutePrice:
    ticker: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    vwap: float  # Volume-weighted average price
```

#### OptionsContract

```python
@dataclass
class OptionsContract:
    ticker: str  # Underlying ticker
    symbol: str  # Full options symbol
    date: date   # Trade date
    strike: float
    expiration: date
    option_type: str  # 'call' or 'put'
    bid: float
    ask: float
    last: float
    volume: int
    open_interest: int
    implied_volatility: Optional[float] = None
```

#### DataQualityReport

```python
@dataclass
class DataQualityReport:
    ticker: str
    data_type: str  # 'daily', 'minute', 'options'
    date_range: Tuple[date, date]
    total_records: int
    missing_dates: List[date]
    anomalies: List[str]
    quality_score: float  # 0.0 to 1.0
```

## Data Storage Design

### Directory Structure

```
data/
├── daily/
│   ├── AAPL/
│   │   ├── aapl_daily_2024.parquet
│   │   ├── aapl_daily_2023.parquet
│   │   └── ...
│   ├── SPY/
│   │   ├── spy_daily_2024.parquet
│   │   ├── spy_daily_2023.parquet
│   │   └── ...
│   └── SPX/
│       ├── spx_daily_2024.parquet
│       ├── spx_daily_2023.parquet
│       └── ...
├── minute/
│   ├── AAPL/
│   │   ├── 2024/
│   │   │   ├── aapl_minute_20240101.parquet
│   │   │   ├── aapl_minute_20240102.parquet
│   │   │   └── ...
│   │   └── 2023/
│   │       └── ...
│   └── SPY/
│       ├── 2024/
│       └── 2023/
├── options/
│   ├── AAPL/
│   │   ├── 2024/
│   │   │   ├── aapl_options_20240101.parquet
│   │   │   ├── aapl_options_20240102.parquet
│   │   │   └── ...
│   │   └── metadata/
│   │       └── expiration_calendar.json
│   └── SPY/
│       ├── 2024/
│       └── metadata/
├── metadata/
│   ├── checksums.json
│   ├── data_catalog.json
│   └── ticker_list.json
└── logs/
    ├── data_operations.log
    └── api_calls.log
```

### File Organization Strategy

#### Daily Data

- **Partitioning**: Annual files per ticker (e.g., `aapl_daily_2024.parquet`)
- **Rationale**: ~252 trading days per year = optimal file size for fast loading
- **Columns**: ticker, date, open, high, low, close, volume, vwap
- **Indexing**: Date-based index for fast time-series queries
- **Compression**: Snappy compression for balance of speed and size

#### Minute Data

- **Partitioning**: Daily files per ticker (e.g., `aapl_minute_20240101.parquet`)
- **Rationale**: ~390 minutes per trading day = manageable file sizes
- **Columns**: ticker, timestamp, open, high, low, close, volume, vwap
- **Indexing**: Timestamp-based index for intraday queries
- **Compression**: Snappy compression with dictionary encoding for timestamps

#### Options Data

- **Partitioning**: Daily files per ticker by trading date
- **Columns**: All options contract fields plus underlying ticker
- **Indexing**: Multi-index on (expiration, strike, option_type)
- **Compression**: Snappy compression with dictionary encoding

### Metadata Management

- **Checksums**: SHA-256 hashes for data integrity verification per file
- **Data Catalog**: JSON manifest of available data with ticker, timeframe, and date ranges
- **Ticker List**: Registry of all tickers with metadata (asset class, options availability)
- **Expiration Calendar**: Per-ticker mapping of options expiration dates

## API Integration Design

### Polygon API Integration

#### Rate Limiting Strategy

- **Tier Management**: Respect API tier limits (5 calls/minute for free tier)
- **Request Queuing**: Queue requests with proper spacing across tickers
- **Backoff Strategy**: Exponential backoff on rate limit errors
- **Caching**: Cache API responses to minimize redundant calls
- **Parallel Processing**: Concurrent requests within rate limits for different tickers

#### Error Handling

- **Retry Logic**: 3 attempts with exponential backoff (1s, 2s, 4s)
- **Timeout Handling**: 30-second timeout per request
- **Partial Failure**: Continue processing other tickers on individual failures
- **Logging**: Comprehensive logging of all API interactions with ticker context

#### Data Fetching Strategies

##### Daily Data

```python
# Fetch strategy: Batch requests by ticker and date range
def fetch_daily_data(ticker: str, start_date: date, end_date: date) -> List[DailyData]:
    # Handle weekends and holidays
    # Validate data completeness
    # Store by year for efficient access
```

##### Minute Data

```python
# Fetch strategy: Single day requests per ticker due to data volume
def fetch_minute_data(ticker: str, trade_date: date) -> List[MinutePrice]:
    # Fetch all minutes for specific ticker and date
    # Handle market hours (9:30 AM - 4:00 PM ET)
    # Validate timestamp sequences
```

##### Options Chain Data

```python
# Fetch strategy: Single day requests per ticker
def fetch_options_chain(ticker: str, trade_date: date) -> List[OptionsContract]:
    # Fetch all options for specific ticker and date
    # Filter out zero-bid contracts
    # Validate strike price ranges relative to underlying
```

## Data Validation Strategy

### Validation Rules

#### Daily Data Validation

1. **Completeness**: No missing trading days per ticker
2. **Range Checks**: OHLCV values within reasonable bounds (asset-class specific)
3. **Consistency**: High ≥ Low, High ≥ Open/Close, Low ≤ Open/Close
4. **Volume**: Positive volume on trading days
5. **Sequence**: Dates in chronological order per ticker

#### Minute Data Validation

1. **Market Hours**: Timestamps within trading hours (9:30 AM - 4:00 PM ET)
2. **Sequence**: Continuous minute timestamps with no gaps during market hours
3. **Price Consistency**: Same OHLC validation as daily data
4. **Volume Aggregation**: Daily volume should sum to minute volume totals

#### Options Data Validation

1. **Required Fields**: All essential fields present per contract
2. **Price Relationships**: Bid ≤ Ask, reasonable spreads
3. **Strike Ranges**: Strikes within reasonable bounds of underlying spot price
4. **Expiration Logic**: Expiration dates after trade dates
5. **Volume Consistency**: Open interest ≥ 0, volume ≥ 0

### Quality Scoring

- **Perfect Score (1.0)**: All validation rules pass for ticker
- **Deductions**: -0.1 per missing day, -0.05 per anomaly
- **Minimum Score (0.0)**: Critical validation failures
- **Ticker-Specific**: Separate scores maintained per ticker and timeframe

## Error Handling

### Error Categories

1. **API Errors**: Rate limits, authentication, network issues
2. **Data Errors**: Missing data, format issues, validation failures
3. **Storage Errors**: Disk space, permissions, corruption
4. **Configuration Errors**: Missing API keys, invalid paths
5. **Ticker-Specific Errors**: Invalid symbols, delisted securities

### Recovery Strategies

- **Automatic Retry**: Transient API and network errors
- **Graceful Degradation**: Continue with other tickers when one fails
- **User Notification**: Clear error messages with ticker context and suggested actions
- **Logging**: Detailed error logs with ticker and timeframe information

## Performance Considerations

### Optimization Strategies

1. **Parallel Processing**: Concurrent API requests for different tickers within rate limits
2. **Efficient Storage**: Parquet format with appropriate compression per timeframe
3. **Smart Caching**: Cache frequently accessed tickers in memory
4. **Incremental Updates**: Only fetch new/missing data per ticker
5. **Lazy Loading**: Load data on-demand rather than eagerly
6. **File Concatenation**: Efficient multi-file reading for date range queries

### Expected Performance

- **Data Fetching**: ~50 tickers of daily data per minute (rate limit dependent)
- **Data Loading**: Sub-second retrieval for annual daily data files
- **Storage Efficiency**: ~90% compression ratio vs CSV
- **Memory Usage**: <500MB for typical multi-ticker operations
- **Concurrent Operations**: Support for 10+ simultaneous ticker operations

## Testing Strategy

### Unit Testing

- **API Integration**: Mock Polygon API responses for various tickers
- **Data Validation**: Test validation rules with known good/bad data across asset classes
- **Storage Operations**: Test file I/O with temporary directories and multiple tickers
- **Error Handling**: Simulate various error conditions per ticker

### Integration Testing

- **End-to-End**: Full data fetch, store, retrieve cycle for multiple tickers
- **API Rate Limiting**: Test rate limit handling across concurrent ticker requests
- **Data Integrity**: Verify checksums and data consistency across timeframes
- **CLI Tools**: Test command-line interface functionality with multiple tickers

### Performance Testing

- **Load Testing**: Large ticker universe and date range fetching
- **Storage Performance**: Read/write speed benchmarks across timeframes
- **Memory Usage**: Profile memory consumption patterns with multiple tickers
- **Concurrent Access**: Multiple simultaneous operations across different tickers
