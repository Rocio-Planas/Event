import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from pe_communication.models import Notification
print('Total notifications:', Notification.objects.count())
print('Sample unread:', Notification.objects.filter(is_read=False).count())
print('Sample read:', Notification.objects.filter(is_read=True).count())
