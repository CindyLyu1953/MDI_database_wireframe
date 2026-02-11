# Contextual Metadata Extraction Pipeline

This pipeline extracts contextual metadata indicators from multiple data sources and consolidates them into a unified CSV format.

## Target Countries
- Denmark
- United States
- United Kingdom
- Bosnia and Herzegovina
- Cyprus

## Time Range
2010-2025

## Indicators

| Indicator | Name | Source | File |
|-----------|------|--------|------|
| v2x_libdem | Liberal Democracy | V-Dem | vdem/*.csv |
| v2x_delibdem | Polarization | V-Dem | vdem/*.csv |
| wgi_pv | Governance Quality | WGI | wgi/wgidataset.xlsx |
| internet_freedom_score | Internet Freedom | Freedom House | internet_freedom/*.xlsx, *.pdf |
| internet_penetration | Internet Penetration | World Bank | worldbank/internetpenetration.csv |
| trust_in_news_overall | Trust in News | Reuters Institute | trust_in_news/*.pdf |
| election_period | Election Period | Manual | Generated |
| covid_period | Covid Period | Manual | Generated (2019-2023) |

## Output Format

### Long Format (`output/contextual_metadata_long.csv`)
```csv
country,year,indicator,value,source
Denmark,2010,Liberal Democracy,0.85,V-Dem
Denmark,2010,Internet Penetration,88.72,World Bank
...
```

### Wide Format (`output/contextual_metadata_wide.csv`)
```csv
country,year,Liberal Democracy,Polarization,Governance Quality,...
Denmark,2010,0.85,0.72,95.2,...
```

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Quick Start - Run All Extractions

```bash
# Run all basic extractions (excludes PDF extraction)
python run_extraction.py

# Or run all including PDF extraction (requires Gemini API key)
export GEMINI_API_KEY='your-api-key'
python run_extraction.py --all --pdf
```

### Run Individual Steps

```bash
# Extract V-Dem data
python run_extraction.py --vdem

# Extract WGI data
python run_extraction.py --wgi

# Extract World Bank data
python run_extraction.py --worldbank

# Extract Internet Freedom data (Excel files only)
python run_extraction.py --internet-freedom

# Prepare Trust in News template
python run_extraction.py --trust

# Generate election and COVID period data
python run_extraction.py --periods

# Extract PDF data with Gemini (requires API key)
python run_extraction.py --pdf

# Extract ONLY Internet Freedom PDFs (to manage API quota)
python run_extraction.py --pdf-internet-freedom

# Extract ONLY Trust in News PDFs (to manage API quota)
python run_extraction.py --pdf-trust

# Consolidate all data into final output
python run_extraction.py --consolidate
```

### Run Individual Scripts Directly

```bash
python extract_vdem.py
python extract_wgi.py
python extract_worldbank.py
python extract_internet_freedom.py
python extract_trust_in_news.py
python generate_periods.py
python extract_pdf_with_gemini.py
python consolidate_data.py
```

## PDF Extraction with Gemini API

The Internet Freedom reports (2011-2018, 2025) and Trust in News reports (2012-2025) require extraction from PDF files using Google's Gemini API.

### Setup Gemini API

1. Get an API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Set the environment variable:
   ```bash
   export GEMINI_API_KEY='your-api-key'
   ```
   Or create a `.env` file:
   ```
   GEMINI_API_KEY=your-api-key
   ```

3. Run PDF extraction:
   ```bash
   # Extract both Internet Freedom and Trust in News
   python run_extraction.py --pdf
   
   # Or extract specific indicators (to manage API quota)
   python run_extraction.py --pdf-internet-freedom  # Only Internet Freedom PDFs
   python run_extraction.py --pdf-trust              # Only Trust in News PDFs
   
   # Or run the script directly with options
   python scripts/extract_pdf_with_gemini.py --indicator internet-freedom
   python scripts/extract_pdf_with_gemini.py --indicator trust-in-news
   ```

### API Quota Management

The free tier of Gemini API has a limit of 20 requests per day. If you hit the quota limit, you can:
- Wait until the quota resets (typically 24 hours)
- Extract one indicator at a time using `--pdf-internet-freedom` or `--pdf-trust`
- Upgrade to a paid plan for higher quotas

## Data Sources

### V-Dem (Varieties of Democracy)
- Website: https://www.v-dem.net/
- Uses the `vdemdata` R package for extraction
- Run `Rscript scripts/extract_vdem.R` to extract data (requires R with vdemdata package)
- Or use the existing `vdem/vdem.ipynb` notebook in R
- Indicators: v2x_libdem (Liberal Democracy Index), v2x_delibdem (Deliberative Democracy)

### WGI (World Governance Indicators)
- Website: https://www.worldbank.org/en/publication/worldwide-governance-indicators
- File: `wgi/wgidataset.xlsx`
- Indicator: Political Stability and Absence of Violence

### World Bank
- Website: https://data.worldbank.org/indicator/IT.NET.USER.ZS
- File: `worldbank/internetpenetration.csv`
- Indicator: Individuals using the Internet (% of population)

### Freedom House - Freedom on the Net
- Website: https://freedomhouse.org/report/freedom-net
- Files: `internet_freedom/internetfreedom_*.xlsx` (2019-2024), `internetfreedom_*.pdf` (2011-2018, 2025)
- Indicator: Internet Freedom Score (0-100)

### Reuters Institute - Digital News Report
- Website: https://reutersinstitute.politics.ox.ac.uk/digital-news-report
- Files: `trust_in_news/trustinnews_*.pdf`
- Indicator: Trust in News Overall (%)

## Directory Structure

```
contextual_metadata/
├── config.py                    # Configuration and constants
├── requirements.txt             # Python dependencies
├── run_extraction.py            # Main pipeline script
├── consolidate_data.py          # Data consolidation
├── README.md                    # This file
│
├── scripts/                     # Extraction scripts
│   ├── extract_vdem.py          # V-Dem extraction (Python)
│   ├── extract_vdem.R           # V-Dem extraction (R)
│   ├── extract_wgi.py           # WGI extraction
│   ├── extract_worldbank.py     # World Bank extraction
│   ├── extract_internet_freedom.py  # Internet Freedom extraction
│   ├── extract_trust_in_news.py     # Trust in News preparation
│   ├── extract_pdf_with_gemini.py   # PDF extraction with Gemini
│   └── generate_periods.py          # Election/COVID period generation
│
├── vdem/                        # V-Dem data
│   └── vdem.ipynb               # V-Dem notebook (uses vdemdata R package)
│
├── wgi/                         # World Governance Indicators
│   └── wgidataset.xlsx
│
├── worldbank/                   # World Bank data
│   └── internetpenetration.csv
│
├── internet_freedom/            # Freedom House data
│   ├── internetfreedom_2011.pdf
│   ├── ...
│   └── internetfreedom_2024.xlsx
│
├── trust_in_news/               # Reuters Institute data
│   ├── trustinnews_2012.pdf
│   ├── ...
│   └── trustinnews_2025.pdf
│
├── data_intermediate/           # Intermediate extraction results
│   ├── vdem_raw.csv             # Raw V-Dem data (from R script)
│   ├── vdem_extracted.csv       # Transformed V-Dem data
│   ├── wgi_extracted.csv
│   ├── worldbank_extracted.csv
│   ├── internet_freedom_extracted.csv
│   ├── trust_in_news_extracted.csv
│   └── periods_generated.csv
│
└── output/                      # Final consolidated output
    ├── contextual_metadata_long.csv
    ├── contextual_metadata_wide.csv
    └── data_summary.txt
```

## Election Years (Reference)

| Country | Election Years |
|---------|---------------|
| Denmark | 2011, 2015, 2019, 2022 |
| United States | 2010, 2012, 2014, 2016, 2018, 2020, 2022, 2024 |
| United Kingdom | 2010, 2015, 2017, 2019, 2024 |
| Bosnia and Herzegovina | 2010, 2014, 2018, 2022 |
| Cyprus | 2011, 2013, 2016, 2018, 2021, 2023 |

## COVID Period
Defined as 2019-2023 (inclusive).

## Notes

1. **V-Dem Data**: The V-Dem dataset is large (~2GB). You need to download it manually from the V-Dem website and place it in the `vdem/` directory.

2. **Missing Data**: Some indicators may not have data for all years. The pipeline preserves gaps rather than interpolating.

3. **Country Names**: The pipeline standardizes country names to a canonical form. Various spellings (e.g., "USA", "United States", "US") are mapped to "United States".

4. **PDF Extraction**: Gemini API extraction may not be 100% accurate. Review the extracted data and correct any errors manually if needed.

