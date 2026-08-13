import pandas as pd
from pathlib import Path

# Load cleaned data
df = pd.read_parquet(
    "data/processed/trips_clean.parquet"
)

# Load taxi zone lookup
zones = pd.read_csv(
    "data/raw/taxi_zone_lookup.csv"
)

# --------------------------------------------------
# 1. Hourly performance
# --------------------------------------------------

hourly = (
    df.groupby("pickup_hour")
      .agg(
          trips=("VendorID", "size"),
          revenue=("total_amount", "sum"),
          avg_revenue=("total_amount", "mean"),
          avg_fare_per_mile=("fare_per_mile", "mean"),
          avg_duration_per_mile=("duration_per_mile", "mean"),
          avg_tip_rate=("tip_rate", "mean")
      )
      .reset_index()
)

hourly.to_csv(
    "data/processed/hourly_performance.csv",
    index=False
)


# --------------------------------------------------
# 2. Daily performance
# --------------------------------------------------

daily = (
    df.groupby(["pickup_date", "pickup_day_of_week"])
      .agg(
          trips=("VendorID", "size"),
          revenue=("total_amount", "sum"),
          avg_revenue=("total_amount", "mean")
      )
      .reset_index()
)

daily.to_csv(
    "data/processed/daily_performance.csv",
    index=False
)


# --------------------------------------------------
# 3. Zone performance
# --------------------------------------------------

zone = (
    df.groupby("PULocationID")
      .agg(
          trips=("VendorID", "size"),
          revenue=("total_amount", "sum"),
          avg_revenue=("total_amount", "mean"),
          avg_fare_per_mile=("fare_per_mile", "mean"),
          avg_duration_per_mile=("duration_per_mile", "mean"),
          avg_tip_rate=("tip_rate", "mean")
      )
      .reset_index()
)

zone = zone.merge(
    zones[["LocationID", "Zone", "Borough"]],
    left_on="PULocationID",
    right_on="LocationID",
    how="left"
)

zone = zone.drop(columns=["LocationID"])

zone.to_csv(
    "data/processed/zone_performance.csv",
    index=False
)


# --------------------------------------------------
# 4. Payment performance
# --------------------------------------------------

payment = (
    df.groupby("payment_type_label")
      .agg(
          trips=("VendorID", "size"),
          revenue=("total_amount", "sum"),
          avg_revenue=("total_amount", "mean"),
          avg_tip=("tip_amount", "mean"),
          avg_tip_rate=("tip_rate", "mean")
      )
      .reset_index()
)

payment.to_csv(
    "data/processed/payment_performance.csv",
    index=False
)


# --------------------------------------------------
# 5. Rate-code performance
# --------------------------------------------------

rate = (
    df.groupby("ratecode_label")
      .agg(
          trips=("VendorID", "size"),
          revenue=("total_amount", "sum"),
          avg_revenue=("total_amount", "mean"),
          avg_fare_per_mile=("fare_per_mile", "mean"),
          avg_duration_per_mile=("duration_per_mile", "mean")
      )
      .reset_index()
)

rate.to_csv(
    "data/processed/rate_performance.csv",
    index=False
)


print("Dashboard datasets created successfully.")