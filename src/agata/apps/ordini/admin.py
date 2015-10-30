#-*- coding: utf-8 -*-

from django.contrib import admin
from models import *

def str_or_empty(string):
    if string is None:
        return ''
    else:
        return string

class DettagliTabular(admin.TabularInline):
    model = DettaglioOrdine

class OrdiniAdmin(admin.ModelAdmin):
    list_display = ['numero_ordine', 'stato', 'info', 'esegui' ]
    list_display_links = ['numero_ordine']
    list_filter = [ 'stato', 'tipo', 'anno' ]
    date_hierarchy = 'inserimento'
    readonly_fields = ['stato']
    inlines = [ DettagliTabular ]

admin.site.register(Ordine,OrdiniAdmin)
