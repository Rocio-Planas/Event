# Create your views here.

# ve_invitations/views.py
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from virtualEvent.models import VirtualEvent
from .models import EventFollower, Invitation


@login_required
def follow_event(request, event_id):
    event = get_object_or_404(VirtualEvent, pk=event_id)
    # Verificar si ya sigue
    follow, created = EventFollower.objects.get_or_create(
        user=request.user, event=event
    )
    if not created:
        # Ya sigue, entonces lo eliminamos (toggle)
        follow.delete()
        messages.success(request, f'Has dejado de seguir "{event.title}".')
    else:
        messages.success(
            request, f'Ahora sigues "{event.title}". Recibirás recordatorios.'
        )
    return redirect("virtualEvent:event_detail", pk=event_id)


# Opcional: vista AJAX para seguir sin recargar
@login_required
def follow_event_ajax(request, event_id):
    event = get_object_or_404(VirtualEvent, pk=event_id)
    follow, created = EventFollower.objects.get_or_create(
        user=request.user, event=event
    )
    if not created:
        follow.delete()
        following = False
    else:
        following = True
    return JsonResponse({"following": following, "count": event.followers.count()})


def accept_invitation(request, token):
    invitation = get_object_or_404(Invitation, token=token)
    # Opcional: invitation.accepted = True; invitation.save()
    return redirect(
        "ve_streaming:waiting_room", unique_link=invitation.event.unique_link
    )
