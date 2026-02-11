"""
World Bank Data Extraction Script
Extracts internet_penetration (Individuals using the Internet % of population).

Data source: World Development Indicators
File: worldbank/internetpenetration.csv
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
    WORLDBANK_DIR,
    standardize_country_name,
    INDICATOR_NAMES,
)


def extract_worldbank_data():
    """
    Extract World Bank Internet Penetration data for target countries.

    The CSV file format (World Bank):
    - First few rows are metadata
    - Headers: Country Name, Country Code, Indicator Name, Indicator Code, 1960, 1961, ..., 2024
    - Data is in wide format (years as columns)

    Returns:
        DataFrame with extracted data.
    """
    wb_file = WORLDBANK_DIR / "internetpenetration.csv"

    if not wb_file.exists():
        raise FileNotFoundError(f"World Bank data file not found: {wb_file}")

    print(f"Loading World Bank data from: {wb_file}")

    # Read CSV, skipping metadata rows
    # World Bank CSVs typically have metadata in first 4 rows
    wb_df = pd.read_csv(wb_file, skiprows=4)

    print(f"Columns found: {wb_df.columns.tolist()[:15]}...")  # Show first 15 columns

    # Find country column
    country_col = None
    for col in wb_df.columns:
        if "country name" in str(col).lower():
            country_col = col
            break

    if country_col is None:
        country_col = wb_df.columns[0]
        print(f"Using first column as country: {country_col}")

    # Standardize country names and filter
    wb_df["standardized_country"] = wb_df[country_col].apply(standardize_country_name)
    wb_df_filtered = wb_df[wb_df["standardized_country"].isin(TARGET_COUNTRIES)].copy()

    print(
        f"\nCountries found: {wb_df_filtered['standardized_country'].unique().tolist()}"
    )

    # Convert from wide to long format
    # Year columns are numeric (strings like '2010', '2011', etc.)
    year_columns = []
    for col in wb_df.columns:
        try:
            year = int(col)
            if YEAR_START <= year <= YEAR_END:
                year_columns.append(str(col))
        except (ValueError, TypeError):
            continue

    print(f"Year columns to extract: {year_columns}")

    # Melt the dataframe
    result_rows = []
    for _, row in wb_df_filtered.iterrows():
        country = row["standardized_country"]

        for year_col in year_columns:
            year = int(year_col)
            value = row.get(year_col)

            # Clean the value
            if pd.notna(value) and str(value).strip() != "":
                try:
                    value = float(value)
                    result_rows.append(
                        {
                            "country": country,
                            "year": year,
                            "indicator": INDICATOR_NAMES["internet_penetration"],
                            "value": round(value, 2),
                            "source": "World Bank",
                        }
                    )
                except (ValueError, TypeError):
                    # Skip invalid values
                    pass

    result_df = pd.DataFrame(result_rows)
    return result_df


def main():
    """Main function to extract World Bank data."""
    print("=" * 60)
    print("World Bank Internet Penetration Data Extraction")
    print("=" * 60)

    try:
        result_df = extract_worldbank_data()

        # Save intermediate result
        output_path = DATA_INTERMEDIATE_DIR / "worldbank_extracted.csv"
        result_df.to_csv(output_path, index=False)
        print(f"\nSaved World Bank data to: {output_path}")
        print(f"Total records: {len(result_df)}")

        # Show summary
        print("\nData summary:")
        print(result_df.groupby("country")["year"].agg(["min", "max", "count"]))

        return result_df

    except Exception as e:
        print(f"Error extracting World Bank data: {e}")
        import traceback

        traceback.print_exc()
        return pd.DataFrame()


if __name__ == "__main__":
    main()
