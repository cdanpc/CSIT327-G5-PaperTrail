/**
 * Global Search Functionality
 * Handles search input, API calls, and results display
 */

let searchTimeout = null;
let searchAbortController = null;

// Initialize search functionality
function initGlobalSearch() {
    const searchInput = document.querySelector('.search-box-inline input[type="text"]');
    const searchDropdown = document.getElementById('searchResultsDropdown');
    
    if (!searchInput || !searchDropdown) return;
    
    // Position dropdown below search input
    const searchBox = searchInput.closest('.search-box-inline');
    searchBox.style.position = 'relative';
    searchBox.appendChild(searchDropdown);
    
    // Search input event listener with debouncing
    searchInput.addEventListener('input', function(e) {
        const query = e.target.value.trim();
        
        // Clear previous timeout
        if (searchTimeout) {
            clearTimeout(searchTimeout);
        }
        
        // Hide dropdown if query is empty
        if (query.length === 0) {
            hideSearchResults();
            return;
        }
        
        // Debounce search (300ms delay)
        searchTimeout = setTimeout(() => {
            performGlobalSearch(query);
        }, 300);
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchBox.contains(e.target)) {
            hideSearchResults();
        }
    });
    
    // Prevent form submission, use global search instead
    const searchForm = searchInput.closest('form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const query = searchInput.value.trim();
            if (query) {
                window.location.href = `/search/?q=${encodeURIComponent(query)}`;
            }
        });
    }
}

// Perform global search API call
async function performGlobalSearch(query) {
    const searchLoading = document.getElementById('searchLoading');
    const searchEmpty = document.getElementById('searchEmpty');
    const searchResultsList = document.getElementById('searchResultsList');
    const searchResultsCount = document.getElementById('searchResultsCount');
    const searchDropdown = document.getElementById('searchResultsDropdown');
    
    // Abort previous request if exists
    if (searchAbortController) {
        searchAbortController.abort();
    }
    
    // Create new abort controller
    searchAbortController = new AbortController();
    
    // Show dropdown and loading state
    searchDropdown.style.display = 'block';
    searchLoading.style.display = 'block';
    searchEmpty.style.display = 'none';
    searchResultsList.innerHTML = '';
    
    try {
        const response = await fetch(`/api/global-search/?q=${encodeURIComponent(query)}`, {
            signal: searchAbortController.signal
        });
        
        if (!response.ok) {
            throw new Error('Search failed');
        }
        
        const data = await response.json();
        searchLoading.style.display = 'none';
        
        // Display results
        displaySearchResults(data);
        
        // Update count
        const totalResults = (data.resources?.length || 0) + 
                           (data.quizzes?.length || 0) + 
                           (data.flashcards?.length || 0);
        searchResultsCount.textContent = `(${totalResults})`;
        
        // Update "View All" link
        document.getElementById('viewAllSearchResults').href = `/search/?q=${encodeURIComponent(query)}`;
        
    } catch (error) {
        if (error.name === 'AbortError') {
            // Request was aborted, ignore
            return;
        }
        
        console.error('Search error:', error);
        searchLoading.style.display = 'none';
        searchEmpty.style.display = 'block';
        searchEmpty.innerHTML = '<p class="empty-text">Search failed. Please try again.</p>';
    }
}

// Display search results in dropdown
function displaySearchResults(data) {
    const searchResultsList = document.getElementById('searchResultsList');
    const searchEmpty = document.getElementById('searchEmpty');
    
    const hasResults = (data.resources?.length > 0) || 
                      (data.quizzes?.length > 0) || 
                      (data.flashcards?.length > 0);
    
    if (!hasResults) {
        searchEmpty.style.display = 'block';
        return;
    }
    
    let html = '';
    
    // Resources
    if (data.resources && data.resources.length > 0) {
        html += '<div class="search-results-group">';
        html += '<div class="search-results-group-header">';
        html += '<i class="fas fa-file-alt"></i> Resources';
        html += '</div>';
        
        data.resources.forEach(item => {
            html += `
                <a href="${escapeHtml(item.url)}" class="search-result-item">
                    <div class="search-result-icon">
                        <i class="fas fa-${getResourceIcon(item.resource_type)}"></i>
                    </div>
                    <div class="search-result-content">
                        <div class="search-result-title">${escapeHtml(item.title)}</div>
                        ${item.description ? `<div class="search-result-description">${escapeHtml(truncate(item.description, 80))}</div>` : ''}
                    </div>
                    ${item.is_verified ? '<span class="search-result-badge"><i class="fas fa-check-circle"></i></span>' : ''}
                </a>
            `;
        });
        
        html += '</div>';
    }
    
    // Quizzes
    if (data.quizzes && data.quizzes.length > 0) {
        html += '<div class="search-results-group">';
        html += '<div class="search-results-group-header">';
        html += '<i class="fas fa-question-circle"></i> Quizzes';
        html += '</div>';
        
        data.quizzes.forEach(item => {
            html += `
                <a href="${escapeHtml(item.url)}" class="search-result-item">
                    <div class="search-result-icon">
                        <i class="fas fa-clipboard-question"></i>
                    </div>
                    <div class="search-result-content">
                        <div class="search-result-title">${escapeHtml(item.title)}</div>
                        ${item.description ? `<div class="search-result-description">${escapeHtml(truncate(item.description, 80))}</div>` : ''}
                    </div>
                    ${item.is_verified ? '<span class="search-result-badge"><i class="fas fa-check-circle"></i></span>' : ''}
                </a>
            `;
        });
        
        html += '</div>';
    }
    
    // Flashcards
    if (data.flashcards && data.flashcards.length > 0) {
        html += '<div class="search-results-group">';
        html += '<div class="search-results-group-header">';
        html += '<i class="fas fa-layer-group"></i> Flashcards';
        html += '</div>';
        
        data.flashcards.forEach(item => {
            html += `
                <a href="${escapeHtml(item.url)}" class="search-result-item">
                    <div class="search-result-icon">
                        <i class="fas fa-cards"></i>
                    </div>
                    <div class="search-result-content">
                        <div class="search-result-title">${escapeHtml(item.title)}</div>
                        ${item.description ? `<div class="search-result-description">${escapeHtml(truncate(item.description, 80))}</div>` : ''}
                    </div>
                    ${item.is_verified ? '<span class="search-result-badge"><i class="fas fa-check-circle"></i></span>' : ''}
                </a>
            `;
        });
        
        html += '</div>';
    }
    
    searchResultsList.innerHTML = html;
}

// Hide search results dropdown
function hideSearchResults() {
    const searchDropdown = document.getElementById('searchResultsDropdown');
    if (searchDropdown) {
        searchDropdown.style.display = 'none';
    }
}

// Get icon for resource type
function getResourceIcon(type) {
    const icons = {
        'pdf': 'file-pdf',
        'image': 'image',
        'ppt': 'file-powerpoint',
        'pptx': 'file-powerpoint',
        'docx': 'file-word',
        'txt': 'file-lines',
        'link': 'link'
    };
    return icons[type] || 'file-alt';
}

// Truncate text
function truncate(text, length) {
    if (text.length <= length) return text;
    return text.substring(0, length) + '...';
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initGlobalSearch);
