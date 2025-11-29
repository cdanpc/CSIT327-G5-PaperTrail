/**
 * Profile Stats Component Script
 * Applies data attributes to inline CSS for template variables
 */

document.addEventListener('DOMContentLoaded', function() {
    // Apply width from data attribute to progress bar
    const progressBars = document.querySelectorAll('.study-time-progress-bar[data-width]');
    progressBars.forEach(bar => {
        const width = bar.getAttribute('data-width');
        bar.style.width = width + '%';
    });
});
