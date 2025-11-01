# Reusable Sidebar Documentation

## Overview
This sidebar can be used across multiple pages in the PaperTrail application. It features:
- Collapsible sidebar (desktop)
- Mobile-responsive overlay menu
- Active state indicators
- Local storage for user preferences
- Smooth animations

## Files Created
1. `templates/includes/sidebar.html` - Sidebar HTML template
2. `static/css/sidebar.css` - Sidebar styles
3. `static/js/sidebar.js` - Sidebar JavaScript functionality

## How to Use

### 1. Include in Your Template

Add these lines to any page where you want the sidebar:

```html
{% load static %}
<!DOCTYPE html>
<html>
<head>
    <!-- Your other head content -->
    <link rel="stylesheet" href="{% static 'css/sidebar.css' %}?v=1.0">
</head>
<body>
    <!-- Include the sidebar -->
    {% include 'includes/sidebar.html' %}
    
    <!-- Main content wrapper (IMPORTANT!) -->
    <div class="main-content-wrapper">
        <div class="dashboard-main">
            <div class="container-fluid">
                <!-- Your page content here -->
            </div>
        </div>
    </div>

    <!-- Include sidebar JavaScript before closing body tag -->
    <script src="{% static 'js/sidebar.js' %}?v=1.0"></script>
</body>
</html>
```

### 2. Add Mobile Menu Button (for navbar)

For mobile users, add this button to your navbar:

```html
<button class="mobile-menu-btn">
    <i class="fas fa-bars"></i>
</button>
```

### 3. Page Structure

The sidebar automatically adjusts the main content margin. Use this structure:

```html
<body>
    {% include 'includes/sidebar.html' %}
    
    <div class="main-content-wrapper">
        <!-- This div gets automatic margin-left adjustment -->
        <!-- Your content here -->
    </div>
</body>
```

## Features

### Desktop Features
- **Toggle Collapse**: Click the arrow button in sidebar header to collapse/expand
- **Persistent State**: Collapse state is saved in localStorage
- **Tooltips**: Collapsed sidebar shows tooltips on hover
- **Active Highlighting**: Current page is automatically highlighted

### Mobile Features (≤1024px)
- **Overlay Menu**: Sidebar slides in from left with dark overlay
- **Touch-Friendly**: Large touch targets for mobile users
- **Auto-Close**: Closes when clicking links or overlay

## Customization

### Update Navigation Links

Edit `templates/includes/sidebar.html`:

```html
<li class="nav-item">
    <a href="{% url 'your_url_name' %}" class="nav-link">
        <i class="fas fa-your-icon"></i>
        <span class="nav-text">Your Page</span>
    </a>
</li>
```

### Change Colors

Edit `static/css/sidebar.css`:

```css
:root {
    --sidebar-bg: #1e293b;          /* Background color */
    --sidebar-hover: #334155;        /* Hover state */
    --sidebar-active: #667eea;       /* Active/selected */
    --sidebar-text: #cbd5e1;         /* Text color */
    --sidebar-text-active: #ffffff;  /* Active text */
}
```

### Adjust Width

```css
:root {
    --sidebar-width: 280px;              /* Expanded width */
    --sidebar-collapsed-width: 80px;     /* Collapsed width */
}
```

## Pages Currently Using Sidebar

To add the sidebar to existing pages:

1. **Student Dashboard** - Update `templates/accounts/student_dashboard.html`
2. **Profile Page** - Update `templates/accounts/profile.html`
3. **Settings Page** - Update `templates/accounts/settings.html`
4. **Resources** - Already included in base template

## Troubleshooting

### Sidebar not showing
- Check that sidebar.html is included
- Verify sidebar.css is loaded
- Ensure sidebar.js is included at end of body

### Content overlapping sidebar
- Make sure your content is wrapped in `<div class="main-content-wrapper">`
- Check that sidebar.css is loaded before your custom CSS

### Mobile menu not working
- Add the mobile menu button to your navbar
- Ensure it has class `mobile-menu-btn`
- Check that sidebar.js is loaded

### Active state not working
- URL names in sidebar.html must match your urls.py
- Check Django's `{% url %}` tags are correct
- Verify JavaScript is running (check console)

## Browser Support
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Notes
- Sidebar state persists across page loads
- Works with Django's template system
- Fully responsive design
- Accessibility-friendly (keyboard navigation)
