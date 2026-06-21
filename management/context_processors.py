from .models import ComplaintSuggestion


def sidebar_counts(request):
    pending_complaints = 0
    if request.user.is_authenticated and request.user.role in ['admin', 'staff']:
        pending_complaints = ComplaintSuggestion.objects.filter(status='pending').count()
    return {'pending_complaints': pending_complaints}
