"""
PDF Data Extraction Script using Google Gemini API
Extracts:
1. Internet Freedom scores from PDF files (2011-2018, 2025)
2. Trust in News data from PDF files (2012-2025)

Requires:
- Google Gemini API key (set as GEMINI_API_KEY environment variable or in .env file)
- PDF files in respective directories

Usage:
    python scripts/extract_pdf_with_gemini.py [--indicator <internet-freedom|trust-in-news>]

    Options:
        --indicator  Extract only the specified indicator (internet-freedom or trust-in-news)
                     If not specified, extracts both

Set your API key:
    export GEMINI_API_KEY="your-api-key-here"
    or create a .env file with: GEMINI_API_KEY=your-api-key-here
"""

import os
import sys
import json
import time
import pandas as pd
from pathlib import Path
from typing import Optional

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
    TRUST_IN_NEWS_DIR,
    standardize_country_name,
    INDICATOR_NAMES,
)

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv(PROJECT_DIR / ".env")
except ImportError:
    pass

# Gemini API setup
try:
    import google.generativeai as genai

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai package not installed.")
    print("Install with: pip install google-generativeai")


def setup_gemini():
    """Configure Gemini API with API key."""
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment variables.")
        print("Please set it using:")
        print("  export GEMINI_API_KEY='your-api-key'")
        print("Or create a .env file with: GEMINI_API_KEY=your-api-key")
        return False

    genai.configure(api_key=api_key)
    return True


def upload_pdf_to_gemini(pdf_path: Path) -> Optional[object]:
    """
    Upload a PDF file to Gemini for processing.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Uploaded file object or None if failed
    """
    try:
        print(f"  Uploading: {pdf_path.name}...")
        file = genai.upload_file(pdf_path, mime_type="application/pdf")

        # Wait for file to be processed
        while file.state.name == "PROCESSING":
            time.sleep(2)
            file = genai.get_file(file.name)

        if file.state.name == "FAILED":
            print(f"  Error: File processing failed for {pdf_path.name}")
            return None

        return file
    except Exception as e:
        print(f"  Error uploading {pdf_path.name}: {e}")
        return None


def extract_internet_freedom_from_pdf(year: int) -> pd.DataFrame:
    """
    Extract Internet Freedom scores from PDF using Gemini.

    The PDF contains a page titled "Key Internet Controls by Country"
    with FOTN Score (Freedom on the Net Score).
    Our score = 100 - FOTN Score (higher = more free)

    Args:
        year: Year of the PDF (2011-2018, 2025)

    Returns:
        DataFrame with extracted data
    """
    pdf_path = INTERNET_FREEDOM_DIR / f"internetfreedom_{year}.pdf"

    if not pdf_path.exists():
        print(f"  PDF not found: {pdf_path}")
        return pd.DataFrame()

    # Upload PDF
    uploaded_file = upload_pdf_to_gemini(pdf_path)
    if not uploaded_file:
        return pd.DataFrame()

    # Create prompt for extraction
    countries_str = ", ".join(TARGET_COUNTRIES)

    prompt = f"""
    Please analyze this Freedom House "Freedom on the Net" report PDF and extract the Internet Freedom scores.

    I need the FOTN (Freedom on the Net) scores for these specific countries:
    {countries_str}

    Look for a page or section titled "Key Internet Controls by Country" or similar.
    The FOTN Score is usually on a scale of 0-100.

    IMPORTANT: 
    - If a country is not covered in this report, indicate "Not covered"
    - Return the raw FOTN score (do not convert)
    - Be precise with the country names

    Please return the data in this exact JSON format:
    {{
        "year": {year},
        "data": [
            {{"country": "country_name", "fotn_score": score_or_null, "covered": true_or_false}},
            ...
        ]
    }}

    If you cannot find the data, return:
    {{
        "year": {year},
        "data": [],
        "error": "Description of what happened"
    }}
    """

    try:
        # Use Gemini model
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content([uploaded_file, prompt])

        # Parse response
        response_text = response.text

        # Extract JSON from response
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            result = json.loads(json_str)
        else:
            print(f"  Warning: Could not parse JSON from response for year {year}")
            print(f"  Response: {response_text[:500]}...")
            return pd.DataFrame()

        # Process results
        result_rows = []
        for item in result.get("data", []):
            country_name = item.get("country")
            fotn_score = item.get("fotn_score")
            covered = item.get("covered", True)

            if not covered or fotn_score is None:
                continue

            # Standardize country name
            std_country = standardize_country_name(country_name)
            if std_country is None:
                continue

            # Convert FOTN score to Internet Freedom score (100 - FOTN)
            # Note: Freedom House changed their scoring over the years
            # In earlier reports, higher FOTN = less free, so we invert
            internet_freedom_score = 100 - float(fotn_score)

            result_rows.append(
                {
                    "country": std_country,
                    "year": year,
                    "indicator": INDICATOR_NAMES["internet_freedom_score"],
                    "value": internet_freedom_score,
                    "source": "Freedom House",
                }
            )

        # Clean up uploaded file
        try:
            genai.delete_file(uploaded_file.name)
        except:
            pass

        return pd.DataFrame(result_rows)

    except Exception as e:
        print(f"  Error extracting from PDF {year}: {e}")
        return pd.DataFrame()


def extract_trust_in_news_from_pdf(year: int) -> pd.DataFrame:
    """
    Extract Trust in News data from Reuters Institute PDF using Gemini.

    The PDF contains survey data about trust in news.
    We need to find "Trust in News Overall %" for each country.

    Args:
        year: Year of the PDF (2012-2025)

    Returns:
        DataFrame with extracted data
    """
    pdf_path = TRUST_IN_NEWS_DIR / f"trustinnews_{year}.pdf"

    if not pdf_path.exists():
        print(f"  PDF not found: {pdf_path}")
        return pd.DataFrame()

    # Upload PDF
    uploaded_file = upload_pdf_to_gemini(pdf_path)
    if not uploaded_file:
        return pd.DataFrame()

    # Create prompt for extraction
    countries_str = ", ".join(TARGET_COUNTRIES)

    prompt = f"""
    Please analyze this Reuters Institute Digital News Report PDF and extract Trust in News data.

    I need the "Trust in News Overall" percentage for these specific countries:
    {countries_str}

    The trust percentage is usually found in:
    - Tables showing country-level trust metrics
    - Sections about "Trust in News"
    - Charts comparing trust levels across countries
    - The percentage typically shows how many people trust most news most of the time

    IMPORTANT:
    - If a country is not covered in this report, indicate "Not covered"
    - Return the percentage value (0-100)
    - Be precise with the country names
    - Look for "overall trust" or "trust in news" specifically

    Please return the data in this exact JSON format:
    {{
        "year": {year},
        "data": [
            {{"country": "country_name", "trust_percentage": percentage_or_null, "covered": true_or_false}},
            ...
        ]
    }}

    If you cannot find the data, return:
    {{
        "year": {year},
        "data": [],
        "error": "Description of what happened"
    }}
    """

    try:
        # Use Gemini model
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content([uploaded_file, prompt])

        # Parse response
        response_text = response.text

        # Extract JSON from response
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            result = json.loads(json_str)
        else:
            print(f"  Warning: Could not parse JSON from response for year {year}")
            print(f"  Response: {response_text[:500]}...")
            return pd.DataFrame()

        # Process results
        result_rows = []
        for item in result.get("data", []):
            country_name = item.get("country")
            trust_pct = item.get("trust_percentage")
            covered = item.get("covered", True)

            if not covered or trust_pct is None:
                continue

            # Standardize country name
            std_country = standardize_country_name(country_name)
            if std_country is None:
                continue

            result_rows.append(
                {
                    "country": std_country,
                    "year": year,
                    "indicator": INDICATOR_NAMES["trust_in_news_overall"],
                    "value": float(trust_pct),
                    "source": "Reuters Institute",
                }
            )

        # Clean up uploaded file
        try:
            genai.delete_file(uploaded_file.name)
        except:
            pass

        return pd.DataFrame(result_rows)

    except Exception as e:
        print(f"  Error extracting from PDF {year}: {e}")
        return pd.DataFrame()


def extract_all_internet_freedom_pdfs() -> pd.DataFrame:
    """Extract Internet Freedom data from all PDF files (2011-2018, 2025)."""
    all_data = []

    # Extract 2011-2018
    for year in range(2011, 2019):
        print(f"\nProcessing Internet Freedom {year}...")
        df = extract_internet_freedom_from_pdf(year)
        if not df.empty:
            all_data.append(df)
            print(f"  Extracted {len(df)} records")
        else:
            print(f"  No data extracted")

        # Rate limiting
        time.sleep(2)

    # Extract 2025 if in range
    if 2025 >= YEAR_START and 2025 <= YEAR_END:
        print(f"\nProcessing Internet Freedom 2025...")
        df = extract_internet_freedom_from_pdf(2025)
        if not df.empty:
            all_data.append(df)
            print(f"  Extracted {len(df)} records")
        else:
            print(f"  No data extracted")

        # Rate limiting
        time.sleep(2)

    if all_data:
        return pd.concat(all_data, ignore_index=True)
    return pd.DataFrame()


def extract_all_trust_in_news_pdfs() -> pd.DataFrame:
    """Extract Trust in News data from all PDF files."""
    all_data = []

    # Get available years
    pdf_files = list(TRUST_IN_NEWS_DIR.glob("trustinnews_*.pdf"))
    years = []
    for pdf_file in pdf_files:
        try:
            year_str = pdf_file.stem.split("_")[1]
            year = int(year_str)
            if YEAR_START <= year <= YEAR_END:
                years.append(year)
        except (IndexError, ValueError):
            continue

    years = sorted(years)
    print(f"Found Trust in News PDFs for years: {years}")

    for year in years:
        print(f"\nProcessing Trust in News {year}...")
        df = extract_trust_in_news_from_pdf(year)
        if not df.empty:
            all_data.append(df)
            print(f"  Extracted {len(df)} records")
        else:
            print(f"  No data extracted")

        # Rate limiting
        time.sleep(2)

    if all_data:
        return pd.concat(all_data, ignore_index=True)
    return pd.DataFrame()


def main():
    """Main function to extract PDF data using Gemini."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract data from PDFs using Gemini API"
    )
    parser.add_argument(
        "--indicator",
        choices=["internet-freedom", "trust-in-news", "both"],
        default="both",
        help="Which indicator to extract (default: both)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("PDF Data Extraction with Gemini API")
    print("=" * 60)

    if not GEMINI_AVAILABLE:
        print("\nError: google-generativeai package not available.")
        print("Install with: pip install google-generativeai")
        return

    # Setup Gemini
    if not setup_gemini():
        return

    print("\nGemini API configured successfully.")

    extract_internet_freedom = args.indicator in ["internet-freedom", "both"]
    extract_trust = args.indicator in ["trust-in-news", "both"]

    # Extract Internet Freedom PDFs
    if extract_internet_freedom:
        print("\n" + "=" * 60)
        print("[1] Extracting Internet Freedom data from PDFs (2011-2018, 2025)")
        print("=" * 60)

        internet_freedom_df = extract_all_internet_freedom_pdfs()

        if not internet_freedom_df.empty:
            # Load existing Excel data and merge
            existing_path = DATA_INTERMEDIATE_DIR / "internet_freedom_extracted.csv"
            if existing_path.exists():
                existing_df = pd.read_csv(existing_path)
                # Keep only rows with values (Excel data should have values)
                existing_with_values = existing_df[existing_df["value"].notna()]
                # Combine with PDF data
                combined_df = pd.concat(
                    [existing_with_values, internet_freedom_df], ignore_index=True
                )
                combined_df = combined_df.sort_values(["country", "year"]).reset_index(
                    drop=True
                )
            else:
                combined_df = internet_freedom_df

            # Save
            output_path = DATA_INTERMEDIATE_DIR / "internet_freedom_extracted.csv"
            combined_df.to_csv(output_path, index=False)
            print(f"\nSaved Internet Freedom data to: {output_path}")
            print(f"Total records: {len(combined_df)}")

    # Extract Trust in News PDFs
    if extract_trust:
        print("\n" + "=" * 60)
        print("[2] Extracting Trust in News data from PDFs")
        print("=" * 60)

        trust_df = extract_all_trust_in_news_pdfs()

        if not trust_df.empty:
            output_path = DATA_INTERMEDIATE_DIR / "trust_in_news_extracted.csv"
            trust_df.to_csv(output_path, index=False)
            print(f"\nSaved Trust in News data to: {output_path}")
            print(f"Total records: {len(trust_df)}")

    print("\n" + "=" * 60)
    print("PDF extraction complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
