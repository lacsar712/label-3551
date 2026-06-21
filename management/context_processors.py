from .models import ComplaintSuggestion, Package


def sidebar_counts(request):
    pending_complaints = 0
    pending_packages = 0
    if request.user.is_authenticated and request.user.role in ['admin', 'staff']:
        pending_complaints = ComplaintSuggestion.objects.filter(status='pending').count()
        pending_packages = Package.objects.filter(status='pending').count()
    return {
        'pending_complaints': pending_complaints,
        'pending_packages': pending_packages,
    }
