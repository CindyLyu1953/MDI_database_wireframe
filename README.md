# Questionnaire Database Platform

A centralized questionnaire database platform that collects key information from social media-related experimental research, helping scholars quickly find appropriate measurement methods and avoid redundant work.

## 🚀 Features

### Core Functionality
- **Dynamic Data Loading**: Loads research data from CSV files
- **Keyword Search**: Search across titles, abstracts, journals, and author names
- **Multi-Paper Comparison**: Compare up to 3 research papers side-by-side
- **Progressive Information Disclosure**: 
  - Concise overviews in search results
  - Detailed features in article view
  - Full verbatim text with "View Full" functionality

### User Interface
- **Clean Search Interface**: Simplified search results without unnecessary tags
- **Dynamic Comparison Table**: Features column fixed on left, papers dynamically added on right
- **Full-Width Headers**: Modern layout with headers extending to screen edges
- **Responsive Design**: Works on different screen sizes

## 📁 Project Structure

```
database_wireframe/
├── app.py                    # Main Flask application
├── run.py                    # Application runner script
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── data/
│   └── papers_extracted.csv  # Research data (CSV format)
├── templates/                # Jinja2 HTML templates
│   ├── base.html            # Base template with header/footer
│   ├── index.html           # Home page
│   ├── search.html          # Search results page
│   ├── article.html         # Article detail page
│   └── compare.html         # Comparison page
└── static/
    └── css/                 # Stylesheets
        ├── main.css         # Core styles
        ├── home.css         # Home page styles
        ├── search.css       # Search page styles
        ├── article.css      # Article page styles
        └── compare.css      # Comparison page styles
```

## 📋 File Descriptions

### Backend Files
- **`app.py`**: Main Flask application with routes for all pages and API endpoints
- **`run.py`**: Simple script to start the Flask server
- **`requirements.txt`**: Lists required Python packages (Flask, Werkzeug)

### Data Files
- **`data/papers_extracted.csv`**: Contains extracted research features in CSV format
  - Includes basic information (title, authors, journal, year)
  - Contains extracted features (independent/dependent variables, survey questions, etc.)
  - Features have both condensed and verbatim versions

### Template Files
- **`templates/base.html`**: Base template with common header, navigation, and footer
- **`templates/index.html`**: Home page with search functionality
- **`templates/search.html`**: Search results with filtering options
- **`templates/article.html`**: Detailed article view with all extracted features
- **`templates/compare.html`**: Side-by-side comparison of multiple papers

### Style Files
- **`static/css/main.css`**: Core styles, layout, and components
- **`static/css/home.css`**: Home page specific styles
- **`static/css/search.css`**: Search page specific styles
- **`static/css/article.css`**: Article page specific styles
- **`static/css/compare.css`**: Comparison page specific styles

## 🎯 How to Use

### 1. Search for Research
- **Home Page**: Enter keywords in the search box
- **Search Results**: Browse filtered results, click "Compare" to add papers
- **Keywords**: Search works across titles, abstracts, journals, and author names

### 2. View Article Details
- **Click "View Details"**: See condensed version of all extracted features
- **"View Full" Button**: Expand to see complete verbatim text (when available)
- **Add to Compare**: Use the button to add papers to comparison list

### 3. Compare Papers
- **Add Papers**: Click "Compare" buttons in search results (max 3 papers)
- **Comparison Table**: Features listed vertically on left, papers on right
- **Dynamic Columns**: Table adjusts based on number of papers selected

### 4. Navigation
- **Header Navigation**: Use Home, Search, Compare links
- **Breadcrumb**: Clear navigation between different views
- **Responsive**: Works on desktop and mobile devices

## 🛠️ Local Setup and Running

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation Steps

1. **Clone or Download** the project to your local machine

2. **Navigate** to the project directory:
   ```bash
   cd database_wireframe
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:
   ```bash
   python run.py
   ```

5. **Access the Website**:
   - Open your web browser
   - Go to: `http://localhost:5001`
   - The application will be running locally

### Alternative Running Method
You can also run the application directly:
```bash
python app.py
```

### Stopping the Application
- Press `Ctrl+C` in the terminal to stop the server

## 📊 Data Format

The application expects research data in CSV format (`data/papers_extracted.csv`) with the following structure:

### Required Columns
- `title`: Paper title
- `authors`: Author names (semicolon-separated)
- `journal`: Journal name
- `year`: Publication year
- `abstract`: Paper abstract
- `sample_size`: Sample size (numeric)

### Extracted Features
Each feature should have both condensed and verbatim versions:
- `independent_variables` / `independent_variables_verbatim`
- `dependent_variables` / `dependent_variables_verbatim`
- `survey_questions` / `survey_questions_verbatim`
- `incentive` / `incentive_verbatim`
- `study_type` / `study_type_verbatim`
- `analysis_equations` / `analysis_equations_verbatim`
- `level_of_analysis` / `level_of_analysis_verbatim`
- `main_effects` / `main_effects_verbatim`
- `statistical_power` / `statistical_power_verbatim`
- `moderators` / `moderators_verbatim`
- `moderation_results` / `moderation_results_verbatim`
- `demographics` / `demographics_verbatim`
- `recruitment_source` / `recruitment_source_verbatim`
- `country_region`: Country or region
- `sociocultural_context`: Sociocultural context
- `political_context`: Political context
- `platform_technological_context`: Platform/technological context
- `temporal_context`: Temporal context
- `recommended_moderators`: Recommended moderators
- `research_context`: Research context
- `intervention_insights`: Intervention insights

## 🔧 Technical Details

### Architecture
- **Backend**: Flask (Python web framework)
- **Frontend**: HTML5, CSS3, JavaScript
- **Templates**: Jinja2 templating engine
- **Data**: CSV file-based storage
- **Styling**: Custom CSS with responsive design

### Key Features
- **Dynamic Column Count**: CSS variables adjust comparison table based on paper count
- **Progressive Disclosure**: Three levels of information detail
- **Local Storage**: Browser storage for comparison lists
- **Responsive Grid**: CSS Grid layout for comparison tables
- **Search Functionality**: Cross-field keyword matching

## 📝 Notes

- The application is designed for academic research purposes
- All extracted features are displayed only if they contain data (not empty or "NOT SPECIFIED")
- The comparison feature supports up to 3 papers simultaneously
- The interface is optimized for desktop use but responsive for mobile
- All text and interface elements are in English

## 🤝 Contributing

To add new research papers:
1. Update the `data/papers_extracted.csv` file with new data
2. Ensure the CSV follows the required format
3. Restart the application to load new data

For feature extraction integration:
- The current system expects pre-extracted features in CSV format
- Future integration with automated extraction tools can be added to the Flask backend