#-*- coding: utf-8 -*-
import decimal, re, posixpath

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Max
from django.utils.safestring import mark_safe

import agata.apps.anagrafiche.models as anagrafiche_db

def sanitize_path(unsafe_path):
    return re.sub(r'[^\w\.\/]+', r'_', posixpath.normpath(unsafe_path))

class Fattura(models.Model):

    def upload_img(instance, filename):
        anno = instance.data.year
        mese = instance.data.month
        return u'contabilita/fatture/%04d/%02d/%s' % (anno, mese, sanitize_path(filename))

    origine = models.CharField(verbose_name="società", max_length=32, choices=settings.ORIGINI_FATTURE, default=settings.DEFAULT_ORIGINE_FATTURA)
    cliente = models.ForeignKey(anagrafiche_db.Societa)
    data = models.DateField()
    numero = models.IntegerField()
    importo = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=64, choices=settings.TIPI_FATTURA)
    tipo_attivita = models.CharField(max_length=128, choices=settings.TIPI_ATTIVITA, null=True, blank=True)
    ra_ricevuta = models.BooleanField(default=False, help_text="Vale solo per lo Studio associato")
    fattura = models.FileField(upload_to=upload_img, null=True, blank=True)
    note = models.TextField(null=True, blank=True)

    def file_fattura(self):
        if self.fattura:
            return mark_safe('<a href="%s" target="_blank">Scarica PDF</a>' % self.fattura.url)
        else:
            return mark_safe('<strong>PDF mancante</strong>')
    file_fattura.allow_tags = True
    file_fattura.short_description = 'Scarica PDF'

    def __unicode__(self):
        anno = self.data.year
        return "%d/%d" % (anno, self.numero)

    class Meta:
        verbose_name_plural = 'fatture clienti'

    def pagata(instance):
        totale = decimal.Decimal('0.0')
        for p in instance.pagamento_set.all():
            totale += p.importo
        if totale == instance.importo:
            return '<img src="/static/admin/img/icon-yes.gif" alt="True">'
        else:
            return '<img src="/static/admin/img/icon-no.gif" alt="False">'
    pagata.allow_tags = True

    def pagata_bool(instance):
        totale = decimal.Decimal('0.0')
        for p in instance.pagamento_set.all():
            totale += p.importo
        if totale == instance.importo:
            return True
        return False

    def da_incassare(instance):
        totale = instance.importo
        for p in instance.pagamento_set.all():
            totale -= p.importo
        return totale

class TipoServizio(models.Model):
    nome = models.CharField(max_length=64, unique=True)

    class Meta(object):
        verbose_name_plural = "tipi servizi"

    def __unicode__(self):
        return self.nome


class Servizio(models.Model):
    fattura = models.ForeignKey(Fattura, null=True, blank=True)
    tipo = models.ForeignKey(TipoServizio)
    data_inizio = models.DateField(null=True, blank=True)
    data_fine = models.DateField(null=True, blank=True)
    descrizione = models.TextField(null=True, blank=True)
    importo = models.DecimalField(max_digits=10, decimal_places=2)
    iva = models.DecimalField(max_digits=10, decimal_places=2, default=settings.IVA)

    class Meta(object):
        verbose_name_plural = "servizi"

    def __unicode__(self):
        return u'%s' % (self.tipo.nome)

    def fatturato(instance):
        if instance.fattura:
            return '<img src="/static/admin/img/icon-yes.gif" alt="True">'
        else:
            return '<img src="/static/admin/img/icon-no.gif" alt="False">'
    fatturato.allow_tags = True


class TipoAttivita(models.Model):
    nome = models.CharField(max_length=64, unique=True)

    class Meta(object):
        verbose_name_plural = "tipi attivita"

    def __unicode__(self):
        return self.nome


class Attivita(models.Model):
    fattura = models.ForeignKey(Fattura, null=True, blank=True)

    tipo = models.ForeignKey(TipoAttivita)
    data_inizio = models.DateField(null=True, blank=True)
    data_fine = models.DateField(null=True, blank=True)
    descrizione = models.TextField(null=True, blank=True)
    importo = models.DecimalField(max_digits=10, decimal_places=2)
    iva = models.DecimalField(max_digits=10, decimal_places=2, default=settings.IVA)
    quantita = models.IntegerField(null=True, blank=True)
    prezzo_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rif_ordine = models.ForeignKey('RigaOrdineAcquisto', blank=True, null=True)

    class Meta(object):
        verbose_name_plural = "Attività"

    def __unicode__(self):
        return u'%s' % (self.tipo.nome)

    def fatturato(instance):
        if instance.fattura:
            return '<img src="/static/admin/img/icon-yes.gif" alt="True">'
        else:
            return '<img src="/static/admin/img/icon-no.gif" alt="False">'
    fatturato.allow_tags = True

class TipoPagamento(models.Model):
    nome = models.CharField(max_length=64, unique=True)

    class Meta(object):
        verbose_name_plural = "tipi pagamenti"

    def __unicode__(self):
        return self.nome

class Pagamento(models.Model):
    fattura = models.ForeignKey(Fattura)
    tipo = models.ForeignKey(TipoPagamento)
    data = models.DateField()
    importo = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.CharField(max_length=256, null=True, blank=True)

    def origine_fattura(instance):
        return instance.fattura.origine
    origine_fattura.allow_tags = True
    origine_fattura.admin_order_field = 'fattura__origine'

    def cliente_fattura(instance):
        return instance.fattura.cliente
    cliente_fattura.allow_tags = True
    cliente_fattura.admin_order_field = 'fattura__cliente'

    class Meta(object):
        verbose_name_plural = "pagamenti clienti"

    def __unicode__(self):
        return self.tipo.nome

class TipoFatturaFornitore(models.Model):
    nome = models.CharField(max_length=64, unique=True)

    class Meta(object):
        verbose_name_plural = "tipi fatture fornitore"

    def __unicode__(self):
        return self.nome

class FatturaFornitore(models.Model):

    def upload_img(instance, filename):
        anno = instance.data.year
        mese = instance.data.month
        return u'contabilita/fornitori/%04d/%02d/%s' % (anno, mese, sanitize_path(filename))

    origine = models.CharField(verbose_name="società", max_length=32, choices=settings.ORIGINI_FATTURE, default=settings.DEFAULT_ORIGINE_FATTURA)
    tipo = models.ForeignKey(TipoFatturaFornitore)
    fornitore = models.ForeignKey(anagrafiche_db.Societa)
    data = models.DateField()
    numero = models.CharField(max_length=128)
    importo = models.DecimalField(max_digits=10, decimal_places=2, help_text='Inserire l\'importo ivato')
    fattura = models.FileField(upload_to=upload_img, null=True, blank=True)

    def file_fattura(self):
        if self.fattura:
            return mark_safe('<a href="%s" target="_blank">Scarica PDF</a>' % self.fattura.url)
        else:
            return mark_safe('<strong>PDF mancante</strong>')
    file_fattura.allow_tags = True
    file_fattura.short_description = 'Scarica PDF'

    def __unicode__(self):
        anno = self.data.year
        return "%d/%s" % (anno, self.numero)

    class Meta:
        verbose_name_plural = 'fatture fornitori'

    def pagata(instance):
        totale = decimal.Decimal('0.0')
        for p in instance.pagamentofatturafornitore_set.all():
            totale += p.importo
        if totale == instance.importo:
            return '<img src="/static/admin/img/icon-yes.gif" alt="True">'
        else:
            return '<img src="/static/admin/img/icon-no.gif" alt="False">'
    pagata.allow_tags = True

    def pagata_bool(instance):
        totale = decimal.Decimal('0.0')
        for p in instance.pagamentofatturafornitore_set.all():
            totale += p.importo
        print totale
        if totale == instance.importo:
            return True
        return False


class PagamentoFatturaFornitore(models.Model):
    fattura = models.ForeignKey(FatturaFornitore)
    tipo = models.ForeignKey(TipoPagamento)
    data = models.DateField()
    importo = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.CharField(max_length=256, null=True, blank=True)

    def origine_fattura(instance):
        return instance.fattura.origine
    origine_fattura.allow_tags = True
    origine_fattura.admin_order_field = 'fattura__origine'

    def fornitore_fattura(instance):
        return instance.fattura.fornitore
    fornitore_fattura.allow_tags = True
    fornitore_fattura.admin_order_field = 'fattura__fornitore'

    class Meta(object):
        verbose_name_plural = "pagamenti fornitori"

    def __unicode__(self):
        return self.tipo.nome


class TipoSpesa(models.Model):
    nome = models.CharField(max_length=64, unique=True)

    class Meta(object):
        verbose_name_plural = "tipi spese"

    def __unicode__(self):
        return self.nome

class Spesa(models.Model):

    def upload_img(instance, filename):
        anno = instance.data.year
        mese = instance.data.month
        return u'contabilita/fornitori/%04d/%02d/%s' % (anno, mese, sanitize_path(filename))

    origine = models.CharField(verbose_name="società", max_length=32, choices=settings.ORIGINI_FATTURE, default=settings.DEFAULT_ORIGINE_FATTURA)
    tipo = models.ForeignKey(TipoSpesa)
    fornitore = models.ForeignKey(anagrafiche_db.Societa)
    data = models.DateField()
    numero = models.CharField(max_length=128)
    importo = models.DecimalField(max_digits=10, decimal_places=2, help_text='Inserire l\'importo ivato')
    iva = models.DecimalField(max_digits=10, decimal_places=2, default=settings.IVA)
    spesa = models.FileField(upload_to=upload_img, null=True, blank=True)

    def file_spesa(self):
        if self.spesa:
            return mark_safe('<a href="%s" target="_blank">Scarica PDF</a>' % self.spesa.url)
        else:
            return mark_safe('<strong>PDF mancante</strong>')
    file_spesa.allow_tags = True
    file_spesa.short_description = 'Scarica PDF'

    def __unicode__(self):
        anno = self.data.year
        return "%d/%s" % (anno, self.numero)

    class Meta:
        verbose_name_plural = 'spese'

    def pagata(instance):
        totale = decimal.Decimal('0.0')
        for p in instance.pagamentospesa_set.all():
            totale += p.importo
        if totale == instance.importo:
            return '<img src="/static/admin/img/icon-yes.gif" alt="True">'
        else:
            return '<img src="/static/admin/img/icon-no.gif" alt="False">'
    pagata.allow_tags = True

    def pagata_bool(instance):
        totale = decimal.Decimal('0.0')
        for p in instance.pagamentospesa_set.all():
            totale += p.importo
        print totale
        if totale == instance.importo:
            return True
        return False


class PagamentoSpesa(models.Model):
    spesa = models.ForeignKey(Spesa)
    tipo = models.ForeignKey(TipoPagamento)
    data = models.DateField()
    importo = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.CharField(max_length=256, null=True, blank=True)

    def origine_spesa(instance):
        return instance.spesa.origine
    origine_spesa.allow_tags = True
    origine_spesa.admin_order_field = 'spesa__origine'

    def fornitore_spesa(instance):
        return instance.spesa.fornitore
    fornitore_spesa.allow_tags = True
    fornitore_spesa.admin_order_field = 'spesa__fornitore'

    class Meta(object):
        verbose_name_plural = "pagamenti spese"

    def __unicode__(self):
        return self.tipo.nome


class TipoTassa(models.Model):
    nome = models.CharField(max_length=64, unique=True)

    class Meta(object):
        verbose_name_plural = "tipi tasse"

    def __unicode__(self):
        return self.nome

class Tassa(models.Model):

    def upload_img(instance, filename):
        anno = instance.data.year
        mese = instance.data.month
        return u'contabilita/tasse/%04d/%02d/%s' % (anno, mese, sanitize_path(filename))

    origine = models.CharField(verbose_name="società", max_length=32, choices=settings.ORIGINI_FATTURE, default=settings.DEFAULT_ORIGINE_FATTURA)
    user = models.ForeignKey(User, null=True, blank=True)
    tipo = models.ForeignKey(TipoTassa)
    data = models.DateField()
    numero = models.CharField(max_length=64)
    importo = models.DecimalField(max_digits=10, decimal_places=2, help_text='Inserire l\'importo ivato')
    tassa = models.FileField(upload_to=upload_img, null=True, blank=True)

    def file_tassa(self):
        if self.tassa:
            return mark_safe('<a href="%s" target="_blank">Scarica PDF</a>' % self.tassa.url)
        else:
            return mark_safe('<strong>PDF mancante</strong>')
    file_tassa.allow_tags = True
    file_tassa.short_description = 'Scarica PDF'

    def __unicode__(self):
        anno = self.data.year
        return "%d/%s" % (anno, self.numero)

    class Meta:
        verbose_name_plural = 'tasse'

    def pagata(instance):
        totale = decimal.Decimal('0.0')
        for p in instance.pagamentotassa_set.all():
            totale += p.importo
        if totale == instance.importo:
            return '<img src="/static/admin/img/icon-yes.gif" alt="True">'
        else:
            return '<img src="/static/admin/img/icon-no.gif" alt="False">'
    pagata.allow_tags = True

    def pagata_bool(instance):
        totale = decimal.Decimal('0.0')
        for p in instance.pagamentotassa_set.all():
            totale += p.importo
        if totale == instance.importo:
            return True
        return False


class PagamentoTassa(models.Model):
    tassa = models.ForeignKey(Tassa)
    tipo = models.ForeignKey(TipoPagamento)
    data = models.DateField()
    importo = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.CharField(max_length=256, null=True, blank=True)

    def origine_tassa(instance):
        return instance.tassa.origine
    origine_tassa.allow_tags = True
    origine_tassa.admin_order_field = 'tassa__origine'

    class Meta(object):
        verbose_name_plural = "pagamenti tasse"

    def __unicode__(self):
        return self.tipo.nome


class Stipendio(models.Model):
    origine = models.CharField(verbose_name="società", max_length=32, choices=settings.ORIGINI_FATTURE, default=settings.DEFAULT_ORIGINE_FATTURA)
    user = models.ForeignKey(User)
    data = models.DateField()
    importo = models.DecimalField(max_digits=10, decimal_places=2, help_text='Inserire l\'importo ivato')

    def __unicode__(self):
        anno = self.data.year
        return "%s - %s" % (self.data.strftime("%d/%m/%Y"), self.user.first_name)

    class Meta:
        verbose_name_plural = 'stipendi'


    def pagata_bool(instance):
        totale = decimal.Decimal('0.0')
        for p in instance.pagamentostipendio_set.all():
            totale += p.importo
        if totale == instance.importo:
            return True
        return False


class PagamentoStipendio(models.Model):
    stipendio = models.ForeignKey(Stipendio)
    tipo = models.ForeignKey(TipoPagamento)
    data = models.DateField()
    importo = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.CharField(max_length=256, null=True, blank=True)

    def origine_stipendio(instance):
        return instance.stipendio.origine
    origine_stipendio.allow_tags = True
    origine_stipendio.admin_order_field = 'stipendio__origine'

    class Meta(object):
        verbose_name_plural = "pagamenti stipendi"

    def __unicode__(self):
        return self.tipo.nome


class Dividendo(models.Model):
    origine = models.CharField(verbose_name="società", max_length=32, choices=settings.ORIGINI_FATTURE, default=settings.DEFAULT_ORIGINE_FATTURA)
    user = models.ForeignKey(User)
    data = models.DateField()
    importo = models.DecimalField(max_digits=10, decimal_places=2, help_text='Inserire l\'importo ivato')

    def __unicode__(self):
        anno = self.data.year
        return "%s - %s" % (self.data.strftime("%d/%m/%Y"), self.user.first_name)

    class Meta:
        verbose_name_plural = 'dividendi'


class OrdineAcquisto(models.Model):
    def upload_img(instance, filename):
        anno = instance.data.year
        mese = instance.data.month
        return u'contabilita/ordini_acquisto/%04d/%02d/%s' % (anno, mese, sanitize_path(filename))

    destinatario = models.CharField(verbose_name='Destinatario acquisto',
                                    max_length=32,
                                    choices=settings.ORIGINI_FATTURE,
                                    default=settings.DEFAULT_ORIGINE_FATTURA)
    cliente = models.ForeignKey(anagrafiche_db.Societa)
    data = models.DateField()
    numero = models.CharField(max_length=64, null=True, blank=True)
    ordine_cartaceo = models.FileField(upload_to=upload_img, null=True, blank=True)
    note = models.TextField(blank=True, null=True)

    def file_ordine_cartaceo(self):
        if self.ordine_cartaceo:
            return mark_safe('<a href="%s" target="_blank">Scarica ordine cartaceo</a>' % self.ordine_cartaceo.url)
        else:
            return mark_safe('<strong>PDF mancante</strong>')
    file_ordine_cartaceo.allow_tags = True
    file_ordine_cartaceo.short_description = 'Scarica Ordine'

    def __unicode__(self):
        return "Ordine %s del %s" % (self.numero, self.data.strftime('%d/%m/%Y'))

    class Meta:
        verbose_name = 'Ordine di acquisto'
        verbose_name_plural = 'Ordini di acquisto'


class RigaOrdineAcquisto(models.Model):
    ordine = models.ForeignKey(OrdineAcquisto)
    indice_riga = models.IntegerField(default=-1)
    rda = models.CharField(max_length=32, null=True, blank=True)
    descrizione = models.TextField(null=True, blank=True)
    quantita = models.IntegerField(null=True, blank=True)
    quantita_fornita = models.IntegerField(null=True, blank=True)
    data_consegna = models.DateField(null=True, blank=True)
    prezzo_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def ordine_data(self):
        return self.ordine.data.strftime('%d/%m/%Y')
    ordine_data.admin_order_field = 'ordine__data'
    ordine_data.short_description = 'Data'

    def ragione_sociale(self):
        return self.ordine.cliente.ragione_sociale
    ragione_sociale.admin_order_field = 'ordine__cliente__ragione_sociale'
    ragione_sociale.short_description = 'Ragione sociale cliente'

    def save(self, *args, **kwargs):
        if self.indice_riga == -1:
            max_idx = RigaOrdineAcquisto.objects.filter(ordine=self.ordine).aggregate(Max('indice_riga'))['indice_riga__max']
            if max_idx != None:
                self.indice_riga = max_idx + 1
            else:
                self.indice_riga = 1
        super(RigaOrdineAcquisto, self).save(*args, **kwargs)

    class Meta(object):
        verbose_name = 'Riga ordine acquisto'
        verbose_name_plural = 'Righe ordini acquisto'
        ordering = ['indice_riga']

    def __unicode__(self):
        return u'riga %03d ordine %s del %s' % (self.indice_riga,
                                                self.ordine.numero,
                                                self.ordine.data.strftime('%d/%m/%Y'))
