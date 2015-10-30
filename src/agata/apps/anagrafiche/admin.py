#-*- coding: utf-8 -*-

from django import forms
from django.contrib import admin
from models import *

class IndirizzoAdmin(admin.ModelAdmin):
    list_display = ['societa', 'etichetta', 'tipo', 'indirizzo']
    list_display_links = ['etichetta']
    list_filter = ['tipo']

class ProvinciaAdmin(admin.ModelAdmin):
    list_display = ['sigla', 'nome']
    list_display_links = ['nome']

class NazioneAdmin(admin.ModelAdmin):
    list_display = ['sigla', 'nome']
    list_display_links = ['nome']


class IndirizzoInlineFormset(forms.models.BaseInlineFormSet):
    """ Funzione per validare l'inserimento di una sola sede legale"""
    def clean(self):
        count = 0
        for form in self.forms:
            try:
                if form.cleaned_data:
                    if form.cleaned_data['tipo'] == 'Sede legale':
                        count += 1
            except AttributeError:
                # annoyingly, if a subform is invalid Django explicity raises
                # an AttributeError for cleaned_data
                pass
        if count == 0:
            raise forms.ValidationError('Inserire la sede legale')
        if count > 1:
            raise forms.ValidationError('Si può inserire una sola sede legale')

class IndirizzoInline(admin.StackedInline):
    model = Indirizzo
    formset = IndirizzoInlineFormset


class SocietaAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'ragione_sociale']
    list_display_links = ['ragione_sociale']
    list_filter = ['tipo']
    #raw_id_fields = ['sede_legale']
    ordering = ['ragione_sociale']
    inlines = [IndirizzoInline]
    search_fields = ['id', 'ragione_sociale', 'codice_fiscale', 'sito_web']

admin.site.register(Societa, SocietaAdmin)
admin.site.register(Indirizzo, IndirizzoAdmin)
admin.site.register(Provincia, ProvinciaAdmin)
admin.site.register(Nazione, NazioneAdmin)
