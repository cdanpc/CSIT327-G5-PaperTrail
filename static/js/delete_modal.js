/**
 * Delete Confirmation Modal Handler
 * Manages the unified delete confirmation modal across the application
 */

/**
 * Shows the delete confirmation modal
 * @param {string} itemId - The ID of the item to delete
 * @param {string} itemName - The name of the item to display in the message
 * @param {string} deleteUrl - The URL to POST the delete request to
 */
function showDeleteModal(itemId, itemName, deleteUrl) {
    const modal = document.getElementById('deleteModal');
    const form = document.getElementById('deleteForm');
    const message = document.getElementById('deleteModalMessage');
    
    if (!modal || !form || !message) {
        console.error('Delete modal elements not found');
        return;
    }
    
    // Update the form action
    form.action = deleteUrl;
    
    // Update the message with the item name
    message.innerHTML = `Are you sure you want to delete <strong>${escapeHtml(itemName)}</strong>? This action cannot be undone.`;
    
    // Show the modal
    modal.style.display = 'flex';
    
    // Prevent body scroll when modal is open
    document.body.style.overflow = 'hidden';
}

/**
 * Closes the delete confirmation modal
 */
function closeDeleteModal() {
    const modal = document.getElementById('deleteModal');
    
    if (!modal) {
        console.error('Delete modal not found');
        return;
    }
    
    // Hide the modal
    modal.style.display = 'none';
    
    // Restore body scroll
    document.body.style.overflow = '';
}

/**
 * Escapes HTML to prevent XSS attacks
 * @param {string} text - The text to escape
 * @returns {string} - The escaped text
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Close modal when clicking outside the modal content
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('deleteModal');
    
    if (modal) {
        modal.addEventListener('click', function(event) {
            if (event.target === modal) {
                closeDeleteModal();
            }
        });
    }
    
    // Close modal on ESC key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            closeDeleteModal();
        }
    });
});
