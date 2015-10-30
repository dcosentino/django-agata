#-*- coding: utf-8 -*-

from django.conf.urls import *
from django.contrib import admin


urlpatterns = patterns('',
                       ############################################################################
                       ##########     U R L   P R O T E T T E   D A   L O G I N          ##########
                       ############################################################################
                       url('operazione_completata', 'magazzino.views.operazione_completata', name="operazione_completata"),
                       url('operazioni/ubicazioni/(?P<tipo>(deposito|prelievo))', 'magazzino.views.operazioni_ubicazioni', name="operazione_magazzino_ubicazioni"),
                       url('operazioni/(?P<tipo>(deposito|prelievo))/(?P<id_operazione>\d+)', 'magazzino.views.operazioni', name="operazione_magazzino"),
                       url('operazioni/(?P<tipo>(deposito|prelievo))/(?P<tutto>.*)', 'magazzino.views.operazioni', {'manuale':True}, name="operazione_magazzino"),
                       url('vedi_ordine/(?P<id_ordine>\d+)', 'magazzino.views.vedi_ordine', name="magazzino_vedi_ordine"),
                       url('apri_ordine/(?P<id_ordine>\d+)', 'magazzino.views.apri_ordine', name="magazzino_apri_ordine"),

                       url('storico_articoli_download/(?P<codice>.*)', 'magazzino.views.storico_articoli_download', name="magazzino_storico_articoli_download"),
                       url('storico_articoli', 'magazzino.views.storico_articoli', name="magazzino_storico_articoli"),
)
