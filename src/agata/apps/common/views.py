#-*- coding: utf-8 -*-
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.conf import settings

 
def index(request):
    return HttpResponseRedirect('/admin')


def help(request):
    return render_to_response('common/help.html')

def jolly(request):
    # QUI SI PUÒ FARE QUELLO CHE SI VUOLE
    return HttpResponseRedirect('/admin')
    

