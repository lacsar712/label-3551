from .models import ComplaintSuggestion, Package, Equipment
from django.utils import timezone


def sidebar_counts(request):
    pending_complaints = 0
    pending_packages = 0
    upcoming_maintenance = 0
    overdue_maintenance = 0
    if request.user.is_authenticated and request.user.role in ['admin', 'staff']:
        pending_complaints = ComplaintSuggestion.objects.filter(status='pending').count()
        pending_packages = Package.objects.filter(status='pending').count()
        today = timezone.localdate()
        thirty_days_later = today + timezone.timedelta(days=30)
        upcoming_maintenance = Equipment.objects.filter(
            next_maintenance_date__lte=thirty_days_later,
            next_maintenance_date__gte=today
        ).count()
        overdue_maintenance = Equipment.objects.filter(
            next_maintenance_date__lt=today
        ).count()
    return {
        'pending_complaints': pending_complaints,
        'pending_packages': pending_packages,
        'upcoming_maintenance': upcoming_maintenance,
        'overdue_maintenance': overdue_maintenance,
    }
