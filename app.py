from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import csv
import os
import json
import sqlite3
from datetime import datetime
from functools import wraps
import pytz

app = Flask(__name__)
app.secret_key = (
    "your-secret-key-change-this-in-production"  # Change this in production!
)


def word_count(value):
    """Return word count for a given string value."""
    if not value:
        return 0
    if isinstance(value, (list, tuple)):
        return len(value)
    return len(str(value).split())


def truncate_words(value, limit=30):
    """Truncate text to a specific number of words, adding ellipsis when needed."""
    if not value:
        return ""
    words = str(value).split()
    if len(words) <= limit:
        return str(value)
    return " ".join(words[:limit]) + "..."


app.jinja_env.filters["word_count"] = word_count
app.jinja_env.filters["truncate_words"] = truncate_words

# Admin credentials (in production, use environment variables or a proper auth system)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"  # Change this!

# Global variable to store papers data
papers_data = []


def load_papers_from_csv():
    """Load papers data from CSV file"""
    global papers_data
    papers_data = []

    csv_file = os.path.join("data", "input", "papers_extracted.csv")
    if not os.path.exists(csv_file):
        alt_path = os.path.join("data", "input", "paper_extracted.csv")
        if os.path.exists(alt_path):
            csv_file = alt_path

    try:
        with open(csv_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            print(f"CSV columns found: {len(reader.fieldnames)}")
            print(f"First few columns: {reader.fieldnames[:5]}")

            for i, row in enumerate(reader, 1):
                # Debug: print first row to see structure
                if i == 1:
                    print(f"First row keys: {list(row.keys())[:5]}")
                    print(f"Title from first row: '{row.get('title', 'NOT_FOUND')}'")

                paper = {
                    "id": f"paper_{str(i).zfill(3)}",
                    "title": row.get("title", "Untitled"),
                    "title_verbatim": row.get("title_verbatim", ""),
                    "authors": [
                        author.strip()
                        for author in row.get("authors", "").split(";")
                        if author.strip()
                    ],
                    "authors_verbatim": row.get("authors_verbatim", ""),
                    "journal": row.get("journal", ""),
                    "journal_verbatim": row.get("journal_verbatim", ""),
                    "year": (
                        int(row.get("year", 2023))
                        if row.get("year", "").isdigit()
                        else 2023
                    ),
                    "citation": row.get("citation", ""),
                    "abstract": row.get("abstract", ""),
                    "abstract_verbatim": row.get("abstract_verbatim", ""),
                    "sample_size": (
                        int(row.get("sample_size", "0").replace(",", ""))
                        if row.get("sample_size", "").replace(",", "").isdigit()
                        else 0
                    ),
                    "countries": (
                        [row.get("country_region", "USA")]
                        if row.get("country_region")
                        and row.get("country_region") != "NOT SPECIFIED"
                        else ["USA"]
                    ),
                    "methodology": row.get("study_type", "Unknown"),
                    "research_type": "Experimental Research",
                    "citations": 0,
                    "impact_factor": 0,
                    "keywords": ["social media", "politics"],
                    "extracted_features": {
                        "independent_variables": row.get("independent_variables", ""),
                        "independent_variables_verbatim": row.get(
                            "independent_variables_verbatim", ""
                        ),
                        "dependent_variables": row.get("dependent_variables", ""),
                        "dependent_variables_verbatim": row.get(
                            "dependent_variables_verbatim", ""
                        ),
                        "survey_questions": row.get("survey_questions", ""),
                        "survey_questions_verbatim": row.get(
                            "survey_questions_verbatim", ""
                        ),
                        "incentive": row.get("incentive", ""),
                        "incentive_verbatim": row.get("incentive_verbatim", ""),
                        "study_type": row.get("study_type", ""),
                        "study_type_verbatim": row.get("study_type_verbatim", ""),
                        "analysis_equations": row.get("analysis_equations", ""),
                        "analysis_equations_verbatim": row.get(
                            "analysis_equations_verbatim", ""
                        ),
                        "level_of_analysis": row.get("level_of_analysis", ""),
                        "level_of_analysis_verbatim": row.get(
                            "level_of_analysis_verbatim", ""
                        ),
                        "main_effects": row.get("main_effects", ""),
                        "main_effects_verbatim": row.get("main_effects_verbatim", ""),
                        "statistical_power": row.get("statistical_power", ""),
                        "statistical_power_verbatim": row.get(
                            "statistical_power_verbatim", ""
                        ),
                        "moderators": row.get("moderators", ""),
                        "moderators_verbatim": row.get("moderators_verbatim", ""),
                        "moderation_results": row.get("moderation_results", ""),
                        "moderation_results_verbatim": row.get(
                            "moderation_results_verbatim", ""
                        ),
                        "demographics": row.get("demographics", ""),
                        "demographics_verbatim": row.get("demographics_verbatim", ""),
                        "recruitment_source": row.get("recruitment_source", ""),
                        "recruitment_source_verbatim": row.get(
                            "recruitment_source_verbatim", ""
                        ),
                        "sample_size": row.get("sample_size", ""),
                        "sample_size_verbatim": row.get("sample_size_verbatim", ""),
                        "country_region": row.get("country_region", ""),
                        "sociocultural_context": row.get("sociocultural_context", ""),
                        "political_context": row.get("political_context", ""),
                        "platform_technological_context": row.get(
                            "platform_technological_context", ""
                        ),
                        "temporal_context": row.get("temporal_context", ""),
                        "recommended_moderators": row.get("recommended_moderators", ""),
                        "research_context": row.get("research_context", ""),
                        "intervention_insights": row.get("intervention_insights", ""),
                    },
                }
                papers_data.append(paper)

        print(f"Successfully loaded {len(papers_data)} papers from CSV")
        if papers_data:
            print(f"First paper title: '{papers_data[0]['title']}'")
        return papers_data

    except Exception as e:
        print(f"Error loading CSV: {e}")
        import traceback

        traceback.print_exc()
        return []


def search_papers(query="", filters=None):
    """Search papers based on query and filters"""
    if filters is None:
        filters = {}

    results = papers_data.copy()

    # Text search - search in title, abstract, journal, and author names
    if query:
        search_terms = query.lower().split()
        results = [
            paper
            for paper in results
            if all(
                term
                in " ".join(
                    [
                        paper["title"],
                        paper["abstract"],
                        " ".join(paper["authors"]),
                        paper["journal"],
                    ]
                ).lower()
                for term in search_terms
            )
        ]

    # Apply filters
    if filters.get("year_from"):
        results = [
            paper for paper in results if paper["year"] >= int(filters["year_from"])
        ]

    if filters.get("year_to"):
        results = [
            paper for paper in results if paper["year"] <= int(filters["year_to"])
        ]

    if filters.get("journal"):
        results = [
            paper
            for paper in results
            if filters["journal"].lower() == paper["journal"].lower()
        ]

    if filters.get("country"):
        results = [
            paper
            for paper in results
            if filters["country"].lower()
            in paper.get("extracted_features", {}).get("country_region", "").lower()
        ]

    # Sort by year (most recent first) by default
    results.sort(key=lambda x: x["year"], reverse=True)

    return results


def get_statistics():
    """Get platform statistics"""
    total_studies = sum(paper["sample_size"] for paper in papers_data)
    total_countries = len(
        set(country for paper in papers_data for country in paper["countries"])
    )
    methodologies = list(set(paper["methodology"] for paper in papers_data))
    journals = list(set(paper["journal"] for paper in papers_data))
    years = sorted(list(set(paper["year"] for paper in papers_data)), reverse=True)

    return {
        "totalPapers": len(papers_data),
        "totalStudies": total_studies,
        "totalCountries": total_countries,
        "methodologies": methodologies,
        "journals": journals,
        "years": years,
    }


# Routes
@app.route("/")
def index():
    """Home page"""
    stats = get_statistics()
    return render_template("index.html", stats=stats)


@app.route("/search")
def search():
    """Search page"""
    query = request.args.get("q", "")
    year_from = request.args.get("year_from", "")
    year_to = request.args.get("year_to", "")
    journal = request.args.get("journal", "")
    country = request.args.get("country", "")

    filters = {
        "year_from": year_from,
        "year_to": year_to,
        "journal": journal,
        "country": country,
    }

    # Remove empty filters
    filters = {k: v for k, v in filters.items() if v}

    results = search_papers(query, filters)

    # Get unique journals for filter dropdown
    journals = sorted(list(set(p["journal"] for p in papers_data if p["journal"])))

    return render_template(
        "search.html",
        query=query,
        results=results,
        filters=filters,
        journals=journals,
    )


@app.route("/article/<paper_id>")
def article(paper_id):
    """Article details page"""
    paper = next((p for p in papers_data if p["id"] == paper_id), None)
    if not paper:
        return "Paper not found", 404

    return render_template("article.html", paper=paper)


@app.route("/compare")
def compare():
    """Compare page"""
    # Get comparison list from query parameters
    ids_param = request.args.get("ids", "")
    if ids_param:
        comparison_ids = ids_param.split(",")
    else:
        comparison_ids = []

    comparison_papers = [p for p in papers_data if p["id"] in comparison_ids]

    return render_template("compare.html", papers=comparison_papers)


@app.route("/profile")
def profile():
    """Profile page"""
    return render_template("profile.html")


# API endpoints
@app.route("/api/papers")
def api_papers():
    """API endpoint to get all papers"""
    return jsonify(papers_data)


@app.route("/api/search")
def api_search():
    """API endpoint for search"""
    query = request.args.get("q", "")
    filters = {
        "year": request.args.get("year", ""),
        "journal": request.args.get("journal", ""),
        "methodology": request.args.get("methodology", ""),
        "country": request.args.get("country", ""),
        "sampleSize": request.args.get("sampleSize", ""),
        "sortBy": request.args.get("sortBy", "relevance"),
    }

    # Remove empty filters
    filters = {k: v for k, v in filters.items() if v}

    results = search_papers(query, filters)
    return jsonify(results)


@app.route("/api/paper/<paper_id>")
def api_paper(paper_id):
    """API endpoint to get a specific paper"""
    paper = next((p for p in papers_data if p["id"] == paper_id), None)
    if not paper:
        return jsonify({"error": "Paper not found"}), 404

    return jsonify(paper)


@app.route("/api/statistics")
def api_statistics():
    """API endpoint to get statistics"""
    return jsonify(get_statistics())


# Database helper functions
def get_db_connection():
    """Get database connection"""
    db_path = os.path.join("data", "output", "tracking.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn


def get_eastern_time():
    """Get current time in US Eastern timezone"""
    eastern = pytz.timezone("US/Eastern")
    return datetime.now(eastern).strftime("%Y-%m-%d %H:%M:%S")


def require_admin(f):
    """Decorator to require admin authentication"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("is_admin"):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)

    return decorated_function


# Tracking functions (Database-based)


@app.route("/api/track/search", methods=["POST"])
def track_search():
    """Track a search query"""
    try:
        data = request.json or {}
        search_query = data.get("search_query", "")
        filters_used = json.dumps(data.get("filters_used", {}))
        num_results = data.get("num_results", 0)
        user_session = session.get("user_id", "anonymous")
        timestamp = get_eastern_time()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO search_logs (timestamp, search_query, filters_used, num_results, user_session)
            VALUES (?, ?, ?, ?, ?)
            """,
            (timestamp, search_query, filters_used, num_results, user_session),
        )
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Search tracked"})
    except Exception as e:
        print(f"Error tracking search: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/track/compare_view", methods=["POST"])
def track_compare_view():
    """Track a comparison page view"""
    try:
        data = request.json or {}
        paper_ids = data.get("paper_ids", [])
        user_session = session.get("user_id", "anonymous")
        timestamp = get_eastern_time()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO compare_view_logs (timestamp, paper_ids, num_papers, user_session)
            VALUES (?, ?, ?, ?)
            """,
            (timestamp, json.dumps(paper_ids), len(paper_ids), user_session),
        )
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Compare view tracked"})
    except Exception as e:
        print(f"Error tracking compare view: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/track/download", methods=["POST"])
def track_download():
    """Track a comparison download"""
    try:
        data = request.json or {}
        paper_ids = data.get("paper_ids", [])
        user_session = session.get("user_id", "anonymous")
        timestamp = get_eastern_time()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO download_logs (timestamp, paper_ids, num_papers, user_session)
            VALUES (?, ?, ?, ?)
            """,
            (timestamp, json.dumps(paper_ids), len(paper_ids), user_session),
        )
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Download tracked"})
    except Exception as e:
        print(f"Error tracking download: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/tracking/stats")
def get_tracking_stats():
    """Get tracking statistics (public endpoint for Profile page)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as count FROM compare_view_logs")
        total_visits = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) as count FROM download_logs")
        total_downloads = cursor.fetchone()["count"]

        conn.close()

        return jsonify(
            {
                "total_visits": total_visits,
                "total_downloads": total_downloads,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Admin routes
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """Admin login page"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["is_admin"] = True
            session["user_id"] = "admin"
            return redirect(url_for("admin_dashboard"))
        else:
            return render_template("admin_login.html", error="Invalid credentials")

    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    """Admin logout"""
    session.pop("is_admin", None)
    session.pop("user_id", None)
    return redirect(url_for("index"))


@app.route("/admin/dashboard")
@require_admin
def admin_dashboard():
    """Admin dashboard page"""
    return render_template("admin_dashboard.html")


@app.route("/admin/requests")
@require_admin
def admin_requests():
    """Admin requests review page"""
    return render_template("admin_requests.html")


@app.route("/api/admin/search_logs")
@require_admin
def get_search_logs():
    """Get search logs for admin"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM search_logs 
            ORDER BY timestamp DESC 
            LIMIT 1000
        """
        )
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(logs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/compare_view_logs")
@require_admin
def get_compare_view_logs():
    """Get compare view logs for admin"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM compare_view_logs 
            ORDER BY timestamp DESC 
            LIMIT 1000
        """
        )
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(logs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/download_logs")
@require_admin
def get_download_logs():
    """Get download logs for admin"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM download_logs 
            ORDER BY timestamp DESC 
            LIMIT 1000
        """
        )
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(logs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/stats")
@require_admin
def get_admin_stats():
    """Get statistics for admin dashboard"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get counts
        cursor.execute("SELECT COUNT(*) as count FROM search_logs")
        total_searches = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) as count FROM compare_view_logs")
        total_compares = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) as count FROM download_logs")
        total_downloads = cursor.fetchone()["count"]

        # Get recent activity (last 7 days)
        cursor.execute(
            """
            SELECT COUNT(*) as count FROM search_logs 
            WHERE timestamp >= datetime('now', '-7 days')
        """
        )
        recent_searches = cursor.fetchone()["count"]

        cursor.execute(
            """
            SELECT COUNT(*) as count FROM compare_view_logs 
            WHERE timestamp >= datetime('now', '-7 days')
        """
        )
        recent_compares = cursor.fetchone()["count"]

        cursor.execute(
            """
            SELECT COUNT(*) as count FROM download_logs 
            WHERE timestamp >= datetime('now', '-7 days')
        """
        )
        recent_downloads = cursor.fetchone()["count"]

        # Get top search queries
        cursor.execute(
            """
            SELECT search_query, COUNT(*) as count 
            FROM search_logs 
            WHERE search_query != '' 
            GROUP BY search_query 
            ORDER BY count DESC 
            LIMIT 10
        """
        )
        top_searches = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return jsonify(
            {
                "total_searches": total_searches,
                "total_compares": total_compares,
                "total_downloads": total_downloads,
                "recent_searches": recent_searches,
                "recent_compares": recent_compares,
                "recent_downloads": recent_downloads,
                "top_searches": top_searches,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/my-requests")
def my_requests():
    """Get user's upload requests"""
    try:
        # For now, return all requests (in a real app, you'd filter by user session/email)
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, timestamp, request_name, institution, email, paper_info, 
                   change_requests, pdf_filename, status
            FROM upload_requests 
            ORDER BY timestamp DESC
        """
        )

        requests = []
        for row in cursor.fetchall():
            requests.append(
                {
                    "id": row[0],
                    "timestamp": row[1],
                    "request_name": row[2],
                    "institution": row[3],
                    "email": row[4],
                    "paper_info": row[5],
                    "change_requests": row[6],
                    "pdf_filename": row[7],
                    "status": row[8],
                }
            )

        conn.close()

        return jsonify({"requests": requests})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/upload-request", methods=["POST"])
def upload_request():
    """Handle paper upload requests"""
    try:
        # Get form data
        request_name = request.form.get("requestName")
        institution = request.form.get("institution")
        email = request.form.get("email")
        paper_info = request.form.get("paperInfo")
        change_requests = request.form.get("changeRequests", "")

        # Handle PDF file upload
        pdf_file = request.files.get("pdfFile")
        pdf_filename = None
        if pdf_file and pdf_file.filename:
            # Save PDF to user uploads directory
            upload_dir = os.path.join("data", "user_uploads")
            os.makedirs(upload_dir, exist_ok=True)

            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_filename = f"upload_{timestamp}_{pdf_file.filename}"
            pdf_path = os.path.join(upload_dir, pdf_filename)

            pdf_file.save(pdf_path)

        # Store request in database
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO upload_requests 
            (timestamp, request_name, institution, email, paper_info, change_requests, pdf_filename)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                get_eastern_time(),
                request_name,
                institution,
                email,
                paper_info,
                change_requests,
                pdf_filename,
            ),
        )

        conn.commit()
        conn.close()

        return jsonify(
            {"success": True, "message": "Upload request submitted successfully"}
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/admin/requests")
@require_admin
def get_admin_requests():
    """Get all upload requests for admin review"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, timestamp, request_name, institution, email, paper_info, 
                   change_requests, pdf_filename, status
            FROM upload_requests 
            ORDER BY timestamp DESC
        """
        )

        requests = []
        for row in cursor.fetchall():
            requests.append(
                {
                    "id": row[0],
                    "timestamp": row[1],
                    "request_name": row[2],
                    "institution": row[3],
                    "email": row[4],
                    "paper_info": row[5],
                    "change_requests": row[6],
                    "pdf_filename": row[7],
                    "status": row[8],
                }
            )

        conn.close()

        return jsonify({"requests": requests})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/requests/<int:request_id>/status", methods=["POST"])
@require_admin
def update_request_status(request_id):
    """Update request status (approve/reject)"""
    try:
        data = request.get_json()
        new_status = data.get("status")

        if new_status not in ["pending", "approved", "rejected"]:
            return jsonify({"error": "Invalid status"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE upload_requests SET status = ? WHERE id = ?",
            (new_status, request_id),
        )

        conn.commit()
        conn.close()

        return jsonify(
            {"success": True, "message": f"Request {new_status} successfully"}
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Load data on startup
    load_papers_from_csv()

    # Run the app
    app.run(debug=True, host="0.0.0.0", port=5001)
