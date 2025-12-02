// Learning Hub JavaScript

/**
 * Component Function: Resource Detail View
 * Generates the HTML for a detailed resource card based on the user's requested layout.
 * @param {object} resource - Resource data object.
 * @returns {string} HTML string for the detailed view.
 */
function ResourceDetailView(resource) {
    // Determine the accent color for the rating based on the score
    const ratingColor = resource.rating >= 4.0 ? 'text-success-color' : resource.rating >= 2.0 ? 'text-warning-color' : 'text-danger';
    
    // Format the rating to one decimal place
    const formattedRating = resource.rating.toFixed(1);

    return `
        <div class="resource-detail-grid">
            
            <!-- 1. Resource Header (Title, Tags, Description) -->
            <div class="header-area card card-border-left border-warning">
                <div class="flex items-center space-x-2 mb-3 text-sm font-medium text-secondary-color">
                    <span class="px-2 py-1 bg-gray-100 rounded">${resource.type}</span>
                    
                    <span class="flex items-center text-success-color">
                        <!-- Verified Tag -->
                        <svg class="w-4 h-4 mr-1 verified-icon" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>
                        Verified
                    </span>
                    <span class="text-primary-color"> • Public</span>
                </div>

                <!-- Resource Title and Description -->
                <h2 class="text-3xl font-extrabold text-primary-color mb-1">${resource.title.toUpperCase()}</h2>
                <p class="text-base text-secondary-color">${resource.description}</p>
            </div>

            <!-- 2. Uploader Info (Desktop/Tablet Top Right) -->
            <div class="uploader-area card">
                <h3 class="text-sm font-semibold text-secondary-color uppercase mb-3 border-b pb-2">Uploaded By</h3>
                <div class="flex items-center space-x-3">
                    <img class="avatar-md" src="${resource.uploader.avatarUrl}" onerror="this.onerror=null; this.src='https://placehold.co/40x40/cccccc/333333?text=U'" alt="${resource.uploader.name}">
                    <span class="font-semibold text-primary-color text-base">${resource.uploader.name}</span>
                </div>
            </div>

            <!-- 3. Actions (Download, Preview, Likes/Rate, Bookmark) -->
            <div class="actions-area card">
                <h3 class="text-sm font-semibold text-secondary-color uppercase mb-3 border-b pb-2">Actions</h3>
                <div class="space-y-3">
                    <!-- Bookmark Button -->
                    <button class="action-button border border-current text-primary-color hover:bg-gray-100">
                        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"></path></svg>
                        Bookmark
                    </button>
                    <!-- Download Button -->
                    <button class="action-button bg-gray-200 text-primary-color hover:bg-gray-300">
                        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                        Download
                    </button>
                    <!-- Preview Button -->
                    <button class="action-button border border-current link-color hover:bg-cyan-50">
                        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
                        Preview
                    </button>
                    <!-- Rate Resource Button -->
                    <button class="action-button bg-warning-color bg-opacity-10 text-warning-color border border-warning-color hover:bg-warning-color hover:text-white">
                        <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.695h3.462c.969 0 1.371 1.24.588 1.81l-2.817 2.039a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.817-2.039a1 1 0 00-1.175 0l-2.817 2.039c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.002 8.724c-.783-.57-.381-1.81.588-1.81h3.461a1 1 0 00.951-.695l1.07-3.292z"></path></svg>
                        Rate Resource
                    </button>

                    <!-- Likes count -->
                    <div class="flex items-center justify-center pt-2">
                        <span class="text-2xl font-bold text-danger">${resource.likes}</span>
                        <span class="text-sm font-medium text-secondary-color ml-2">Likes</span>
                    </div>
                </div>
            </div>
            
            <!-- 4. Stats Rows (Full Width Below Header) -->
            <div class="stats-area grid grid-cols-1 gap-4 mt-2">
                <!-- Stat: Downloads -->
                <div class="stat-card card card-border-left border-warning">
                    <div class="flex items-center justify-between">
                        <span class="text-3xl font-bold text-warning-color">${resource.downloads}</span>
                        <span class="text-xs text-secondary-color uppercase">Downloads</span>
                    </div>
                </div>
                <!-- Stat: Rating -->
                <div class="stat-card card card-border-left border-success">
                    <div class="flex items-center justify-between">
                        <span class="text-3xl font-bold ${ratingColor}">${formattedRating}</span>
                        <span class="text-xs text-secondary-color uppercase">Rating</span>
                    </div>
                </div>
                <!-- Stat: Views -->
                <div class="stat-card card card-border-left border-warning">
                    <div class="flex items-center justify-between">
                        <span class="text-3xl font-bold text-warning-color">${resource.views}</span>
                        <span class="text-xs text-secondary-color uppercase">Views</span>
                    </div>
                </div>
                <!-- Stat: Uploaded -->
                <div class="stat-card card card-border-left border-success">
                    <div class="flex items-center justify-between">
                        <span class="text-base font-bold text-success-color">${resource.uploadedDate}</span>
                        <span class="text-xs text-secondary-color uppercase">Uploaded</span>
                    </div>
                </div>
            </div>

        </div>
        
        <!-- 5. Comments Section -->
        <div class="mt-8">
            <h2 class="text-2xl font-bold text-primary-color mb-4">Comments (2)</h2>
            <div class="space-y-4">
                <!-- Example Comment 1 -->
                <div class="card card-border-left border-gray-200">
                    <div class="flex items-center mb-2">
                        <img class="avatar-sm mr-3" src="https://placehold.co/32x32/1a1a1a/f9fafb?text=JS" onerror="this.onerror=null; this.src='https://placehold.co/32x32/cccccc/333333?text=JS'" alt="User 1">
                        <span class="font-semibold text-primary-color text-sm">Jane Smith</span>
                        <span class="text-xs text-secondary-color ml-3">2 hours ago</span>
                    </div>
                    <p class="text-sm text-primary-color">This is exactly what I needed for my project! Very clear and well-organized. Thank you!</p>
                </div>
                
                <!-- Example Comment 2 -->
                <div class="card card-border-left border-gray-200">
                    <div class="flex items-center mb-2">
                        <img class="avatar-sm mr-3" src="https://placehold.co/32x32/1a1a1a/f9fafb?text=AT" onerror="this.onerror=null; this.src='https://placehold.co/32x32/cccccc/333333?text=AT'" alt="User 2">
                        <span class="font-semibold text-primary-color text-sm">Alex Torres</span>
                        <span class="text-xs text-secondary-color ml-3">1 day ago</span>
                    </div>
                    <p class="text-sm text-primary-color">I found a small typo on page 5, but otherwise, fantastic resource!</p>
                </div>
                
                <!-- Comment Input Area -->
                <div class="pt-4">
                    <textarea class="comment-textarea" rows="3" placeholder="Add your comment..."></textarea>
                    <button class="mt-2 btn-primary">Post Comment</button>
                </div>
            </div>
        </div>
    `;
}

// Data structure to hold the content for each navigation page
const pageContent = {
    'Resources': {
        title: 'Detailed Resource View',
        subtitle: 'A closer look at a saved document, including its metrics and action options.',
        contentHtml: ResourceDetailView({
            title: 'Testing Documentation Guide',
            description: 'A comprehensive guide to testing methodologies and writing clear documentation.',
            type: 'DOCX',
            downloads: 4,
            rating: 4.5,
            views: 31,
            uploadedDate: 'Nov 30, 2025',
            likes: 12,
            uploader: {
                name: 'Raphael Cambal',
                avatarUrl: 'https://placehold.co/40x40/22d3ee/1a1a1a?text=RC' 
            }
        })
    },
    'Flashcards': {
        title: 'Flashcards Decks',
        subtitle: 'Practice key concepts and definitions with your customized flashcard decks.',
        contentHtml: `
            <div class="card card-border-left link-color border-opacity-70 text-secondary-color text-base">
                <h3 class="text-2xl font-bold text-primary-color mb-4">Start Learning</h3>
                <p class="mb-6 text-sm">This is where your list of flashcard decks would be displayed. Select a topic to begin practicing.</p>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                        <p class="font-semibold link-color text-base">SQL Basics</p>
                        <p class="text-sm text-secondary-color">20 cards</p>
                    </div>
                    <div class="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                        <p class="font-semibold link-color text-base">Tailwind CSS Classes</p>
                        <p class="text-sm text-secondary-color">35 cards</p>
                    </div>
                    <div class="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                        <p class="font-semibold link-color text-base">Project Management Terms</p>
                        <p class="text-sm text-secondary-color">12 cards</p>
                    </div>
                </div>
            </div>
        `
    },
    'Quizzes': {
        title: 'Quizzes & Assessments',
        subtitle: 'Test your knowledge and track your progress across different subjects.',
        contentHtml: `
            <div class="card card-border-left border-success text-secondary-color text-base">
                <h3 class="text-2xl font-bold text-primary-color mb-4">Available Quizzes</h3>
                <p class="mb-6 text-sm">Click on a quiz to start the timer!</p>
                <div class="space-y-3">
                    <a href="#" class="flex justify-between items-center p-4 border border-gray-200 rounded-lg bg-green-50 hover:bg-green-100 transition">
                        <span class="font-medium text-success-color text-base">Web Development Fundamentals</span>
                        <span class="text-sm text-secondary-color">20 Questions</span>
                    </a>
                    <a href="#" class="flex justify-between items-center p-4 border border-gray-200 rounded-lg bg-green-50 hover:bg-green-100 transition">
                        <span class="font-medium text-success-color text-base">Cloud Computing 101</span>
                        <span class="text-sm text-secondary-color">15 Questions</span>
                    </a>
                </div>
            </div>
        `
    },
    'Bookmarks': {
        title: 'My Bookmarks',
        subtitle: 'Quick access to the most important resources you have saved.',
        contentHtml: `
            <div class="card card-border-left border-warning text-secondary-color text-base">
                <h3 class="text-2xl font-bold text-primary-color mb-4">Saved Content</h3>
                <p class="mb-6 text-sm">These are the pages and cards you've bookmarked for later review.</p>
                <ul class="space-y-3">
                    <li class="p-3 border-b border-gray-100 flex justify-between items-center">
                        <span class="font-medium text-primary-color text-base">The Ultimate Python Guide</span>
                        <a href="#" class="text-sm text-warning-color hover:underline">Go to Link</a>
                    </li>
                    <li class="p-3 border-b border-gray-100 flex justify-between items-center">
                        <span class="font-medium text-primary-color text-base">Testing Checklist for APIs</span>
                        <a href="#" class="text-sm text-warning-color hover:underline">Go to Link</a>
                    </li>
                    <li class="p-3 flex justify-between items-center">
                        <span class="font-medium text-primary-color text-base">Design Patterns in Java</span>
                        <a href="#" class="text-sm text-warning-color hover:underline">Go to Link</a>
                    </li>
                </ul>
            </div>
        `
    }
};

/**
 * Handles the navigation logic by updating the UI with the selected page content.
 * @param {string} pageName - The key name of the page to navigate to (e.g., 'Resources').
 * @param {HTMLElement} target - The anchor element that was clicked.
 */
function navigateTo(pageName, target) {
    // 1. Update Document Title
    document.getElementById('doc-title').textContent = `Learning Hub: ${pageName}`;

    // 2. Update Active Link State (Sidebar)
    document.querySelectorAll('.nav-link').forEach(link => {
        // Remove active classes
        link.classList.remove('nav-link-active');
        // Add inactive classes
        link.classList.add('nav-link-inactive');
    });
    
    // Set active classes on the clicked element
    target.classList.remove('nav-link-inactive');
    target.classList.add('nav-link-active');

    // 3. Update Main Content
    const content = pageContent[pageName];
    if (!content) return; // Guard clause if content is missing

    document.getElementById('main-title').textContent = content.title;
    document.getElementById('main-subtitle').textContent = content.subtitle;
    document.getElementById('main-content-area').innerHTML = content.contentHtml;
}

// Initialize: Load the Resources content when the page loads
window.onload = () => {
    const resourcesLink = document.querySelector('[data-page="Resources"]');
    if (resourcesLink) {
        navigateTo('Resources', resourcesLink);
    }
};
