/**
 * Deck Detail Page Functionality
 * Handles empty deck warning toast and delete modals
 */

document.addEventListener('DOMContentLoaded', function() {
    // Empty deck study button
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

    // Delete deck button
    const deleteDeckBtn = document.querySelector('.delete-deck-btn');
    if (deleteDeckBtn) {
        deleteDeckBtn.addEventListener('click', function() {
            const deckId = this.dataset.deckId;
            const deckTitle = this.dataset.deckTitle;
            const deleteUrl = this.dataset.deleteUrl;
            showDeleteModal(deckId, deckTitle, deleteUrl);
        });
    }

    // Delete comment buttons
    const deleteCommentBtns = document.querySelectorAll('.delete-comment-btn');
    deleteCommentBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const commentId = this.dataset.commentId;
            const deleteUrl = this.dataset.deleteUrl;
            showDeleteModal(commentId, 'this comment', deleteUrl);
        });
    });

    // Delete card buttons
    const deleteCardBtns = document.querySelectorAll('.delete-card-btn');
    deleteCardBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const cardId = this.dataset.cardId;
            const cardTitle = this.dataset.cardTitle;
            const deleteUrl = this.dataset.deleteUrl;
            showDeleteModal(cardId, `Card: ${cardTitle}`, deleteUrl);
        });
    });
});
