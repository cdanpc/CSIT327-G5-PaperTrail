/**
 * Deck Detail Page Functionality
 * Handles empty deck warning toast and related interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    const emptyDeckBtn = document.getElementById('emptyDeckStudyBtn');
    if (emptyDeckBtn) {
        emptyDeckBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const toastEl = document.getElementById('emptyDeckToast');
            const toast = new bootstrap.Toast(toastEl, {
                autohide: true,
                delay: 4000
            });
            toast.show();
        });
    }
});
