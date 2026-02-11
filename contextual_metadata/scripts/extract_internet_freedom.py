"""
Internet Freedom Data Extraction Script
Extracts internet_freedom_score from Freedom House data.

Data sources:
- 2019-2024: Excel files (internetfreedom_*.xlsx) - Direct read
- 2011-2018, 2025: PDF files (internetfreedom_*.pdf) - Requires Gemini extraction

Excel format (2019-2024):
- Country: Country name
- Total: Internet freedom score (0-100, higher = more free)

PDF format (2011-2018, 2025):
- Page titled "Key Internet Controls by Country"
- Contains FOTN Score (Freedom on the Net Score)
- Our score = 100 - FOTN Score (to align with later years where higher = more free)
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
    INTERNET_FREEDOM_DIR,
    standardize_country_name,
    INDICATOR_NAMES,
)


def extract_excel_data(year: int) -> pd.DataFrame:
    """
    Extract Internet Freedom data from Excel file for a specific year.

    Freedom House Excel format:
    - Row 0: Title row
    - Row 1: Headers (Country, Edition, Status, ..., Total)
    - Row 2+: Data

    Args:
        year: Year to extract (2019-2024)

    Returns:
        DataFrame with extracted data for target countries.
    """
    excel_file = INTERNET_FREEDOM_DIR / f"internetfreedom_{year}.xlsx"

    if not excel_file.exists():
        print(f"Excel file not found: {excel_file}")
        return pd.DataFrame()

    print(f"  Reading Excel: {excel_file.name}")

    try:
        # Read Excel file with header at row 1 (0-indexed, so skiprows=1 or header=1)
        df = pd.read_excel(excel_file, header=1)
        print(f"  Columns: {df.columns.tolist()[:10]}...")  # Show first 10 columns

        # Find country column (should be first column or named 'Country')
        country_col = None
        for col in df.columns:
            if "country" in str(col).lower():
                country_col = col
                break

        if country_col is None:
            country_col = df.columns[0]

        # Find total/score column (should be 'Total' or last column)
        score_col = None
        for col in df.columns:
            col_lower = str(col).lower()
            if col_lower == "total":
                score_col = col
                break

        if score_col is None:
            # Try the last column
            score_col = df.columns[-1]

        print(f"  Using country col: '{country_col}', score col: '{score_col}'")

        # Filter for target countries
        df["standardized_country"] = df[country_col].apply(standardize_country_name)
        df_filtered = df[df["standardized_country"].isin(TARGET_COUNTRIES)].copy()

        print(f"  Found {len(df_filtered)} target countries")

        # Create result rows
        result_rows = []
        for _, row in df_filtered.iterrows():
            country = row["standardized_country"]
            value = row[score_col]

            if pd.notna(value):
                try:
                    result_rows.append(
                        {
                            "country": country,
                            "year": year,
                            "indicator": INDICATOR_NAMES["internet_freedom_score"],
                            "value": float(value),
                            "source": "Freedom House",
                        }
                    )
                except (ValueError, TypeError):
                    print(f"  Warning: Could not convert value '{value}' for {country}")

        return pd.DataFrame(result_rows)

    except Exception as e:
        print(f"  Error reading {excel_file}: {e}")
        import traceback

        traceback.print_exc()
        return pd.DataFrame()


def extract_all_excel_data() -> pd.DataFrame:
    """
    Extract Internet Freedom data from all available Excel files (2019-2024).

    Returns:
        DataFrame with all extracted data.
    """
    all_data = []

    for year in range(2019, 2025):
        df = extract_excel_data(year)
        if not df.empty:
            all_data.append(df)

    if all_data:
        return pd.concat(all_data, ignore_index=True)
    return pd.DataFrame()


def create_pdf_extraction_template() -> pd.DataFrame:
    """
    Create a template for PDF data that needs to be extracted via Gemini.

    Returns:
        DataFrame template for years 2011-2018 and 2025.
    """
    rows = []
    # 2011-2018 PDFs
    for year in range(2011, 2019):
        for country in TARGET_COUNTRIES:
            rows.append(
                {
                    "country": country,
                    "year": year,
                    "indicator": INDICATOR_NAMES["internet_freedom_score"],
                    "value": None,  # To be filled by Gemini extraction
                    "source": "Freedom House",
                }
            )

    # 2025 PDF (if within range)
    if 2025 >= YEAR_START and 2025 <= YEAR_END:
        for country in TARGET_COUNTRIES:
            rows.append(
                {
                    "country": country,
                    "year": 2025,
                    "indicator": INDICATOR_NAMES["internet_freedom_score"],
                    "value": None,  # To be filled by Gemini extraction
                    "source": "Freedom House",
                }
            )

    return pd.DataFrame(rows)


def main():
    """Main function to extract Internet Freedom data."""
    print("=" * 60)
    print("Internet Freedom Data Extraction")
    print("=" * 60)

    # Extract Excel data (2019-2024)
    print("\n[1] Extracting from Excel files (2019-2024)...")
    excel_df = extract_all_excel_data()

    if not excel_df.empty:
        print(f"  Extracted {len(excel_df)} records from Excel files")

    # Create template for PDF data (2011-2018, 2025)
    print("\n[2] Creating template for PDF data (2011-2018, 2025)...")
    print("  Note: PDF data needs to be extracted using Gemini API")
    print("  Run 'python run_extraction.py --pdf' to extract PDF data")
    pdf_template = create_pdf_extraction_template()

    # Combine all data
    if not excel_df.empty:
        result_df = pd.concat([excel_df, pdf_template], ignore_index=True)
    else:
        result_df = pdf_template

    # Sort by country and year
    result_df = result_df.sort_values(["country", "year"]).reset_index(drop=True)

    # Save intermediate result
    output_path = DATA_INTERMEDIATE_DIR / "internet_freedom_extracted.csv"
    result_df.to_csv(output_path, index=False)
    print(f"\nSaved Internet Freedom data to: {output_path}")
    print(f"Total records: {len(result_df)}")

    # Show summary
    print("\nData summary (records with values):")
    has_values = result_df[result_df["value"].notna()]
    if not has_values.empty:
        print(has_values.groupby("country")["year"].agg(["min", "max", "count"]))

    print("\nMissing data (needs PDF extraction):")
    missing = result_df[result_df["value"].isna()]
    if not missing.empty:
        print(f"  {len(missing)} records need extraction from PDFs")

    return result_df


if __name__ == "__main__":
    main()
