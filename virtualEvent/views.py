from datetime import timedelta

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from .models import EventAnalytics, OnlineViewer, VirtualEvent
from ve_streaming.models import StreamingRoom
from ve_invitations.models import Invitation
from ve_invitations.models import EventFollower
from ve_invitations.utils import send_invitation_email
import uuid
import re
import json
from django.views.decorators.csrf import csrf_exempt
from .report_generator import generate_event_pdf  # type: ignore
from .utils.calendar_utils import generate_ics  # type: ignore


# Lista de eventos (pública)
def event_list(request):
    events = VirtualEvent.objects.all()
    return render(request, "virtualEvent/event_list.html", {"events": events})


def event_detail(request, pk):
    event = get_object_or_404(VirtualEvent, pk=pk)

    # Calculate end datetime
    end_datetime = event.start_datetime + timedelta(minutes=event.duration_minutes)

    # Formats for Google Calendar and display
    start_google = event.start_datetime.strftime("%Y%m%dT%H%M%S")
    end_google = end_datetime.strftime("%Y%m%dT%H%M%S")
    display_date = event.start_datetime.strftime("%d/%m/%Y %H:%M")

    # Prepare context (all keys in English)
    context = {
        "event": {
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "image": (
                event.image.url if event.image else "/static/images/default-event.jpg"
            ),
            "display_date": display_date,
            "start_google": start_google,
            "end_google": end_google,
            "type": "Virtual",
            "duration_minutes": event.duration_minutes,
            "category": event.category,
            "privacy": event.privacy,
            "organizer": event.created_by.get_full_name() or event.created_by.username,
        },
        "is_following": request.user.is_authenticated
        and EventFollower.objects.filter(user=request.user, event=event).exists(),
        "reviews": [],  # placeholder
        "average_rating": 0,  # placeholder
        "total_reviews": 0,  # placeholder
    }
    return render(request, "virtualEvents/event_detail.html", context)


# Crear evento (solo organizador autenticado)
@login_required
def event_create(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        category = request.POST.get("category")
        custom_category = request.POST.get("custom_category", "").strip()
        image = request.FILES.get("event_image")
        start_time_str = request.POST.get("start_time")
        duration = request.POST.get("duration")
        access_type = request.POST.get("access_type")
        invitations_text = request.POST.get("invitations", "")

        errors = {}
        if not title:
            errors["title"] = "El título es obligatorio"
        if not description:
            errors["description"] = "La descripción es obligatoria"
        if not start_time_str:
            errors["start_time"] = "Fecha y hora son obligatorias"
        else:
            from django.utils.dateparse import parse_datetime
            from django.utils.timezone import make_aware

            start_datetime = parse_datetime(start_time_str)
            if not start_datetime:
                errors["start_time"] = "Formato inválido"
            else:
                start_datetime = make_aware(start_datetime)
                if start_datetime < timezone.now():
                    errors["start_time"] = "La fecha no puede ser pasada"
        if not duration:
            errors["duration"] = "Duración requerida"
        else:
            try:
                duration_minutes = int(duration)
                if duration_minutes < 1:
                    errors["duration"] = "Mínimo 1 minuto"
            except ValueError:
                errors["duration"] = "Número inválido"
        if not access_type:
            errors["access_type"] = "Selecciona tipo de acceso"
        if category == "custom" and not custom_category:
            errors["custom_category"] = "Ingresa categoría personalizada"

        if errors:
            context = {
                "errors": errors,
                "title": title,
                "description": description,
                "category": category,
                "custom_category": custom_category,
                "start_time": start_time_str,
                "duration": duration,
                "access_type": access_type,
                "invitations_text": invitations_text,
                "predefined_categories": VirtualEvent.PREDEFINED_CATEGORIES,
            }
            return render(request, "virtualEvents/event_form.html", context)

        image_path = None
        if image:
            ext = image.name.split(".")[-1]
            image_name = f"event_{uuid.uuid4().hex}.{ext}"
            image_path = default_storage.save(
                f"event_images/{image_name}", ContentFile(image.read())
            )

        final_category = custom_category if category == "custom" else category

        event = VirtualEvent.objects.create(
            title=title,
            description=description,
            category=final_category,
            custom_category=custom_category if category == "custom" else "",
            image=image_path,
            start_datetime=start_datetime,
            duration_minutes=duration_minutes,
            privacy=access_type,
            created_by=request.user,
        )

        StreamingRoom.objects.create(event=event)

        if access_type == "private" and invitations_text:
            emails = [
                email.strip() for email in invitations_text.split(",") if email.strip()
            ]
            for email in emails:
                token = uuid.uuid4().hex
                Invitation.objects.create(event=event, email=email, token=token)
                send_invitation_email(email, event, token)

        messages.success(request, f'Evento "{event.title}" creado exitosamente.')
        return redirect("virtualEvent:organizer_dashboard", event_id=event.id)

    return render(
        request,
        "virtualEvents/event_form.html",
        {"predefined_categories": VirtualEvent.PREDEFINED_CATEGORIES},
    )


# Editar evento
@login_required
def event_edit(request, pk):
    event = get_object_or_404(VirtualEvent, pk=pk, created_by=request.user)
    if request.method == "POST":
        event.title = request.POST.get("title")
        event.description = request.POST.get("description")
        category = request.POST.get("category")
        custom_category = request.POST.get("custom_category", "").strip()
        event.category = custom_category if category == "custom" else category
        event.custom_category = custom_category if category == "custom" else ""

        if request.FILES.get("event_image"):
            if event.image:
                default_storage.delete(event.image.name)
            image = request.FILES["event_image"]
            ext = image.name.split(".")[-1]
            image_name = f"event_{uuid.uuid4().hex}.{ext}"
            event.image = default_storage.save(
                f"event_images/{image_name}", ContentFile(image.read())
            )

        start_time_str = request.POST.get("start_time")
        if start_time_str:
            from django.utils.dateparse import parse_datetime
            from django.utils.timezone import make_aware

            start_datetime = parse_datetime(start_time_str)
            if start_datetime:
                event.start_datetime = make_aware(start_datetime)
        event.duration_minutes = request.POST.get("duration")
        event.privacy = request.POST.get("access_type")
        event.save()

        if event.privacy == "private":
            invitations_text = request.POST.get("emails", "")
            if invitations_text:
                emails = [
                    email.strip()
                    for email in invitations_text.split(",")
                    if email.strip()
                ]
                for email in emails:
                    if not Invitation.objects.filter(event=event, email=email).exists():
                        token = uuid.uuid4().hex
                        Invitation.objects.create(event=event, email=email, token=token)
                        send_invitation_email(email, event, token)

        messages.success(request, "Evento actualizado correctamente.")
        return redirect("virtualEvent:organizer_dashboard", event_id=event.id)

    context = {
        "event": event,
        "predefined_categories": VirtualEvent.PREDEFINED_CATEGORIES,
        "editing": True,
    }
    return render(request, "virtualEvents/event_form.html", context)


# Eliminar evento
@login_required
def event_delete(request, pk):
    event = get_object_or_404(VirtualEvent, pk=pk, created_by=request.user)
    if request.method == "POST":
        event_title = event.title
        event.delete()
        messages.success(request, f'Evento "{event_title}" eliminado.')
        return redirect("core:home")
    return render(request, "virtualEvents/event_confirm_delete.html", {"event": event})


# Panel del organizador
@login_required
def organizer_dashboard(request, event_id):
    event = get_object_or_404(VirtualEvent, pk=event_id, created_by=request.user)
    invitations = Invitation.objects.filter(event=event)

    youtube_embed = event.settings.get("youtube_embed", "")
    if youtube_embed and 'src="' in youtube_embed:
        match = re.search(r'src="([^"]+)"', youtube_embed)
        if match:
            youtube_embed = match.group(1)

    if request.method == "POST":
        event.title = request.POST.get("title", event.title)
        event.description = request.POST.get("description", event.description)
        start_time_str = request.POST.get("start_time")
        if start_time_str:
            from django.utils.dateparse import parse_datetime
            from django.utils.timezone import make_aware

            start_datetime = parse_datetime(start_time_str)
            if start_datetime:
                event.start_datetime = make_aware(start_datetime)
        duration = request.POST.get("duration")
        if duration:
            event.duration_minutes = int(duration)
        event.privacy = request.POST.get("access_type", event.privacy)
        event.save()

        if request.FILES.get("event_image"):
            if event.image:
                default_storage.delete(event.image.name)
            image = request.FILES["event_image"]
            ext = image.name.split(".")[-1]
            image_name = f"event_{uuid.uuid4().hex}.{ext}"
            event.image = default_storage.save(
                f"event_images/{image_name}", ContentFile(image.read())
            )
            event.save()

        youtube_url = request.POST.get("youtube_url", "")
        if youtube_url:
            if "?" in youtube_url:
                youtube_url = youtube_url.split("?")[0]
            if "youtube.com/embed/" not in youtube_url:
                if "youtube.com/watch?v=" in youtube_url:
                    video_id = youtube_url.split("v=")[1].split("&")[0]
                    youtube_url = f"https://www.youtube.com/embed/{video_id}"
                elif "youtu.be/" in youtube_url:
                    video_id = youtube_url.split("youtu.be/")[1].split("?")[0]
                    youtube_url = f"https://www.youtube.com/embed/{video_id}"
            event.settings["youtube_embed"] = youtube_url
            event.save()

        if event.privacy == "private":
            emails_text = request.POST.get("emails", "")
            if emails_text:
                emails = [e.strip() for e in emails_text.split(",") if e.strip()]
                for email in emails:
                    if not Invitation.objects.filter(event=event, email=email).exists():
                        token = uuid.uuid4().hex
                        Invitation.objects.create(event=event, email=email, token=token)
                        send_invitation_email(email, event, token)

        messages.success(request, "Evento actualizado correctamente.")
        return redirect("virtualEvent:organizer_dashboard", event_id=event.id)

    invite_link = request.build_absolute_uri(
        reverse("ve_streaming:waiting_room", args=[event.unique_link])
    )
    invited_emails = ", ".join([inv.email for inv in invitations])
    start_time_str = (
        event.start_datetime.strftime("%Y-%m-%dT%H:%M") if event.start_datetime else ""
    )

    context = {
        "event": event,
        "invitations": invitations,
        "invited_emails": invited_emails,
        "youtube_embed": youtube_embed,
        "invite_link": invite_link,
        "start_time_str": start_time_str,
    }
    return render(request, "virtualEvents/organizer_dashboard.html", context)


# Generar nueva invitación vía AJAX
@login_required
def generate_invitation(request, event_id):
    if request.method == "POST":
        event = get_object_or_404(VirtualEvent, pk=event_id, created_by=request.user)
        email = request.POST.get("email")
        if email:
            token = uuid.uuid4().hex
            Invitation.objects.create(event=event, email=email, token=token)
            send_invitation_email(email, event, token)
            return JsonResponse(
                {"status": "ok", "message": f"Invitación enviada a {email}"}
            )
    return JsonResponse({"status": "error", "message": "Email requerido"}, status=400)


def event_metrics(request, event_id):
    event = get_object_or_404(VirtualEvent, pk=event_id)
    analytics, _ = EventAnalytics.objects.get_or_create(event=event)

    cutoff = timezone.now() - timezone.timedelta(minutes=1)
    current_viewers = OnlineViewer.objects.filter(
        event=event, last_heartbeat__gte=cutoff
    ).count()

    elapsed_seconds = 0
    if event.start_datetime <= timezone.now():
        elapsed = timezone.now() - event.start_datetime
        elapsed_seconds = int(elapsed.total_seconds())
    elapsed_str = f"{elapsed_seconds // 3600:02d}:{(elapsed_seconds % 3600) // 60:02d}:{elapsed_seconds % 60:02d}"

    participation = 0
    if analytics.unique_viewers > 0:
        participation = int(
            (analytics.total_poll_votes / analytics.unique_viewers) * 100
        )

    data = {
        "active_viewers": current_viewers,
        "total_messages": analytics.total_messages,
        "total_hands": analytics.total_hands,
        "total_poll_votes": analytics.total_poll_votes,
        "unique_viewers": analytics.unique_viewers,
        "average_satisfaction": analytics.average_satisfaction,
        "elapsed_time": elapsed_str,
        "participation_percent": participation,
    }
    return JsonResponse(data)


@login_required
def save_youtube_embed(request, event_id):
    if request.method == "POST":
        event = get_object_or_404(VirtualEvent, pk=event_id, created_by=request.user)
        data = json.loads(request.body)
        youtube_url = data.get("youtube_url", "")
        if youtube_url:
            if "?" in youtube_url:
                youtube_url = youtube_url.split("?")[0]
            if "youtube.com/watch?v=" in youtube_url:
                video_id = youtube_url.split("v=")[1].split("&")[0]
                youtube_url = f"https://www.youtube.com/embed/{video_id}"
            elif "youtu.be/" in youtube_url:
                video_id = youtube_url.split("youtu.be/")[1].split("?")[0]
                youtube_url = f"https://www.youtube.com/embed/{video_id}"
        event.settings["youtube_embed"] = youtube_url
        event.save(update_fields=["settings"])
        return JsonResponse({"status": "ok", "url": youtube_url})
    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def update_heartbeat(request, event_id):
    if request.method == "POST":
        event = get_object_or_404(VirtualEvent, pk=event_id)
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        ip = request.META.get("REMOTE_ADDR")
        OnlineViewer.objects.update_or_create(
            event=event,
            session_key=session_key,
            defaults={"ip_address": ip, "last_heartbeat": timezone.now()},
        )
        return JsonResponse({"status": "ok"})
    return JsonResponse({"error": "Método no permitido"}, status=405)


@login_required
def generate_pdf_report(request, event_id):
    event = get_object_or_404(VirtualEvent, pk=event_id, created_by=request.user)
    analytics, _ = EventAnalytics.objects.get_or_create(event=event)
    from ve_chat.models import ChatMessage

    room = event.streaming_room
    messages = ChatMessage.objects.filter(room=room).order_by("timestamp")
    anonymous_questions = messages.filter(anonymous=True)

    messages_per_hour = {}
    for msg in messages:
        hour = msg.timestamp.strftime("%Y-%m-%d %H:00")
        messages_per_hour[hour] = messages_per_hour.get(hour, 0) + 1

    context = {
        "event": event,
        "analytics": analytics,
        "total_messages": messages.count(),
        "anonymous_questions": anonymous_questions,
        "messages_per_hour": messages_per_hour,
        "generated_at": timezone.now(),
    }
    pdf_buffer = generate_event_pdf(context)
    response = HttpResponse(pdf_buffer, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="reporte_{event.id}_{timezone.now().date()}.pdf"'
    )
    return response


@login_required
def upload_material(request, event_id):
    event = get_object_or_404(VirtualEvent, pk=event_id, created_by=request.user)
    if request.method == "POST":
        recording_url = request.POST.get("recording_url", "").strip()
        if recording_url:
            if "materials" not in event.__dict__:
                event.materials = {}
            event.materials["recording"] = recording_url

        if request.FILES.get("slides"):
            slides_file = request.FILES["slides"]
            ext = slides_file.name.split(".")[-1]
            safe_name = f"material_{event.id}_{uuid.uuid4().hex}.{ext}"
            saved_path = default_storage.save(
                f"event_materials/{safe_name}", ContentFile(slides_file.read())
            )
            if "materials" not in event.__dict__:
                event.materials = {}
            event.materials["slides_url"] = default_storage.url(saved_path)

        event.save(update_fields=["materials"])
        from ve_invitations.utils import send_material_notification

        send_material_notification(event)
        messages.success(request, "Material subido y notificaciones enviadas.")
        return redirect("virtualEvent:organizer_dashboard", event_id=event.id)
    return redirect("virtualEvent:organizer_dashboard", event_id=event.id)


def download_ics(request, event_id):
    event = get_object_or_404(VirtualEvent, pk=event_id)
    ics_content = generate_ics(event)
    response = HttpResponse(ics_content, content_type="text/calendar")
    response["Content-Disposition"] = f'attachment; filename="event_{event.id}.ics"'
    return response
