from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json
from virtualEvent.models import VirtualEvent
import re


def waiting_room(request, unique_link):
    event = get_object_or_404(VirtualEvent, unique_link=unique_link)
    start_iso = event.start_datetime.isoformat()
    return render(
        request,
        "ve_streaming/waiting_room.html",
        {
            "event": event,
            "start_iso": start_iso,
        },
    )


def clean_youtube_embed(url):
    """Convierte cualquier URL de YouTube en una URL de embed limpia."""
    if not url:
        return ""
    patterns = [
        r"youtube\.com/embed/([a-zA-Z0-9_-]+)",
        r"youtu\.be/([a-zA-Z0-9_-]+)",
        r"youtube\.com/watch\?v=([a-zA-Z0-9_-]+)",
        r"youtube\.com/shorts/([a-zA-Z0-9_-]+)",
    ]
    video_id = None
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            break
    if video_id:
        return f"https://www.youtube.com/embed/{video_id}"
    return url


def streaming_room(request, unique_link):
    event = get_object_or_404(VirtualEvent, unique_link=unique_link)

    # El organizador es el creador del evento (sin forzados de pruebas)
    is_organizer = request.user.is_authenticated and request.user == event.created_by
    raw_embed = event.settings.get("youtube_embed", "")
    youtube_embed = clean_youtube_embed(raw_embed)
    return render(
        request,
        "ve_streaming/streaming_room.html",
        {
            "event": event,
            "event_id": event.id,
            "is_organizer": is_organizer,
            "youtube_embed": youtube_embed,
        },
    )


@login_required
def save_youtube_embed(request, event_id):
    if request.method == "POST":
        event = get_object_or_404(VirtualEvent, pk=event_id, created_by=request.user)
        data = json.loads(request.body)
        embed_code = data.get("embed_code", "")
        if 'src="' in embed_code:
            match = re.search(r'src="([^"]+)"', embed_code)
            if match:
                embed_code = match.group(1)
        embed_code = clean_youtube_embed(embed_code)
        event.settings["youtube_embed"] = embed_code
        event.save()
        return JsonResponse({"status": "ok"})
    return JsonResponse({"error": "Invalid request"}, status=400)


def event_id_by_slug(request, unique_link):
    from virtualEvent.models import VirtualEvent

    event = get_object_or_404(VirtualEvent, unique_link=unique_link)
    return JsonResponse({"event_id": event.id})
