"""
Data Consolidation Script
Merges all extracted data into a single unified CSV file.

Output format:
- country: Standard country name
- year: Year (2010-2025)
- indicator: Indicator name
- value: Numeric value
- source: Data source
"""

import pandas as pd
import os
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
    OUTPUT_DIR,
    INDICATOR_NAMES,
    INDICATOR_SOURCES,
)


def load_intermediate_data():
    """
    Load all intermediate data files.

    Returns:
        Dictionary of DataFrames keyed by source name.
    """
    data_files = {
        "vdem": DATA_INTERMEDIATE_DIR / "vdem_extracted.csv",
        "wgi": DATA_INTERMEDIATE_DIR / "wgi_extracted.csv",
        "worldbank": DATA_INTERMEDIATE_DIR / "worldbank_extracted.csv",
        "internet_freedom": DATA_INTERMEDIATE_DIR / "internet_freedom_extracted.csv",
        "trust_in_news": DATA_INTERMEDIATE_DIR / "trust_in_news_extracted.csv",
        "periods": DATA_INTERMEDIATE_DIR / "periods_generated.csv",
    }

    loaded_data = {}

    for name, filepath in data_files.items():
        if filepath.exists():
            try:
                df = pd.read_csv(filepath)
                if df.empty:
                    print(f"  Warning: {name} file is empty: {filepath}")
                    loaded_data[name] = pd.DataFrame()
                else:
                    loaded_data[name] = df
                    print(f"  Loaded {name}: {len(df)} records")
            except pd.errors.EmptyDataError:
                print(f"  Warning: {name} file is empty or has no data: {filepath}")
                loaded_data[name] = pd.DataFrame()
            except Exception as e:
                print(f"  Error loading {name}: {e}")
                loaded_data[name] = pd.DataFrame()
        else:
            print(f"  Warning: {name} file not found: {filepath}")
            loaded_data[name] = pd.DataFrame()

    return loaded_data


def consolidate_data(data_dict: dict) -> pd.DataFrame:
    """
    Consolidate all data into a single DataFrame.

    Args:
        data_dict: Dictionary of DataFrames

    Returns:
        Consolidated DataFrame
    """
    # Combine all non-empty DataFrames
    dfs_to_combine = []

    for name, df in data_dict.items():
        if not df.empty:
            # Ensure standard columns exist
            required_cols = ["country", "year", "indicator", "value", "source"]
            for col in required_cols:
                if col not in df.columns:
                    df[col] = None

            # Select only required columns
            df = df[required_cols].copy()
            dfs_to_combine.append(df)

    if not dfs_to_combine:
        print("Warning: No data to consolidate!")
        return pd.DataFrame(columns=["country", "year", "indicator", "value", "source"])

    # Concatenate all data
    consolidated = pd.concat(dfs_to_combine, ignore_index=True)

    # Remove rows with missing values (except for templates)
    # Keep rows that have actual values
    consolidated = consolidated[consolidated["value"].notna()].copy()

    # Sort by country, year, indicator
    consolidated = consolidated.sort_values(
        ["country", "year", "indicator"]
    ).reset_index(drop=True)

    return consolidated


def create_wide_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a wide-format version of the data (indicators as columns).

    Args:
        df: Long-format DataFrame

    Returns:
        Wide-format DataFrame with indicators as columns
    """
    if df.empty:
        return df

    # Pivot to wide format
    wide_df = df.pivot_table(
        index=["country", "year"],
        columns="indicator",
        values="value",
        aggfunc="first",  # Take first value if duplicates
    ).reset_index()

    # Flatten column names
    wide_df.columns.name = None

    # Reorder columns
    indicator_order = [
        "Liberal Democracy",
        "Polarization",
        "Governance Quality",
        "Internet Freedom",
        "Internet Penetration",
        "Trust in News",
        "Election Period",
        "Covid Period",
    ]

    # Get available indicators in order
    available_cols = ["country", "year"]
    for ind in indicator_order:
        if ind in wide_df.columns:
            available_cols.append(ind)

    # Add any remaining indicators
    for col in wide_df.columns:
        if col not in available_cols:
            available_cols.append(col)

    wide_df = wide_df[available_cols]

    return wide_df


def generate_data_summary(df: pd.DataFrame) -> str:
    """
    Generate a summary of the consolidated data.

    Args:
        df: Consolidated DataFrame

    Returns:
        Summary string
    """
    summary = []
    summary.append("\n" + "=" * 60)
    summary.append("DATA SUMMARY")
    summary.append("=" * 60)

    # Overall stats
    summary.append(f"\nTotal records: {len(df)}")
    summary.append(f"Countries: {df['country'].nunique()}")
    summary.append(f"Year range: {df['year'].min()} - {df['year'].max()}")
    summary.append(f"Indicators: {df['indicator'].nunique()}")

    # By indicator
    summary.append("\n--- Records by Indicator ---")
    for indicator in df["indicator"].unique():
        count = len(df[df["indicator"] == indicator])
        summary.append(f"  {indicator}: {count}")

    # By country
    summary.append("\n--- Records by Country ---")
    for country in sorted(df["country"].unique()):
        count = len(df[df["country"] == country])
        summary.append(f"  {country}: {count}")

    # Missing data check
    summary.append("\n--- Data Coverage Check ---")
    for country in TARGET_COUNTRIES:
        country_data = df[df["country"] == country]
        for indicator in INDICATOR_NAMES.values():
            ind_data = country_data[country_data["indicator"] == indicator]
            if ind_data.empty:
                summary.append(f"  Missing: {country} - {indicator}")
            else:
                years = sorted(ind_data["year"].tolist())
                year_range = f"{min(years)}-{max(years)}" if years else "none"
                summary.append(
                    f"  {country} - {indicator}: {len(years)} years ({year_range})"
                )

    return "\n".join(summary)


def main():
    """Main function to consolidate all data."""
    print("=" * 60)
    print("Data Consolidation")
    print("=" * 60)

    # Load intermediate data
    print("\n[1] Loading intermediate data files...")
    data_dict = load_intermediate_data()

    # Consolidate data
    print("\n[2] Consolidating data...")
    consolidated_df = consolidate_data(data_dict)
    print(f"  Total consolidated records: {len(consolidated_df)}")

    # Save long format
    print("\n[3] Saving consolidated data (long format)...")
    output_path_long = OUTPUT_DIR / "contextual_metadata_long.csv"
    consolidated_df.to_csv(output_path_long, index=False)
    print(f"  Saved to: {output_path_long}")

    # Create and save wide format
    print("\n[4] Creating wide format...")
    wide_df = create_wide_format(consolidated_df)
    output_path_wide = OUTPUT_DIR / "contextual_metadata_wide.csv"
    wide_df.to_csv(output_path_wide, index=False)
    print(f"  Saved to: {output_path_wide}")
    print(f"  Wide format: {len(wide_df)} rows x {len(wide_df.columns)} columns")

    # Generate and print summary
    summary = generate_data_summary(consolidated_df)
    print(summary)

    # Save summary to file
    summary_path = OUTPUT_DIR / "data_summary.txt"
    with open(summary_path, "w") as f:
        f.write(summary)
    print(f"\nSummary saved to: {summary_path}")

    return consolidated_df


if __name__ == "__main__":
    main()
