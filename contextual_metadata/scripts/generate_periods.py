"""
Election Period and COVID Period Generation Script
Generates binary indicators for:
1. Election Period - 1 if the country had a major election that year, 0 otherwise
2. COVID Period - 1 if year is 2019-2023, 0 otherwise

Election data is based on major national elections (parliamentary/presidential).
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
    ELECTION_YEARS,
    COVID_START_YEAR,
    COVID_END_YEAR,
    is_election_period,
    is_covid_period,
    INDICATOR_NAMES,
)


def generate_election_period_data() -> pd.DataFrame:
    """
    Generate Election Period indicator for all target countries and years.

    Returns:
        DataFrame with Election Period data (binary: 1 = election year, 0 = not)
    """
    rows = []

    for country in TARGET_COUNTRIES:
        for year in range(YEAR_START, YEAR_END + 1):
            value = is_election_period(country, year)
            rows.append(
                {
                    "country": country,
                    "year": year,
                    "indicator": INDICATOR_NAMES["election_period"],
                    "value": value,
                    "source": "Manual",
                }
            )

    return pd.DataFrame(rows)


def generate_covid_period_data() -> pd.DataFrame:
    """
    Generate COVID Period indicator for all target countries and years.

    Returns:
        DataFrame with COVID Period data (binary: 1 = 2019-2023, 0 = otherwise)
    """
    rows = []

    for country in TARGET_COUNTRIES:
        for year in range(YEAR_START, YEAR_END + 1):
            value = is_covid_period(year)
            rows.append(
                {
                    "country": country,
                    "year": year,
                    "indicator": INDICATOR_NAMES["covid_period"],
                    "value": value,
                    "source": "Manual",
                }
            )

    return pd.DataFrame(rows)


def main():
    """Main function to generate period indicators."""
    print("=" * 60)
    print("Election Period and COVID Period Generation")
    print("=" * 60)

    # Print election years for reference
    print("\n[1] Election years by country:")
    for country, years in ELECTION_YEARS.items():
        print(f"  {country}: {years}")

    print(f"\n[2] COVID period defined as: {COVID_START_YEAR}-{COVID_END_YEAR}")

    # Generate data
    print("\n[3] Generating Election Period data...")
    election_df = generate_election_period_data()
    print(f"  Generated {len(election_df)} records")

    print("\n[4] Generating COVID Period data...")
    covid_df = generate_covid_period_data()
    print(f"  Generated {len(covid_df)} records")

    # Combine
    result_df = pd.concat([election_df, covid_df], ignore_index=True)

    # Save
    output_path = DATA_INTERMEDIATE_DIR / "periods_generated.csv"
    result_df.to_csv(output_path, index=False)
    print(f"\nSaved period data to: {output_path}")
    print(f"Total records: {len(result_df)}")

    # Show summary
    print("\nElection Period summary (years with elections):")
    election_years_df = election_df[election_df["value"] == 1]
    for country in TARGET_COUNTRIES:
        country_elections = election_years_df[election_years_df["country"] == country][
            "year"
        ].tolist()
        print(f"  {country}: {country_elections}")

    return result_df


if __name__ == "__main__":
    main()
