# 🔧 PROFILE PAGE ISSUES & FIXES TRACKER

**Created:** November 26, 2025  
**Priority Analysis:** Complete  
**Status:** Ready for Implementation

---

## 📊 ISSUES SUMMARY

| # | Issue | Priority | Difficulty | Impact | Status |
|---|-------|----------|-----------|--------|--------|
| 1 | Missing Quiz Count Display | 🟡 High | 🟢 Easy | Medium | Not Started |
| 2 | Public Profile Feature Missing | 🟠 Medium | 🟠 Medium | High | Not Started |
| 3 | Profile Visibility Not Enforced | 🟡 High | 🟠 Medium | High | Not Started |
| 4 | Recent Activity Limited | 🟡 High | 🟠 Medium | Medium | Not Started |
| 5 | Study Progress Not Calculated | 🟡 High | 🟠 Medium | Medium | Not Started |
| 6 | Helpful Votes Coming Soon | 🟡 High | 🟢 Easy | Low | Not Started |

---

## 🔴 HIGH PRIORITY ISSUES

### Issue #1: Quiz Count Not Displaying

**Problem:**  
- Profile shows "0 Quizzes Created" regardless of actual count
- Hard-coded `0` in template instead of querying database
- Users can't see their contribution to quizzes

**Location:**
- `accounts/views.py` line 838-896 (profile view)
- `templates/accounts/profile.html` line 400-413

**Current Code:**
```html
<div class="impact-stat-card">
    <div class="impact-icon-wrapper blue">
        <i class="fas fa-clipboard-check"></i>
    </div>
    <div class="impact-stat-content">
        <div class="impact-stat-value">0</div>  <!-- HARDCODED ZERO -->
        <div class="impact-stat-label">Quizzes Created</div>
        <small class="text-muted">Coming Soon</small>
    </div>
</div>
```

**Fix:**
```python
# In profile() view (line ~860):
# Add before context assignment:
quizzes_count = Quiz.objects.filter(creator=request.user).count()

# In impact_data dictionary:
impact_data = {
    'resources_uploaded': stats.resources_uploaded,
    'quizzes_created': quizzes_count,  # CHANGE FROM stats.quizzes_created
    'flashcards_created': stats.flashcards_created,
    'students_helped': stats.students_helped,
}
```

**Template Fix:**
```html
<div class="impact-stat-value">{{ impact_data.quizzes_created }}</div>
<div class="impact-stat-label">Quizzes Created</div>
<!-- REMOVE "Coming Soon" text -->
```

**Files to Modify:**
1. `accounts/views.py` (profile function)
2. `templates/accounts/profile.html` (impact section)

**Testing:**
1. Create a quiz as test user
2. Go to profile
3. Verify count updates

**Effort:** 15 minutes  
**Risk:** Very Low

---

### Issue #2: Public Profile Feature Missing

**Problem:**  
- No way to view other users' profiles
- Profile page only shows logged-in user
- Users can't browse other students' achievements/resources
- Limits community engagement

**Location:**
- No route: `accounts/urls.py` missing pattern
- No view: `accounts/views.py` missing public_profile function
- Missing template: `templates/accounts/public_profile.html`

**Current Limitation:**
```python
# Only shows current user's profile
@login_required
def profile(request):
    # Always shows request.user profile
    user = request.user  # No parameter to view others
```

**Solution:**

1. **Add URL Pattern** (accounts/urls.py):
```python
path('profile/<str:username>/', views.public_profile, name='public_profile'),
path('profile/', views.profile, name='profile'),  # Keep personal
```

2. **Add View** (accounts/views.py):
```python
def public_profile(request, username):
    """View another user's public profile"""
    try:
        viewed_user = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.error(request, 'User not found')
        return redirect('accounts:student_dashboard')
    
    # Check profile_visibility
    if viewed_user.profile_visibility == 'private':
        if request.user != viewed_user:
            messages.error(request, 'This profile is private')
            return redirect('accounts:student_dashboard')
    elif viewed_user.profile_visibility == 'students_only':
        if not request.user.is_authenticated:
            return redirect('accounts:login')
    
    # Get profile data
    user_resources = Resource.objects.filter(uploader=viewed_user, is_public=True)[:10]
    user_bookmarks = Bookmark.objects.filter(user=viewed_user)[:10]
    user_achievements = viewed_user.achievements.filter(is_displayed=True)
    
    context = {
        'viewed_user': viewed_user,
        'user_resources': user_resources,
        'user_bookmarks': user_bookmarks,
        'user_achievements': user_achievements,
        'is_own_profile': request.user == viewed_user,
        'can_edit': request.user == viewed_user,
    }
    return render(request, 'accounts/public_profile.html', context)
```

3. **Create Template** (templates/accounts/public_profile.html):
```html
{% extends 'base_dashboard.html' %}
{% load static %}

{% block content %}
<!-- Show public profile with limited editing -->
<!-- Hide email/sensitive info for non-owner viewers -->

{% if is_own_profile %}
    <!-- Show edit buttons -->
{% else %}
    <!-- Show view-only version -->
{% endif %}
{% endblock %}
```

**Files to Create/Modify:**
1. `accounts/urls.py` - Add URL pattern
2. `accounts/views.py` - Add public_profile function
3. `templates/accounts/public_profile.html` - Create new template

**Testing:**
1. Create 2 user accounts
2. Go to user 1's profile as user 2
3. Verify can view public sections
4. Verify cannot edit
5. Test profile_visibility settings

**Effort:** 2-3 hours  
**Risk:** Low (new feature, doesn't affect existing)

---

### Issue #3: Profile Visibility Field Not Used

**Problem:**  
- User model has `profile_visibility` field with choices
- Field exists in database but not enforced anywhere
- Users cannot change their visibility setting
- No privacy protection

**Current Field:**
```python
# In accounts/models.py line ~54:
profile_visibility = models.CharField(
    max_length=20,
    choices=[
        ('public', 'Public - Anyone can view'),
        ('students_only', 'Students Only - Only CIT students'),
        ('private', 'Private - Only you can view'),
    ],
    default='students_only'
)
```

**Where It Should Be Used:**
1. **Profile view** - Check visibility when viewing
2. **Settings page** - Let users change setting
3. **Public profile** - Enforce visibility rules

**Fix:**

1. **Add to Settings Form** (accounts/forms.py):
```python
class ProfileVisibilityForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_visibility']
```

2. **Add to Settings View** (accounts/views.py):
```python
def settings_view(request):
    if request.method == 'POST':
        if 'save_visibility' in request.POST:
            visibility = request.POST.get('profile_visibility')
            request.user.profile_visibility = visibility
            request.user.save()
            messages.success(request, 'Profile visibility updated')
            return redirect('accounts:settings')
```

3. **Add to Settings Template** (templates/accounts/settings.html):
```html
<div class="settings-section">
    <h3>Profile Visibility</h3>
    <form method="post">
        {% csrf_token %}
        <select name="profile_visibility">
            <option value="public" {% if user.profile_visibility == 'public' %}selected{% endif %}>
                Public - Anyone can view
            </option>
            <option value="students_only" {% if user.profile_visibility == 'students_only' %}selected{% endif %}>
                Students Only - CIT students only
            </option>
            <option value="private" {% if user.profile_visibility == 'private' %}selected{% endif %}>
                Private - Only you
            </option>
        </select>
        <button type="submit" name="save_visibility">Save</button>
    </form>
</div>
```

**Files to Modify:**
1. `accounts/forms.py` - Add form field
2. `accounts/views.py` - Enforce in public_profile
3. `templates/accounts/settings.html` - Add UI

**Testing:**
1. Change visibility to "private"
2. Try to view as another user → Should be blocked
3. Change back to "public"
4. Should be viewable again

**Effort:** 1-2 hours  
**Risk:** Low (new feature, doesn't break existing)

---

### Issue #4: Recent Activity Limited

**Problem:**  
- Only shows resource uploads (3 items)
- Missing: Quiz attempts, Flashcard studies, Bookmarks, Comments
- No date grouping
- Limited visibility of user engagement

**Current Code:**
```html
{% for resource in user_resources|slice:":3" %}
    <div class="recent-activity-item">
        Uploaded <strong>{{ resource.title }}</strong>
    </div>
{% endfor %}
```

**Solution:**

```python
# In profile() view:
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

# Get activities from last 30 days
thirty_days_ago = timezone.now() - timedelta(days=30)

# Combine multiple activity types
activities = []

# Resource uploads
for r in Resource.objects.filter(uploader=request.user, created_at__gte=thirty_days_ago)[:5]:
    activities.append({
        'type': 'upload',
        'title': r.title,
        'time': r.created_at,
        'icon': 'fa-file-upload',
        'message': f'Uploaded {r.title}',
    })

# Quiz creations
for q in Quiz.objects.filter(creator=request.user, created_at__gte=thirty_days_ago)[:5]:
    activities.append({
        'type': 'quiz',
        'title': q.title,
        'time': q.created_at,
        'icon': 'fa-clipboard-check',
        'message': f'Created quiz {q.title}',
    })

# Flashcard decks
for d in Deck.objects.filter(owner=request.user, created_at__gte=thirty_days_ago)[:5]:
    activities.append({
        'type': 'flashcard',
        'title': d.title,
        'time': d.created_at,
        'icon': 'fa-layer-group',
        'message': f'Created flashcards {d.title}',
    })

# Sort by date descending
activities.sort(key=lambda x: x['time'], reverse=True)
recent_activities = activities[:10]  # Top 10

# In learning_summary:
learning_summary = {
    'recent_activities': recent_activities,
}
```

**Template Update:**
```html
<div class="recent-activity-list">
    {% for activity in learning_summary.recent_activities %}
        <div class="recent-activity-item">
            <i class="fas {{ activity.icon }} text-secondary"></i>
            <div class="recent-activity-content">
                <div class="recent-activity-text">
                    {{ activity.message }}
                </div>
                <div class="recent-activity-time">
                    {{ activity.time|timesince }} ago
                </div>
            </div>
        </div>
    {% endfor %}
</div>
```

**Files to Modify:**
1. `accounts/views.py` - Enhance activity gathering
2. `templates/accounts/profile.html` - Update template

**Testing:**
1. Create resource, quiz, flashcard
2. Go to profile
3. All activities should show up
4. Should be sorted by date

**Effort:** 1-2 hours  
**Risk:** Low (enhancement, doesn't break)

---

### Issue #5: Study Progress Not Calculated

**Problem:**  
- Learning summary shows 0% progress
- Study time not tracked or calculated
- Progress bar always empty
- No accurate learning metrics

**Current Code:**
```html
<div class="learning-progress-bar">
    <div class="learning-progress-fill" style="width: 0%"></div>
</div>
```

**Solution:**

```python
# In profile() view:
from quizzes.models import QuizAttempt
from flashcards.models import Card

# Calculate study progress
quiz_attempts = QuizAttempt.objects.filter(user=request.user, completed_at__isnull=False).count()
flashcards_studied = Deck.objects.filter(owner=request.user, last_studied_at__isnull=False).count()

# Calculate progress percentage
total_learning_activities = quiz_attempts + flashcards_studied
# Or base on study time if available
study_progress_percent = min((total_learning_activities / 50) * 100, 100)  # 50 activities = 100%

learning_summary = {
    'study_progress': stats.total_study_time,
    'study_progress_percent': study_progress_percent,
    'quiz_attempts': quiz_attempts,
    'flashcards_studied': flashcards_studied,
}
```

**Template Update:**
```html
<div class="learning-progress-header">
    <span class="learning-progress-label">Study Progress</span>
    <span class="learning-progress-percentage">
        {{ learning_summary.study_progress_percent|floatformat:0 }}%
    </span>
</div>
<div class="learning-progress-bar">
    <div class="learning-progress-fill" 
         style="width: {{ learning_summary.study_progress_percent }}%">
    </div>
</div>
```

**Files to Modify:**
1. `accounts/views.py` - Add study progress calculation
2. `templates/accounts/profile.html` - Update percentage display

**Testing:**
1. Complete a quiz attempt
2. Go to profile
3. Progress bar should show some percentage
4. Complete more → percentage increases

**Effort:** 1 hour  
**Risk:** Very Low

---

### Issue #6: Helpful Votes Coming Soon Placeholder

**Problem:**  
- "Helpful Votes" shows 0 with "Coming Soon" text
- Field `helpful_votes` might not exist in model
- Impact metric incomplete

**Current Code:**
```html
<div class="impact-stat-card">
    <div class="impact-icon-wrapper gold">
        <i class="fas fa-star"></i>
    </div>
    <div class="impact-stat-content">
        <div class="impact-stat-value">0</div>
        <div class="impact-stat-label">Helpful Votes</div>
        <small class="text-muted">Coming Soon</small>
    </div>
</div>
```

**Solution Options:**

**Option A: Remove until feature ready**
```html
<!-- Comment out entire section -->
<!-- When ready, implement rating system -->
```

**Option B: Implement now using existing Rating model**
```python
# In profile() view:
from resources.models import Rating

helpful_votes = Rating.objects.filter(
    resource__uploader=request.user,
    stars__gte=4  # 4-5 stars = helpful
).count()

impact_data = {
    ...
    'helpful_votes': helpful_votes,
}
```

**Effort:** 30 minutes  
**Risk:** Very Low

---

## 📋 IMPLEMENTATION ROADMAP

### Phase 1: Quick Fixes (Week 1)
- [ ] Issue #1: Fix Quiz Count Display (15 min)
- [ ] Issue #6: Handle Helpful Votes (30 min)
- [ ] Issue #5: Calculate Study Progress (1 hour)

### Phase 2: Enhancements (Week 2)
- [ ] Issue #4: Enhanced Recent Activity (2 hours)
- [ ] Issue #3: Profile Visibility Settings (2 hours)

### Phase 3: Major Feature (Week 3)
- [ ] Issue #2: Public Profile Feature (3-4 hours)

---

## 🧪 TESTING CHECKLIST

### Before Deployment
- [ ] All quiz counts accurate
- [ ] Study progress calculates correctly
- [ ] Recent activities show multiple types
- [ ] Profile visibility respected
- [ ] Public profiles accessible
- [ ] Private profiles blocked for others
- [ ] No errors in console
- [ ] Responsive on mobile

### Database Checks
- [ ] No missing migrations
- [ ] All counts query correctly
- [ ] No N+1 queries
- [ ] Performance acceptable

---

## 📊 PRIORITY MATRIX

```
High Impact, Easy (DO FIRST)
- Issue #1: Quiz Count ⚡ DO THIS FIRST
- Issue #6: Helpful Votes
- Issue #5: Study Progress

High Impact, Medium
- Issue #3: Profile Visibility
- Issue #4: Recent Activity

High Impact, Hard
- Issue #2: Public Profiles ⭐ BIG FEATURE
```

---

## 💰 EFFORT ESTIMATION

| Issue | Time | Complexity |
|-------|------|-----------|
| #1 Quiz Count | 15 min | Easy |
| #6 Helpful Votes | 30 min | Easy |
| #5 Study Progress | 1 hour | Easy |
| #4 Recent Activity | 2 hours | Medium |
| #3 Visibility | 2 hours | Medium |
| #2 Public Profile | 3-4 hours | Hard |
| **TOTAL** | **9-11 hours** | **Medium** |

---

**Document Version:** 1.0  
**Last Updated:** November 26, 2025  
**Ready for Implementation:** ✅

