#-*- coding: utf-8 -*-

from django.conf.urls import *
from django.contrib import admin


urlpatterns = patterns('',
                       ############################################################################
                       ##########     U R L   P R O T E T T E   D A   L O G I N          ##########
                       ############################################################################
                       ('statistiche/(?P<which>(fatturato|entrate_uscite))/(?P<chi>(studio|snc|all))', 'agata.apps.contabilita.views.statistiche'),
                       ('debitori/(?P<chi>(studio|snc|all))', 'agata.apps.contabilita.views.debitori'),
                       ('ritenute_acconto/(?P<anno>\d+)', 'agata.apps.contabilita.views.ritenute_acconto'),
                       ('tipologia_clientela/(?P<chi>(studio|snc))/(?P<anno>\d+)', 'agata.apps.contabilita.views.tipologia_clientela'),
                       ('tipologia_compensi/(?P<chi>(studio|snc))/(?P<anno>\d+)', 'agata.apps.contabilita.views.tipologia_compensi'),
                       ('area_di_mercato/(?P<chi>(studio|snc))/(?P<anno>\d+)', 'agata.apps.contabilita.views.area_di_mercato'),
)
