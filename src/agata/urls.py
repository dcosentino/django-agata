#-*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

from django.conf import settings

# Include here all the urls.py files from the various apps
urlpatterns = patterns('',
                       # Specifico dell'applicazione contabilita
                       (r'^contabilita/', include('agata.apps.contabilita.urls')),

                       # Specifico dell'applicazione magazzino
                       (r'^magazzino/', include('agata.apps.magazzino.urls')),

                       # Specifico dell'applicazione ordini
                       (r'^ordini/', include('agata.apps.ordini.urls')),
)

