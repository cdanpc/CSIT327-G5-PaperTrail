# PaperTrail System Documentation
## Complete System Requirements for Rebuilding

---

## 1. SYSTEM OVERVIEW

### 1.1 Project Vision
A centralized academic resource management system for CIT-U College of Computer Studies that enables students and faculty to share, discover, and collaborate on educational materials including lecture notes, quizzes, and flashcards.

### 1.2 Core Objectives
- Centralize fragmented academic resources into one unified platform
- Enable peer-to-peer resource sharing with quality control mechanisms
- Facilitate interactive learning through quizzes and flashcards
- Provide verification system for content quality assurance
- Track user engagement and contribution metrics
- Support personalized learning through bookmarks and collections

### 1.3 Target Users
- **Students**: Primary users who upload, access, and interact with resources
- **Professors**: Verify and moderate content, create official study materials
- **Admins**: System management, user administration, content moderation

---

## 2. TECHNOLOGY STACK

### 2.1 Backend
- **Framework**: Django 4.2+ (Python web framework)
- **Authentication**: Django's built-in authentication with custom User model
- **API**: Django REST Framework (if API endpoints needed)

### 2.2 Frontend
- **Templates**: Django Template Language (DTL)
- **CSS Framework**: Bootstrap 5.3.0
- **Icons**: Font Awesome 6.4.0
- **JavaScript**: Vanilla JS (no framework required)
- **Charts**: Chart.js 4.4.1 (for dashboard visualizations)

### 2.3 Database
- **Production**: PostgreSQL (via Supabase)
- **Development**: SQLite3 (local development)
- **File Storage**: Supabase Storage (cloud file hosting)

### 2.4 Infrastructure
- **Hosting**: Render.com
- **Static Files**: WhiteNoise middleware
- **Environment**: Python 3.10+

---

## 3. DATABASE SCHEMA

### 3.1 User Management (accounts app)

#### User Model (extends AbstractUser)
```
Fields:
- username (unique, required)
- password (hashed)
- first_name
- last_name
- stud_id (format: ##-####-### for students, #### for professors)
- univ_email (must end with @cit.edu)
- profile_picture (ImageField, stored in Supabase)
- bio (max 500 chars)
- role (choices: 'student', 'professor', 'admin')
- is_email_verified (boolean)
- is_professor_verified (boolean)
- force_password_change (boolean, for initial setup)
- date_joined (auto)
- last_login (auto)

Relationships:
- One-to-Many: uploaded_resources, created_quizzes, created_decks
- One-to-Many: bookmarks, ratings, comments
- One-to-Many: notifications
```

#### Notification Model
- User notification system for platform activities
- Support multiple notification types (uploads, comments, ratings, verifications)
- Read/unread status tracking
- GenericForeignKey for flexible content linking

#### UserStats Model
- Track user contribution metrics
- Total uploads, bookmarks, ratings given
- OneToOne relationship with User

#### Badge Model (Achievement System)
- Gamification system for user achievements
- Multiple badge types (resource, quiz, flashcard, engagement, streak)
- Icon and color customization
- Requirement thresholds

#### Achievement Model
- Track earned badges per user
- Timestamp when badge was earned
- Link users to their badges

### 3.2 Resources (resources app)

#### Resource Model
- Central model for uploaded academic materials
- Support multiple resource types (PDF, PPT, DOCX, images, external links)
- File storage via Supabase Storage URLs
- Verification workflow (pending → verified/not_verified)
- Privacy controls (public/private)
- View and download tracking
- Tag-based categorization

**Business Rules:**
- Either file_url OR external_url must be provided (not both)
- Only professors can verify resources
- Public resources visible to all, private only to uploader

#### Tag Model
- Simple categorization system
- Unique tag names for consistent filtering

#### Bookmark Model
- Save resources for later access
- User can bookmark each resource only once
- Unique constraint: (user, resource)

#### Rating Model
- 1-5 star rating system
- One rating per user per resource
- Unique constraint: (user, resource)

#### Comment Model
- Discussion and feedback on resources
- Support threaded/nested comments (parent-child)
- Track edit history
- Timestamp tracking

#### Like Model
- Upvote system for comments
- One like per user per comment
- Unique constraint: (user, comment)

### 3.3 Quizzes (quizzes app)

#### Quiz Model
- Container for multiple-choice quiz questions
- Verification workflow similar to Resources
- Privacy controls (public/private)
- Track total attempts count

#### Question Model
- Individual quiz questions
- Belong to a specific quiz
- Ordered sequence within quiz

**Business Rules:**
- Each question must have at least one correct option

#### Option Model
- Multiple choice options for questions
- Mark correct/incorrect answers
- Ordered display within question

#### QuizAttempt Model
- Track user quiz submissions and results
- Calculate score percentage
- Record correct/incorrect answers count
- Track start and completion times

#### QuizAttemptAnswer Model
- Individual answer records per attempt
- Link question → selected option
- Store correctness evaluation

#### QuizBookmark Model
- Save quizzes for later practice
- Unique constraint: (user, quiz)

#### QuizRating Model
- 1-5 star rating system for quizzes
- One rating per user per quiz
- Unique constraint: (user, quiz)

#### QuizComment Model
- Discussion on quiz content/difficulty
- Support threaded comments
- Edit tracking

#### QuizLike Model
- Upvote quiz comments
- Unique constraint: (user, comment)

### 3.4 Flashcards (flashcards app)

#### Deck Model
- Container for flashcard sets
- Category-based organization (definitions, formulas, concepts, etc.)
- Tag-based filtering (comma-separated)
- Visibility controls (public/private)
- Verification workflow
- Track last studied timestamp

#### Card Model
- Individual flashcards within a deck
- Front side: Question/term
- Back side: Answer/definition
- Simple two-sided card structure

#### DeckRating Model
- 1-5 star rating system for decks
- One rating per user per deck
- Unique constraint: (user, deck)

#### DeckComment Model
- Feedback on deck quality/content
- Support threaded comments
- Edit tracking

#### DeckLike Model
- Upvote deck comments
- Unique constraint: (user, comment)

#### DeckBookmark Model
- Save favorite decks for quick access
- Unique constraint: (user, deck)

---

## 4. CORE FEATURES & USER FLOWS

### 4.1 Authentication System

#### Registration Flow
1. User visits registration page
2. Chooses role (Student or Professor)
3. **Students**: Provides username, university email (@cit.edu), course (BSCS or BSIT), Year level(1-5),  student ID (format: ##-####-###), password
4. **Professors**: Provides username, university email (@cit.edu), employee ID (####), password
5. Email verification sent
6. User redirects to login after successful registration
7. First login forces password change (security measure for professors)

#### Login Flow
1. User enters username/email and password
2. System validates credentials
3. If force_password_change is True, redirect to password change page
4. Otherwise, redirect to role-specific dashboard

#### Password Reset Flow (3-Step Process)
1. **Step 1**: User selects reset 
2. **Step 2**: User enters student id, and university email, if matched with id and email the admin will provide a code  
3. **Step 3**: User enters code, sets new password

### 4.2 Resource Management

#### Upload Resource
1. Student/Professor clicks "Upload Resource"
2. Fills form:
   - Title (required)
   - Description (optional)
   - Resource Type (link or files), if link there will be a new input for link, else, the input will hide and the access to file button will appear
   - add files or add links
   - Tags (multi-select or comma-separated)
   - Privacy (public/private toggle)
3. Submit triggers:
   - File upload to Supabase Storage
   - Database record creation with status "pending"
   - Notification to professors for verification

#### Resource Verification (Professors Only)
1. Professor navigates to verification queue
2. Reviews pending resources
3. Actions:
   - **Approve**: Sets verification_status to "verified"
   - **Reject**: Sets verification_status to "not_verified"
4. User receives notification of decision

#### View Resource
1. User browses resource list or search
2. Clicks resource card
3. Detail page shows:
   - File preview/download button
   - Description and metadata
   - Tags, uploader info, upload date
   - Ratings (star display)
   - Comments section (threaded)
   - Bookmark button
4. Actions:
   - Download (increments download_count)
   - Rate (1-5 stars)
   - Comment (nested replies supported)
   - Bookmark/Unbookmark

#### Search & Filter
- **Search**: By title, description, tags (full-text search)
- **Filters**:
  - Resource type (PDF, PPT, etc.)
  - Verification status (verified only)
  - Date range
  - Tag categories
  - Uploader

### 4.3 Quiz System

#### Create Quiz
1. Student clicks "Create Quiz"
2. Enters quiz title and description
3. Adds questions:
   - Question text
   - 2-6 multiple choice options
   - Mark correct answer(s)
   - Reorder questions via drag-and-drop
4. Sets privacy (public/private)
5. Submit for verification (if student)

#### Take Quiz
1. User browses quiz list
2. Clicks "Start Quiz"
3. Timer starts (optional)
4. User selects answers for each question
5. Submits quiz
6. System calculates:
   - Score percentage
   - Correct/incorrect answers
   - Time taken
7. Results page shows:
   - Final score
   - Question-by-question breakdown
   - Correct answers highlighted
8. QuizAttempt record saved to database

#### Quiz Interactions
- **Rate**: 1-5 stars after completion
- **Comment**: Discuss quiz difficulty/content
- **Bookmark**: Save for later practice
- **Clone quiz**: Duplicate to personal collection (with attribution)

### 4.4 Flashcard System

#### Create Deck
1. User clicks "Create Flashcard Deck"
2. Enters deck title, description, category
3. Adds cards:
   - Front: Question/term
   - Back: Answer/definition
   - Add multiple cards in bulk
4. Sets visibility (public/private)
5. Submits for verification

#### Study Mode
1. User selects deck
2. Clicks "Study Now"
3. Study interface:
   - Shows front of card
   - User mentally answers
   - Clicks "Flip" to see back
   - Marks as "Know" or "Don't Know"
   - Next card loads
4. Shuffle mode option
5. Progress tracking: X/Y cards completed
6. Session statistics at end

#### Deck Interactions
- **Rate**: 1-5 stars
- **Comment**: Feedback on deck quality
- **Bookmark**: Save favorite decks
- **Clone Deck**: Duplicate to personal collection (with attribution)

### 4.5 Dashboard Features

#### Student Dashboard
- **Stats Cards** (4 metrics):
  - Total Resources Uploaded
  - Quizzes Attempted
  - Bookmarks Saved
  - Flashcard Decks Created
- **Quick Actions** (2x2 grid):
  - Upload Resource
  - Browse Library
  - Create Quiz
  - Flashcards
- **New Uploads Widget**:
  - Last 5-10 recent resources across platform
  - Links to resource details
- **Suggested Features** (choose 1-2):
  - Upcoming Deadlines
  - Study Streak Tracker
  - Recent Notifications Feed

#### Professor Dashboard
- **Verification Queue**:
  - Pending resources count
  - Pending quizzes count
  - Quick approve/reject actions
- **Content Moderation**:
  - Flagged content review
  - User reports

#### Admin Dashboard
- System statistics
- User management (view, edit, delete)
- Content moderation (global)
- Platform settings

### 4.6 Notification System

#### Notification Types
1. **new_upload**: "New resource uploaded in [tag]"
2. **new_comment**: "[User] commented on your [resource/quiz/deck]"
3. **new_rating**: "[User] rated your [resource] X stars"
4. **verification_approved**: "Your [resource] was verified by [Professor]"
5. **verification_rejected**: "Your [resource] was not verified"
6. **new_bookmark**: "[User] bookmarked your [resource]"
7. **quiz_attempt**: "[User] completed your quiz with score X%"

#### Notification Delivery
- **In-App**: Bell icon in navbar with red badge counter
- **Email**: Optional (user preferences)
- **Real-time**: AJAX polling every 30s or WebSocket (optional)

---

## 5. USER INTERFACE REQUIREMENTS

### 5.1 Design System

#### Color Scheme
- **Primary**: #1f2937 (Purple)#1f2937
- **Secondary**: #22d3ee (Dark Purple)
- **Success**: #10b981 (Green)
- **Warning**: #fbbf24 (Amber)
- **Danger**: #ef4444 (Red)
- **Text Primary**: #1a1a1a
- **Text Secondary**: #6b7280
- **Background**: #f9fafb

#### Typography
- **Headings**: Font weight 700, gradient text effects
- **Body**: Font size 0.875rem - 1rem
- **System Font Stack**: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto

#### Spacing
- **Grid**: 8px base unit
- **Card Padding**: 1.5rem
- **Section Margins**: 2rem
- **Gap Between Cards**: 1rem - 1.5rem

#### Components
- **Cards**: White background, border-radius 12px, subtle shadow
- **Buttons**: Gradient backgrounds, rounded corners, hover effects
- **Forms**: Clean inputs with focus states
- **Modals**: Centered, backdrop blur
- **Toasts**: Top-right position, auto-dismiss

### 5.2 Responsive Breakpoints
- **Mobile**: < 576px
- **Tablet**: 576px - 991px
- **Desktop**: 992px - 1399px
- **Large Desktop**: ≥ 1400px

### 5.3 Key Pages

#### Navigation Bar (All Pages)
- Logo (left)
- Search bar (center, global search)
- Notification bell with badge (right)
- User profile dropdown (right)
  - View Profile
  - Settings
  - Logout

#### Home/Landing Page (Unauthenticated)
- Hero section with call-to-action
- Feature highlights (3 columns)
- Statistics (total users, resources, quizzes)
- Footer with links

#### Resource List Page
- Filter sidebar (left)
- Resource cards grid (main area)
- Pagination
- Sort options (newest, most downloaded, highest rated)

#### Resource Detail Page
- File preview/download section
- Resource metadata (title, description, uploader, date)
- Tags
- Rating widget (stars)
- Comments section (threaded)
- Related resources sidebar

#### Quiz List Page
- Quiz cards grid
- Filter by verification status, difficulty
- Search bar

#### Quiz Detail Page
- Quiz info (title, description, creator)
- Statistics (attempts, average score)
- "Start Quiz" button
- Leaderboard (optional)
- Comments section

#### Quiz Taking Page
- Question counter (1/10)
- Progress bar
- Question text (large)
- Multiple choice options (radio buttons)
- "Previous" and "Next" buttons
- "Submit Quiz" button (last question)

#### Quiz Results Page
- Score display (large, colorful)
- Congratulations message
- Question breakdown table
- "Retake Quiz" button
- Share score (optional)

#### Flashcard Deck List
- Deck cards grid
- Filter by category, tags
- "Create New Deck" button

#### Flashcard Study Interface
- Card display (front/back flip animation)
- "Know" and "Don't Know" buttons
- Progress indicator
- "Shuffle" and "Reset" options
- Exit button

#### User Profile Page
- Profile header (avatar, name, tagline, bio)
- Statistics (uploads, contributions)
- Tabs:
  - Uploaded Resources
  - Created Quizzes
  - Created Decks
  - Bookmarks
  - Activity History
- Edit profile button (own profile only)

#### Settings Page
- Account settings (email, password)
- Notification preferences
- Privacy settings
- Theme customization (optional)

---

## 6. SECURITY REQUIREMENTS

### 6.1 Authentication
- Password hashing with Django's PBKDF2
- Session-based authentication
- CSRF protection on all forms
- Force password change on first login

### 6.2 Authorization
- Role-based access control (Student, Professor, Admin)
- Professors can verify content
- Users can only edit/delete their own content
- Private resources only accessible to owner

### 6.3 Input Validation
- Server-side validation for all forms
- File type validation (whitelist: PDF, PPT, DOCX, TXT, images)
- File size limits (e.g., 25MB per file)
- SQL injection prevention (Django ORM)
- XSS prevention (template auto-escaping)

### 6.4 File Upload Security
- Store files in Supabase Storage (not local filesystem)
- Generate unique filenames (UUID-based)
- Validate file extensions and MIME types
- Scan uploads for malware (optional, 3rd-party service)

### 6.5 Rate Limiting
- Login attempts: Max 5 per 15 minutes per IP
- API requests: Max 100 per minute per user
- File uploads: Max 10 per hour per user

---

## 7. PERFORMANCE REQUIREMENTS

### 7.1 Response Times
- Page load: < 2 seconds
- Search results: < 1 second
- File download initiation: < 500ms
- Database queries: < 100ms

### 7.2 Scalability
- Support 1000+ concurrent users
- Handle 10,000+ resources
- Efficient pagination (50 items per page)
- Database indexing on frequently queried fields:
  - User.username, User.email, User.stud_id
  - Resource.title, Resource.tags, Resource.created_at
  - Quiz.title, Quiz.created_at

### 7.3 Caching Strategy
- Static files: Cached with WhiteNoise (1 year)
- User sessions: Redis cache (optional)
- Query results: Django's built-in cache (15 minutes)

---

## 8. DEPLOYMENT CONFIGURATION

### 8.1 Environment Variables
```
# Django Core
SECRET_KEY=<django-secret-key>
DEBUG=False
ALLOWED_HOSTS=<domain>,*.onrender.com
CSRF_TRUSTED_ORIGINS=https://<domain>

# Database
DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/<database>

# Supabase
SUPABASE_URL=<supabase-project-url>
SUPABASE_ANON_KEY=<anon-public-key>
SUPABASE_SERVICE_KEY=<service-role-key>
SUPABASE_BUCKET=papertrail-storage

# Email (Gmail SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<gmail-address>
EMAIL_HOST_PASSWORD=<gmail-app-password>
DEFAULT_FROM_EMAIL=<gmail-address>
```

### 8.2 Production Settings
- DEBUG=False
- SECURE_SSL_REDIRECT=True
- SESSION_COOKIE_SECURE=True
- CSRF_COOKIE_SECURE=True
- SECURE_BROWSER_XSS_FILTER=True
- SECURE_CONTENT_TYPE_NOSNIFF=True
- WhiteNoise for static files
- PostgreSQL connection pooling

### 8.3 Static Files
- Collected to `/staticfiles/` directory
- Served by WhiteNoise middleware
- CDN integration (optional)

---

## 9. ADDITIONAL FEATURES (OPTIONAL/FUTURE)

### 9.1 Advanced Search
- Elasticsearch integration
- Fuzzy matching
- Search suggestions

### 9.2 Analytics Dashboard
- User engagement metrics
- Popular resources
- Quiz performance trends
- Activity heatmaps

### 9.3 Social Features
- Follow users
- Activity feed
- Direct messaging
- Study groups

### 9.4 Collaboration Tools
- Shared collections
- Collaborative decks
- Group quizzes

### 9.5 Mobile App
- React Native or Flutter
- Offline mode
- Push notifications

---

## 10. TESTING REQUIREMENTS

### 10.1 Unit Tests
- Model methods
- Form validation
- Utility functions
- Coverage target: 80%+

### 10.2 Integration Tests
- User registration flow
- Resource upload and verification
- Quiz creation and taking
- Notification delivery

### 10.3 Manual Testing Checklist
- [ ] User registration (student, professor)
- [ ] Email verification
- [ ] Login/logout
- [ ] Password reset (3-step flow)
- [ ] Upload resource (file + external link)
- [ ] Resource verification (professor)
- [ ] Create and take quiz
- [ ] Create and study flashcard deck
- [ ] Bookmark resources
- [ ] Rate and comment
- [ ] Search and filter
- [ ] Notification system
- [ ] Dashboard metrics
- [ ] Mobile responsiveness

---

## 11. API ENDPOINTS (If REST API Needed)

### Authentication
- POST `/api/auth/register/` - User registration
- POST `/api/auth/login/` - User login
- POST `/api/auth/logout/` - User logout
- POST `/api/auth/password-reset/` - Request password reset

### Resources
- GET `/api/resources/` - List resources (with filters)
- POST `/api/resources/` - Create resource
- GET `/api/resources/{id}/` - Resource detail
- PUT `/api/resources/{id}/` - Update resource
- DELETE `/api/resources/{id}/` - Delete resource
- POST `/api/resources/{id}/bookmark/` - Bookmark resource
- POST `/api/resources/{id}/rate/` - Rate resource
- POST `/api/resources/{id}/comment/` - Comment on resource

### Quizzes
- GET `/api/quizzes/` - List quizzes
- POST `/api/quizzes/` - Create quiz
- GET `/api/quizzes/{id}/` - Quiz detail
- POST `/api/quizzes/{id}/attempt/` - Submit quiz attempt
- GET `/api/quizzes/{id}/attempts/` - User's attempts

### Flashcards
- GET `/api/decks/` - List decks
- POST `/api/decks/` - Create deck
- GET `/api/decks/{id}/` - Deck detail
- POST `/api/decks/{id}/cards/` - Add card to deck
- PUT `/api/decks/{id}/cards/{card_id}/` - Update card

### Notifications
- GET `/api/notifications/` - User's notifications
- PUT `/api/notifications/{id}/read/` - Mark as read
- DELETE `/api/notifications/{id}/` - Delete notification

---

## 12. MIGRATION NOTES

### Data Migration (If Rebuilding)
1. Export existing data:
   - Users (preserve passwords)
   - Resources with file URLs
   - Quizzes with questions/options
   - Flashcard decks with cards
   - Ratings, comments, bookmarks

2. Schema mapping:
   - Map old field names to new schema
   - Handle nullable/required changes
   - Preserve timestamps

3. File migration:
   - Keep existing Supabase storage URLs
   - No need to re-upload files

### Code Migration Strategy
1. Set up fresh Django project
2. Create apps: accounts, resources, quizzes, flashcards
3. Define models per this documentation
4. Migrate data from old database
5. Build views and templates
6. Test thoroughly before deployment

---

## 13. MAINTENANCE REQUIREMENTS

### Regular Tasks
- Database backups (daily)
- Security updates (monthly)
- Performance monitoring
- Error log review
- User feedback collection

### Support Channels
- Email: support@papertrail.com
- In-app help center
- User documentation/FAQ

---

## END OF DOCUMENTATION

This document provides complete specifications for rebuilding the PaperTrail system. All models, features, UI requirements, and business logic are detailed. Use this as the single source of truth for development.

**Last Updated**: December 1, 2025
**Version**: 2.0
**Status**: Ready for Development
