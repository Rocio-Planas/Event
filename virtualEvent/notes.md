def pin_message(request, room_slug, message_id):
    room, error_response = get_room_or_error(room_slug)
    if error_response:
        return error_response

    # if request.user != room.event.created_by:
    #     return JsonResponse({'error': 'No autorizado'}, status=403)

    message = get_object_or_404(ChatMessage, id=message_id, room=room)
    data = json.loads(request.body)
    message.is_pinned = data.get('pinned', False)
    message.save()
    return JsonResponse({'status': 'ok', 'pinned': message.is_pinned})

Luego, en la función `create_poll`, comenta la misma comprobación:
