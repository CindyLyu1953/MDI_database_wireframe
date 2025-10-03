// Data loader for the questionnaire database platform
class DataLoader {
    constructor() {
        this.papers = [];
        this.currentSearchResults = [];
        this.comparisonList = [];
        this.favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
        this.searchHistory = JSON.parse(localStorage.getItem('searchHistory') || '[]');
    }

    // Load papers data from CSV file
    async loadPapers() {
        try {
            // Try to load CSV data first
            if (window.csvDataLoader) {
                const data = await window.csvDataLoader.loadCSVData();
                this.papers = data.papers;
                return this.papers;
            }
            
            // Fallback to JSON if CSV loader not available
            const response = await fetch('data/papers.json');
            const data = await response.json();
            this.papers = data.papers;
            return this.papers;
        } catch (error) {
            console.error('Error loading papers:', error);
            return [];
        }
    }

    // Search papers based on query and filters
    searchPapers(query = '', filters = {}) {
        let results = [...this.papers];
        
        console.log('Search query:', query);
        console.log('Total papers available:', this.papers.length);

        // Text search - search in title, abstract, journal, and author names
        if (query) {
            const searchTerms = query.toLowerCase().split(' ');
            console.log('Search terms:', searchTerms);
            
            results = results.filter(paper => {
                const searchText = [
                    paper.title,
                    paper.abstract,
                    paper.authors.join(' '),
                    paper.journal
                ].join(' ').toLowerCase();
                
                console.log(`Checking paper: ${paper.title}`);
                console.log('Search text:', searchText);
                
                const matches = searchTerms.every(term => {
                    const found = searchText.includes(term);
                    console.log(`  Term "${term}" found: ${found}`);
                    return found;
                });
                
                console.log(`  Overall match: ${matches}`);
                return matches;
            });
        }
        
        console.log('Search results count:', results.length);

        // Apply filters
        if (filters.year) {
            results = results.filter(paper => paper.year >= filters.year);
        }
        if (filters.journal) {
            results = results.filter(paper => 
                paper.journal.toLowerCase().includes(filters.journal.toLowerCase())
            );
        }
        if (filters.methodology) {
            results = results.filter(paper => 
                paper.methodology === filters.methodology
            );
        }
        if (filters.country) {
            results = results.filter(paper => 
                paper.countries.some(country => 
                    country.toLowerCase().includes(filters.country.toLowerCase())
                )
            );
        }
        if (filters.sampleSize) {
            results = results.filter(paper => 
                paper.sample_size >= filters.sampleSize
            );
        }

        // Sort results
        const sortBy = filters.sortBy || 'relevance';
        switch (sortBy) {
            case 'year':
                results.sort((a, b) => b.year - a.year);
                break;
            case 'citations':
                results.sort((a, b) => b.citations - a.citations);
                break;
            case 'sampleSize':
                results.sort((a, b) => b.sample_size - a.sample_size);
                break;
            default: // relevance
                // Keep original order for now (could implement more sophisticated ranking)
                break;
        }

        this.currentSearchResults = results;
        this.addToSearchHistory(query, filters);
        return results;
    }

    // Get paper by ID
    getPaperById(id) {
        return this.papers.find(paper => paper.id === id);
    }

    // Add paper to comparison list
    addToComparison(paperId) {
        const paper = this.getPaperById(paperId);
        if (paper && !this.comparisonList.find(p => p.id === paperId)) {
            this.comparisonList.push(paper);
            this.saveComparison();
        }
    }

    // Remove paper from comparison list
    removeFromComparison(paperId) {
        this.comparisonList = this.comparisonList.filter(p => p.id !== paperId);
        this.saveComparison();
    }

    // Get comparison list
    getComparisonList() {
        return this.comparisonList;
    }

    // Save comparison list to localStorage
    saveComparison() {
        localStorage.setItem('comparisonList', JSON.stringify(this.comparisonList));
    }

    // Load comparison list from localStorage
    loadComparison() {
        const saved = localStorage.getItem('comparisonList');
        if (saved) {
            this.comparisonList = JSON.parse(saved);
        }
    }

    // Add paper to favorites
    addToFavorites(paperId) {
        if (!this.favorites.includes(paperId)) {
            this.favorites.push(paperId);
            this.saveFavorites();
        }
    }

    // Remove paper from favorites
    removeFromFavorites(paperId) {
        this.favorites = this.favorites.filter(id => id !== paperId);
        this.saveFavorites();
    }

    // Check if paper is favorited
    isFavorited(paperId) {
        return this.favorites.includes(paperId);
    }

    // Get favorites
    getFavorites() {
        return this.favorites.map(id => this.getPaperById(id)).filter(Boolean);
    }

    // Save favorites to localStorage
    saveFavorites() {
        localStorage.setItem('favorites', JSON.stringify(this.favorites));
    }

    // Add search to history
    addToSearchHistory(query, filters) {
        if (query) {
            const searchEntry = {
                query,
                filters,
                timestamp: new Date().toISOString(),
                resultCount: this.currentSearchResults.length
            };
            this.searchHistory.unshift(searchEntry);
            this.searchHistory = this.searchHistory.slice(0, 10); // Keep only last 10 searches
            localStorage.setItem('searchHistory', JSON.stringify(this.searchHistory));
        }
    }

    // Get search history
    getSearchHistory() {
        return this.searchHistory;
    }


    // Get statistics
    getStatistics() {
        return {
            totalPapers: this.papers.length,
            totalStudies: this.papers.reduce((sum, paper) => sum + (paper.sample_size || 0), 0),
            totalCountries: new Set(this.papers.flatMap(paper => paper.countries)).size,
            methodologies: [...new Set(this.papers.map(paper => paper.methodology))],
            journals: [...new Set(this.papers.map(paper => paper.journal))],
            years: [...new Set(this.papers.map(paper => paper.year))].sort((a, b) => b - a)
        };
    }

    // Get all papers
    getAllPapers() {
        return this.papers;
    }
}

// Initialize global data loader
window.dataLoader = new DataLoader();

// Data loading is handled by individual pages

// Utility functions for UI updates
function updateSearchResults(results) {
    const resultsContainer = document.getElementById('search-results');
    if (!resultsContainer) return;

    resultsContainer.innerHTML = '';
    
    if (results.length === 0) {
        resultsContainer.innerHTML = '<div class="no-results">No results found. Try adjusting your search criteria.</div>';
        return;
    }

    results.forEach(paper => {
        const resultCard = createResultCard(paper);
        resultsContainer.appendChild(resultCard);
    });

    // Update result count
    const resultCount = document.getElementById('result-count');
    if (resultCount) {
        resultCount.textContent = `Found ${results.length} results`;
    }
}

function createResultCard(paper) {
    const card = document.createElement('article');
    card.className = 'result-item';
    card.innerHTML = `
        <div class="result-header">
            <h3 class="result-title">
                <a href="article.html?id=${paper.id}">${paper.title}</a>
            </h3>
            <div class="result-actions">
                <button class="btn btn-outline btn-sm" onclick="addToCompare('${paper.id}')">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M9 11H5a2 2 0 0 0-2 2v3c0 1.1.9 2 2 2h4m0-7v7m0-7h10a2 2 0 0 1 2 2v3c0 1.1-.9 2-2 2H9m0-7V9a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2"></path>
                    </svg>
                    Compare
                </button>
                <button class="btn btn-outline btn-sm" onclick="toggleFavorite('${paper.id}')">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                    </svg>
                    Favorite
                </button>
            </div>
        </div>
        
        <div class="result-meta">
            <div class="result-authors">
                <strong>Authors:</strong> ${paper.authors.join(', ')}
            </div>
            <div class="result-journal">
                <strong>Journal:</strong> ${paper.journal}, ${paper.year}
            </div>
            <div class="result-citations">
                <strong>Citations:</strong> ${paper.citations} times
            </div>
        </div>

        <div class="result-abstract">
            <p>${paper.abstract}</p>
        </div>

        <div class="result-features">
            <div class="feature-tags">
                <span class="tag tag-primary">${paper.methodology}</span>
                <span class="tag">Social Media</span>
                <span class="tag">Political Psychology</span>
                <span class="tag">Cross-National</span>
            </div>
        </div>

        <div class="result-footer">
            <a href="article.html?id=${paper.id}" class="btn btn-primary">View Details</a>
            <div class="result-stats">
                <span class="stat-item">Sample Size: ${paper.sample_size.toLocaleString()}</span>
                <span class="stat-item">Countries: ${paper.countries.join(', ')}</span>
                <span class="stat-item">Method: ${paper.methodology}</span>
            </div>
        </div>
    `;
    return card;
}

// Global functions for UI interactions
function addToComparison(paperId) {
    window.dataLoader.addToComparison(paperId);
    updateComparisonUI();
    showNotification('Added to comparison');
}

function toggleFavorite(paperId) {
    if (window.dataLoader.isFavorited(paperId)) {
        window.dataLoader.removeFromFavorites(paperId);
    } else {
        window.dataLoader.addToFavorites(paperId);
    }
    updateFavoritesUI();
    showNotification('Favorites updated');
}

function viewDetails(paperId) {
    // Handle both file:// and http:// protocols
    if (window.location.protocol === 'file:') {
        // For file:// protocol, use relative path
        window.location.href = `article.html?id=${paperId}`;
    } else {
        // For http:// protocol, use absolute path
        window.location.href = `${window.location.origin}/article.html?id=${paperId}`;
    }
}

function updateComparisonUI() {
    const comparisonList = window.dataLoader.getComparisonList();
    const comparisonCount = document.getElementById('comparison-count');
    if (comparisonCount) {
        comparisonCount.textContent = comparisonCount.textContent.replace(/\d+/, comparisonList.length);
    }
}

function updateFavoritesUI() {
    // Update favorite buttons throughout the interface
    const favoriteButtons = document.querySelectorAll('.btn-favorite');
    favoriteButtons.forEach(button => {
        const paperId = button.getAttribute('onclick').match(/'([^']+)'/)[1];
        if (window.dataLoader.isFavorited(paperId)) {
            button.classList.add('favorited');
            button.textContent = 'Favorited';
        } else {
            button.classList.remove('favorited');
            button.textContent = 'Favorite';
        }
    });
}

function showNotification(message) {
    // Simple notification system
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Initialize data when page loads
document.addEventListener('DOMContentLoaded', async () => {
    await window.dataLoader.loadPapers();
    window.dataLoader.loadComparison();
    
    // Initialize UI based on current page
    const currentPage = window.location.pathname.split('/').pop();
    
    switch (currentPage) {
        case 'search.html':
            initializeSearchPage();
            break;
        case 'article.html':
            initializeArticlePage();
            break;
        case 'compare.html':
            initializeComparePage();
            break;
    }
});

// Page-specific initialization functions
function initializeSearchPage() {
    // Load search results if there's a query parameter
    const urlParams = new URLSearchParams(window.location.search);
    const query = urlParams.get('q') || '';
    const filters = {
        year: urlParams.get('year') || '',
        journal: urlParams.get('journal') || '',
        methodology: urlParams.get('methodology') || '',
        country: urlParams.get('country') || '',
        sampleSize: urlParams.get('sampleSize') || '',
        sortBy: urlParams.get('sortBy') || 'relevance'
    };
    
    if (query) {
        const results = window.dataLoader.searchPapers(query, filters);
        updateSearchResults(results);
    }
}

function initializeArticlePage() {
    const urlParams = new URLSearchParams(window.location.search);
    const paperId = urlParams.get('id');
    
    if (paperId) {
        const paper = window.dataLoader.getPaperById(paperId);
        if (paper) {
            updateArticleDetails(paper);
        }
    }
}

function initializeComparePage() {
    const comparisonList = window.dataLoader.getComparisonList();
    if (comparisonList.length > 0) {
        updateComparisonTable(comparisonList);
    }
}

