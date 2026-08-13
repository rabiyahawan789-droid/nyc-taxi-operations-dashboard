"""
NYC TLC Yellow Taxi — Data Cleaning Pipeline

Cleans raw NYC TLC Yellow Taxi trip data into an
analysis-ready dataset for EDA and business analysis.

Usage:
    python3 src/cleaning.py \
        --input data/raw/yellow_tripdata_2025-01.parquet \
        --output data/processed/trips_clean.parquet
"""

import argparse
import logging
from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

EXPECTED_YEAR = 2025
EXPECTED_MONTH = 1

MAX_TRIP_DURATION_MIN = 180
MAX_TRIP_DISTANCE_MILES = 100
MAX_PASSENGERS = 6


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# ============================================================
# LOOKUP TABLES
# ============================================================

RATECODE_MAP = {
    1: "Standard rate",
    2: "JFK",
    3: "Newark",
    4: "Nassau or Westchester",
    5: "Negotiated fare",
    6: "Group ride",
    99: "Unknown/Null",
}

PAYMENT_TYPE_MAP = {
    0: "Flex Fare",
    1: "Credit card",
    2: "Cash",
    3: "No charge",
    4: "Dispute",
    5: "Unknown",
    6: "Voided trip",
}


# ============================================================
# LOAD DATA
# ============================================================

def load_raw(path: str) -> pd.DataFrame:
    """Load raw TLC parquet data."""

    logger.info("Loading raw data from: %s", path)

    df = pd.read_parquet(path)

    logger.info(
        "Loaded %s rows and %s columns",
        df.shape[0],
        df.shape[1],
    )

    return df


# ============================================================
# MISSING VALUES
# ============================================================

def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values while preserving as many records as possible.

    Passenger count:
        Median imputation is used because dropping these records would
        remove a substantial portion of the dataset.

    RatecodeID:
        Missing values are labelled as Unknown/Null.

    store_and_fwd_flag:
        Missing values are explicitly labelled Unknown.

    Fee fields:
        Missing values are retained as 0 for analytical purposes,
        treating unavailable fee values as no recorded fee.
    """

    logger.info("Handling missing values...")

    before_nulls = df.isnull().sum().sum()

    # Passenger count
    passenger_median = df["passenger_count"].median()

    df["passenger_count"] = (
        df["passenger_count"]
        .fillna(passenger_median)
    )

    # Rate code
    df["RatecodeID"] = (
        df["RatecodeID"]
        .fillna(99)
    )

    # Store and forward flag
    df["store_and_fwd_flag"] = (
        df["store_and_fwd_flag"]
        .fillna("Unknown")
    )

    # Fee fields
    fee_columns = [
        "congestion_surcharge",
        "Airport_fee",
    ]

    for column in fee_columns:
        df[column] = df[column].fillna(0)

    after_nulls = df.isnull().sum().sum()

    logger.info(
        "Missing values: %s -> %s",
        before_nulls,
        after_nulls,
    )

    return df


# ============================================================
# DERIVED FEATURES
# ============================================================

def add_derived_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Create analytical features from raw trip fields."""

    logger.info("Creating derived features...")

    # --------------------------------------------------------
    # Trip duration
    # --------------------------------------------------------

    df["trip_duration_min"] = (
        df["tpep_dropoff_datetime"]
        - df["tpep_pickup_datetime"]
    ).dt.total_seconds() / 60

    # --------------------------------------------------------
    # Time features
    # --------------------------------------------------------

    df["pickup_hour"] = (
        df["tpep_pickup_datetime"].dt.hour
    )

    df["pickup_day_of_week"] = (
        df["tpep_pickup_datetime"].dt.day_name()
    )

    df["pickup_date"] = (
        df["tpep_pickup_datetime"].dt.date
    )

    df["pickup_month"] = (
        df["tpep_pickup_datetime"].dt.month
    )

    df["is_weekend"] = (
        df["tpep_pickup_datetime"].dt.dayofweek >= 5
    )

    # --------------------------------------------------------
    # Time period
    # --------------------------------------------------------

    def get_time_period(hour):

        if 5 <= hour < 12:
            return "Morning"

        elif 12 <= hour < 17:
            return "Afternoon"

        elif 17 <= hour < 21:
            return "Evening"

        else:
            return "Night"

    df["time_period"] = (
        df["pickup_hour"]
        .apply(get_time_period)
    )

    # --------------------------------------------------------
    # Fare efficiency
    # --------------------------------------------------------

    df["fare_per_mile"] = np.where(
        df["trip_distance"] > 0,
        df["fare_amount"] / df["trip_distance"],
        np.nan,
    )

    df["fare_per_minute"] = np.where(
        df["trip_duration_min"] > 0,
        df["fare_amount"] / df["trip_duration_min"],
        np.nan,
    )

    # --------------------------------------------------------
    # Duration efficiency
    # --------------------------------------------------------

    df["duration_per_mile"] = np.where(
        df["trip_distance"] > 0,
        df["trip_duration_min"] / df["trip_distance"],
        np.nan,
    )

    # --------------------------------------------------------
    # Tip rate
    # --------------------------------------------------------

    df["tip_rate"] = np.where(
        df["fare_amount"] > 0,
        df["tip_amount"] / df["fare_amount"],
        np.nan,
    )

    # --------------------------------------------------------
    # Lookup labels
    # --------------------------------------------------------

    df["ratecode_label"] = (
        df["RatecodeID"]
        .map(RATECODE_MAP)
        .fillna("Unknown/Null")
    )

    df["payment_type_label"] = (
        df["payment_type"]
        .map(PAYMENT_TYPE_MAP)
        .fillna("Unknown")
    )

    logger.info(
        "Created %s analytical features",
        13,
    )

    return df


# ============================================================
# FILTER INVALID RECORDS
# ============================================================

def filter_invalid_trips(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove records that are unsuitable for business analysis.

    Every filtering step is logged so the cleaning process
    remains auditable and reproducible.
    """

    logger.info("Filtering invalid trips...")

    before = len(df)

    # --------------------------------------------------------
    # 1. Expected month
    # --------------------------------------------------------

    mask = (
        (df["tpep_pickup_datetime"].dt.year == EXPECTED_YEAR)
        & (
            df["tpep_pickup_datetime"].dt.month
            == EXPECTED_MONTH
        )
    )

    removed = (~mask).sum()

    logger.info(
        "Outside expected month: %s rows removed",
        removed,
    )

    df = df.loc[mask]

    # --------------------------------------------------------
    # 2. Trip duration
    # --------------------------------------------------------

    mask = (
        (df["trip_duration_min"] > 0)
        & (
            df["trip_duration_min"]
            <= MAX_TRIP_DURATION_MIN
        )
    )

    removed = (~mask).sum()

    logger.info(
        "Invalid trip duration: %s rows removed",
        removed,
    )

    df = df.loc[mask]

    # --------------------------------------------------------
    # 3. Trip distance
    # --------------------------------------------------------

    mask = (
        (df["trip_distance"] > 0)
        & (
            df["trip_distance"]
            <= MAX_TRIP_DISTANCE_MILES
        )
    )

    removed = (~mask).sum()

    logger.info(
        "Invalid trip distance: %s rows removed",
        removed,
    )

    df = df.loc[mask]

    # --------------------------------------------------------
    # 4. Fare and total amount
    # --------------------------------------------------------

    mask = (
        (df["fare_amount"] > 0)
        & (df["total_amount"] > 0)
    )

    removed = (~mask).sum()

    logger.info(
        "Invalid fare/total amount: %s rows removed",
        removed,
    )

    df = df.loc[mask]

    # --------------------------------------------------------
    # 5. Passenger count
    # --------------------------------------------------------

    mask = df["passenger_count"].between(
        1,
        MAX_PASSENGERS,
    )

    removed = (~mask).sum()

    logger.info(
        "Invalid passenger count: %s rows removed",
        removed,
    )

    df = df.loc[mask]

    logger.info(
        "Filtering complete: %s -> %s rows (%.1f%% retained)",
        before,
        len(df),
        100 * len(df) / before,
    )

    return df.reset_index(drop=True)


# ============================================================
# DUPLICATES
# ============================================================

def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove exact duplicate records."""

    before = len(df)

    df = df.drop_duplicates()

    removed = before - len(df)

    logger.info(
        "Exact duplicate rows removed: %s",
        removed,
    )

    return df


# ============================================================
# DATA QUALITY CHECK
# ============================================================

def run_quality_checks(df: pd.DataFrame) -> None:
    """Run final validation checks."""

    logger.info("Running final data quality checks...")

    assert df["trip_duration_min"].gt(0).all()
    assert df["trip_distance"].gt(0).all()
    assert df["total_amount"].gt(0).all()
    assert df["passenger_count"].between(1, 6).all()

    logger.info("All quality checks passed.")


# ============================================================
# COMPLETE CLEANING PIPELINE
# ============================================================

def clean(df: pd.DataFrame) -> pd.DataFrame:

    df = handle_missing_values(df)

    df = add_derived_fields(df)

    df = filter_invalid_trips(df)

    df = remove_duplicates(df)

    run_quality_checks(df)

    return df


# ============================================================
# MAIN
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description="Clean NYC TLC Yellow Taxi trip data."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to raw parquet file",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path for cleaned parquet file",
    )

    args = parser.parse_args()

    # --------------------------------------------------------
    # Create output directory if necessary
    # --------------------------------------------------------

    output_path = Path(args.output)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Pipeline
    # --------------------------------------------------------

    df = load_raw(args.input)

    df_clean = clean(df)

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    logger.info(
        "Writing cleaned data to: %s",
        args.output,
    )

    df_clean.to_parquet(
        args.output,
        index=False,
    )

    logger.info(
        "Pipeline complete. Final dataset: %s rows × %s columns",
        df_clean.shape[0],
        df_clean.shape[1],
    )


if __name__ == "__main__":
    main()