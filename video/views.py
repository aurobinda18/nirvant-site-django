from django.shortcuts import render

# Create your views here.
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from django.http import HttpResponseForbidden
from scheduler.models import Call

def join_call(request, call_id):
    call = get_object_or_404(Call, id=call_id)

    # Permission check
    if request.user != call.student and request.user != call.mentor.user:
        return HttpResponseForbidden("You are not allowed to join this call.")

    now = timezone.now()

    # Time window: allow join from 5 min before start to end
    if now < call.start_time - timezone.timedelta(minutes=5) or now > call.end_time:
        return HttpResponseForbidden("Call is not active right now.")

    meet_link = call.mentor.meet_link

    if not meet_link:
        return HttpResponseForbidden("Mentor has not configured a meeting link.")

    return redirect(meet_link)
