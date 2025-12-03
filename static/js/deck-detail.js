/**
 * Deck Detail Page Functionality
 * Handles empty deck warning toast, delete modals, and inline editing
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get CSRF token
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
    const csrftoken = getCookie('csrftoken');

    // Empty deck study button
    const emptyDeckBtn = document.getElementById('emptyDeckStudyBtn');
    if (emptyDeckBtn) {
        emptyDeckBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const toastEl = document.getElementById('emptyDeckToast');
            if (toastEl) {
                const toast = new bootstrap.Toast(toastEl, {
                    autohide: true,
                    delay: 4000
                });
                toast.show();
            }
        });
    }

    // === INLINE DECK TITLE EDITING ===
    const editDeckTitleBtn = document.getElementById('editDeckTitleBtn');
    const deckTitleEditContainer = document.getElementById('deckTitleEditContainer');
    const deckActions = document.getElementById('deckActions');
    const deckTitleDisplay = document.getElementById('deckTitleDisplay');
    const saveDeckTitleBtn = document.getElementById('saveDeckTitleBtn');
    const cancelDeckTitleBtn = document.getElementById('cancelDeckTitleBtn');
    const deckTitleInput = document.getElementById('deckTitleInput');

    if (editDeckTitleBtn && deckTitleEditContainer && deckActions && deckTitleDisplay) {
        // Show Edit Form
        editDeckTitleBtn.addEventListener('click', function() {
            deckTitleDisplay.classList.add('d-none');
            deckActions.classList.add('d-none');
            deckTitleEditContainer.classList.remove('d-none');
            deckTitleInput.focus();
        });

        // Cancel Edit
        cancelDeckTitleBtn.addEventListener('click', function() {
            deckTitleEditContainer.classList.add('d-none');
            deckTitleDisplay.classList.remove('d-none');
            deckActions.classList.remove('d-none');
            deckTitleInput.value = deckTitleDisplay.textContent.trim(); // Reset input
        });

        // Save Edit
        saveDeckTitleBtn.addEventListener('click', function() {
            const newTitle = deckTitleInput.value.trim();
            const updateUrl = this.dataset.updateUrl;

            if (!newTitle) {
                alert('Title cannot be empty');
                return;
            }

            // Disable button
            this.disabled = true;

            fetch(updateUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ title: newTitle })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    deckTitleDisplay.textContent = data.title;
                    deckTitleEditContainer.classList.add('d-none');
                    deckTitleDisplay.classList.remove('d-none');
                    deckActions.classList.remove('d-none');
                } else {
                    alert(data.error || 'Error updating title');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while saving.');
            })
            .finally(() => {
                this.disabled = false;
            });
        });
    }

    // === INLINE CARD EDITING ===
    
    // Edit Card Button Click
    document.addEventListener('click', function(e) {
        if (e.target.closest('.edit-card-btn')) {
            const btn = e.target.closest('.edit-card-btn');
            const cardId = btn.dataset.cardId;
            const cardItem = document.getElementById(`card-${cardId}`);
            
            if (cardItem) {
                const viewMode = cardItem.querySelector('.card-view-mode');
                const editMode = cardItem.querySelector('.card-edit-mode');
                
                viewMode.classList.add('d-none');
                editMode.classList.remove('d-none');
            }
        }
    });

    // Cancel Card Edit
    document.addEventListener('click', function(e) {
        if (e.target.closest('.cancel-card-edit-btn')) {
            const btn = e.target.closest('.cancel-card-edit-btn');
            const cardId = btn.dataset.cardId;
            const cardItem = document.getElementById(`card-${cardId}`);
            
            if (cardItem) {
                const viewMode = cardItem.querySelector('.card-view-mode');
                const editMode = cardItem.querySelector('.card-edit-mode');
                const frontInput = editMode.querySelector('.card-front-input');
                const backInput = editMode.querySelector('.card-back-input');
                const frontContent = viewMode.querySelector('.card-front-content');
                const backContent = viewMode.querySelector('.card-back-content');
                
                // Reset inputs
                frontInput.value = frontContent.textContent.trim();
                backInput.value = backContent.textContent.trim();
                
                editMode.classList.add('d-none');
                viewMode.classList.remove('d-none');
            }
        }
    });

    // Save Card Edit
    document.addEventListener('click', function(e) {
        if (e.target.closest('.save-card-edit-btn')) {
            const btn = e.target.closest('.save-card-edit-btn');
            const cardId = btn.dataset.cardId;
            const updateUrl = btn.dataset.updateUrl;
            const cardItem = document.getElementById(`card-${cardId}`);
            
            if (cardItem) {
                const editMode = cardItem.querySelector('.card-edit-mode');
                const frontInput = editMode.querySelector('.card-front-input');
                const backInput = editMode.querySelector('.card-back-input');
                
                const frontText = frontInput.value.trim();
                const backText = backInput.value.trim();
                
                if (!frontText || !backText) {
                    alert('Front and back text cannot be empty');
                    return;
                }
                
                btn.disabled = true;
                
                fetch(updateUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken,
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify({ 
                        front_text: frontText,
                        back_text: backText
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const viewMode = cardItem.querySelector('.card-view-mode');
                        const frontContent = viewMode.querySelector('.card-front-content');
                        const backContent = viewMode.querySelector('.card-back-content');
                        
                        frontContent.textContent = data.front_text;
                        backContent.textContent = data.back_text;
                        
                        editMode.classList.add('d-none');
                        viewMode.classList.remove('d-none');
                    } else {
                        alert(data.error || 'Error updating card');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred. Please try again.');
                })
                .finally(() => {
                    btn.disabled = false;
                });
            }
        }
    });

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
