#-*- coding: utf-8 -*-
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect

def index(request):
    return HttpResponseRedirect('/admin')


def jolly(request):
    from custom.hikkaduwa.models import *
    elenco = Articolo.objects.all()
    for e in elenco:
        e.codice = e.codice.strip()
        e.save()

    return HttpResponseRedirect('/admin')
    

