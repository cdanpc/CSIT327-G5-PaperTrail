# QUICK START: Running Tests & Deployment
**Last Updated:** November 26, 2025

---

## ✅ CURRENT STATUS

```
✅ Code Review: COMPLETE (23 issues identified & documented)
✅ Bug Fixes: COMPLETE (Critical & High-priority fixed)
✅ Migrations: COMPLETE (Applied successfully)
👉 NEXT: Run 6 Test Scenarios (20-30 minutes)
👉 THEN: Deploy to Production
```

---

## 🚀 QUICK START GUIDE

### Step 1: Start Django Development Server
```powershell
cd "c:\Users\Dan\Documents\Academic Files\3RD YEAR\IM2\PaperTrail"
python manage.py runserver
```
✅ Should see: "Starting development server at http://127.0.0.1:8000/"

---

### Step 2: Run Test Scenario 1 (5 minutes)
**Test:** User A bookmarks deck, User B doesn't see it

```
1. Open http://127.0.0.1:8000/admin/ in Chrome
2. Login as admin (superuser)
3. Go to Flashcards → Decks
4. Click on any deck → Copy the deck ID
5. Open http://127.0.0.1:8000/flashcards/deck/<deck_id>/
6. Click the bookmark button (book icon in header)
7. ✅ Icon should fill in
8. ✅ Message should say "Deck bookmarked"
9. Open incognito window (Ctrl+Shift+N in Chrome)
10. Navigate to same deck URL
11. ✅ Icon should be EMPTY (not bookmarked)
12. ✅ This proves User A's bookmark not visible to User B

STATUS: [ ] PASSED [ ] FAILED
```

---

### Step 3: Run Test Scenario 2 (5 minutes)
**Test:** Toggle bookmark via form (with page reload)

```
1. On deck detail page (from Test 1)
2. Click bookmark icon again
3. ✅ Page should reload
4. ✅ Icon should EMPTY out
5. ✅ Message should say "Bookmark removed"
6. Click bookmark again
7. ✅ Icon should FILL in again
8. ✅ Verify no errors in browser console

STATUS: [ ] PASSED [ ] FAILED
```

---

### Step 4: Run Test Scenario 3 (5 minutes)
**Test:** Toggle bookmark via AJAX (no page reload)

```
1. Go to Flashcards → Deck List
2. Hover over any deck card
3. Click bookmark icon (should NOT reload page)
4. ✅ Icon should fill immediately
5. ✅ Should see small toast notification
6. Click bookmark icon again
7. ✅ Icon should empty immediately
8. ✅ Toast should say "Removed"
9. Open browser console (F12)
10. ✅ Should show 200 OK for AJAX request
11. ✅ No errors in console

STATUS: [ ] PASSED [ ] FAILED
```

---

### Step 5: Run Test Scenario 4 (5 minutes)
**Test:** Unified bookmark list shows flashcards

```
1. Bookmark 3 different flashcard decks (click bookmark on deck list)
2. Go to Dashboard → My Bookmarks
3. ✅ Should see "Flashcards" section
4. ✅ Should list the 3 decks you bookmarked
5. ✅ Count should show "3"
6. Click on one of the flashcard bookmarks
7. ✅ Should navigate to deck detail page
8. ✅ Bookmark icon should be FILLED

STATUS: [ ] PASSED [ ] FAILED
```

---

### Step 6: Run Test Scenario 5 (5 minutes)
**Test:** Admin can moderate quizzes

```
1. Go to Quizzes → Create Quiz (as any user)
2. Make it PUBLIC
3. Don't publish yet (leave as pending)
4. Go to admin panel → Login as admin
5. Go to Quizzes → Moderation
6. ✅ Should see list of pending quizzes
7. ✅ Should see the quiz you just created
8. Click "Approve" button
9. ✅ Should see success message
10. ✅ Quiz status should change to "verified"
11. Go back, create another quiz, try "Reject"
12. ✅ Should see rejection message
13. ✅ Quiz should be marked as "rejected"

STATUS: [ ] PASSED [ ] FAILED
```

---

### Step 7: Run Test Scenario 6 (5 minutes)
**Test:** Non-admin cannot access moderation

```
1. Logout (if logged in as admin)
2. Login as regular student
3. Try to access: http://127.0.0.1:8000/quizzes/moderation/
4. ✅ Should redirect to home or show 403 error
5. ✅ Should see message like "Permission denied"
6. ✅ Should NOT see moderation interface
7. Try to access: http://127.0.0.1:8000/flashcards/moderation/
8. ✅ Should redirect or show 403
9. ✅ Student cannot access flashcard moderation either

STATUS: [ ] PASSED [ ] FAILED
```

---

## 📋 VERIFICATION CHECKLIST

After running all 6 tests, verify:

- [ ] Test 1: PASSED ✅
- [ ] Test 2: PASSED ✅
- [ ] Test 3: PASSED ✅
- [ ] Test 4: PASSED ✅
- [ ] Test 5: PASSED ✅
- [ ] Test 6: PASSED ✅
- [ ] No errors in Django console
- [ ] No errors in browser F12 console
- [ ] Admin panel loads without errors
- [ ] All migrations applied (python manage.py showmigrations)

---

## 🔍 QUICK VERIFICATION COMMANDS

```powershell
# Verify migrations applied
python manage.py showmigrations flashcards
# Should show all with [X]

# Verify DeckBookmark model exists
python manage.py shell
# >>> from flashcards.models import DeckBookmark
# >>> DeckBookmark.objects.count()
# >>> exit()

# Check for any errors
python manage.py check
# Should show "System check identified no issues"
```

---

## ✅ IF ALL TESTS PASS

Congratulations! You're ready to deploy. Follow these steps:

```powershell
# 1. Stop development server (Ctrl+C)

# 2. Create database backup
Copy-Item db.sqlite3 db.sqlite3.backup_20251126.bak

# 3. Review deployment checklist
# See: DEPLOYMENT_CHECKLIST.md

# 4. Deploy to production
# Follow steps in DEPLOYMENT_CHECKLIST.md

# 5. Monitor logs after deployment
# Watch for any errors in the first 24 hours
```

---

## ❌ IF TESTS FAIL

**Don't panic!** Follow these troubleshooting steps:

### Issue: "Permission denied" on test 5 or 6
```powershell
# Check if user is admin
python manage.py shell
# >>> from django.contrib.auth.models import User
# >>> admin = User.objects.get(username='admin')
# >>> print(admin.is_staff, admin.is_superuser)
# Should show: True True
```

### Issue: Bookmark icon not changing
```powershell
# Check if DeckBookmark imported correctly
python manage.py shell
# >>> from flashcards.models import DeckBookmark
# >>> print(DeckBookmark._meta.unique_together)
# Should show: (('user', 'deck'),)

# Check browser console for errors (F12)
# Look for CSRF token errors or JavaScript errors
```

### Issue: Migration errors
```powershell
# Verify migration is applied
python manage.py showmigrations flashcards
# Last one should be: [X] 0009_remove_deck_is_bookmarked_deckbookmark

# If not applied, run:
python manage.py migrate flashcards
```

### Issue: "is_bookmarked" field still referenced
```powershell
# Check admin.py was updated
# Should NOT have 'is_bookmarked' in list_display
type flashcards/admin.py | findstr "is_bookmarked"
# Should return nothing

# Check views.py uses DeckBookmark, not field
type flashcards/views.py | findstr "is_bookmarked"
# Should return nothing
```

---

## 📊 RESULTS SUMMARY

**Fill this out after completing all tests:**

```
Test Date: __________________
Tester Name: __________________
Environment: Staging / Production

TEST RESULTS:
[ ] Test 1: User isolation - PASSED / FAILED
[ ] Test 2: Form toggle - PASSED / FAILED
[ ] Test 3: AJAX toggle - PASSED / FAILED
[ ] Test 4: Unified bookmarks - PASSED / FAILED
[ ] Test 5: Admin moderation - PASSED / FAILED
[ ] Test 6: Non-admin blocked - PASSED / FAILED

OVERALL STATUS:
[ ] ALL TESTS PASSED - APPROVED FOR DEPLOYMENT ✅
[ ] SOME TESTS FAILED - NEEDS FIXES 🔧
[ ] CRITICAL FAILURE - ROLLBACK 🚨

Comments:
_________________________________________________
_________________________________________________

Tester Signature: __________________ Date: __________
```

---

## 📞 NEED HELP?

1. **Check the detailed test guide:** TEST_SCENARIOS.md
2. **Check deployment guide:** DEPLOYMENT_CHECKLIST.md
3. **Check code changes:** FIXES_IMPLEMENTED.md
4. **Check quality assessment:** CODE_QUALITY_ASSESSMENT.md
5. **Check executive summary:** EXECUTIVE_SUMMARY.md

---

## 🎉 YOU'RE DONE!

Once all 6 tests pass and you've verified the checklist, you have successfully:

✅ Fixed critical flashcard bookmark bug  
✅ Fixed high-priority quiz permissions  
✅ Applied database migrations  
✅ Verified all changes work correctly  
✅ Documented everything  

You're ready to deploy! 🚀

---

**Quick Reference Cards Created:**
- TEST_SCENARIOS.md - Detailed test procedures
- DEPLOYMENT_CHECKLIST.md - Pre/post deployment steps
- EXECUTIVE_SUMMARY.md - High-level overview
- This file - Quick start guide

All documentation located in: `c:\Users\Dan\Documents\Academic Files\3RD YEAR\IM2\PaperTrail\`

