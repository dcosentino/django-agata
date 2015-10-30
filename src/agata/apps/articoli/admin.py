#-*- coding: utf-8 -*-

from django.contrib import admin
from django.forms import ModelForm
from models import *


class ArticoloForm(ModelForm):
    class Meta:
        model = Articolo

    def clean_codice_ean(self):
        return self.cleaned_data['codice_ean'] or None


class ArticoloAdmin(admin.ModelAdmin):
    list_display = ['produttore', 'codice', 'codice_ean', 'descrizione']
    list_display_links = ['codice']
    list_filter = ['produttore']
    search_fields = ['codice', 'codice_ean', 'descrizione']
    #form = ArticoloForm

admin.site.register(Articolo, ArticoloAdmin)
