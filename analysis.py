import pandas as pd

# Load the dataset
df = pd.read_parquet("yellow_tripdata_2025-01.parquet")

# Basic inspection
print("Dataset shape:", df.shape)

print("\nFirst 5 rows:")
print(df.head())

print("\nColumn information:")
print(df.info())

print("\nMissing values:")
print(df.isnull().sum())