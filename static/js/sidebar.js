/* ============================================
   UNIFIED SIDEBAR JAVASCRIPT
   Version: 2.0 - Redesigned for System Consistency
   ============================================ */

document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const sidebarOverlay = document.querySelector('.sidebar-overlay');
    
    // Add hover listeners for sidebar expansion (desktop only)
    if (sidebar) {
        sidebar.addEventListener('mouseenter', function() {
            if (window.innerWidth > 768) {
                document.body.classList.add('sidebar-expanded');
            }
        });
        
        sidebar.addEventListener('mouseleave', function() {
            if (window.innerWidth > 768 && !sidebar.classList.contains('locked')) {
                document.body.classList.remove('sidebar-expanded');
            }
        });
    }
    
    // Toggle sidebar lock state (desktop)
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Only toggle lock on desktop
            if (window.innerWidth > 768) {
                sidebar.classList.toggle('locked');
                
                // Save state to localStorage
                const isLocked = sidebar.classList.contains('locked');
                localStorage.setItem('sidebarLocked', isLocked);
                
                // Keep body class if locked
                if (isLocked) {
                    document.body.classList.add('sidebar-expanded');
                } else {
                    document.body.classList.remove('sidebar-expanded');
                }
            }
        });
    }
    
    // Mobile menu toggle
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function() {
            sidebar.classList.toggle('mobile-open');
            sidebarOverlay.classList.toggle('active');
            document.body.style.overflow = sidebar.classList.contains('mobile-open') ? 'hidden' : '';
        });
    }
    
    // Close sidebar when clicking overlay
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function() {
            sidebar.classList.remove('mobile-open');
            sidebarOverlay.classList.remove('active');
            document.body.style.overflow = '';
        });
    }
    
    // Close sidebar on mobile when clicking a link
    const sidebarLinks = document.querySelectorAll('.sidebar-item, .sidebar-link');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth <= 768) {
                sidebar.classList.remove('mobile-open');
                if (sidebarOverlay) {
                    sidebarOverlay.classList.remove('active');
                }
                document.body.style.overflow = '';
            }
        });
    });
    
    // Restore sidebar state from localStorage (desktop only)
    if (window.innerWidth > 768) {
        const sidebarLocked = localStorage.getItem('sidebarLocked');
        if (sidebarLocked === 'true') {
            sidebar.classList.add('locked');
            document.body.classList.add('sidebar-expanded');
        }
    }
    
    // Handle window resize
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            // Remove mobile classes on desktop
            if (window.innerWidth > 768) {
                sidebar.classList.remove('mobile-open');
                if (sidebarOverlay) {
                    sidebarOverlay.classList.remove('active');
                }
                document.body.style.overflow = '';
                
                // Restore locked state on desktop
                const sidebarLocked = localStorage.getItem('sidebarLocked');
                if (sidebarLocked === 'true') {
                    sidebar.classList.add('locked');
                    document.body.classList.add('sidebar-expanded');
                } else {
                    document.body.classList.remove('sidebar-expanded');
                }
            } else {
                // Remove locked state and expanded body class on mobile
                sidebar.classList.remove('locked');
                document.body.classList.remove('sidebar-expanded');
            }
        }, 250);
    });
    
    // Set active state based on current URL
    const currentPath = window.location.pathname;
    sidebarLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath.includes(href) && href !== '#') {
            // Remove active from all links
            sidebarLinks.forEach(l => l.classList.remove('active'));
            // Add active to current link
            link.classList.add('active');
        }
    });
    
    // Handle coming soon features
    const comingSoonLinks = document.querySelectorAll('[data-feature="coming-soon"]');
    comingSoonLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            showComingSoonToast();
        });
    });
});

// Toast notification for coming soon features
function showComingSoonToast() {
    // Check if toast exists, if not create it
    let toast = document.querySelector('.coming-soon-toast');
    
    if (!toast) {
        toast = document.createElement('div');
        toast.className = 'coming-soon-toast';
        toast.innerHTML = `
            <i class="fas fa-info-circle"></i>
            <span>This feature is coming soon!</span>
        `;
        document.body.appendChild(toast);
        
        // Add styles if not already added
        if (!document.getElementById('toast-styles')) {
            const style = document.createElement('style');
            style.id = 'toast-styles';
            style.textContent = `
                .coming-soon-toast {
                    position: fixed;
                    bottom: 2rem;
                    right: 2rem;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 1rem 1.5rem;
                    border-radius: 0.75rem;
                    box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
                    display: flex;
                    align-items: center;
                    gap: 0.75rem;
                    font-weight: 500;
                    z-index: 10000;
                    animation: slideInUp 0.3s ease, fadeOut 0.3s ease 2.7s;
                    pointer-events: none;
                }
                
                .coming-soon-toast i {
                    font-size: 1.25rem;
                }
                
                @keyframes slideInUp {
                    from {
                        transform: translateY(100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateY(0);
                        opacity: 1;
                    }
                }
                
                @keyframes fadeOut {
                    from {
                        opacity: 1;
                    }
                    to {
                        opacity: 0;
                    }
                }
                
                @media (max-width: 768px) {
                    .coming-soon-toast {
                        bottom: 1rem;
                        right: 1rem;
                        left: 1rem;
                        justify-content: center;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    // Show toast
    toast.style.display = 'flex';
    
    // Hide after 3 seconds
    setTimeout(() => {
        toast.style.display = 'none';
    }, 3000);
}
