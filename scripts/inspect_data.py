import pandas as pd
import os

data_path = "data"
all_data = []

for file in os.listdir(data_path):
    if file.endswith(".xlsx"):
        print(f"Loading: {file}")

        file_path = os.path.join(data_path, file)

        df = pd.read_excel(
            file_path,
            sheet_name="Monthly by Route",
            header=7
        )

        # Fix column names
        df.columns = df.iloc[0]
        df = df[1:]

        all_data.append(df)

combined = pd.concat(all_data, ignore_index=True)

id_cols = [
    "Mode",
    "Route Type",
    "Route Num",
    "Route Name",
    "RPTP Level of Service",
    "Area"
]

# 🔥 FIX: detect date columns properly
date_cols = [
    col for col in combined.columns
    if str(col).startswith("20")  # catches 2023-07-01 etc
]

long_df = combined.melt(
    id_vars=id_cols,
    value_vars=date_cols,
    var_name="month",
    value_name="passengers"
)

# Clean month
long_df["month"] = pd.to_datetime(long_df["month"], errors="coerce")

# Clean passenger values
long_df["passengers"] = (
    long_df["passengers"]
    .astype(str)
    .str.replace(",", "")
    .str.strip()
)

long_df["passengers"] = pd.to_numeric(long_df["passengers"], errors="coerce")

# Drop bad rows
long_df = long_df.dropna(subset=["passengers"])
long_df = long_df[long_df["Route Num"].notna()]
long_df = long_df[long_df["Route Num"] != "ADJUST"]

# Save clean data
long_df.to_csv("data/clean_patronage_by_route.csv", index=False)

print("✅ Saved clean data to data/clean_patronage_by_route.csv")
print(long_df.head())
print(long_df.shape)