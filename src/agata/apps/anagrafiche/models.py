#-*- coding: utf-8 -*-
from django.db import models
from django.conf import settings

"""
class Societa(models.Model):
    tipo = models.CharField(max_length=32, choices=settings.TIPI_SOCIETA)
    ragione_sociale = models.CharField(max_length=512, unique=True)
    class Meta(object):
        verbose_name = "societa"
        verbose_name_plural = "società"

    def __unicode__(self):
        return u"%s"%(self.ragione_sociale)
"""

class Provincia(models.Model):
    sigla = models.CharField(max_length=5, unique=True)
    nome = models.CharField(max_length=64, unique=True)

    class Meta(object):
        verbose_name_plural = "province"
        ordering = ['nome']

    def __unicode__(self):
        return self.nome


class Nazione(models.Model):
    sigla = models.CharField(max_length=5, unique=True)
    nome = models.CharField(max_length=64, unique=True)

    class Meta(object):
        verbose_name_plural = "nazioni"
        ordering = ['nome']

    def __unicode__(self):
        return self.nome

class Societa(models.Model):
    tipo = models.CharField(max_length=512, choices=settings.TIPOLOGIA_CLIENTELA, default='D38-Societa\'')
    ragione_sociale = models.CharField(max_length=512, verbose_name='Ragione Sociale o Nome e Cognome', unique=True)
    codice_fiscale = models.CharField(max_length=16, blank=True, null=True)
    partita_iva = models.CharField(max_length=16, blank=True, null=True)
    data_inserimento = models.DateField(auto_now_add = True)
    data_modifica = models.DateField(auto_now = True)
    sito_web = models.CharField(max_length=256, blank=True, null=True)
    note = models.TextField(blank=True, null=True,)

    #sede_legale = models.OneToOneField(Indirizzo)
    #altre_sedi = models.ManyToManyField(Indirizzo, related_name='altre_sedi', null=True, blank=True)

    class Meta(object):
        verbose_name_plural = "Società"

    def __unicode__(self):
        return u"%s"%(self.ragione_sociale)

    def sede_legale(self):
        try:
            return self.indirizzo_set.get(tipo='Sede legale')
        except Indirizzo.DoesNotExist:
            return None


class Indirizzo(models.Model):
    societa = models.ForeignKey(Societa)
    etichetta = models.CharField(max_length=64)
    tipo = models.CharField(max_length=64, choices=settings.TIPI_INDIRIZZO)
    indirizzo = models.CharField(max_length=256)
    citta = models.CharField(max_length=256)
    cap = models.CharField(max_length=16)
    provincia = models.ForeignKey(Provincia)
    nazione = models.ForeignKey(Nazione)
    telefono = models.CharField(max_length=256, blank=True, null=True,)
    cellulare = models.CharField(max_length=256, blank=True, null=True,)
    fax = models.CharField(max_length=256, blank=True, null=True)
    email = models.EmailField(max_length=256, blank=True, null=True)
    note = models.TextField(blank=True, null=True,)

    class Meta(object):
        verbose_name_plural = "indirizzi"

    def __unicode__(self):
        if self.etichetta:
            return self.etichetta
        else:
            return self.indirizzo
