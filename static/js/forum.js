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

    try {
      const response = await fetch('/forum/api/topics/');
      const data = await response.json();

      if (data.success) {
        loading.style.display = 'none';
        
        if (data.topics.length === 0) {
          container.innerHTML = '<p class="no-data">No topics available yet.</p>';
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
      } else {
        this.showError(container, 'Failed to load topics');
      }
    } catch (error) {
      console.error('Error loading topics:', error);
      this.showError(container, 'An error occurred while loading topics');
    }
  },

  /**
   * Load threads for a specific topic
   */
  async loadTopicThreads(topicId) {
    const container = document.getElementById('threadsContainer');
    const loading = document.getElementById('threadsLoading');

    try {
      const response = await fetch(`/forum/api/topics/`);
      const data = await response.json();

      if (data.success) {
        // For now, we'll fetch from the page or implement a separate endpoint
        // This is a placeholder - in production, add GET /api/topic/<id>/threads/
        loading.innerHTML = '<p class="no-data">Thread loading will be implemented with topic-specific endpoint</p>';
      }
    } catch (error) {
      console.error('Error loading threads:', error);
      this.showError(container, 'An error occurred while loading threads');
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

    try {
      const response = await fetch(`/forum/api/thread/${threadId}/posts/`);
      const data = await response.json();

      if (data.success) {
        loading.style.display = 'none';
        
        // Update counts
        repliesCountElem.textContent = data.total_replies;
        totalRepliesCountElem.textContent = data.total_replies;

        if (data.posts.length === 0) {
          container.innerHTML = '<p class="no-data">No replies yet. Be the first to reply!</p>';
          return;
        }

        // Render posts (handle nesting)
        container.innerHTML = this.renderPosts(data.posts);
        this.attachReplyButtonListeners();
      } else {
        this.showError(container, 'Failed to load replies');
      }
    } catch (error) {
      console.error('Error loading posts:', error);
      this.showError(container, 'An error occurred while loading replies');
    }
  },

  /**
   * Render posts with nesting
   */
  renderPosts(posts) {
    // Group posts by parent
    const postsByParent = {};
    posts.forEach(post => {
      const parentId = post.parent_post_id || 'root';
      if (!postsByParent[parentId]) {
        postsByParent[parentId] = [];
      }
      postsByParent[parentId].push(post);
    });

    // Recursive function to render nested posts
    const renderPostTree = (parentId, level = 0) => {
      const children = postsByParent[parentId] || [];
      return children.map(post => `
        <div class="forum-post" data-post-id="${post.id}" style="margin-left: ${level * 40}px;">
          <div class="forum-post__header">
            <div class="forum-post__avatar">
              <i class="fas fa-user-circle"></i>
            </div>
            <div class="forum-post__author-info">
              <span class="forum-post__author">${post.author.full_name}</span>
              <span class="forum-post__username">@${post.author.username}</span>
              <span class="forum-post__timestamp">
                <i class="far fa-clock"></i>
                ${this.formatTimeAgo(post.created_at)}
              </span>
            </div>
          </div>
          
          <div class="forum-post__content">
            ${post.content.replace(/\n/g, '<br>')}
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
   * Focus reply form for specific post
   */
  focusReplyForm(postId) {
    const replyForm = document.getElementById('replyForm');
    const parentPostIdInput = document.getElementById('parentPostId');
    const cancelBtn = document.getElementById('cancelReply');
    const textarea = document.getElementById('replyContent');

    parentPostIdInput.value = postId;
    cancelBtn.style.display = 'inline-block';
    
    // Scroll to form and focus
    replyForm.scrollIntoView({ behavior: 'smooth' });
    setTimeout(() => textarea.focus(), 500);
  },

  /**
   * Initialize reply form
   */
  initReplyForm(threadId) {
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

        // Reload posts to show new reply
        await this.loadThreadPosts(threadId);

        // Scroll to new post
        setTimeout(() => {
          const newPost = document.querySelector(`[data-post-id="${data.post.id}"]`);
          if (newPost) {
            newPost.scrollIntoView({ behavior: 'smooth', block: 'center' });
            newPost.classList.add('forum-post--highlight');
            setTimeout(() => newPost.classList.remove('forum-post--highlight'), 2000);
          }
        }, 500);

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
