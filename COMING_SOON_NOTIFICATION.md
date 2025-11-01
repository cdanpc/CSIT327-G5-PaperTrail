# Coming Soon Notification Component

## Overview
A beautiful, reusable toast notification component that informs users about features currently under development.

## Files
1. **`static/css/coming-soon-notification.css`** - Notification styles with animations
2. **`static/js/coming-soon-notification.js`** - Notification functionality

## Features
- ✅ Beautiful gradient design (purple theme)
- ✅ Smooth slide-in animation
- ✅ Auto-dismiss after 3 seconds
- ✅ Manual close button
- ✅ Custom messages per feature
- ✅ Mobile responsive
- ✅ Accessible (keyboard friendly)

## Usage

### 1. Include in Your Template

Add to your HTML `<head>`:
```html
<link rel="stylesheet" href="{% static 'css/coming-soon-notification.css' %}?v=1.0">
```

Add before closing `</body>`:
```html
<script src="{% static 'js/coming-soon-notification.js' %}?v=1.0"></script>
```

### 2. Add to HTML Elements

Use the `data-coming-soon` attribute on any clickable element:

```html
<!-- Simple usage -->
<a href="#" data-coming-soon>Feature Name</a>

<!-- With custom message -->
<a href="#" 
   data-coming-soon="This awesome feature is coming in the next update!"
   data-feature-name="Flashcards">
    Flashcards
</a>
```

### 3. JavaScript Usage

You can also trigger the notification programmatically:

```javascript
// Simple usage
showComingSoon();

// With custom message
showComingSoon("Custom message here");

// With custom title and message
showComingSoon("Custom message here", "Feature Name");

// Using the class instance
window.comingSoonNotification.show("Message", "Title");
```

## Current Implementation

The notification is currently applied to these sidebar features:

### Flashcards
```html
<a href="#" 
   data-coming-soon="Flashcards feature is coming soon! Create and study flashcards from your resources." 
   data-feature-name="Flashcards">
    <i class="fas fa-layer-group"></i>
    <span>Flashcards</span>
</a>
```

### Quizzes
```html
<a href="#" 
   data-coming-soon="Quizzes feature is coming soon! Test your knowledge with interactive quizzes." 
   data-feature-name="Quizzes">
    <i class="fas fa-clipboard-check"></i>
    <span>Quizzes</span>
</a>
```

### Analytics
```html
<a href="#" 
   data-coming-soon="Analytics feature is coming soon! Track your study progress and performance." 
   data-feature-name="Analytics">
    <i class="fas fa-chart-line"></i>
    <span>Analytics</span>
</a>
```

## Customization

### Change Colors

Edit `static/css/coming-soon-notification.css`:

```css
.coming-soon-toast {
    /* Default gradient (purple) */
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Alternative styles available */
.coming-soon-toast.info {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.coming-soon-toast.warning {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.coming-soon-toast.success {
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}
```

### Adjust Auto-Dismiss Time

Edit `static/js/coming-soon-notification.js`:

```javascript
// Find this line (around line 60)
this.hideTimeout = setTimeout(() => this.hide(), 3000); // 3000ms = 3 seconds

// Change to your desired duration (in milliseconds)
this.hideTimeout = setTimeout(() => this.hide(), 5000); // 5 seconds
```

### Change Position

Edit `static/css/coming-soon-notification.css`:

```css
.coming-soon-toast {
    position: fixed;
    bottom: 2rem;  /* Distance from bottom */
    right: 2rem;   /* Distance from right */
    
    /* Alternative positions: */
    /* top: 2rem; right: 2rem; */  /* Top-right */
    /* top: 2rem; left: 2rem; */   /* Top-left */
    /* bottom: 2rem; left: 2rem; */ /* Bottom-left */
}
```

## Adding to New Features

To add the notification to any new feature:

1. Add the data attributes to your HTML element:
```html
<button data-coming-soon="Your custom message" data-feature-name="Feature">
    Click Me
</button>
```

2. Or call it via JavaScript:
```javascript
document.getElementById('myButton').addEventListener('click', function(e) {
    e.preventDefault();
    showComingSoon("Feature coming soon!", "Feature Name");
});
```

## Animation Details

### Slide In (Entry)
- Duration: 0.3s
- Effect: Slides up from bottom with fade-in
- Easing: ease

### Fade Out (Exit)
- Duration: 0.3s  
- Effect: Fades out with slight downward movement
- Easing: ease

### Trigger
- Animation plays on show
- Auto-dismiss after 3 seconds
- Manual close via X button

## Browser Support
- ✅ Chrome (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Edge (latest)
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## Accessibility Features
- Proper ARIA labels
- Keyboard accessible close button
- Screen reader friendly
- Focus management
- ESC key to dismiss (can be added if needed)

## Mobile Responsive
- Full width on mobile (≤768px)
- Maintains padding on sides
- Touch-friendly close button
- Proper spacing from screen edges

## Tips

1. **Keep messages concise** - Users should understand quickly
2. **Be specific** - Tell users when or what to expect
3. **Positive tone** - "Coming soon" is better than "Not available"
4. **Use feature names** - Helps users identify what's being built

## Example Messages

Good examples:
- ✅ "Flashcards feature is coming soon! Create and study flashcards from your resources."
- ✅ "Analytics dashboard launches next month. Track your study progress and performance."
- ✅ "Quiz feature in development! Test your knowledge with interactive quizzes."

Avoid:
- ❌ "Not available"
- ❌ "This doesn't work yet"
- ❌ "Coming soon" (too vague)

## Future Enhancements

Possible improvements:
- [ ] Progress indicator for features
- [ ] Notification queue system
- [ ] Different notification types (success, error, warning)
- [ ] Notification history
- [ ] Customizable icons per notification
- [ ] Sound effects (optional)
- [ ] Multiple notifications support

## Troubleshooting

### Notification not showing
1. Check that CSS and JS files are loaded
2. Verify data-coming-soon attribute is present
3. Check browser console for errors
4. Ensure element is clickable (not disabled)

### Notification shows but no animation
1. Check that CSS animations are enabled in browser
2. Verify CSS file is loaded correctly
3. Check for CSS conflicts

### Multiple clicks cause issues
- The component handles this automatically
- Only one notification shows at a time
- New clicks reset the auto-dismiss timer

### Notification appears behind other elements
- Increase z-index in CSS:
  ```css
  .coming-soon-toast {
      z-index: 10000; /* Increase if needed */
  }
  ```
