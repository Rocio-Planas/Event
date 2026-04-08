from django.contrib import admin

# Register your models here.
from .models import ChatMessage, HandRaise, Poll, PollOption, PollVote, SatisfactionRating

admin.site.register(ChatMessage)
admin.site.register(HandRaise)
admin.site.register(Poll)
admin.site.register(PollOption)
admin.site.register(PollVote)
admin.site.register(SatisfactionRating)
