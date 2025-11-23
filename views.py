import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Conversation, Message
from .olama_client import call_olama

@ensure_csrf_cookie
def index(request):
    # main page (template below)
    return render(request, "chat/index.html")

@require_POST
def api_chat(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest("Invalid JSON")

    message_text = payload.get("message", "").strip()
    conv_id = payload.get("conversation_id")
    if not message_text:
        return JsonResponse({"error": "Empty message"}, status=400)

    if conv_id:
        conv = get_object_or_404(Conversation, id=conv_id)
    else:
        conv = Conversation.objects.create(title=message_text[:60])

    # save user message
    Message.objects.create(conversation=conv, role="user", content=message_text)

    # call Olama
    reply, err = call_olama(message_text)
    if err:
        reply = "Kechirasiz, serverda xatolik yuz berdi: " + str(err)

    # save assistant message
    Message.objects.create(conversation=conv, role="assistant", content=reply)

    # prepare messages for response
    msgs = [
        {"id": m.id, "role": m.role, "content": m.content, "created_at": m.created_at.isoformat()}
        for m in conv.messages.all()
    ]
    return JsonResponse({"conversation_id": conv.id, "messages": msgs})