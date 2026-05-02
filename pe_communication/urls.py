from django.urls import path
from pe_communication import views

app_name = 'pe_communication'

urlpatterns = [
    path('send-notification/', views.SendManualNotificationView.as_view(), name='send_notification'),
    path('toggle-subscription/', views.toggle_activity_subscription, name='toggle_subscription'),
    path('unread-notifications/', views.get_unread_notifications, name='unread_notifications'),
    path('mark-notification-read/', views.mark_notification_read, name='mark_notification_read'),
    path('delete-notification/', views.delete_notification, name='delete_notification'),
    path('notifications/', views.NotificationListView.as_view(), name='notification_list'),
]