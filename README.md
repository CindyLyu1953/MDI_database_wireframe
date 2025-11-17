# Social Media Effects Research Database Platform

A structured database of social media effects studies enabling systematic comparison of methods, measures, and study contexts.

## Features

### Search & Discovery
- **Keyword Search**: Search across titles, abstracts, journals, and author names
- **Advanced Filters**: Filter by year range, journal, country/region
- **Comprehensive Results**: View all relevant social media effects studies in one place

### Compare Studies
- **Side-by-Side Comparison**: Compare up to 5 research papers simultaneously
- **Organized Features**: Compare bibliographic information, research design, measurement & analysis, findings, and context
- **Download Results**: Export comparisons as CSV files
- **Save Comparisons**: Save comparison results for future reference

### Progressive Information Disclosure
- **Search Results**: View concise overviews with key information
- **Article Details**: See condensed versions of all extracted features
- **View Full Text**: Expand condensed content when it exceeds the preview length.
- **View Verbatim Text**: Read the original verbatim excerpt when provided.

### Personal Management
- **User Profile**: Set your username and institution
- **Favorites**: Mark articles as favorites for quick access
- **Saved Comparisons**: Keep track of your saved comparison results

### Contribute Research
- **Upload Papers**: Request to add new papers to the database
- **Provide Feedback**: Report issues with existing papers in the database

## How to Use

### Getting Started
- **Visit the Platform**: Access the database at `http://localhost:5001`

### Searching for Studies
- **Enter Keywords**: Type any relevant terms (topic, author, journal, etc.)
- **Apply Filters**: Use year range, journal, or country/region filters to narrow results
- **Review Results**: Browse the concise overview of each study

### Viewing Article Details
- **Click "View Details"**: Opens the detailed article page
- **Review Features**: See condensed versions of all extracted features
- **View Full Text**: Expand condensed content when it exceeds the preview length.
- **View Verbatim Text**: Expand to read the verbatim version when available.
- **Add to Favorites**: Mark articles as favorites for quick access
- **Compare Papers**: Add papers to your comparison list

### Comparing Multiple Studies
- **Select Papers**: Click "Compare" on up to 3 papers from search results
- **View Comparison**: See side-by-side comparison table
- **View Full Text**: Open truncated content when a preview is shortened.
- **View Verbatim Text**: Access the original verbatim excerpt when available.
- **Save Comparison**: Save comparison results for future reference
- **Download**: Export comparison as a CSV file

### Managing Your Profile
- **Access Profile**: Click "Profile" in the navigation menu
- **Edit Information**: Update your username and institution
- **View Favorites**: See all your favorited articles
- **Manage Saved Comparisons**: View and reload previously saved comparisons
- **Track Requests**: Monitor the status of your paper upload requests
- **View Statistics**: See your activity statistics including searches, comparisons, and article views

### Submitting New Papers
1. **Navigate to Profile**: Go to Profile - Upload Papers
2. **Fill Out Form**: Provide request name, institution, email, and paper information
3. **Upload PDF** (optional): Upload the PDF file if you have permission to share it
4. **Describe Issues** (optional): Report any issues with existing papers
5. **Submit**: Submit your request for admin review
6. **Track Status**: Check "My Requests" to see the approval status

## Data Format

The platform displays research data with the following structure:

### Basic Information
- Title
- Authors
- Journal
- Year
- Citation
- Abstract

### Research Design & Sample
- Sample size
- Country/Region
- Recruitment source
- Demographics
- Incentive

### Measurement & Analysis
- Treatment/Independent variable(s)
- Survey measures for treatment variables
- Outcome/Dependent variable(s)
- Survey measures for outcome variables
- Analysis (estimating equation)

### Findings
- Main effects
- Moderators
- Moderation results

### Context Information
- Socio-cultural context
- Political context
- Platform/Technological context
- Temporal context

## Notes

- **Data Storage**: User data (profile, favorites, saved comparisons) is stored in your browser
- **Upload Requests**: All upload requests require admin approval
- **Responsive Design**: Works on both desktop and mobile devices
- **Maximum Comparison**: You can compare up to 3 papers simultaneously

## How the Platform Was Set Up and Created

### Technology Stack

The platform is built using:
- **Backend**: Flask (Python web framework) for server-side logic and API endpoints
- **Frontend**: HTML5, CSS3, and JavaScript for user interface and interactions
- **Templates**: Jinja2 templating engine for dynamic page rendering
- **Database**: SQLite for tracking user activity and managing upload requests
- **Data Storage**: CSV file-based storage for research paper data

### Project Structure

The platform is organized into the following key components:

- **`app.py`**: Main Flask application handling all routes, search functionality, and data management
- **`templates/`**: HTML templates for all pages (home, search, article details, comparison, profile, admin)
- **`static/css/`**: Stylesheets for each page component
- **`data/input/`**: CSV file containing extracted research features (`paper_extracted.csv` or `papers_extracted.csv`)
- **`data/output/`**: SQLite database for usage tracking and analytics
- **`data/user_uploads/`**: Directory for storing user-submitted PDF files
- **`database/init_db.py`**: Database initialization script

### Setup Process

1. **Installation**: The platform requires Python 3.7+ and dependencies listed in `requirements.txt` (Flask, Werkzeug, pytz)

2. **Database Initialization**: The SQLite tracking database is initialized using `database/init_db.py`, which creates tables for search logs, comparison views, downloads, and upload requests

3. **Data Loading**: Research paper data is loaded from CSV files in `data/input/` directory at application startup. The system automatically detects files named `paper_extracted.csv`, `papers_extracted.csv`, or `papers.csv`

4. **Running the Application**: The platform runs locally using `python app.py` on port 5001, with debug mode enabled for development

### Key Design Principles

- **Progressive Information Disclosure**: Information is presented in three levels - concise overviews in search results, condensed versions in article view, and full verbatim text when available
- **Dynamic Content Loading**: CSV data is loaded at startup, enabling real-time search and filtering without database queries
- **User State Management**: User preferences (profile, favorites, saved comparisons) are stored in browser localStorage, while activity tracking is stored in the SQLite database
- **Responsive Design**: The interface adapts to different screen sizes using CSS Grid and Flexbox layouts

### Data Format

Research data is stored in CSV format with features organized into categories:
- Bibliographic information (title, authors, journal, year, citation, abstract)
- Research design and sample details
- Measurement and analysis methods
- Findings and results
- Contextual information (socio-cultural, political, platform, temporal)

Each feature can have both a condensed version (for quick viewing) and a verbatim version (original extracted text), following the naming convention: `feature_name` and `feature_name_verbatim`.

## Getting Help

If you encounter any issues or have questions:
1. Check the admin guide if you're an administrator
2. Use the "Requests for Changes" section when submitting papers
3. Contact the database administrators for additional support

## Privacy & Data

- Your profile information, favorites, and saved comparisons are stored locally in your browser
- Upload requests are stored securely in the database
- All research data is publicly available for academic use
