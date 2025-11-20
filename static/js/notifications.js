/**
 * Notification System
 * Handles real-time notifications display and interactions
 */

let notificationPollingInterval = null;

// Initialize notification system
function initNotificationSystem() {
    const notificationBellBtn = document.getElementById('notificationBellBtn');
    const notificationDropdown = document.getElementById('notificationDropdown');
    const markAllReadBtn = document.getElementById('markAllReadBtn');
    
    if (!notificationBellBtn) return;
    
    // Load initial unread count
    fetchUnreadCount();
    
    // Poll for updates every 30 seconds
    notificationPollingInterval = setInterval(fetchUnreadCount, 30000);
    
    // Toggle notification dropdown
    notificationBellBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        toggleNotificationDropdown();
    });
    
    // Mark all as read
    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', function(e) {
            e.preventDefault();
            markAllNotificationsAsRead();
        });
    }
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.notification-bell-wrapper')) {
            hideNotificationDropdown();
        }
    });
}

// Fetch unread notification count
async function fetchUnreadCount() {
    try {
        const response = await fetch('/api/notifications/unread-count/');
        if (!response.ok) throw new Error('Failed to fetch count');
        
        const data = await response.json();
        updateNotificationBadge(data.count);
    } catch (error) {
        console.error('Error fetching unread count:', error);
    }
}

// Update notification badge
function updateNotificationBadge(count) {
    const badge = document.getElementById('notificationBadge');
    if (!badge) return;
    
    if (count > 0) {
        badge.textContent = count > 99 ? '99+' : count;
        badge.style.display = 'flex';
    } else {
        badge.style.display = 'none';
    }
}

// Toggle notification dropdown
async function toggleNotificationDropdown() {
    const dropdown = document.getElementById('notificationDropdown');
    if (!dropdown) return;
    
    if (dropdown.style.display === 'block') {
        hideNotificationDropdown();
    } else {
        showNotificationDropdown();
        await loadNotifications();
    }
}

// Show notification dropdown
function showNotificationDropdown() {
    const dropdown = document.getElementById('notificationDropdown');
    if (dropdown) {
        dropdown.style.display = 'block';
    }
}

// Hide notification dropdown
function hideNotificationDropdown() {
    const dropdown = document.getElementById('notificationDropdown');
    if (dropdown) {
        dropdown.style.display = 'none';
    }
}

// Load notifications
async function loadNotifications() {
    const notificationLoading = document.getElementById('notificationLoading');
    const notificationEmpty = document.getElementById('notificationEmpty');
    const notificationList = document.getElementById('notificationList');
    const markAllReadBtn = document.getElementById('markAllReadBtn');
    
    // Show loading
    notificationLoading.style.display = 'flex';
    notificationEmpty.style.display = 'none';
    notificationList.innerHTML = '';
    markAllReadBtn.style.display = 'none';
    
    try {
        const response = await fetch('/api/notifications/list/');
        if (!response.ok) throw new Error('Failed to load notifications');
        
        const data = await response.json();
        notificationLoading.style.display = 'none';
        
        if (data.notifications && data.notifications.length > 0) {
            displayNotifications(data.notifications);
            
            // Show "Mark all as read" if there are unread notifications
            const hasUnread = data.notifications.some(n => !n.is_read);
            if (hasUnread) {
                markAllReadBtn.style.display = 'block';
            }
        } else {
            notificationEmpty.style.display = 'flex';
        }
        
    } catch (error) {
        console.error('Error loading notifications:', error);
        notificationLoading.style.display = 'none';
        notificationEmpty.style.display = 'flex';
        notificationEmpty.innerHTML = '<i class="fas fa-exclamation-triangle"></i><p>Failed to load notifications</p>';
    }
}

// Display notifications
function displayNotifications(notifications) {
    const notificationList = document.getElementById('notificationList');
    
    let html = '';
    
    notifications.forEach(notification => {
        const icon = getNotificationIcon(notification.type);
        const timeAgo = formatTimeAgo(notification.created_at);
        const unreadClass = notification.is_read ? '' : 'notification-item--unread';
        
        html += `
            <div class="notification-item ${unreadClass}" data-notification-id="${notification.id}" data-url="${escapeHtml(notification.url || '')}">
                <div class="notification-icon notification-icon--${notification.type}">
                    <i class="fas fa-${icon}"></i>
                </div>
                <div class="notification-content">
                    <div class="notification-message">${escapeHtml(notification.message)}</div>
                    <div class="notification-time">${timeAgo}</div>
                </div>
                ${!notification.is_read ? '<span class="notification-unread-dot"></span>' : ''}
            </div>
        `;
    });
    
    notificationList.innerHTML = html;
    
    // Add click handlers
    notificationList.querySelectorAll('.notification-item').forEach(item => {
        item.addEventListener('click', function() {
            handleNotificationClick(this);
        });
    });
}

// Get notification icon based on type
function getNotificationIcon(type) {
    const icons = {
        'new_upload': 'upload',
        'new_comment': 'comment',
        'new_rating': 'star',
        'verification_approved': 'check-circle',
        'verification_rejected': 'times-circle',
        'new_bookmark': 'bookmark',
        'quiz_attempt': 'clipboard-check'
    };
    return icons[type] || 'bell';
}

// Format time ago
function formatTimeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);
    
    const intervals = {
        year: 31536000,
        month: 2592000,
        week: 604800,
        day: 86400,
        hour: 3600,
        minute: 60
    };
    
    for (const [unit, secondsInUnit] of Object.entries(intervals)) {
        const interval = Math.floor(seconds / secondsInUnit);
        if (interval >= 1) {
            return `${interval} ${unit}${interval === 1 ? '' : 's'} ago`;
        }
    }
    
    return 'Just now';
}

// Handle notification click
async function handleNotificationClick(notificationElement) {
    const notificationId = notificationElement.dataset.notificationId;
    const url = notificationElement.dataset.url;
    
    // Mark as read
    await markNotificationAsRead(notificationId);
    
    // Navigate to URL if exists
    if (url && url !== '') {
        window.location.href = url;
    }
}

// Mark notification as read
async function markNotificationAsRead(notificationId) {
    try {
        const response = await fetch('/api/notifications/mark-read/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({ notification_id: notificationId })
        });
        
        if (response.ok) {
            // Update UI
            const notificationElement = document.querySelector(`[data-notification-id="${notificationId}"]`);
            if (notificationElement) {
                notificationElement.classList.remove('notification-item--unread');
                const dot = notificationElement.querySelector('.notification-unread-dot');
                if (dot) dot.remove();
            }
            
            // Update badge count
            fetchUnreadCount();
        }
    } catch (error) {
        console.error('Error marking notification as read:', error);
    }
}

// Mark all notifications as read
async function markAllNotificationsAsRead() {
    try {
        const response = await fetch('/api/notifications/mark-all-read/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            }
        });
        
        if (response.ok) {
            // Reload notifications
            await loadNotifications();
            
            // Update badge
            updateNotificationBadge(0);
        }
    } catch (error) {
        console.error('Error marking all as read:', error);
    }
}

// Get CSRF token
function getCsrfToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    if (token) return token.value;
    
    // Try to get from cookie
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    return '';
}

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (notificationPollingInterval) {
        clearInterval(notificationPollingInterval);
    }
});

// Initialize on page load
document.addEventListener('DOMContentLoaded', initNotificationSystem);
