#-*- coding: utf-8 -*-

import re, os, datetime

from django.db import models
import articoli.models as articoli_db
import anagrafiche.models as anagrafiche_db
from django.forms import ModelForm
from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe



class Magazzino(models.Model):
    nome = models.CharField(max_length=256, unique=True)

    class Meta:
        verbose_name_plural = 'magazzini'

    def __unicode__(self):
        return self.nome

    def giacenza(instance):
        totale = 0
        for g in instance.giacenza_set.all():
            totale += g.quantita
        return u'%d pezzi - <a href="/admin/magazzino/giacenza/?magazzino__id__exact=%d">Vedi dettaglio</a>' % (totale, instance.id)
    giacenza.allow_tags = True


class Giacenza(models.Model):
    magazzino = models.ForeignKey(Magazzino)
    articolo = models.ForeignKey(articoli_db.Articolo)
    quantita = models.IntegerField()
    ubicazione = models.CharField(max_length=5, null=True, blank=True)
    in_prelievo = models.IntegerField(default=0)
    in_deposito = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = 'giacenze'

    def __unicode__(self):
        return self.articolo.codice

    def codice_ean(instance):
        return instance.articolo.codice_ean
    codice_ean.allow_tags = True
    codice_ean.admin_order_field = 'articolo__codice_ean'

    def produttore(instance):
        return instance.articolo.produttore
    produttore.allow_tags = True
    produttore.admin_order_field = 'articolo__produttore'


STATI_OPERAZIONI = (
    ('Inserito', 'Inserito'),
    ('In Corso', 'In Corso'),
    ('Annullata', 'Annullata'),
    ('Completata', 'Completata'),
)

TIPI_OPERAZIONI = (
    ('prelievo', 'prelievo'),
    ('deposito', 'deposito'),
    ('trasferimento', 'trasferimento'),
    (settings.PRELIEVO_PER_VENDITA, settings.PRELIEVO_PER_VENDITA),
    )

class OperazioneMagazzino(models.Model):
    tipo = models.CharField(max_length=64, choices=TIPI_OPERAZIONI)
    magazzino_ingresso = models.ForeignKey(Magazzino, null=True, blank=True, related_name='magazzino_da', verbose_name="Magazzino ingresso")
    magazzino_uscita = models.ForeignKey(Magazzino, null=True, blank=True, verbose_name='magazzino uscita' )
    letture = models.TextField()
    richiesta = models.TextField(null=True, blank=True) # Questo campo viene popolato con i barcode della richiesta originale (se esiste) e usato per fare le verifiche
    ts_operazione = models.DateTimeField(auto_now_add=True)
    stato = models.CharField(max_length=64, choices=STATI_OPERAZIONI)
    note = models.TextField(null=True, blank=True)
    pezzi = models.IntegerField()

    class Meta:
        verbose_name_plural = 'storico operazioni'

    def __unicode__(self):
        return u'%s' % (self.tipo)

    def verifica(self):
        # Questa funzione dovrà restituire il risultato del confronto tra le letture e la richiesta
        pass

class OperazioneMagazzinoForm(ModelForm):
    class Meta:
        model = OperazioneMagazzino
        exclude = ['stato', 'ts_operazione', 'tipo', 'pezzi', 'richiesta']


class GiacenzaForm(ModelForm):
    class Meta:
        model = Giacenza
        exclude = ['articolo', 'in_prelievo', 'in_deposito']

    codice_articolo = forms.CharField()
    note = forms.CharField(required=False)

    def clean_codice_articolo(self):
        # Verifico l'esistenza dell'articolo
        codice = self.cleaned_data['codice_articolo']
        try:
            test = articoli_db.Articolo.objects.get(codice=codice)
        except  articoli_db.Articolo.DoesNotExist:
            raise forms.ValidationError('Articolo non presente in anagrafica')
        return codice



class Ordine(models.Model):
    """ Questo modello serve a contenere le richieste di prelievo / deposito che vengono inserite.
        A seguito della verifica dell'operazione, si procede con la creazione della relativa operazione di magazzino
    """

    def upload_file(instance, filename):
        # ignoro il filename, lo rinomino
        anno = datetime.datetime.now().year
        rag_sociale = re.sub(r'\W', '_', instance.societa.ragione_sociale)
        filename = os.path.basename(filename)
        filename, ext = os.path.splitext(filename)
        filename = re.sub(r'\W', '_', filename)
        return u'ordini/import/%d/%s/%s%s' % (anno, rag_sociale, filename, ext)

    # CAMPI NOSTRI
    ts_ordine = models.DateTimeField(auto_now=True)
    societa = models.ForeignKey(anagrafiche_db.Societa)
    tipo = models.CharField(max_length=64, choices=TIPI_OPERAZIONI)
    stato = models.CharField(max_length=64, choices=STATI_OPERAZIONI)
    magazzino_ingresso = models.ForeignKey(Magazzino, null=True, blank=True, related_name='magazzino_ingresso', verbose_name="Magazzino ingresso")
    magazzino_uscita = models.ForeignKey(Magazzino, null=True, blank=True, related_name='magazzino_uscita', verbose_name='magazzino uscita' )
    richiesta = models.TextField()
    note = models.TextField(null=True, blank=True)
    operazione = models.OneToOneField(OperazioneMagazzino, null=True, blank=True)
    pezzi = models.IntegerField()
    file_originale = models.FileField(max_length=1024, null=True, blank=True, upload_to=upload_file)
    richiesta_modificata = models.BooleanField(default=False)

    # CAMPI DI QUELLO CHE GENERA L'ORDINE
    numero_documento = models.CharField(max_length=64, null=True, blank=True)
    data_documento = models.DateField(null=True, blank=True)
    codice_cliente_fornitore = models.CharField(max_length=128, null=True, blank=True)
    ragione_sociale_anagrafica = models.CharField(max_length=128, null=True, blank=True)

    note_logistica = models.TextField(null=True, blank=True)
    peso_lordo = models.FloatField(null=True, blank=True)
    peso_netto = models.FloatField(null=True, blank=True)
    numero_colli = models.IntegerField(null=True, blank=True)
    esportato = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Ordini'

    def __unicode__(self):
        return u'%s' % (self.numero_documento)

    def stampa_lista(self):
        return mark_safe('<a href="/magazzino/vedi_ordine/%d" target="_blank">Stampa lista</a>' % self.id)

    stampa_lista.allow_tags = True
    stampa_lista.short_description = 'Stampa lista'


    def apri_ordine(self):
        if self.stato not in ['Annullata','Completata']:
            return mark_safe('<a href="/magazzino/apri_ordine/%d" target="_blank">Apri</a>' % self.id)
        else:
            return mark_safe('<a href="/magazzino/apri_ordine/%d" target="_blank">Vedi</a>' % self.id)

    apri_ordine.allow_tags = True
    apri_ordine.short_description = 'Apri ordine'

    def richiesta_hr(self):
        import custom.soedis.models as soedis_db
        import views
        from views import parse_barcodes_con_ubicazioni
        retval = []
        if self.operazione and self.richiesta_modificata:
            letture_pulite = parse_barcodes_con_ubicazioni(self.operazione.letture)
        else:
            letture_pulite = parse_barcodes_con_ubicazioni(self.richiesta)

        print 'letture_pulite', letture_pulite

        for k, dati in letture_pulite.iteritems():
            qta = dati['tot']
            ubicazioni = dati['ubicazioni']
            try:
                test = articoli_db.Articolo.objects.get(codice=k)
            except:
                print k
            test = articoli_db.Articolo.objects.filter(codice_ean=k)
            try:
                test = articoli_db.Articolo.objects.get(codice_ean=k)
            except:
                test = articoli_db.Articolo.objects.get(codice=k)

            dato = {
                'articolo': test,
                'quantita': qta,
                'ubicazioni': ubicazioni
                }
            retval.append(dato)
        return retval


class OrdineForm(ModelForm):
    class Meta:
        model = Ordine
        exclude = ['ts_ordine', 'societa', 'stato', 'magazzino_ingresso', 'magazzino_uscita', 'richiesta', 'operazione', 'pezzi', 'numero_documento', 'data_documento', 'codice_cliente_fornitore', 'ragione_sociale_anagrafica' ]
