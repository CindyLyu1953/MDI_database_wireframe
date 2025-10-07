from flask import Flask, render_template, request, jsonify
import csv
import os

app = Flask(__name__)

# Global variable to store papers data
papers_data = []


def load_papers_from_csv():
    """Load papers data from CSV file"""
    global papers_data
    papers_data = []

    csv_file = os.path.join("data", "papers_extracted.csv")

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
    if filters.get("year"):
        results = [paper for paper in results if paper["year"] >= int(filters["year"])]

    if filters.get("journal"):
        results = [
            paper
            for paper in results
            if filters["journal"].lower() in paper["journal"].lower()
        ]

    if filters.get("methodology"):
        results = [
            paper for paper in results if paper["methodology"] == filters["methodology"]
        ]

    if filters.get("country"):
        results = [
            paper
            for paper in results
            if any(
                filters["country"].lower() in country.lower()
                for country in paper["countries"]
            )
        ]

    if filters.get("sampleSize"):
        results = [
            paper
            for paper in results
            if paper["sample_size"] >= int(filters["sampleSize"])
        ]

    # Sort results
    sort_by = filters.get("sortBy", "relevance")
    if sort_by == "year":
        results.sort(key=lambda x: x["year"], reverse=True)
    elif sort_by == "citations":
        results.sort(key=lambda x: x["citations"], reverse=True)
    elif sort_by == "sampleSize":
        results.sort(key=lambda x: x["sample_size"], reverse=True)

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
    year = request.args.get("year", "")
    journal = request.args.get("journal", "")
    methodology = request.args.get("methodology", "")
    country = request.args.get("country", "")
    sample_size = request.args.get("sampleSize", "")
    sort_by = request.args.get("sortBy", "relevance")

    filters = {
        "year": year,
        "journal": journal,
        "methodology": methodology,
        "country": country,
        "sampleSize": sample_size,
        "sortBy": sort_by,
    }

    # Remove empty filters
    filters = {k: v for k, v in filters.items() if v}

    results = search_papers(query, filters)

    return render_template(
        "search.html",
        query=query,
        results=results,
        filters=filters,
        stats=get_statistics(),
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


if __name__ == "__main__":
    # Load data on startup
    load_papers_from_csv()

    # Run the app
    app.run(debug=True, host="0.0.0.0", port=5001)
