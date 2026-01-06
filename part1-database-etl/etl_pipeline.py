import pandas as pd
import glob
import os
import numpy as np
import re
from sqlalchemy import create_engine



# Path to your folder
folder_path = r"C:\Users\Hp\Documents\BITSOM graded assigments" 

# Find all CSV files in the folder
csv_files = glob.glob(os.path.join(folder_path, "*.csv"))

print("Found CSV files:", csv_files)

# Read all CSVs into a list of DataFrames
dfs = [pd.read_csv(file) for file in csv_files]

# Optionally, concatenate them into one DataFrame
combined_df = pd.concat(dfs, ignore_index=True)

# Show first few rows
print(combined_df.head())

# --- Helper functions ---

def standardize_phone(phone):
    """Convert phone numbers to +91-XXXXXXXXXX format if possible."""
    if pd.isna(phone):
        return np.nan
    s = re.sub(r"\D", "", str(phone))  # keep only digits
    if len(s) == 10:  # assume Indian mobile
        return f"+91-{s}"
    elif s.startswith("91") and len(s) >= 12:
        return f"+91-{s[-10:]}"
    elif s.startswith("0") and len(s) >= 11:
        return f"+91-{s[-10:]}"
    else:
        return np.nan  # drop invalids

def standardize_category(cat):
    """Normalize category names to title case."""
    if pd.isna(cat):
        return np.nan
    return str(cat).strip().title()

def parse_date_to_iso(date_val):
    """Convert dates to YYYY-MM-DD format."""
    if pd.isna(date_val) or str(date_val).strip() == "":
        return np.nan
    try:
        ts = pd.to_datetime(date_val, errors="coerce", dayfirst=True)
        if pd.isna(ts):
            return np.nan
        return ts.strftime("%Y-%m-%d")
    except Exception:
        return np.nan

# --- Transformation pipeline ---

def transform_data(df):
    # Remove duplicates
    df = df.drop_duplicates()

    # Handle missing values
    # Drop rows missing essential fields
    essential_cols = ["name", "phone", "category", "date"]
    df = df.dropna(subset=[c for c in essential_cols if c in df.columns])

    # Fill optional fields with defaults
    if "email" in df.columns:
        df["email"] = df["email"].fillna("unknown@example.com")
    if "address" in df.columns:
        df["address"] = df["address"].fillna("Unknown")

    # Standardize phone
    if "phone" in df.columns:
        df["phone"] = df["phone"].apply(standardize_phone)

    # Standardize category
    if "category" in df.columns:
        df["category"] = df["category"].apply(standardize_category)

    # Convert dates
    if "date" in df.columns:
        df["date"] = df["date"].apply(parse_date_to_iso)

    # Add surrogate keys (auto-increment IDs)
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)

    return df



