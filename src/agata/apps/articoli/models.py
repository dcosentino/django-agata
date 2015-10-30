#-*- coding: utf-8 -*-

from django.db import models

import agata.apps.anagrafiche.models as anagrafiche_db

class Articolo(models.Model):
    produttore = models.ForeignKey(anagrafiche_db.Societa)
    codice = models.CharField(max_length=128)
    codice_ean = models.CharField(max_length=128, null=True, blank=True)
    descrizione = models.CharField(max_length=512)

    class Meta:
        verbose_name_plural = 'articoli'

    def __unicode__(self):
        return self.codice

    def giacenze(self):
        return self.giacenza_set.all()
