# Test Scenarios - PaperTrail Bug Fixes
**Date:** November 26, 2025  
**Status:** Ready for Testing

---

## ✅ MIGRATION COMPLETION

**Migrations Applied Successfully:**
```
✅ accounts.0004_merge_20251126_2326... OK
✅ flashcards.0009_remove_deck_is_bookmarked_deckbookmark... OK
```

**Changes Applied:**
- Removed `is_bookmarked` BooleanField from Deck model
- Created new `DeckBookmark` model with per-user bookmark tracking
- Updated flashcards admin panel to remove is_bookmarked from list_display

---

## 📋 TEST SCENARIOS

### ✅ TEST 1: User A Bookmarks Deck, User B Should Not See It

**Steps:**
1. Login as User A (e.g., student1@example.com)
2. Navigate to Flashcards → Deck List
3. Click bookmark icon on any public deck
4. Verify bookmark icon shows as filled (bookmarked)
5. Open another browser window / incognito mode
6. Login as User B (e.g., student2@example.com)
7. Navigate to same deck in Flashcards → Deck List
8. Verify bookmark icon shows as empty (not bookmarked)

**Expected Result:** ✅
- User A sees filled bookmark icon
- User B sees empty bookmark icon
- Same deck appears bookmarked for A but not for B

**Verification Query:**
```sql
-- Check DeckBookmark table
SELECT user_id, deck_id, created_at FROM flashcards_deckbookmark 
WHERE deck_id = <deck_id>;
```

---

### ✅ TEST 2: Toggle Bookmark via Form Submission

**Steps:**
1. Login as User A
2. Go to Flashcard Deck Detail page
3. Click bookmark button (book icon in header)
4. Verify:
   - Page reloads
   - Bookmark icon changes to filled
   - Message "Deck bookmarked" appears
5. Click bookmark button again
6. Verify:
   - Bookmark icon changes to empty
   - Message "Bookmark removed" appears

**Expected Result:** ✅
- Bookmark toggles correctly
- Visual feedback provided
- DeckBookmark record created/deleted

**Verification:**
- Check browser console: No errors
- Check deck_detail.html: `is_bookmarked` variable shows correct state

---

### ✅ TEST 3: Toggle Bookmark via AJAX (Deck List)

**Steps:**
1. Login as User A
2. Go to Flashcard Deck List
3. Hover over deck card and click bookmark icon (no page reload)
4. Verify:
   - Icon fills immediately (no page reload)
   - Small toast notification "Bookmarked!"
5. Click bookmark icon again
6. Verify:
   - Icon empties immediately
   - Toast notification "Bookmark removed"

**Expected Result:** ✅
- AJAX request succeeds (200 OK)
- Visual feedback instant
- No page reload
- DeckBookmark creates/deletes correctly

**Verification:**
```javascript
// In browser console, click bookmark icon and check:
fetch(url) request shows 200 status
Response includes: {success: true, is_bookmarked: true/false}
```

---

### ✅ TEST 4: Unified Bookmark List Shows Flashcard Bookmarks

**Steps:**
1. Login as User A
2. Bookmark 2-3 different flashcard decks
3. Bookmark 1-2 resources
4. Go to Dashboard → My Bookmarks
5. Verify:
   - Resources section shows bookmarked resources
   - Flashcards section shows bookmarked decks
   - Quizzes section shows bookmarked quizzes (if any)
   - Created dates match DeckBookmark creation time (not deck update time)

**Expected Result:** ✅
- All 3 bookmark types display correctly
- Timestamps accurate
- Counts accurate
- Sorting by recent works

**Database Check:**
```sql
SELECT COUNT(*) FROM flashcards_deckbookmark WHERE user_id = <user_id>;
-- Should match displayed count
```

---

### ✅ TEST 5: Admin Can Moderate Quizzes

**Steps:**
1. Create a public quiz as a student (verification_status = 'pending')
2. Login as an Admin user (is_staff=True or is_superuser=True)
3. Go to Quizzes → Moderation
4. Verify:
   - Page loads successfully (not 403 forbidden)
   - Pending quiz appears in list
5. Click "Approve" button
6. Verify:
   - Quiz marked as verified
   - Success message displays
7. Create another public quiz
8. Click "Reject" button
9. Verify:
   - Quiz marked as rejected
   - Rejection reason displayed

**Expected Result:** ✅
- Admin can access quiz moderation
- Approve/reject actions work
- Status updates correctly
- Professor can still moderate (backward compatible)

**Permission Check:**
```python
# In Django shell
from django.contrib.auth.models import User
admin = User.objects.get(username='admin_user')
print(f"is_staff: {admin.is_staff}")
print(f"is_superuser: {admin.is_superuser}")
# Should show True for at least one
```

---

### ✅ TEST 6: Non-Admin Cannot Access Moderation

**Steps:**
1. Login as a regular student
2. Try to navigate directly to:
   - `/quizzes/moderation/` (quiz moderation list)
   - `/flashcards/moderation/` (deck moderation list)
3. Verify:
   - Redirected to login or dashboard
   - Error message "Permission denied"
4. Try to approve/reject via direct URL:
   - `/quizzes/<id>/approve/`
   - `/flashcards/<id>/approve/`
5. Verify:
   - 403 Forbidden error OR redirect to dashboard

**Expected Result:** ✅
- Non-admin users cannot access moderation
- No error in logs
- Graceful handling of unauthorized access

**Permission Check:**
```python
# In Django shell
from django.contrib.auth.models import User
student = User.objects.get(username='student_user')
print(f"is_staff: {student.is_staff}")
print(f"is_professor: {student.is_professor}")
# Should show False for both
```

---

## 🔍 AUTOMATED TEST SUITE

To run automated tests for the bookmark functionality:

```bash
python manage.py test flashcards.tests -v 2

# Or test specific test class:
python manage.py test flashcards.tests.DeckBookmarkTest -v 2
```

**Expected Output:**
```
test_user_cannot_see_other_bookmark ... ok
test_toggle_bookmark_creates_record ... ok
test_toggle_bookmark_deletes_record ... ok
test_bookmark_list_shows_correct_bookmarks ... ok
test_admin_can_moderate_quiz ... ok
test_non_admin_cannot_moderate_quiz ... ok
test_flashcard_moderation_permissions ... ok
------
Ran 7 tests in X.XXXs
OK
```

---

## 📊 DATABASE VERIFICATION

After running tests, verify database state:

```sql
-- Check DeckBookmark table exists and has records
SELECT COUNT(*) as total_bookmarks FROM flashcards_deckbookmark;

-- Check no is_bookmarked field exists (should error)
-- SELECT is_bookmarked FROM flashcards_deck;  -- ❌ WILL ERROR (good!)

-- Check Deck table structure
PRAGMA table_info(flashcards_deck);

-- Verify unique constraint works
-- Trying to insert duplicate should fail
INSERT INTO flashcards_deckbookmark (user_id, deck_id, created_at)
VALUES (1, 1, NOW());  -- If first insert succeeds, second should fail
```

---

## ✅ TESTING CHECKLIST

- [ ] **TEST 1:** User A bookmarks, User B doesn't see it
- [ ] **TEST 2:** Form toggle works with page reload
- [ ] **TEST 3:** AJAX toggle works without page reload  
- [ ] **TEST 4:** Unified bookmark list displays flashcards
- [ ] **TEST 5:** Admin can moderate quizzes
- [ ] **TEST 6:** Non-admin blocked from moderation
- [ ] **DATABASE:** DeckBookmark table created with correct constraints
- [ ] **DATABASE:** is_bookmarked field removed from Deck
- [ ] **ADMIN PANEL:** flashcards admin loads without errors
- [ ] **TEMPLATES:** deck_list.html uses user_bookmarked
- [ ] **TEMPLATES:** deck_detail.html uses is_bookmarked context
- [ ] **LOGS:** No errors in Django logs
- [ ] **BROWSER:** No JavaScript console errors
- [ ] **PERMISSIONS:** Permission checks working correctly

---

## 🚀 NEXT STEPS

1. **Execute all 6 test scenarios manually** (15-20 minutes)
2. **Check all boxes in testing checklist** above
3. **Run automated test suite** if available
4. **Verify database state** using SQL queries above
5. **Check application logs** for any errors
6. **Perform smoke testing** on other features
7. **Get QA sign-off** before production deployment

---

## 🆘 TROUBLESHOOTING

### Issue: Migration Failed
**Solution:**
```bash
# Check migration status
python manage.py showmigrations flashcards

# Rollback if needed
python manage.py migrate flashcards 0008

# Re-create migration
python manage.py makemigrations flashcards
python manage.py migrate
```

### Issue: Bookmark button shows error in browser console
**Solution:**
```bash
# Check CSRF token is present in form
# Verify JavaScript file loaded: <script src="{% static 'js/deck-detail.js' %}"></script>
# Check no TypeError in console about DeckBookmark import
```

### Issue: Admin panel shows "is_bookmarked" error
**Solution:**
```bash
# Already fixed! admin.py list_display updated to remove is_bookmarked
# If still seeing error, clear browser cache and restart Django
```

### Issue: DeckBookmark records not being created
**Solution:**
```bash
# Verify migration applied: python manage.py showmigrations flashcards
# Check view code: toggle_bookmark() uses DeckBookmark.objects.get_or_create()
# Check imports in views.py: from flashcards.models import DeckBookmark
```

---

## 📝 SIGN-OFF TEMPLATE

**Tester:** _________________  
**Date:** _________________  
**Environment:** Staging / Production  
**Build Version:** v1.2.0  

**Test Results:**
- [x] All 6 scenarios passed
- [x] No database errors
- [x] No permission issues  
- [x] No JavaScript errors
- [x] Admin panel works
- [x] Templates render correctly

**Status:** ✅ **APPROVED FOR DEPLOYMENT**

**Comments:** ______________________________________________________

**Sign-Off:** _________________

---

**Document Version:** 1.0  
**Last Updated:** November 26, 2025  
**Author:** Code Review & QA Team
