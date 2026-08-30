import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from .services import get_chatbot_reply

# Create your views here.

@require_POST
@csrf_protect
def chatbot_reply(request):
    try:
        data = json.loads(request.body)
        message = data.get("message", "").strip()
    except (json.JSONDecodeError, AttributeError):
        message = ""

    if not message:
        return JsonResponse({"reply": "Could you say that again?"})

    history = request.session.get("chat_history", [])
    reply = get_chatbot_reply(message, history)
    history.append({"role": "user", "text": message})
    history.append({"role": "assistant", "text": reply})
    request.session["chat_history"] = history[-12:]  # cap stored history so the session doesn't grow forever
    request.session.modified = True

    return JsonResponse({"reply": reply})