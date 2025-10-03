# Questionnaire Database Platform

A web-based platform for searching and comparing research articles with extracted features.

## Features

- **Search**: Search articles by title, abstract, journal, or author name
- **Article Details**: View detailed article information with progressive disclosure of features
- **Comparison**: Compare multiple articles side-by-side with structured feature comparison
- **Real Data**: Uses actual research data from CSV files

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure your data file is in the correct location:
   - Place your CSV file at `data/papers_extracted.csv`

## Running the Application

### Method 1: Using run.py
```bash
python run.py
```

### Method 2: Direct Flask
```bash
python app.py
```

The application will be available at: http://localhost:5000

## Project Structure

```
database_wireframe/
├── app.py                 # Main Flask application
├── run.py                 # Application runner
├── requirements.txt       # Python dependencies
├── data/
│   └── papers_extracted.csv  # Research data
├── templates/             # Jinja2 templates
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── search.html       # Search results
│   ├── article.html      # Article details
│   └── compare.html      # Comparison page
├── static/               # Static files
│   └── css/             # Stylesheets
└── README.md            # This file
```

## API Endpoints

- `GET /` - Home page
- `GET /search` - Search page with results
- `GET /article/<paper_id>` - Article details page
- `GET /compare` - Comparison page
- `GET /api/papers` - Get all papers (JSON)
- `GET /api/search` - Search papers (JSON)
- `GET /api/paper/<paper_id>` - Get specific paper (JSON)
- `GET /api/statistics` - Get platform statistics (JSON)

## Search Functionality

The search function supports:
- **Keyword search** across title, abstract, journal, and author names
- **Filtering** by year, journal, methodology, country, and sample size
- **Sorting** by relevance, year, citations, or sample size

## Data Format

The CSV file should contain research article data with the following key fields:
- `title` - Article title
- `abstract` - Article abstract
- `authors` - Author names (semicolon-separated)
- `journal` - Journal name
- `year` - Publication year
- `sample_size` - Sample size
- `country_region` - Country or region
- Various extracted features with optional `_verbatim` versions

## Development

The application uses Flask with Jinja2 templates for server-side rendering. This ensures:
- All pages are dynamically generated from real data
- Search functionality works reliably
- Easy modification of templates and logic
- Better performance and SEO

## Troubleshooting

1. **Port already in use**: Change the port in `app.py` or `run.py`
2. **CSV not loading**: Check file path and format
3. **Search not working**: Verify CSV data contains expected fields
4. **Templates not found**: Ensure `templates/` directory exists

## License

This project is for academic research purposes.