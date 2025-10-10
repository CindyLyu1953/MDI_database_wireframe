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
```

### Programmatic Export
The admin API endpoints return JSON data that can be exported:
- `/api/admin/search_logs` - All search logs
- `/api/admin/compare_view_logs` - All compare view logs
- `/api/admin/download_logs` - All download logs
- `/api/admin/stats` - Summary statistics

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

-- Vacuum to reclaim space
VACUUM;
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

## Future Enhancements

Potential additions to consider:
- Export data to CSV/Excel from admin dashboard
- Data visualization (charts, graphs)
- Email reports
- Geographic tracking (with user consent)
- Custom date range filters
- User feedback tracking

