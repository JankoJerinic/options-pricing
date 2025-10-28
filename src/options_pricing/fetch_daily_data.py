from datetime import date, timedelta
from pathlib import Path
import pandas as pd

from options_pricing.config import POLYGON_API_KEY, RAW_DIR
# from polygon_utils import mk_client, get_aggs_daily


if __name__ == "__main__":
    # 20Y window ending today (use U.S. business days later in QA)
    today = date.today()
    start = (
        today - timedelta(days=365 * 20 + 6)
    ).isoformat()  # +6 to cushion leap-years
    end = today.isoformat()
