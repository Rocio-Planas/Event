import json
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.db.models import Avg
from ve_streaming.models import StreamingRoom
from .models import (
    ChatMessage,
    HandRaise,
    Poll,
    PollOption,
    PollVote,
    SatisfactionRating,
)


# ------------------------------------------------------------
# Helper para obtener la sala de forma segura
# ------------------------------------------------------------
def get_room_or_error(room_slug):
    """Intenta obtener StreamingRoom a partir del slug (event__unique_link).
    Retorna (room, None) si éxito, o (None, JsonResponse) si error.
    """
    try:
        room = get_object_or_404(StreamingRoom, event__unique_link=room_slug)
        return room, None
    except (ValueError, TypeError):
        return None, JsonResponse({"error": "Slug inválido"}, status=400)


def moderate_content(content):
    """Reemplaza palabras ofensivas por ***"""
    for word in settings.OFFENSIVE_WORDS:
        content = content.replace(word, "***")
    return content


# ------------------------------------------------------------
# CHAT
# ------------------------------------------------------------
@csrf_exempt
@require_http_methods(["POST"])
def send_message(request, room_slug):
    """
    Envía un mensaje. Permite usuarios anónimos (sin login).
    Si el usuario está autenticado, puede elegir anonymous=True.
    """
    room, error_response = get_room_or_error(room_slug)
    if error_response:
        return error_response

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    content = data.get("content", "").strip()
    anonymous = data.get("anonymous", False)

    if not content:
        return JsonResponse({"error": "Mensaje vacío"}, status=400)

    # Moderación automática
    moderated = any(word in content.lower() for word in settings.OFFENSIVE_WORDS)
    if moderated:
        content = moderate_content(content)

    # Determinar usuario (None si anónimo o no autenticado)
    user = None
    display_name = "Anónimo"

    if request.user.is_authenticated and not anonymous:
        user = request.user
        display_name = user.email

    message = ChatMessage.objects.create(
        room=room,
        user=user,
        anonymous=anonymous or not request.user.is_authenticated,
        content=content,
        moderated=moderated,
    )

    return JsonResponse(
        {
            "id": message.id,
            "username": display_name,
            "content": message.content,
            "timestamp": message.timestamp.isoformat(),
            "is_pinned": message.is_pinned,
            "moderated": message.moderated,
        }
    )


@require_http_methods(["GET"])
def get_messages(request, room_slug):
    room, error_response = get_room_or_error(room_slug)
    if error_response:
        return error_response

    pinned = room.messages.filter(is_pinned=True).order_by("-timestamp")
    recent = room.messages.filter(is_pinned=False).order_by("timestamp")[:50]

    messages = list(pinned) + list(recent)

    data = []
    for msg in messages:
        data.append(
            {
                "id": msg.id,
                "username": (
                    "Anónimo"
                    if msg.anonymous
                    else (msg.user.email if msg.user else "Usuario eliminado")
                ),
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "is_pinned": msg.is_pinned,
                "moderated": msg.moderated,
                "is_mine": request.user.is_authenticated and msg.user == request.user,
            }
        )
    return JsonResponse({"messages": data})


# ------------------------------------------------------------
# MANOS
# ------------------------------------------------------------
@login_required
@require_http_methods(["POST"])
def raise_hand(request, room_slug):
    room, error_response = get_room_or_error(room_slug)
    if error_response:
        return error_response

    hand, created = HandRaise.objects.get_or_create(
        room=room, user=request.user, defaults={"attended": False}
    )
    if not created and not hand.attended:
        return JsonResponse({"error": "Ya tienes la mano levantada"}, status=400)
    if not created:
        hand.attended = False
        hand.save()
    return JsonResponse({"status": "hand_raised"})


@login_required
@require_http_methods(["POST"])
def attend_hand(request, room_slug, user_id):
    room, error_response = get_room_or_error(room_slug)
    if error_response:
        return error_response

    if request.user != room.event.created_by:
        return JsonResponse({"error": "No autorizado"}, status=403)
    hand = get_object_or_404(HandRaise, room=room, user_id=user_id)
    hand.attended = True
    hand.save()
    return JsonResponse({"status": "attended"})


@login_required
@require_http_methods(["GET"])
def get_hands(request, room_slug):
    room, error_response = get_room_or_error(room_slug)
    if error_response:
        return error_response

    if request.user != room.event.created_by:
        return JsonResponse({"error": "No autorizado"}, status=403)
    hands = HandRaise.objects.filter(room=room, attended=False).select_related("user")
    data = [{"user_id": h.user.id, "username": h.user.email} for h in hands]
    return JsonResponse({"hands": data})


# ------------------------------------------------------------
# FIJAR MENSAJES
# ------------------------------------------------------------
@csrf_exempt
@login_required
@require_http_methods(["POST"])
def pin_message(request, room_slug, message_id):
    room, error_response = get_room_or_error(room_slug)
    if error_response:
        return error_response

    # Verificar que el usuario sea el organizador
    if request.user != room.event.created_by:
        return JsonResponse({"error": "No autorizado"}, status=403)

    message = get_object_or_404(ChatMessage, id=message_id, room=room)
    data = json.loads(request.body)
    message.is_pinned = data.get("pinned", False)
    message.save()
    return JsonResponse({"status": "ok", "pinned": message.is_pinned})


# ------------------------------------------------------------
# ENCUESTAS
# ------------------------------------------------------------
@csrf_exempt
@login_required
@require_http_methods(["POST"])
def create_poll(request, room_slug):
    room, error_response = get_room_or_error(room_slug)
    if error_response:
        return error_response

    # Solo el organizador puede crear encuestas
    if request.user != room.event.created_by:
        return JsonResponse({"error": "No autorizado"}, status=403)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    question = data.get("question")
    options_text = data.get("options", [])
    if not question or len(options_text) < 2:
        return JsonResponse(
            {"error": "La pregunta y al menos 2 opciones son requeridas"}, status=400
        )

    Poll.objects.filter(room=room, is_active=True).update(is_active=False)

    poll = Poll.objects.create(room=room, question=question, is_active=True)
    for txt in options_text:
        PollOption.objects.create(poll=poll, text=txt)

    options_with_id = [{"id": opt.id, "text": opt.text} for opt in poll.options.all()]
    return JsonResponse(
        {"poll_id": poll.id, "question": question, "options": options_with_id}
    )


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def vote_poll(request, room_slug, poll_id):
    """Registra el voto de un usuario autenticado en una encuesta activa."""
    room, error_response = get_room_or_error(room_slug)
    if error_response:
        return error_response

    poll = get_object_or_404(Poll, id=poll_id, room=room, is_active=True)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    option_id = data.get("option_id")
    option = get_object_or_404(PollOption, id=option_id, poll=poll)

    # Como ahora el modelo PollVote requiere user, ya no necesitamos lógica de anónimos
    vote, created = PollVote.objects.get_or_create(
        poll=poll, user=request.user, defaults={"option": option}
    )
    if not created:
        vote.option = option
        vote.save()
    return JsonResponse({"status": "voted"})


@require_http_methods(["GET"])
def get_poll_results(request, room_slug, poll_id):
    room, error_response = get_room_or_error(room_slug)
    if error_response:
        return error_response

    poll = get_object_or_404(Poll, id=poll_id, room=room)
    total_votes = PollVote.objects.filter(poll=poll).count()
    results = []
    for opt in poll.options.all():
        votes = PollVote.objects.filter(option=opt).count()
        percentage = (votes / total_votes * 100) if total_votes > 0 else 0
        results.append(
            {"option": opt.text, "votes": votes, "percentage": round(percentage, 1)}
        )
    return JsonResponse(
        {
            "poll_id": poll.id,
            "question": poll.question,
            "results": results,
            "total_votes": total_votes,
        }
    )


@require_http_methods(["GET"])
def get_active_poll(request, room_slug):
    room, error_response = get_room_or_error(room_slug)
    if error_response:
        return error_response

    try:
        poll = Poll.objects.filter(room=room, is_active=True).latest("created_at")
        options = [{"id": opt.id, "text": opt.text} for opt in poll.options.all()]
        return JsonResponse(
            {"poll_id": poll.id, "question": poll.question, "options": options}
        )
    except Poll.DoesNotExist:
        return JsonResponse({"active_poll": None})


# ------------------------------------------------------------
# SATISFACCIÓN
# ------------------------------------------------------------
@require_http_methods(["POST"])
def satisfaction_rating(request, room_slug):
    room, error_response = get_room_or_error(room_slug)
    if error_response:
        return error_response

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    rating = data.get("rating")
    if rating not in [1, 2, 3, 4, 5]:
        return JsonResponse({"error": "Rating inválido"}, status=400)

    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    user = request.user if request.user.is_authenticated else None

    if user:
        obj, created = SatisfactionRating.objects.update_or_create(
            room=room, user=user, defaults={"rating": rating}
        )
    else:
        obj, created = SatisfactionRating.objects.update_or_create(
            room=room,
            session_key=session_key,
            defaults={"rating": rating, "user": None},
        )

    avg = (
        SatisfactionRating.objects.filter(room=room).aggregate(Avg("rating"))[
            "rating__avg"
        ]
        or 0
    )
    return JsonResponse({"status": "ok", "average": round(avg, 1)})
