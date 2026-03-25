import pandas as pd

df = pd.read_csv("data.csv")

# Downcast numeric columns
for col in df.select_dtypes(include=['int', 'float']).columns:
    df[col] = pd.to_numeric(df[col], downcast='unsigned' if df[col].min() >= 0 else 'float')

# Convert text columns to category
for col in df.select_dtypes(include=['object']).columns:
    if df[col].nunique() < 0.5 * len(df):  # heuristic
        df[col] = df[col].astype('category')

# Save as parquet (with compression)
df.to_parquet("data.parquet", compression="snappy", index=False)