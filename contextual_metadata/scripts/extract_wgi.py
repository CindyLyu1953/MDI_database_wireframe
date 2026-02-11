"""
WGI (World Governance Indicators) Data Extraction Script
Extracts wgi_pv (Political Stability and Absence of Violence) as Governance Quality indicator.

Data source: World Bank WGI Dataset
File: wgi/wgidataset.xlsx
"""

import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path for config import
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_DIR))

from config import (
    TARGET_COUNTRIES,
    YEAR_START,
    YEAR_END,
    DATA_INTERMEDIATE_DIR,
    WGI_DIR,
    standardize_country_name,
    INDICATOR_NAMES,
)


def extract_wgi_data():
    """
    Extract WGI Political Stability indicator for target countries.

    Expected columns in the Excel file:
    - Economy (name): Country name
    - Year: Year
    - Governance score (0-100): The wgi_pv indicator (Political Stability percentile rank)

    Returns:
        DataFrame with extracted data.
    """
    wgi_file = WGI_DIR / "wgidataset.xlsx"

    if not wgi_file.exists():
        raise FileNotFoundError(f"WGI data file not found: {wgi_file}")

    print(f"Loading WGI data from: {wgi_file}")

    # Read Excel file - may need to check sheet names
    try:
        # First, check available sheets
        xl = pd.ExcelFile(wgi_file)
        print(f"Available sheets: {xl.sheet_names}")

        # Try to read the first sheet or a specific sheet
        wgi_df = pd.read_excel(wgi_file, sheet_name=0)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        # Try reading with different parameters
        wgi_df = pd.read_excel(wgi_file, engine="openpyxl")

    print(f"Columns found: {wgi_df.columns.tolist()}")
    print(f"First few rows:\n{wgi_df.head()}")

    # Find the correct column names based on actual WGI file structure
    # Expected columns: 'Economy (name)', 'Year', 'Governance score (0-100)'

    # Look for country column
    country_col = None
    for col in wgi_df.columns:
        col_lower = str(col).lower()
        if "economy (name)" in col_lower or col_lower == "economy (name)":
            country_col = col
            break
        elif "economy" in col_lower and "name" in col_lower:
            country_col = col
            break

    if country_col is None:
        # Try other patterns
        for col in wgi_df.columns:
            col_lower = str(col).lower()
            if "country" in col_lower:
                country_col = col
                break

    if country_col is None:
        # Check if 'Economy (name)' exists exactly
        if "Economy (name)" in wgi_df.columns:
            country_col = "Economy (name)"
        else:
            raise ValueError(
                f"Cannot find country column. Available: {wgi_df.columns.tolist()}"
            )

    # Look for year column (exact match first)
    year_col = None
    if "Year" in wgi_df.columns:
        year_col = "Year"
    else:
        for col in wgi_df.columns:
            col_lower = str(col).lower()
            if col_lower == "year":
                year_col = col
                break

    if year_col is None:
        raise ValueError("Cannot find year column in WGI data")

    # Look for governance score column (exact match first)
    score_col = None
    if "Governance score (0-100)" in wgi_df.columns:
        score_col = "Governance score (0-100)"
    else:
        for col in wgi_df.columns:
            col_lower = str(col).lower()
            if "governance score" in col_lower or "score (0-100)" in col_lower:
                score_col = col
                break

    if score_col is None:
        raise ValueError(
            f"Cannot find governance score column. Available: {wgi_df.columns.tolist()}"
        )

    print(f"\nUsing columns:")
    print(f"  Country: {country_col}")
    print(f"  Year: {year_col}")
    print(f"  Score: {score_col}")

    # Convert Year column to numeric (it might be string)
    wgi_df[year_col] = pd.to_numeric(wgi_df[year_col], errors="coerce")

    # Filter by year
    wgi_df = wgi_df[(wgi_df[year_col] >= YEAR_START) & (wgi_df[year_col] <= YEAR_END)]

    # Standardize country names and filter
    wgi_df["standardized_country"] = wgi_df[country_col].apply(standardize_country_name)
    wgi_df = wgi_df[wgi_df["standardized_country"].isin(TARGET_COUNTRIES)]

    # Create result DataFrame
    result_rows = []
    for _, row in wgi_df.iterrows():
        country = row["standardized_country"]
        year = int(row[year_col])
        value = row[score_col]

        if pd.notna(value):
            result_rows.append(
                {
                    "country": country,
                    "year": year,
                    "indicator": INDICATOR_NAMES["wgi_pv"],
                    "value": value,
                    "source": "WGI",
                }
            )

    result_df = pd.DataFrame(result_rows)
    return result_df


def main():
    """Main function to extract WGI data."""
    print("=" * 60)
    print("WGI Data Extraction")
    print("=" * 60)

    try:
        result_df = extract_wgi_data()

        # Save intermediate result
        output_path = DATA_INTERMEDIATE_DIR / "wgi_extracted.csv"
        result_df.to_csv(output_path, index=False)
        print(f"\nSaved WGI data to: {output_path}")
        print(f"Total records: {len(result_df)}")

        # Show summary
        print("\nData summary:")
        print(result_df.groupby(["country", "indicator"]).size())

        return result_df

    except Exception as e:
        print(f"Error extracting WGI data: {e}")
        import traceback

        traceback.print_exc()
        return pd.DataFrame()


if __name__ == "__main__":
    main()
