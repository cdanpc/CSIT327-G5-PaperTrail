from django.contrib.auth.decorators import login_required

@login_required
def add_study_reminder(request):
    from django.shortcuts import redirect
    from django.contrib import messages
    from ..models import StudyReminder
    from datetime import datetime
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        due_date_raw = request.POST.get('due_date', '').strip()
        due_dt = None
        if due_date_raw:
            try:
                due_dt = datetime.strptime(due_date_raw, "%Y-%m-%d")
            except Exception:
                due_dt = None
        
        if title and due_dt:
            StudyReminder.objects.create(user=request.user, title=title, due_date=due_dt)
            messages.success(request, 'Study reminder added successfully!')
        else:
            messages.error(request, 'Please provide a valid title and due date.')
    return redirect('accounts:student_dashboard')


@login_required
def toggle_study_reminder(request, pk):
    from django.shortcuts import redirect
    from ..models import StudyReminder
    
    reminder = StudyReminder.objects.filter(pk=pk, user=request.user).first()
    if reminder:
        reminder.completed = not reminder.completed
        reminder.save(update_fields=['completed'])
    return redirect('accounts:student_dashboard')


@login_required
def delete_study_reminder(request, pk):
    from django.shortcuts import redirect
    from ..models import StudyReminder
    
    reminder = StudyReminder.objects.filter(pk=pk, user=request.user).first()
    if reminder:
        reminder.delete()
    return redirect('accounts:student_dashboard')
