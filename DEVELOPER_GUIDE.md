# Developer Guide

Technical documentation for developers working on the Social Media Effects Research Database Platform.

## Table of Contents
- [Project Structure](#project-structure)
- [File Descriptions](#file-descriptions)
- [Setup & Installation](#setup--installation)
- [Running the Application](#running-the-application)
- [Architecture Overview](#architecture-overview)
- [Key Components](#key-components)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Development Guidelines](#development-guidelines)

## Project Structure

```
database_wireframe/
├── app.py                         # Main Flask application
├── requirements.txt               # Python dependencies
├── README.md                      # User-facing documentation
├── DEVELOPER_GUIDE.md             # This file
├── ADMIN_GUIDE.md                 # Admin dashboard guide
├── data/
│   ├── input/
│   │   └── papers_extracted.csv   # Research data (CSV format)
│   ├── output/
│   │   └── tracking.db            # Usage tracking database (SQLite)
│   └── user_uploads/              # User-submitted PDF files (awaiting feature extraction)
├── database/
│   └── init_db.py                 # Database initialization script
├── templates/                     # Jinja2 HTML templates
│   ├── base.html                  # Base template with header/footer
│   ├── index.html                 # Home page
│   ├── search.html                # Search results page
│   ├── article.html               # Article detail page
│   ├── compare.html               # Comparison page
│   ├── profile.html               # User profile page
│   ├── admin_login.html           # Admin login page
│   ├── admin_dashboard.html       # Admin dashboard
│   └── admin_requests.html        # Admin request review page
└── static/
    └── css/                       # Stylesheets
        ├── main.css               # Core styles
        ├── home.css               # Home page styles
        ├── search.css             # Search page styles
        ├── article.css            # Article page styles
        ├── compare.css            # Comparison page styles
        └── profile.css            # Profile page styles
```

## File Descriptions

### Backend Files

**`app.py`**
- Main Flask application with all routes and business logic
- Handles CSV data loading and parsing
- Contains search functionality, paper management
- Implements API endpoints for tracking and admin functions
- Manages file uploads and request processing
- Admin authentication and authorization
- Database connection management
- Run directly with: `python app.py`

**`requirements.txt`**
- Lists required Python packages:
  - `Flask==2.3.3`: Web framework
  - `Werkzeug==2.3.7`: WSGI utilities
  - `pytz==2023.3`: Timezone handling

### Data Files

**`data/input/papers_extracted.csv`**
- Contains extracted research features in CSV format
- Features have both condensed and verbatim versions
- Feature columns follow pattern: `feature_name` and `feature_name_verbatim`

**`data/output/tracking.db`**
- SQLite database for usage tracking
- Tables: search_logs, compare_view_logs, download_logs, upload_requests
- Tracks user activity and admin requests

**`data/user_uploads/`**
- Directory for storing user-submitted PDF files
- Files are renamed with timestamps for uniqueness
- These files are waiting to be processed through the feature extraction pipeline
- After feature extraction, the processed data should be added to `papers_extracted.csv`

### Database Files

**`database/init_db.py`**
- Initializes the SQLite tracking database
- Creates all required tables
- Can be run independently: `python database/init_db.py`

### Template Files

**`templates/base.html`**
- Base template with common header, navigation, and footer
- Extended by all other templates
- Includes common CSS and JavaScript

**`templates/index.html`**
- Home page with search box
- Displays platform description
- Entry point for user searches

**`templates/search.html`**
- Search results page with filtering options
- Shows year range, journal, and country/region filters
- Displays search results with "View Details" and "Compare" buttons
- Tracks search queries for analytics

**`templates/article.html`**
- Detailed article view with all extracted features
- Progressive disclosure: condensed - verbatim
- Add to favorites and comparison functionality

**`templates/compare.html`**
- Side-by-side comparison of multiple papers
- Features listed vertically on left, papers on right
- Download and save comparison functionality
- View Full button implementation

**`templates/profile.html`**
- User profile management page
- Multiple sections: Profile, Favorites, Saved Comparisons, Upload Papers, My Requests
- Local storage integration for user data
- Activity statistics display

**`templates/admin_login.html`**
- Admin authentication page
- Simple username/password login

**`templates/admin_dashboard.html`**
- Admin dashboard with usage statistics
- Displays search logs, comparison views, and downloads
- Shows top search queries and recent activity

**`templates/admin_requests.html`**
- Admin page for reviewing and approving user upload requests
- Lists all pending requests
- Allows approve/reject actions

### Style Files

**`static/css/main.css`**
- Core styles, layout, and components
- Common UI elements and typography

**`static/css/home.css`**
- Home page specific styles
- Search box and hero section

**`static/css/search.css`**
- Search page specific styles
- Filter components and result cards

**`static/css/article.css`**
- Article page specific styles
- Feature display and View Full functionality

**`static/css/compare.css`**
- Comparison page specific styles
- Dynamic grid layout and table styling

**`static/css/profile.css`**
- Profile page specific styles
- Sidebar navigation and content sections
- Request cards and status badges

## Setup & Installation

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

4. **Initialize Database**:
   ```bash
   python database/init_db.py
   ```

5. **Run the Application**:
   ```bash
   python app.py
   ```

6. **Access the Website**:
   - Open browser at: `http://localhost:5001`
   - Application will be running locally

## Running the Application

```bash
python app.py
```
- Runs on port 5001
- Debug mode enabled
- Auto-reload on code changes
- Access at: `http://localhost:5001`

### Stopping the Application
- Press `Ctrl+C` in the terminal

## Architecture Overview

### Technology Stack
- **Backend**: Flask (Python web framework)
- **Frontend**: HTML5, CSS3, JavaScript
- **Templates**: Jinja2 templating engine
- **Database**: SQLite for tracking and requests
- **Data Storage**: CSV file-based for research data

### Key Concepts

**1. Progressive Information Disclosure**
- Three levels of information:
  1. Concise overviews in search results
  2. Condensed versions in article view
  3. Full verbatim text with View Verbatim Text
- Smart button display based on content comparison

**2. Dynamic Content Loading**
- CSV data loaded at startup
- Real-time search and filtering
- Dynamic comparison table generation

**3. User State Management**
- Browser localStorage for user data
- Session management for admin
- Tracking database for analytics

## Key Components

### Search Functionality
- Cross-field keyword matching
- Filter support (year, journal, country)
- Results tracking and analytics
- URL parameter handling

### Comparison Feature
- CSS variable-based dynamic columns
- Max 5 papers per comparison
- Intelligent button labeling (View Full Text vs View Verbatim Text)
- Feature categorization and display
- Download and save functionality

### Request Management
- User upload request system
- File upload handling
- Admin approval workflow
- Status tracking (pending, approved, rejected)

### Admin Interface
- Authentication and authorization
- Usage statistics dashboard
- Request review and approval
- Search log analysis

## API Endpoints

### User-Facing APIs
- `GET /` - Home page
- `GET /search` - Search results page
- `GET /article/<paper_id>` - Article detail page
- `GET /compare` - Comparison page
- `GET /profile` - User profile page

### Data APIs
- `GET /api/papers` - Get all papers (JSON)
- `POST /api/track/search` - Track search query
- `POST /api/track/compare_view` - Track comparison view
- `POST /api/track/download` - Track download
- `GET /api/tracking/stats` - Get usage statistics
- `POST /api/upload-request` - Submit upload request
- `GET /api/my-requests` - Get user requests

### Admin APIs
- `POST /admin/login` - Admin login
- `GET /admin/logout` - Admin logout
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/requests` - Admin request review page
- `GET /api/admin/search_logs` - Get search logs
- `GET /api/admin/compare_view_logs` - Get comparison logs
- `GET /api/admin/download_logs` - Get download logs
- `GET /api/admin/stats` - Get admin statistics
- `GET /api/admin/requests` - Get all upload requests
- `POST /api/admin/requests/<id>/status` - Update request status

## Database Schema

### search_logs
- `id` (INTEGER PRIMARY KEY)
- `timestamp` (DATETIME)
- `search_query` (TEXT)
- `filters_used` (TEXT - JSON)
- `num_results` (INTEGER)
- `user_session` (TEXT)

### compare_view_logs
- `id` (INTEGER PRIMARY KEY)
- `timestamp` (DATETIME)
- `paper_ids` (TEXT)
- `num_papers` (INTEGER)
- `user_session` (TEXT)

### download_logs
- `id` (INTEGER PRIMARY KEY)
- `timestamp` (DATETIME)
- `paper_ids` (TEXT)
- `num_papers` (INTEGER)
- `file_format` (TEXT)
- `user_session` (TEXT)

### upload_requests
- `id` (INTEGER PRIMARY KEY)
- `timestamp` (DATETIME)
- `request_name` (TEXT)
- `institution` (TEXT)
- `email` (TEXT)
- `paper_info` (TEXT)
- `change_requests` (TEXT)
- `pdf_filename` (TEXT)
- `status` (TEXT - default: 'pending')

## Development Guidelines

### Adding New Features

1. **New Routes**: Add to `app.py` in the appropriate section
2. **New Templates**: Create in `templates/` directory
3. **New Styles**: Add to corresponding CSS file
4. **API Endpoints**: Follow RESTful conventions
5. **Database Changes**: Update `database/init_db.py`

### Code Style
- Follow PEP 8 Python style guide
- Use descriptive variable names
- Add comments for complex logic
- Keep functions focused and single-purpose

### Testing
- Test locally before committing
- Verify all routes work correctly
- Check responsive design on different screen sizes
- Test admin functionality separately

### Common Tasks

**Adding a New Paper**:
1. Update `data/input/papers_extracted.csv`
2. Follow CSV format exactly
3. Include both condensed and verbatim versions
4. Restart application

**Updating Database Schema**:
1. Modify `database/init_db.py`
2. Add migration logic if needed
3. Run: `python database/init_db.py`
4. Update affected code

**Adding a New Admin Feature**:
1. Update authentication if needed
2. Add new route with `@require_admin` decorator
3. Create corresponding template
4. Update `ADMIN_GUIDE.md`

## Important Notes

### Feature Extraction Requirements
- **Short features**: Should only include verbatim version
- **Long features**: Should include both condensed and verbatim versions
- **Naming convention**: Use `feature_name` and `feature_name_verbatim`
- **Empty values**: Use "NOT SPECIFIED"

### Expansion Logic (View Full Text & View Verbatim Text)
- Button appears when there are both short condensed version and long verbatim text
- Implemented in Article and Compare pages
- Uses JavaScript content comparison

### User Data
- Profile, favorites, comparisons stored in localStorage
- Not synchronized across devices
- Upload requests stored in database
- Admin can track all activity

### Timezone
- All timestamps in US Eastern Time
- Uses pytz for conversion
- Applies to search logs and upload requests

## Troubleshooting

### Common Issues

**Flask app won't start**:
- Check if port 5001 is in use
- Verify all dependencies installed
- Check for syntax errors in `app.py`

**Data not loading**:
- Verify CSV file format
- Check file path in `app.py`
- Ensure data has required columns

**Database errors**:
- Run `python database/init_db.py` to reset
- Check file permissions for `data/output/`
- Verify SQLite installation

**Search not working**:
- Check CSV data format
- Verify search logic in `app.py`
- Clear browser cache

