from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db import connection
from .forms import EventCreationForm, EditEventForm
from rso_manage.models import RSO, Registrations
from events.models import Event, Attending
from users.models import Member
import events.event_suggestions as event_suggestions
import pygal
import datetime

def AddEvent(request, rso_name):
    event_rso = RSO.objects.get(name=rso_name)
    rso_id = RSO.objects.get(name=rso_name).id
    admin_registrations = Registrations.objects.raw('SELECT * FROM "rso_manage_registrations" WHERE rso_id={} AND admin=1'.format(rso_id))
    admin_names = list(set([m.member.username for m in admin_registrations]))
    if request.user.username not in admin_names and request.user.username != 'admin':
        return redirect('home')

    if request.method == 'POST':
        form = EventCreationForm(request.POST)
        if (form.is_valid()):
            name = form.cleaned_data.get('name')
            time_begin = form.cleaned_data.get('time_begin')
            time_end = form.cleaned_data.get('time_end')
            place = form.cleaned_data.get('place')
            form_save = form.save(commit=False)
            form_save.rso = event_rso
            form.save()
            return redirect('home')
    else:
        form = EventCreationForm()

    events = event_suggestions.members_events(rso_id)
    suggest, conflicts = event_suggestions.get_best_time(events)

    return render(request, 'add_event.html', {'form' : form, "suggest" : suggest.strftime("%Y-%m-%d at %I:00 %p"), "conflicts": str(conflicts)})

def list_all_events(request):
    all_events = Event.objects.all().values()
    all_events = sorted(all_events, key = lambda event: event['time_begin'])
    event_filter = lambda event: event['time_end'].timestamp() > timezone.now().timestamp()
    all_events = list(filter(event_filter, all_events))
    attending = []
    if request.user.is_authenticated:
        attending = [a.event.id for a in Attending.objects.filter(user=request.user)]

    for event in all_events:
        event['rso_name'] = RSO.objects.get(id=event['rso_id'])

    return render(request, 'event_home.html', {'all_events' : all_events, 'attending': attending})

def attendance_chart(request, rso_name):
    attendance_counts = {}
    for attend in Attending.objects.all():
        if attend.event.rso.name == rso_name:
            attendance_counts[attend.event.name] = attendance_counts.get(attend.event.name, 0) + 1

    bar_chart = pygal.Bar()                                            # Then create a bar graph object
    bar_chart.x_labels = [str(x) for x in attendance_counts.keys()]
    bar_chart.add('attendance', attendance_counts.values())  # Add some values

    return bar_chart.render_django_response()

def display_events(request, rso_name):
    rso = get_object_or_404(RSO, name=rso_name)
    rso_id = RSO.objects.get(name=rso_name).id
    all_events = Event.objects.filter(rso_id = rso_id).values()
    all_events = sorted(all_events, key = lambda event: event['time_begin'])
    # all_events = list(filter(lambda event: event['time_end'] > timezone.now(), all_events))
    attending = []
    if request.user.is_authenticated:
        attending = [a.event.id for a in Attending.objects.filter(user=request.user)]

    admin_registrations = Registrations.objects.raw('SELECT * FROM "rso_manage_registrations" WHERE rso_id = {} AND admin = 1'.format(rso_id))
    admin_names = list(set([m.member.username for m in admin_registrations]))

    return render(request, 'event_list.html', {'all_events' : all_events, 'rso' : rso, 'attending' : attending, 'admin_names': admin_names})

def attend_event(request, rso_name, event):
    event_list = Event.objects.filter(name=event)
    event = None
    for e in event_list:
        if e.rso.name == rso_name:
            event = e
            break

    username = request.user.username
    member = Member.objects.get(username=username)
    if not Attending.objects.filter(user=member, event=event).exists():
        attendance = Attending(user=member, event=event)
        attendance.save()

    return redirect(request.META['HTTP_REFERER'])

def cancel_attendance(request, rso_name, event):
    event_list = Event.objects.filter(name=event)
    event = None
    for e in event_list:
        if e.rso.name == rso_name:
            event = e
            break
    username = request.user.username
    member = Member.objects.get(username=username)
    if Attending.objects.filter(user=member, event=event).exists():
            cursor = connection.cursor()
            cursor.execute('DELETE FROM "events_attending" WHERE user_id = "{}" AND event_id = {}'.format(request.user.username, event.id))
            connection.commit()

    return redirect(request.META['HTTP_REFERER'])

def event_statistics(request, rso_name):
    #WIP
    rso = get_object_or_404(RSO, name=rso_name)
    rso_id = RSO.objects.get(name=rso_name).id
    all_events = RSO.objects.raw('SELECT * FROM "events_event" WHERE rso_id = {}'.format(rso_id))
    attendance = RSO.objects.raw('SELECT id, name, count(user_id) FROM "events_event", "events_attending" WHERE rso_id = {} Group By name '.format(rso_id))
# list(RSO.objects.raw('SELECT events_event.id, name, count(user_id) FROM "events_event", "events_attending" Group By name '))
    return None
def people_attending(request, rso_name, event):
    
    people = []
    for attend in Attending.objects.all():
        if attend.event.name == event:
            people.append(attend.user)
    return render(request, "people_attending.html", {"people" : people})

def update_event(request, rso_name, event_name):
    event = get_object_or_404(Event, name=event_name)
    if request.method == 'POST':
        form = EditEventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('/events/')
    else:
        form = EditEventForm(instance=event)
        return render(request, 'update_event.html', {'form' : form, 'event' : event, 'rso_name': rso_name})
