// ChatGPT-Style Sidebar v1.0
document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const sidebarLogo = document.querySelector('.sidebar-logo');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    
    // Function to update body class for content shifting
    function updateBodyClass(isExpanded) {
        if (isExpanded) {
            document.body.classList.add('sidebar-expanded');
        } else {
            document.body.classList.remove('sidebar-expanded');
        }
    }
    
    // Restore saved state on desktop
    if (window.innerWidth > 1024) {
        const isExpanded = localStorage.getItem('sidebarExpanded') === 'true';
        if (isExpanded) {
            sidebar.classList.add('expanded');
            updateBodyClass(true);
        }
    }
    
    // Toggle sidebar on logo click (when collapsed)
    if (sidebarLogo) {
        sidebarLogo.addEventListener('click', function() {
            if (!sidebar.classList.contains('expanded')) {
                sidebar.classList.add('expanded');
                updateBodyClass(true);
                if (window.innerWidth > 1024) {
                    localStorage.setItem('sidebarExpanded', 'true');
                } else {
                    sidebarOverlay.classList.add('active');
                }
            }
        });
    }
    
    // Toggle button click (when expanded)
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.remove('expanded');
            updateBodyClass(false);
            sidebarOverlay.classList.remove('active');
            if (window.innerWidth > 1024) {
                localStorage.setItem('sidebarExpanded', 'false');
            }
        });
    }
    
    // Overlay click (mobile)
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function() {
            sidebar.classList.remove('expanded');
            updateBodyClass(false);
            sidebarOverlay.classList.remove('active');
        });
    }
    
    // Handle window resize
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            if (window.innerWidth > 1024) {
                sidebarOverlay.classList.remove('active');
                const isExpanded = localStorage.getItem('sidebarExpanded') === 'true';
                if (isExpanded) {
                    sidebar.classList.add('expanded');
                    updateBodyClass(true);
                } else {
                    sidebar.classList.remove('expanded');
                    updateBodyClass(false);
                }
            } else {
                sidebar.classList.remove('expanded');
                updateBodyClass(false);
                sidebarOverlay.classList.remove('active');
            }
        }, 250);
    });
    
    // Close on nav link click (mobile) and preserve state on desktop
    const navLinks = document.querySelectorAll('.sidebar .nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth <= 1024) {
                sidebar.classList.remove('expanded');
                updateBodyClass(false);
                sidebarOverlay.classList.remove('active');
            }
            // Don't modify sidebar state on desktop - let it persist
        });
    });

    // Account menu toggle
    const accountToggle = document.getElementById('accountMenuToggle');
    const accountMenu = document.getElementById('accountMenu');
    if (accountToggle && accountMenu) {
        function closeAccountMenu() {
            accountMenu.classList.remove('open');
            accountToggle.setAttribute('aria-expanded', 'false');
        }
        accountToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            const isOpen = accountMenu.classList.toggle('open');
            accountToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        });
        document.addEventListener('click', function(e) {
            if (!accountMenu.contains(e.target) && !accountToggle.contains(e.target)) {
                closeAccountMenu();
            }
        });
        window.addEventListener('resize', closeAccountMenu);
    }
});