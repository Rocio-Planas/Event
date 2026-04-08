from django.contrib import admin

# Register your models here.
# ve_streaming/admin.py
from .models import StreamingRoom

admin.site.register(StreamingRoom)
