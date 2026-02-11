#!/usr/bin/env python3
"""
Main Extraction Pipeline Script
Orchestrates the extraction of all contextual metadata indicators.

Usage:
    python run_extraction.py [--all] [--vdem] [--wgi] [--worldbank] [--internet-freedom] [--trust] [--periods] [--consolidate] [--pdf]

Options:
    --all           Run all extraction steps (default if no options specified)
    --vdem          Extract V-Dem data
    --wgi           Extract WGI data
    --worldbank     Extract World Bank data
    --internet-freedom  Extract Internet Freedom data (Excel only, use --pdf for PDFs)
    --trust         Prepare Trust in News template
    --periods       Generate election and COVID period data
    --consolidate   Consolidate all data into final output
    --pdf           Extract PDF data using Gemini API (requires GEMINI_API_KEY)
"""

import argparse
import sys
import os
from pathlib import Path

# Add scripts directory to path
PROJECT_DIR = Path(__file__).parent
SCRIPTS_DIR = PROJECT_DIR / "scripts"
sys.path.insert(0, str(PROJECT_DIR))
sys.path.insert(0, str(SCRIPTS_DIR))


def run_vdem():
    """Run V-Dem extraction using R script."""
    print("\n" + "=" * 70)
    print("STEP 1: V-Dem Data Extraction (R)")
    print("=" * 70)
    import subprocess

    r_script = SCRIPTS_DIR / "extract_vdem.R"
    try:
        result = subprocess.run(
            ["Rscript", str(r_script)],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_DIR),
        )
        print(result.stdout)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
    except FileNotFoundError:
        print("Error: Rscript not found. Please install R and the vdemdata package.")
        print("Run in R: devtools::install_github('vdeminstitute/vdemdata')")


def run_wgi():
    """Run WGI extraction."""
    print("\n" + "=" * 70)
    print("STEP 2: WGI Data Extraction")
    print("=" * 70)
    from scripts.extract_wgi import main as wgi_main

    wgi_main()


def run_worldbank():
    """Run World Bank extraction."""
    print("\n" + "=" * 70)
    print("STEP 3: World Bank Data Extraction")
    print("=" * 70)
    from scripts.extract_worldbank import main as worldbank_main

    worldbank_main()


def run_internet_freedom():
    """Run Internet Freedom extraction (Excel files only)."""
    print("\n" + "=" * 70)
    print("STEP 4: Internet Freedom Data Extraction (Excel)")
    print("=" * 70)
    from scripts.extract_internet_freedom import main as if_main

    if_main()


def run_trust():
    """Prepare Trust in News extraction template."""
    print("\n" + "=" * 70)
    print("STEP 5: Trust in News Data Preparation")
    print("=" * 70)
    from scripts.extract_trust_in_news import main as trust_main

    trust_main()


def run_periods():
    """Generate election and COVID period data."""
    print("\n" + "=" * 70)
    print("STEP 6: Election & COVID Period Generation")
    print("=" * 70)
    from scripts.generate_periods import main as periods_main

    periods_main()


def run_pdf_extraction(indicator=None):
    """Run PDF extraction using Gemini API.
    
    Args:
        indicator: Optional indicator to extract ('internet-freedom', 'trust-in-news', or None for both)
    """
    print("\n" + "=" * 70)
    print("STEP 7: PDF Data Extraction with Gemini")
    print("=" * 70)
    import subprocess
    
    cmd = [sys.executable, str(SCRIPTS_DIR / "extract_pdf_with_gemini.py")]
    if indicator:
        cmd.extend(["--indicator", indicator])
    
    result = subprocess.run(cmd, cwd=str(PROJECT_DIR))
    if result.returncode != 0:
        print(f"Error: PDF extraction failed with exit code {result.returncode}")


def run_consolidation():
    """Consolidate all data."""
    print("\n" + "=" * 70)
    print("FINAL: Data Consolidation")
    print("=" * 70)
    from scripts.consolidate_data import main as consolidate_main

    consolidate_main()


def main():
    parser = argparse.ArgumentParser(
        description="Contextual Metadata Extraction Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--all", action="store_true", help="Run all extraction steps")
    parser.add_argument("--vdem", action="store_true", help="Extract V-Dem data")
    parser.add_argument("--wgi", action="store_true", help="Extract WGI data")
    parser.add_argument(
        "--worldbank", action="store_true", help="Extract World Bank data"
    )
    parser.add_argument(
        "--internet-freedom",
        action="store_true",
        help="Extract Internet Freedom data (Excel only)",
    )
    parser.add_argument(
        "--trust", action="store_true", help="Prepare Trust in News template"
    )
    parser.add_argument(
        "--periods", action="store_true", help="Generate election and COVID period data"
    )
    parser.add_argument(
        "--pdf", action="store_true", help="Extract PDF data using Gemini API (both indicators)"
    )
    parser.add_argument(
        "--pdf-internet-freedom",
        action="store_true",
        help="Extract only Internet Freedom data from PDFs using Gemini API"
    )
    parser.add_argument(
        "--pdf-trust",
        action="store_true",
        help="Extract only Trust in News data from PDFs using Gemini API"
    )
    parser.add_argument(
        "--consolidate",
        action="store_true",
        help="Consolidate all data into final output",
    )

    args = parser.parse_args()

    # If no options specified, show help or run basic extractions
    no_options = not any(
        [
            args.all,
            args.vdem,
            args.wgi,
            args.worldbank,
            args.internet_freedom,
            args.trust,
            args.periods,
            args.pdf,
            args.pdf_internet_freedom,
            args.pdf_trust,
            args.consolidate,
        ]
    )

    if no_options:
        # Default: run all except PDF extraction (which requires API key)
        args.all = True
        print("\nNo options specified. Running all basic extractions...")
        print("(Use --pdf to also run PDF extraction with Gemini API)")

    print("\n" + "=" * 70)
    print("CONTEXTUAL METADATA EXTRACTION PIPELINE")
    print("=" * 70)
    print(f"\nTarget countries: Denmark, US, UK, Bosnia-Herzegovina, Cyprus")
    print(f"Time range: 2010-2025")
    print("\nIndicators to extract:")
    print("  - Liberal Democracy (V-Dem)")
    print("  - Polarization (V-Dem)")
    print("  - Governance Quality (WGI)")
    print("  - Internet Freedom (Freedom House)")
    print("  - Internet Penetration (World Bank)")
    print("  - Trust in News (Reuters Institute)")
    print("  - Election Period (Manual)")
    print("  - Covid Period (Manual)")

    # Run selected steps
    if args.all or args.vdem:
        run_vdem()

    if args.all or args.wgi:
        run_wgi()

    if args.all or args.worldbank:
        run_worldbank()

    if args.all or args.internet_freedom:
        run_internet_freedom()

    if args.all or args.trust:
        run_trust()

    if args.all or args.periods:
        run_periods()

    if args.pdf:
        run_pdf_extraction(indicator="both")
    elif args.pdf_internet_freedom:
        run_pdf_extraction(indicator="internet-freedom")
    elif args.pdf_trust:
        run_pdf_extraction(indicator="trust-in-news")

    if args.all or args.consolidate:
        run_consolidation()

    print("\n" + "=" * 70)
    print("EXTRACTION PIPELINE COMPLETE")
    print("=" * 70)
    print("\nOutput files:")
    print("  - data_intermediate/  : Individual source extractions")
    print("  - output/contextual_metadata_long.csv  : Final data (long format)")
    print("  - output/contextual_metadata_wide.csv  : Final data (wide format)")
    print("  - output/data_summary.txt  : Data summary report")

    if not args.pdf and args.all:
        print("\n" + "-" * 70)
        print("NOTE: PDF extraction was skipped (requires Gemini API key)")
        print("To extract data from PDFs, run:")
        print("  export GEMINI_API_KEY='your-api-key'")
        print("  python run_extraction.py --pdf")
        print("-" * 70)


if __name__ == "__main__":
    main()
