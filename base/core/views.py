# coding: utf-8
import json

from annoying.decorators import render_to, ajax_request
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect

from .models import Human, Talks
from .forms import TalksForm


@render_to('home.html')
def home(request, cicle=None, topic=None):
	if cicle is None:
		cicle = Talks.objects.get(pk=1).cicle
	if topic and topic != '0':
		talks = Talks.objects.filter(cicle=cicle, topic=topic).exclude(pk=1).order_by('-date')
	else:
		talks = Talks.objects.filter(cicle=cicle).exclude(pk=1).order_by('-date')
	current = Human.objects.get(is_active=True, current=True)
	form = TalksForm(initial={'human': current})
	in_line = Human.objects.filter(is_active=True, in_line__gt=0).order_by('in_line')
	return { 'talks' : talks, 'form': form, 'current': current, 'in_line': in_line }


@ajax_request
def current(request):
	if request.method == 'POST':
		h = Human.objects.get(pk=request.POST.get('human'))
		t = request.POST.get('topic')
		n = request.POST.get('name')
		l = request.POST.get('link')
		cicle = Talks.objects.get(pk=1).cicle
		talk = Talks(human=h, topic=t, name=n, link=l, cicle=cicle)
		talk.save()
		response_data = {}
		response_data['result'] = 'Create post successful!'
		return {'success' : 1}


@render_to('nominee.html')
def nominee(request):
	nominees = Human.objects.filter(is_active=True, lightning=True)
	if request.POST:
		current = Human.objects.get(is_active=True, current=True)
		current.current = False
		current.save()
		victim = Human.objects.get(pk=request.POST.get('user'))
		victim.current = True
		victim.lightning = False
		victim.save()
		return redirect('home')

	return {'nominees': nominees}

@render_to('victim.html')
def victim(request):
	cycle = Talks.objects.get(pk=1)

	current = Human.objects.get(is_active=True, current=True)
	current.in_line = 0
	current.current = False

	available = Human.objects.filter(is_active=True, lightning=True).order_by('?')
	victim = available.first()
	victim.lightning = False
	victim.in_line = 4

	in_lines = Human.objects.filter(is_active=True, in_line__gt=0)
	for n in in_lines:
		n.in_line -= 1
		if n.in_line == 1:
			n.current = True
		n.save()

	current.save()
	victim.save()

	if current.last:
		current.last = False
		current.save()
		cycle.cicle = cycle.cicle + 1
		cycle.save()

	m = ''
	if available.count() == 0:
		victim.last = True
		victim.save()
		m = f'End of cycle #{cycle.cicle}'

		humans = Human.objects.filter(is_active=True)		
		for h in humans:
			h.lightning = True
			h.save()

	return { 'current' : current, 'victim': victim, 'message': m }
