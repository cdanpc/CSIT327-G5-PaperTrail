/**
 * Forum JavaScript - Real-time interactions for discussions
 * Handles AJAX requests for topics, threads, and posts
 */

const ForumApp = {
  /**
   * Get CSRF token from cookie
   */
  getCSRFToken() {
    const name = 'csrftoken';
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
  },

  /**
   * Show error message to user
   */
  showError(container, message) {
    container.innerHTML = `
      <div class="error-message">
        <i class="fas fa-exclamation-triangle"></i>
        <p>${message}</p>
      </div>
    `;
  },

  /**
   * Format date relative to now
   */
  formatTimeAgo(isoString) {
    const date = new Date(isoString);
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

    for (const [name, secondsInInterval] of Object.entries(intervals)) {
      const interval = Math.floor(seconds / secondsInInterval);
      if (interval >= 1) {
        return `${interval} ${name}${interval !== 1 ? 's' : ''} ago`;
      }
    }
    return 'just now';
  },

  /**
   * Load all forum topics
   */
  async loadTopics() {
    const container = document.getElementById('forumTopicsGrid');
    const loading = document.getElementById('topicsLoading');

    if (!container) {
      console.error('Forum topics container not found');
      return;
    }

    console.log('Loading forum topics...');

    try {
      const response = await fetch('/forum/api/topics/');
      console.log('API Response status:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('Topics data:', data);

      // Handle authentication error
      if (!data.success && response.status === 401) {
        if (loading) loading.style.display = 'none';
        this.showError(container, 'Please log in to view forum topics.');
        if (data.redirect) {
          setTimeout(() => {
            window.location.href = data.redirect;
          }, 2000);
        }
        return;
      }

      if (data.success && Array.isArray(data.topics)) {
        if (loading) loading.style.display = 'none';
        
        if (data.topics.length === 0) {
          container.innerHTML = '<p class="no-data">No topics available yet. Contact an administrator to add topics.</p>';
          return;
        }

        container.innerHTML = data.topics.map(topic => `
          <div class="forum-topic-card" data-topic-id="${topic.id}">
            <div class="forum-topic-card__icon">
              <i class="fas fa-layer-group"></i>
            </div>
            
            <div class="forum-topic-card__content">
              <h3 class="forum-topic-card__title">${topic.name}</h3>
              <p class="forum-topic-card__description">${topic.description}</p>
              
              <div class="forum-topic-card__stats">
                <span class="forum-topic-card__stat">
                  <i class="fas fa-comments"></i>
                  <span class="thread-count">${topic.thread_count}</span>
                  ${topic.thread_count === 1 ? 'Thread' : 'Threads'}
                </span>
              </div>
            </div>
            
            <div class="forum-topic-card__action">
              <a href="/forum/topic/${topic.id}/" class="btn btn--primary">
                View Discussions <i class="fas fa-arrow-right"></i>
              </a>
            </div>
          </div>
        `).join('');
        console.log('Successfully rendered', data.topics.length, 'topics');
      } else {
        if (loading) loading.style.display = 'none';
        const errorMsg = data.error || 'Failed to load topics';
        console.error('API returned error:', data);
        this.showError(container, errorMsg);
      }
    } catch (error) {
      if (loading) loading.style.display = 'none';
      console.error('Error loading topics:', error);
      this.showError(container, `Network error: ${error.message}. Please check your connection and try again.`);
    }
  },

  /**
   * Load threads for a specific topic
   */
  async loadTopicThreads(topicId) {
    const container = document.getElementById('threadsContainer');
    const loading = document.getElementById('threadsLoading');

    if (!container) {
      console.error('Threads container not found');
      return;
    }

    console.log('Loading threads for topic:', topicId);

    try {
      const response = await fetch(`/forum/api/topic/${topicId}/threads/`);
      console.log('Threads API response status:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('Threads data:', data);

      // Handle authentication error
      if (!data.success && response.status === 401) {
        if (loading) loading.style.display = 'none';
        this.showError(container, 'Please log in to view threads.');
        if (data.redirect) {
          setTimeout(() => window.location.href = data.redirect, 2000);
        }
        return;
      }

      if (data.success && Array.isArray(data.threads)) {
        if (loading) loading.style.display = 'none';
        
        if (data.threads.length === 0) {
          container.innerHTML = '<p class="no-data">No threads yet. Be the first to start a discussion!</p>';
          return;
        }

        container.innerHTML = data.threads.map(thread => `
          <div class="forum-thread-card" data-thread-id="${thread.id}">
            <a href="/forum/thread/${thread.id}/" class="study-card">
              <div class="study-card__header">
                <h3 class="study-card__title">${thread.title}</h3>
              </div>
              
              <div class="study-card__content">
                <p class="study-card__description">${thread.content}</p>
              </div>
              
              <div class="study-card__footer">
                <div class="forum-thread-card__meta">
                  <span class="forum-thread-card__author">
                    <i class="fas fa-user"></i>
                    ${thread.starter.full_name}
                  </span>
                  <span class="forum-thread-card__date">
                    <i class="far fa-clock"></i>
                    ${this.formatTimeAgo(thread.created_at)}
                  </span>
                </div>
                
                <div class="study-card__metrics">
                  <span class="metric">
                    <i class="fas fa-comments"></i>
                    ${thread.reply_count}
                  </span>
                  <span class="metric">
                    <i class="fas fa-clock"></i>
                    ${this.formatTimeAgo(thread.last_activity_at)}
                  </span>
                </div>
              </div>
            </a>
          </div>
        `).join('');
        console.log('Successfully rendered', data.threads.length, 'threads');
      } else {
        if (loading) loading.style.display = 'none';
        const errorMsg = data.error || 'Failed to load threads';
        console.error('API returned error:', data);
        this.showError(container, errorMsg);
      }
    } catch (error) {
      if (loading) loading.style.display = 'none';
      console.error('Error loading threads:', error);
      this.showError(container, `Network error: ${error.message}. Please refresh the page.`);
    }
  },

  /**
   * Initialize new thread form
   */
  initNewThreadForm(topicId) {
    const newThreadBtn = document.getElementById('newThreadBtn');
    const newThreadForm = document.getElementById('newThreadForm');
    const cancelBtn = document.getElementById('cancelThreadBtn');
    const form = document.getElementById('createThreadForm');

    newThreadBtn.addEventListener('click', () => {
      newThreadForm.style.display = 'block';
      document.getElementById('threadTitle').focus();
    });

    cancelBtn.addEventListener('click', () => {
      newThreadForm.style.display = 'none';
      form.reset();
    });

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      await this.createThread(topicId, form);
    });
  },

  /**
   * Create a new thread
   */
  async createThread(topicId, form) {
    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;

    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating...';

    try {
      const response = await fetch('/forum/api/thread/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCSRFToken()
        },
        body: JSON.stringify({
          topic_id: topicId,
          title: formData.get('title'),
          content: formData.get('content')
        })
      });

      const data = await response.json();

      if (data.success) {
        // Redirect to the new thread
        window.location.href = `/forum/thread/${data.thread_id}/`;
      } else {
        alert('Error: ' + data.error);
      }
    } catch (error) {
      console.error('Error creating thread:', error);
      alert('An error occurred while creating the thread');
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalText;
    }
  },

  /**
   * Load posts for a thread
   */
  async loadThreadPosts(threadId) {
    const container = document.getElementById('postsContainer');
    const loading = document.getElementById('postsLoading');
    const repliesCountElem = document.getElementById('repliesCount');
    const totalRepliesCountElem = document.getElementById('totalRepliesCount');

    if (!container || !loading) {
      console.error('Required DOM elements not found');
      return;
    }

    try {
      const response = await fetch(`/forum/api/thread/${threadId}/posts/`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('Posts loaded:', data);

      // Handle authentication error
      if (!data.success && response.status === 401) {
        loading.style.display = 'none';
        this.showError(container, 'Please log in to view posts.');
        if (data.redirect) {
          setTimeout(() => window.location.href = data.redirect, 2000);
        }
        return;
      }

      if (data.success && Array.isArray(data.posts)) {
        loading.style.display = 'none';
        
        // Update counts safely
        if (repliesCountElem) repliesCountElem.textContent = data.total_replies || 0;
        if (totalRepliesCountElem) totalRepliesCountElem.textContent = data.total_replies || 0;

        if (data.posts.length === 0) {
          container.innerHTML = '<p class="no-data">No replies yet. Be the first to reply!</p>';
          return;
        }

        // Render posts (handle nesting)
        container.innerHTML = this.renderPosts(data.posts);
        this.attachReplyButtonListeners();
      } else {
        loading.style.display = 'none';
        const errorMsg = data.error || 'Failed to load replies';
        this.showError(container, errorMsg);
        console.error('API returned error:', data);
      }
    } catch (error) {
      console.error('Error loading posts:', error);
      loading.style.display = 'none';
      this.showError(container, `Network error: ${error.message}. Please refresh the page.`);
    }
  },

  /**
   * Render posts with nesting
   */
  renderPosts(posts) {
    if (!Array.isArray(posts) || posts.length === 0) {
      return '<p class="no-data">No replies yet. Be the first to reply!</p>';
    }

    // Group posts by parent
    const postsByParent = {};
    posts.forEach(post => {
      if (!post || !post.id) {
        console.warn('Skipping invalid post:', post);
        return;
      }
      const parentId = post.parent_post_id || 'root';
      if (!postsByParent[parentId]) {
        postsByParent[parentId] = [];
      }
      postsByParent[parentId].push(post);
    });

    // Recursive function to render nested posts
    const renderPostTree = (parentId, level = 0) => {
      const children = postsByParent[parentId] || [];
      return children.map(post => {
        // Defensive data extraction
        const authorName = post.author?.full_name || post.author?.username || 'Unknown';
        const authorUsername = post.author?.username || 'unknown';
        const postContent = (post.content || '').replace(/\n/g, '<br>').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        const timestamp = post.created_at ? this.formatTimeAgo(post.created_at) : 'just now';
        
        return `
        <div class="forum-post" data-post-id="${post.id}" style="margin-left: ${level * 40}px;">
          <div class="forum-post__header">
            <div class="forum-post__avatar">
              <i class="fas fa-user-circle"></i>
            </div>
            <div class="forum-post__author-info">
              <span class="forum-post__author">${authorName}</span>
              <span class="forum-post__username">@${authorUsername}</span>
              <span class="forum-post__timestamp">
                <i class="far fa-clock"></i>
                ${timestamp}
              </span>
            </div>
          </div>
          
          <div class="forum-post__content">
            ${postContent}
          </div>
          
          <div class="forum-post__footer">
            <button class="forum-post__reply-btn" data-post-id="${post.id}">
              <i class="fas fa-reply"></i> Reply
            </button>
            ${post.reply_count > 0 ? `
              <span class="forum-post__reply-count">
                <i class="fas fa-comments"></i>
                ${post.reply_count} ${post.reply_count === 1 ? 'Reply' : 'Replies'}
              </span>
            ` : ''}
          </div>
        </div>
        ${renderPostTree(post.id, level + 1)}
      `).join('');
    };

    return renderPostTree('root');
  },

  /**
   * Attach event listeners to reply buttons
   */
  attachReplyButtonListeners() {
    document.querySelectorAll('.forum-post__reply-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const postId = e.currentTarget.getAttribute('data-post-id');
        this.focusReplyForm(postId);
      });
    });
  },

  /**
   * Insert a new post directly into the DOM
   */
  insertNewPost(post, parentPostId) {
    if (!post || !post.id) {
      console.error('Invalid post data:', post);
      return;
    }

    const container = document.getElementById('postsContainer');
    if (!container) {
      console.error('Posts container not found');
      return;
    }

    const noDataMsg = container.querySelector('.no-data');
    if (noDataMsg) noDataMsg.remove();

    // Calculate nesting level
    let level = 0;
    if (parentPostId) {
      const parentPost = document.querySelector(`[data-post-id="${parentPostId}"]`);
      if (parentPost) {
        const parentMargin = parseInt(parentPost.style.marginLeft) || 0;
        level = (parentMargin / 40) + 1;
      }
    }

    // Defensive data extraction
    const authorName = post.author?.full_name || post.author?.username || 'You';
    const authorUsername = post.author?.username || 'you';
    const postContent = (post.content || '').replace(/\n/g, '<br>').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    const timestamp = post.created_at ? this.formatTimeAgo(post.created_at) : 'just now';

    // Create post HTML
    const postHtml = `
      <div class="forum-post" data-post-id="${post.id}" style="margin-left: ${level * 40}px;">
        <div class="forum-post__header">
          <div class="forum-post__avatar">
            <i class="fas fa-user-circle"></i>
          </div>
          <div class="forum-post__author-info">
            <span class="forum-post__author">${authorName}</span>
            <span class="forum-post__username">@${authorUsername}</span>
            <span class="forum-post__timestamp">
              <i class="far fa-clock"></i>
              ${timestamp}
            </span>
          </div>
        </div>
        
        <div class="forum-post__content">
          ${postContent}
        </div>
        
        <div class="forum-post__footer">
          <button class="forum-post__reply-btn" data-post-id="${post.id}">
            <i class="fas fa-reply"></i> Reply
          </button>
        </div>
      </div>
    `;

    // Insert post in correct position
    if (parentPostId) {
      // Find parent post and insert after its last child
      const parentPost = document.querySelector(`[data-post-id="${parentPostId}"]`);
      if (parentPost) {
        let insertAfter = parentPost;
        let nextSibling = parentPost.nextElementSibling;
        
        // Find the last child of this parent
        while (nextSibling && parseInt(nextSibling.style.marginLeft || 0) > parseInt(parentPost.style.marginLeft || 0)) {
          insertAfter = nextSibling;
          nextSibling = nextSibling.nextElementSibling;
        }
        
        insertAfter.insertAdjacentHTML('afterend', postHtml);
      } else {
        container.insertAdjacentHTML('beforeend', postHtml);
      }
    } else {
      // Top-level reply - append at the end
      container.insertAdjacentHTML('beforeend', postHtml);
    }

    // Re-attach event listeners
    this.attachReplyButtonListeners();
  },

  /**
   * Show inline reply form below post
   */
  showInlineReplyForm(postId) {
    // Remove any existing inline forms
    const existingInlineForms = document.querySelectorAll('.forum-post__inline-reply');
    existingInlineForms.forEach(form => form.remove());

    // Find the post element
    const postElement = document.querySelector(`[data-post-id="${postId}"]`);
    if (!postElement) return;

    // Get thread ID from the page
    const threadId = this.currentThreadId || postElement.closest('[data-thread-id]')?.dataset.threadId;

    // Create inline reply form HTML
    const inlineFormHtml = `
      <div class="forum-post__inline-reply" data-reply-to="${postId}">
        <form class="forum-inline-reply-form">
          <div class="forum-inline-reply-form__header">
            <i class="fas fa-reply"></i>
            <span>Write a reply</span>
          </div>
          <textarea 
            class="forum-inline-reply-form__textarea" 
            placeholder="Write your reply here..."
            rows="3"
            required
          ></textarea>
          <div class="forum-inline-reply-form__actions">
            <button type="button" class="forum-inline-reply-form__cancel">
              <i class="fas fa-times"></i> Cancel
            </button>
            <button type="submit" class="forum-inline-reply-form__submit">
              <i class="fas fa-paper-plane"></i> Post Reply
            </button>
          </div>
          <div class="forum-inline-reply-form__status" style="display: none;"></div>
        </form>
      </div>
    `;

    // Insert the form after the post
    postElement.insertAdjacentHTML('afterend', inlineFormHtml);

    // Get the newly created form elements
    const inlineForm = postElement.nextElementSibling;
    const form = inlineForm.querySelector('form');
    const textarea = inlineForm.querySelector('textarea');
    const cancelBtn = inlineForm.querySelector('.forum-inline-reply-form__cancel');
    const statusDiv = inlineForm.querySelector('.forum-inline-reply-form__status');

    // Focus textarea
    setTimeout(() => textarea.focus(), 100);

    // Handle cancel button
    cancelBtn.addEventListener('click', () => {
      inlineForm.remove();
    });

    // Handle form submission
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      await this.submitInlineReply(threadId, postId, form, statusDiv, inlineForm);
    });
  },

  /**
   * Focus reply form for specific post (kept for backward compatibility)
   */
  focusReplyForm(postId) {
    this.showInlineReplyForm(postId);
  },

  /**
   * Initialize reply form
   */
  initReplyForm(threadId) {
    this.currentThreadId = threadId; // Store for inline replies
    const form = document.getElementById('postReplyForm');
    const cancelBtn = document.getElementById('cancelReply');
    const parentPostIdInput = document.getElementById('parentPostId');
    const statusDiv = document.getElementById('replyFormStatus');

    cancelBtn.addEventListener('click', () => {
      parentPostIdInput.value = '';
      cancelBtn.style.display = 'none';
      form.reset();
    });

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      await this.submitReply(threadId, form, statusDiv);
    });
  },

  /**
   * Submit an inline reply
   */
  async submitInlineReply(threadId, parentPostId, form, statusDiv, inlineFormContainer) {
    const textarea = form.querySelector('textarea');
    const content = textarea.value;
    
    // Validate content
    if (!content || content.trim().length === 0) {
      statusDiv.className = 'forum-inline-reply-form__status forum-inline-reply-form__status--error';
      statusDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i> Please enter a reply message.';
      statusDiv.style.display = 'block';
      return;
    }
    
    const submitBtn = form.querySelector('.forum-inline-reply-form__submit');
    const originalText = submitBtn.innerHTML;

    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Posting...';
    statusDiv.style.display = 'none';

    try {
      const response = await fetch(`/forum/api/thread/${threadId}/post/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCSRFToken()
        },
        body: JSON.stringify({
          content: content.trim(),
          parent_post_id: parentPostId
        })
      });

      const data = await response.json();

      if (data.success) {
        // Remove the inline form
        inlineFormContainer.remove();

        // Directly insert the new post
        this.insertNewPost(data.post, parentPostId);
        
        // Update reply counts
        const repliesCountElem = document.getElementById('repliesCount');
        const totalRepliesCountElem = document.getElementById('totalRepliesCount');
        if (repliesCountElem) {
          const currentCount = parseInt(repliesCountElem.textContent) || 0;
          repliesCountElem.textContent = currentCount + 1;
        }
        if (totalRepliesCountElem) {
          const currentCount = parseInt(totalRepliesCountElem.textContent) || 0;
          totalRepliesCountElem.textContent = currentCount + 1;
        }

        // Scroll to and highlight new post
        setTimeout(() => {
          const newPost = document.querySelector(`[data-post-id="${data.post.id}"]`);
          if (newPost) {
            newPost.scrollIntoView({ behavior: 'smooth', block: 'center' });
            newPost.classList.add('forum-post--highlight');
            setTimeout(() => newPost.classList.remove('forum-post--highlight'), 2000);
          }
        }, 100);

      } else {
        statusDiv.className = 'forum-inline-reply-form__status forum-inline-reply-form__status--error';
        statusDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${data.error || 'Failed to post reply'}`;
        statusDiv.style.display = 'block';
        
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
      }
    } catch (error) {
      console.error('Error posting inline reply:', error);
      statusDiv.className = 'forum-inline-reply-form__status forum-inline-reply-form__status--error';
      statusDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i> Network error. Please try again.';
      statusDiv.style.display = 'block';
      
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalText;
    }
  },

  /**
   * Submit a reply
   */
  async submitReply(threadId, form, statusDiv) {
    const formData = new FormData(form);
    const content = formData.get('content');
    const parentPostId = formData.get('parent_post_id');
    
    // Validate content
    if (!content || content.trim().length === 0) {
      statusDiv.className = 'forum-reply-form__status forum-reply-form__status--error';
      statusDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i> Please enter a reply message.';
      statusDiv.style.display = 'block';
      return;
    }
    
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;

    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Posting...';
    statusDiv.style.display = 'none';

    try {
      console.log('Submitting reply:', { threadId, content: content.substring(0, 50), parentPostId });
      
      const response = await fetch(`/forum/api/thread/${threadId}/post/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCSRFToken()
        },
        body: JSON.stringify({
          content: content.trim(),
          parent_post_id: parentPostId || null
        })
      });

      console.log('Response status:', response.status);
      const data = await response.json();
      console.log('Response data:', data);

      if (data.success) {
        // Show success message
        statusDiv.className = 'forum-reply-form__status forum-reply-form__status--success';
        statusDiv.innerHTML = '<i class="fas fa-check-circle"></i> Reply posted successfully!';
        statusDiv.style.display = 'block';

        // Reset form
        form.reset();
        document.getElementById('parentPostId').value = '';
        const cancelBtn = document.getElementById('cancelReply');
        if (cancelBtn) cancelBtn.style.display = 'none';

        // Directly insert the new post instead of reloading
        this.insertNewPost(data.post, parentPostId);
        
        // Update reply counts
        const repliesCountElem = document.getElementById('repliesCount');
        const totalRepliesCountElem = document.getElementById('totalRepliesCount');
        if (repliesCountElem) {
          const currentCount = parseInt(repliesCountElem.textContent) || 0;
          repliesCountElem.textContent = currentCount + 1;
        }
        if (totalRepliesCountElem) {
          const currentCount = parseInt(totalRepliesCountElem.textContent) || 0;
          totalRepliesCountElem.textContent = currentCount + 1;
        }

        // Scroll to new post
        setTimeout(() => {
          const newPost = document.querySelector(`[data-post-id="${data.post.id}"]`);
          if (newPost) {
            newPost.scrollIntoView({ behavior: 'smooth', block: 'center' });
            newPost.classList.add('forum-post--highlight');
            setTimeout(() => newPost.classList.remove('forum-post--highlight'), 2000);
          }
        }, 100);

        // Hide success message after 3 seconds
        setTimeout(() => {
          statusDiv.style.display = 'none';
        }, 3000);

      } else {
        statusDiv.className = 'forum-reply-form__status forum-reply-form__status--error';
        statusDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> Error: ${data.error || 'Unknown error'}`;
        statusDiv.style.display = 'block';
      }
    } catch (error) {
      console.error('Error submitting reply:', error);
      statusDiv.className = 'forum-reply-form__status forum-reply-form__status--error';
      statusDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> Network error: ${error.message}. Please check your connection and try again.`;
      statusDiv.style.display = 'block';
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalText;
    }
  }
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ForumApp;
}
