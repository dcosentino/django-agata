#-*- coding: utf-8 -*-

from django.conf.urls import *
from django.contrib import admin


urlpatterns = patterns('',
                       ############################################################################
                       ##########     U R L   P R O T E T T E   D A   L O G I N          ##########
                       ############################################################################
                       ('^prelievo/(?P<idordine>\d+)$', 'ordini.views.operazioni.prelievo'),
                       ('^verifica_prelievo/(?P<idordine>\d+)$', 'ordini.views.operazioni.verifica_prelievo'),
                       ('^chiudi_prelievo/(?P<idordine>\d+)$', 'ordini.views.operazioni.chiudi_prelievo'),
)
