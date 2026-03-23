# Admin Dashboard Guide

## Overview
The admin dashboard provides comprehensive tracking and analytics for the Questionnaire Database Platform. It tracks user searches, comparison views, and downloads to help demonstrate platform impact and understand user behavior.

## Accessing the Admin Dashboard

### Login Credentials
- **URL**: `http://localhost:5001/admin/login`
- **Username**: `admin`
- **Password**: `admin123`

**⚠️ IMPORTANT**: Change these credentials before deploying to production! Update the values in `app.py`:
```python
ADMIN_USERNAME = "your-username"
ADMIN_PASSWORD = "your-secure-password"
```

## Admin Navigation

The admin dashboard has multiple sections:
- **Dashboard**: View usage statistics and analytics
- **Requests**: Review and manage user upload requests
- **Logout**: End admin session

## User Upload Request Management

### Overview
Users can submit requests to add new papers to the database through the Profile page. As an admin, you can review these requests, download submitted PDFs, and approve or reject them.

### Accessing Upload Requests
1. Login to admin dashboard
2. Click "Requests" in the navigation menu
3. View all pending and processed requests

### Request Information
Each upload request contains:
- **Request Name**: User-provided description
- **Institution**: Requester's institution
- **Email**: Contact email
- **Paper Information**: Details about the paper to be added (title, authors, DOI, etc.)
- **Change Requests**: Any issues reported with existing papers (optional)
- **PDF File**: Uploaded PDF document (optional)
- **Status**: pending, approved, or rejected
- **Timestamp**: When the request was submitted

### Downloading PDFs
When a user submits a PDF file:
1. The PDF is stored securely in `data/user_uploads/`
2. In the Requests page, you'll see the filename with a download icon
3. Click the PDF filename to download and review the file
4. PDFs are only accessible to admins (protected route)

### Approving/Rejecting Requests
1. Review the request details and PDF (if provided)
2. Click **"Approve"** to accept the request
3. Click **"Reject"** to decline the request
4. Status updates immediately and user can see it in their profile

### After Approval
Once a request is approved:
1. The PDF should be processed through your feature extraction pipeline
2. Extract all required features from the paper
3. Add the extracted data to `data/input/papers_extracted.csv`
4. The paper will then appear in the database for all users

## What's Being Tracked

### 1. Search Logs
Captures every search query with the following information:
- **Timestamp**: When the search was performed
- **Search Query**: The exact keywords searched
- **Filters Used**: Any filters applied (currently empty, ready for future filter implementation)
- **Number of Results**: How many papers matched the search
- **User Session**: Anonymous session identifier

### 2. Compare View Logs
Tracks when users view the comparison page with:
- **Timestamp**: When the comparison was viewed
- **Paper IDs**: Which papers were being compared
- **Number of Papers**: How many papers in the comparison (1-3)
- **User Session**: Anonymous session identifier

### 3. Download Logs
Records when users download comparison results with:
- **Timestamp**: When the download occurred
- **Paper IDs**: Which papers were in the downloaded comparison
- **Number of Papers**: How many papers were downloaded
- **File Format**: Currently always CSV
- **User Session**: Anonymous session identifier

## Dashboard Features

### Statistics Cards
The dashboard displays key metrics:
- **Total Searches**: Lifetime count of all searches
- **Compare Views**: Total number of comparison page views
- **Downloads**: Total number of comparison downloads
- Each card also shows activity from the last 7 days

### Top Search Queries
Lists the 10 most frequent search queries with their counts, helping you understand:
- What topics researchers are most interested in
- Which keywords are most popular
- Potential gaps in your database coverage

### Data Tables
Three tabs provide detailed logs:
1. **Search Logs**: Recent search activity
2. **Compare Views**: Recent comparison activity
3. **Downloads**: Recent download activity

All tables show up to 1,000 recent records and are sorted by timestamp (newest first).

## Database Information

### Database Location
- **File**: `data/output/tracking.db`
- **Type**: SQLite
- **Tables**:
  - `search_logs`
  - `compare_view_logs`
  - `download_logs`
  - `upload_requests`

### Database Schema

#### search_logs
```sql
id                INTEGER PRIMARY KEY
timestamp         DATETIME DEFAULT CURRENT_TIMESTAMP
search_query      TEXT NOT NULL
filters_used      TEXT (JSON string)
num_results       INTEGER
user_session      TEXT
```

#### compare_view_logs
```sql
id                INTEGER PRIMARY KEY
timestamp         DATETIME DEFAULT CURRENT_TIMESTAMP
paper_ids         TEXT (JSON array)
num_papers        INTEGER
user_session      TEXT
```

#### download_logs
```sql
id                INTEGER PRIMARY KEY
timestamp         DATETIME DEFAULT CURRENT_TIMESTAMP
paper_ids         TEXT (JSON array)
num_papers        INTEGER
file_format       TEXT DEFAULT 'CSV'
user_session      TEXT
```

#### upload_requests
```sql
id                INTEGER PRIMARY KEY
timestamp         DATETIME DEFAULT CURRENT_TIMESTAMP
request_name      TEXT NOT NULL
institution       TEXT NOT NULL
email             TEXT NOT NULL
paper_info        TEXT NOT NULL
change_requests   TEXT
pdf_filename      TEXT
status            TEXT DEFAULT 'pending'
```

## Exporting Data

### Using SQL Queries
You can directly query the database using any SQLite client:
```bash
sqlite3 data/output/tracking.db
```

Example queries:
```sql
-- Get all searches from the last week
SELECT * FROM search_logs 
WHERE timestamp >= datetime('now', '-7 days')
ORDER BY timestamp DESC;

-- Count searches by day
SELECT date(timestamp) as day, COUNT(*) as searches
FROM search_logs
GROUP BY day
ORDER BY day DESC;

-- Most compared papers
SELECT paper_ids, COUNT(*) as times_compared
FROM compare_view_logs
GROUP BY paper_ids
ORDER BY times_compared DESC
LIMIT 10;

-- Get all pending upload requests
SELECT * FROM upload_requests
WHERE status = 'pending'
ORDER BY timestamp DESC;

-- Count requests by status
SELECT status, COUNT(*) as count
FROM upload_requests
GROUP BY status;
```

### Programmatic Export
The admin API endpoints return JSON data that can be exported:
- `/api/admin/search_logs` - All search logs
- `/api/admin/compare_view_logs` - All compare view logs
- `/api/admin/download_logs` - All download logs
- `/api/admin/requests` - All upload requests
- `/api/admin/stats` - Summary statistics

### Accessing Upload Request Files
- `/uploads/<filename>` - Download PDF files (admin only)
- Files are stored in `data/user_uploads/`
- Only accessible to authenticated admins

## Privacy & Security

### User Privacy
- No personally identifiable information (PII) is collected
- Session IDs are randomly generated and anonymous
- IP addresses are NOT logged
- No user accounts or authentication required for regular users

### Security Considerations
1. **Change Default Credentials**: Update admin username/password before deployment
2. **Use HTTPS**: Always use HTTPS in production
3. **Secure the Database**: Ensure `tracking.db` is not publicly accessible
4. **Session Secret**: Change the Flask secret key in `app.py`

## Maintenance

### Cleaning Old Data
To remove old data and keep the database manageable:
```sql
-- Delete logs older than 1 year
DELETE FROM search_logs WHERE timestamp < datetime('now', '-1 year');
DELETE FROM compare_view_logs WHERE timestamp < datetime('now', '-1 year');
DELETE FROM download_logs WHERE timestamp < datetime('now', '-1 year');

-- Delete processed upload requests older than 1 year (keep pending)
DELETE FROM upload_requests 
WHERE timestamp < datetime('now', '-1 year') 
AND status != 'pending';

-- Vacuum to reclaim space
VACUUM;
```

### Managing Upload Files
To clean up old uploaded PDF files:
```bash
# List files older than 1 year
find data/user_uploads/ -name "upload_*.pdf" -mtime +365

# Delete files older than 1 year (be careful!)
find data/user_uploads/ -name "upload_*.pdf" -mtime +365 -delete
```

### Backup
Regularly backup the database:
```bash
cp data/output/tracking.db data/output/tracking_backup_$(date +%Y%m%d).db
```

## Demonstrating Impact

Use the tracked data to:
1. **Show Usage Trends**: How many searches/comparisons/downloads over time
2. **Identify Popular Topics**: What researchers are searching for most
3. **Prove Value**: Total number of searches, comparisons, and downloads
4. **Understand Behavior**: Which papers are compared most frequently
5. **Report Metrics**: Generate periodic reports for stakeholders

## Troubleshooting

### Can't Login
- Check that you're using the correct username/password
- Ensure the Flask app is running
- Check the browser console for errors

### No Data Showing
- Verify the database exists: `ls -la data/output/tracking.db`
- Check that tracking is working by performing a search/comparison
- Look at Flask logs for any errors

### Database Locked
- Close any other SQLite connections
- Restart the Flask app
- Check file permissions

### Can't Download PDFs
- Ensure you're logged in as admin
- Check that the file exists in `data/user_uploads/`
- Verify file permissions are correct
- Check Flask logs for errors

### Upload Requests Not Showing
- Verify database is initialized: `python database/init_db.py`
- Check that `upload_requests` table exists
- Try submitting a test request from Profile page

## Future Enhancements

Potential additions to consider:
- Export data to CSV/Excel from admin dashboard
- Data visualization (charts, graphs)
- Email reports
- Geographic tracking (with user consent)
- Custom date range filters
- User feedback tracking

