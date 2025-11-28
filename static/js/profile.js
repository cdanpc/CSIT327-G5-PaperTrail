/* Profile Page JavaScript - PaperTrail */
/* Version 5.0 - Testing & Polish */

// ==================== PERFORMANCE OPTIMIZATION (Phase 9) ====================
// Debounce function for performance
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ==================== PHOTO UPLOAD ====================
document.addEventListener('DOMContentLoaded', function() {
    const photoUpload = document.getElementById('photoUpload');
    
    if (photoUpload) {
        photoUpload.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Validate file size (5MB max)
                if (file.size > 5 * 1024 * 1024) {
                    alert('File size must be less than 5MB');
                    this.value = ''; // Clear the input
                    return;
                }
                
                // Validate file type
                if (!file.type.match('image.*')) {
                    alert('Please select an image file');
                    this.value = ''; // Clear the input
                    return;
                }
                
                const reader = new FileReader();
                reader.onload = function(e) {
                    const profileImage = document.getElementById('profileImage');
                    if (profileImage) {
                        profileImage.src = e.target.result;
                        profileImage.setAttribute('data-saved', 'pending');
                    }
                };
                reader.readAsDataURL(file);
                
                // Submit form to save image to database
                document.getElementById('photoUploadForm').submit();
            }
        });
    }
    
    // Initialize tab from URL hash or localStorage
    initializeActiveTab();
    
    // Initialize progress calculation on page load
    calculateProgress();
    
    // Update tab completion badges
    updateTabCompletionBadges();
});

// ==================== TAB SWITCHING ====================
function switchTab(tabName) {
    // Remove active class from all tabs and panels
    const allTabBtns = document.querySelectorAll('.profile-tab-btn');
    const allTabPanels = document.querySelectorAll('.profile-tab-panel');
    
    allTabBtns.forEach(btn => btn.classList.remove('active'));
    allTabPanels.forEach(panel => panel.classList.remove('active'));
    
    // Add active class to selected tab and panel
    const activeBtn = document.querySelector(`[data-tab="${tabName}"]`);
    const activePanel = document.getElementById(`${tabName}-tab`);
    
    if (activeBtn && activePanel) {
        activeBtn.classList.add('active');
        activePanel.classList.add('active');
        
        // Save active tab to localStorage
        localStorage.setItem('profileActiveTab', tabName);
        
        // Update URL hash (without scrolling)
        history.replaceState(null, null, `#${tabName}`);
    }
}

function initializeActiveTab() {
    // Check URL hash first, then localStorage, then default to 'personal'
    let activeTab = window.location.hash.replace('#', '');
    
    if (!activeTab || !document.getElementById(`${activeTab}-tab`)) {
        activeTab = localStorage.getItem('profileActiveTab') || 'personal';
    }
    
    // Validate tab exists
    if (!document.getElementById(`${activeTab}-tab`)) {
        activeTab = 'personal';
    }
    
    switchTab(activeTab);
}

// ==================== TAB COMPLETION BADGES ====================
function updateTabCompletionBadges() {
    const profileData = document.getElementById('profileData');
    if (!profileData) return;
    
    // Personal tab completion (firstName, lastName, personalEmail, phone)
    const hasPersonalComplete = 
        profileData.dataset.hasFirstName === 'true' &&
        profileData.dataset.hasLastName === 'true' &&
        profileData.dataset.hasPersonalEmail === 'true' &&
        profileData.dataset.hasPhone === 'true';
    
    updateTabBadge('personalTab-badge', hasPersonalComplete);
    
    // Academic tab completion (univEmail, studId, department, yearLevel)
    const hasAcademicComplete = 
        profileData.dataset.hasUnivEmail === 'true' &&
        profileData.dataset.hasStudId === 'true' &&
        profileData.dataset.hasDepartment === 'true' &&
        profileData.dataset.hasYearLevel === 'true';
    
    updateTabBadge('academicTab-badge', hasAcademicComplete);
    
    // About tab completion (bio)
    const hasAboutComplete = profileData.dataset.hasBio === 'true';
    
    updateTabBadge('aboutTab-badge', hasAboutComplete);
}

function updateTabBadge(badgeId, isComplete) {
    const badge = document.getElementById(badgeId);
    if (!badge) return;
    
    const icon = badge.querySelector('i');
    if (!icon) return;
    
    if (isComplete) {
        icon.className = 'fas fa-check-circle';
    } else {
        icon.className = 'far fa-circle';
    }
}

// ==================== EDIT MODE TOGGLE ====================
function toggleEditMode(cardId) {
    const displayDiv = document.getElementById(cardId + '-display');
    const editDiv = document.getElementById(cardId + '-edit');
    
    if (displayDiv && editDiv) {
        if (editDiv.classList.contains('active')) {
            // Switch to display mode
            editDiv.classList.remove('active');
            if (cardId === 'bioInfo') {
                displayDiv.style.display = 'block';
            } else {
                displayDiv.style.display = 'grid';
            }
        } else {
            // Switch to edit mode
            displayDiv.style.display = 'none';
            editDiv.classList.add('active');
        }
    }
}

// ==================== PROGRESS CALCULATION ====================
function calculateProgress() {
    let completed = 0;
    const total = 4;
    const circumference = 2 * Math.PI * 60; // radius = 60

    // Get user data from data attributes
    const profileData = document.getElementById('profileData');
    if (!profileData) {
        console.warn('Profile data not found');
        return;
    }

    const hasPhoto = profileData.dataset.hasPhoto === 'true';
    const hasPersonalInfo = profileData.dataset.hasPersonalInfo === 'true';
    const hasUnivEmail = profileData.dataset.hasUnivEmail === 'true';
    const hasBio = profileData.dataset.hasBio === 'true';

    // Check photo
    if (hasPhoto) {
        completed++;
        updateChecklistItem('checkPhoto', true);
    } else {
        updateChecklistItem('checkPhoto', false);
    }

    // Check personal info
    if (hasPersonalInfo) {
        completed++;
        updateChecklistItem('checkPersonal', true);
    } else {
        updateChecklistItem('checkPersonal', false);
    }

    // Check university email
    if (hasUnivEmail) {
        completed++;
        updateChecklistItem('checkUniversity', true);
    } else {
        updateChecklistItem('checkUniversity', false);
    }

    // Check bio
    if (hasBio) {
        completed++;
        updateChecklistItem('checkBio', true);
    } else {
        updateChecklistItem('checkBio', false);
    }

    // Calculate percentage
    const percentage = Math.round((completed / total) * 100);
    const percentageElement = document.getElementById('progressPercentage');
    if (percentageElement) {
        percentageElement.textContent = percentage + '%';
    }

    // Animate SVG ring
    const offset = circumference - (percentage / 100) * circumference;
    const ringFill = document.getElementById('progressRingFill');
    if (ringFill) {
        ringFill.style.strokeDashoffset = offset;
    }
    
    // Update motivational message
    updateMotivationalMessage(percentage);
    
    // Show unlock preview at 75%+
    const unlockPreview = document.getElementById('unlockPreview');
    if (unlockPreview) {
        if (percentage >= 75 && percentage < 100) {
            unlockPreview.style.display = 'block';
        } else {
            unlockPreview.style.display = 'none';
        }
    }
    
    // Trigger celebration at 100%
    if (percentage === 100) {
        const celebratedFlag = localStorage.getItem('profileCelebrated');
        if (!celebratedFlag) {
            setTimeout(() => {
                triggerCelebration();
                localStorage.setItem('profileCelebrated', 'true');
            }, 500);
        }
    }
}

// ==================== MOTIVATIONAL MESSAGE ====================
function updateMotivationalMessage(percentage) {
    const messageElement = document.querySelector('.message-text');
    if (!messageElement) return;
    
    let message = '';
    if (percentage === 0) {
        message = '🚀 Just getting started! Complete your profile to unlock special features.';
    } else if (percentage < 50) {
        message = '📝 You\'re making progress! Keep going to unlock rewards.';
    } else if (percentage < 75) {
        message = '💪 Halfway there! Your profile is taking shape.';
    } else if (percentage < 100) {
        message = '🎯 Almost done! Just a few more steps to unlock everything.';
    } else {
        message = '🎉 Perfect! Your profile is complete. Enjoy your unlocked features!';
    }
    
    messageElement.textContent = message;
}

// ==================== CELEBRATION FUNCTIONS ====================
function triggerCelebration() {
    // Show celebration overlay on progress ring
    const celebrationOverlay = document.getElementById('celebrationOverlay');
    if (celebrationOverlay) {
        celebrationOverlay.classList.add('active');
    }
    
    // Wait 2 seconds, then show modal
    setTimeout(() => {
        showCelebrationModal();
    }, 2000);
}

function showCelebrationModal() {
    const modal = new bootstrap.Modal(document.getElementById('celebrationModal'));
    modal.show();
    
    // Create confetti
    createConfetti();
}

function createConfetti() {
    const container = document.getElementById('confettiContainer');
    if (!container) return;
    
    const colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#fa709a', '#fee140'];
    const confettiCount = 50;
    
    for (let i = 0; i < confettiCount; i++) {
        const confetti = document.createElement('div');
        confetti.style.position = 'absolute';
        confetti.style.width = Math.random() * 10 + 5 + 'px';
        confetti.style.height = confetti.style.width;
        confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.left = Math.random() * 100 + '%';
        confetti.style.top = '-10px';
        confetti.style.borderRadius = Math.random() > 0.5 ? '50%' : '0';
        confetti.style.opacity = Math.random() * 0.5 + 0.5;
        confetti.style.animation = `fall ${Math.random() * 3 + 2}s linear forwards`;
        confetti.style.animationDelay = Math.random() * 0.5 + 's';
        
        container.appendChild(confetti);
        
        // Remove confetti after animation
        setTimeout(() => {
            confetti.remove();
        }, 5000);
    }
}

// ==================== COMPLETION INFO MODAL ====================
function showCompletionModal() {
    const modal = new bootstrap.Modal(document.getElementById('completionInfoModal'));
    modal.show();
}

// ==================== UPDATE CHECKLIST ITEM ====================
function updateChecklistItem(itemId, isCompleted) {
    const item = document.getElementById(itemId);
    if (!item) return;
    
    if (isCompleted) {
        item.classList.add('completed');
        const icon = item.querySelector('.checklist-icon i');
        if (icon) {
            icon.className = 'fas fa-check-circle';
        }
    } else {
        item.classList.remove('completed');
        const icon = item.querySelector('.checklist-icon i');
        if (icon) {
            icon.className = 'far fa-circle';
        }
    }
}

// ==================== HELPER FUNCTIONS ====================
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/* ==================== DOCUMENTATION (Phase 9) ====================
 * Profile Page Interactive Features
 * 
 * Key Features:
 * 1. Photo Upload: File validation (5MB, image types only), preview
 * 2. Tab Switching: Personal/Academic/About tabs with localStorage persistence
 * 3. Profile Completion: Real-time progress tracking (0-100%)
 * 4. Motivational Messages: Dynamic messages based on completion percentage
 * 5. Unlock Preview: Shows at 75%+ completion
 * 6. Celebration: Confetti animation and modal at 100% completion (once per session)
 * 7. Tab Completion Badges: Check/circle icons per tab
 * 8. Edit Mode: Toggle between display and edit modes
 * 
 * LocalStorage Keys:
 * - profileActiveTab: Currently active tab name
 * - profileCelebrated: Flag to prevent duplicate celebration (reset on page reload)
 * 
 * Dependencies:
 * - Bootstrap 5.3.0 (for modals)
 * - Font Awesome 6.4.0 (for icons)
 * 
 * Browser Support:
 * - Chrome/Edge: ✓ Full support
 * - Firefox: ✓ Full support
 * - Safari: ✓ Full support
 * - IE11: ✗ Not supported (uses modern JS features)
 */
