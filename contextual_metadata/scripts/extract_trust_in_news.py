"""
Trust in News Data Extraction Script
Extracts trust_in_news_overall from Reuters Institute Digital News Reports.

Data source: Reuters Institute for the Study of Journalism
Files: trust_in_news/trustinnews_*.pdf (2012-2025)

This indicator requires Gemini API extraction from PDF files.
The script creates a template and the actual extraction is done via extract_pdf_with_gemini.py
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
    TRUST_IN_NEWS_DIR,
    standardize_country_name,
    INDICATOR_NAMES,
)


def get_available_pdf_years() -> list:
    """
    Get list of years for which PDF files are available.

    Returns:
        List of years with available PDFs.
    """
    pdf_files = list(TRUST_IN_NEWS_DIR.glob("trustinnews_*.pdf"))
    years = []

    for pdf_file in pdf_files:
        try:
            # Extract year from filename (trustinnews_YYYY.pdf)
            year_str = pdf_file.stem.split("_")[1]
            year = int(year_str)
            years.append(year)
        except (IndexError, ValueError):
            continue

    return sorted(years)


def create_pdf_extraction_template() -> pd.DataFrame:
    """
    Create a template for Trust in News data that needs to be extracted via Gemini.

    Returns:
        DataFrame template for all available years.
    """
    available_years = get_available_pdf_years()
    print(f"Available PDF years: {available_years}")

    rows = []
    for year in available_years:
        if YEAR_START <= year <= YEAR_END:
            for country in TARGET_COUNTRIES:
                rows.append(
                    {
                        "country": country,
                        "year": year,
                        "indicator": INDICATOR_NAMES["trust_in_news_overall"],
                        "value": None,  # To be filled by Gemini extraction
                        "source": "Reuters Institute",
                    }
                )

    return pd.DataFrame(rows)


def main():
    """Main function to prepare Trust in News data extraction."""
    print("=" * 60)
    print("Trust in News Data Extraction Preparation")
    print("=" * 60)

    # Check available PDF files
    print("\n[1] Checking available PDF files...")
    available_years = get_available_pdf_years()
    print(f"  Found {len(available_years)} PDF files: {available_years}")

    # Create template
    print("\n[2] Creating extraction template...")
    print("  Note: PDF data needs to be extracted using Gemini API")
    print("  Run 'python scripts/extract_pdf_with_gemini.py' to extract PDF data")

    result_df = create_pdf_extraction_template()

    # Save template
    output_path = DATA_INTERMEDIATE_DIR / "trust_in_news_template.csv"
    result_df.to_csv(output_path, index=False)
    print(f"\nSaved Trust in News template to: {output_path}")
    print(f"Total records to extract: {len(result_df)}")

    # Show summary
    print("\nTemplate summary:")
    print(f"  Countries: {result_df['country'].unique().tolist()}")
    print(f"  Years: {sorted(result_df['year'].unique().tolist())}")

    return result_df


if __name__ == "__main__":
    main()
