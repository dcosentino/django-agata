#-*- coding: utf-8 -*-
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

import anagrafiche.models as anagrafiche_db
import articoli.models as articoli_db

TIPO_ORDINE = (
    ( 'Prelievo', 'Prelievo'),
    ( 'Deposito', 'Deposito'),
    )

STATO_ORDINE = (
    ( 'Aperto', 'Aperto'),
    ( 'Chiuso', 'Chiuso'),
    ( 'Annullato', 'Annullato')
    )

class Ordine(models.Model):
    tipo = models.CharField(max_length = 16, choices=TIPO_ORDINE, default = 'Prelievo')
    numero = models.IntegerField()
    anno = models.IntegerField()
    inserimento = models.DateTimeField(auto_now=True)
    completamento = models.DateTimeField(blank=True, null=True)
    annullamento = models.DateTimeField(blank=True, null=True)
    stato = models.CharField(max_length = 16, choices = STATO_ORDINE, default = 'Aperto')
    letture = models.TextField(blank=True, null=True)

    class Meta(object):
        verbose_name_plural = 'ordini'
        unique_together = (("tipo", "numero", "anno"), )


    def lista_articoli(self, out_to_js=True):
        a = self.dettaglioordine_set.all()
        ret = {}

        def jsEscape(s):
            if out_to_js:
                return s.replace("'","\'").replace("\n","<br/>")
            else:
                return s

        for x in a:
            prev = ret.get(x.articolo.codice,None)
            if not prev is None:
                prev['qta'] += x.richiesto
            else:
                prev = { 'bcr': x.articolo.codice,
                         'descr': jsEscape(x.articolo.descrizione),
                         'qta': x.richiesto,
                         'letti': 0,
                         'sconosciuto': False
                         }
            ret[prev['bcr']] = prev

        bcr = self.letture.split()
        for x in bcr:
            # togliamo gli spazi bianchi
            x = x.strip().split(";")
            if x[0] in "+*":
                # cambio collo
                print "Cambio collo"
                continue
            if len(x) == 1:
                x = (x[0],1)
            elif len(x) != 2:
                continue

            if x[0] in ret:
                # solo se conosciuto/precedentemente identificato
                ret[x[0]]["letti"]+=x[1]
            elif not out_to_js:
                # oppure se non dobbiamo andare verso JS
                ret[x[0]] = { 'bcr': x[0],
                              'descr': "Sconosciuto",
                              'qta': 0,
                              'letti': x[1],
                              'sconosciuto': True
                              }

        if out_to_js:
            # modifica per l'output per JS
            ret = [ u"'%(bcr)s': new articolo_obj('%(bcr)s', '%(descr)s', %(qta)d, %(letti)d)"%v for k,v in ret.items() ]

        return ret

    def lista_letture(self):
        bcr = self.letture.split()
        ret = []
        for x in bcr:
            # togliamo gli spazi bianchi
            x = x.strip().split(";")
            if len(x) == 1:
                x = (x[0],1)
            elif len(x) != 2:
                continue

            for n in range(x[1]):
                ret.append(x[0])
        return ",".join([ "'%s'"%x for x in ret ])

    def numero_ordine(self):
        return u"%s %d/%4d"%(self.tipo, self.numero, self.anno)

    def __unicode__(self):
        return self.numero_ordine()

    def isPrelievo(self):
        return True if self.prelievo == 'Prelievo' else False

    def info(self):
        ret = u"Inserito il %d/%02d/%4d"%(self.inserimento.day, self.inserimento.month, self.inserimento.year)
        if not self.annullamento is None:
            ret += u"<br/>Annullato il %d/%02d/%4d"%(self.annullamento.day, self.annullamento.month, self.annullamento.year)
        elif not self.completamento is None:
            ret += u"<br/>Completato il %d/%02d/%4d"%(self.completamento.day, self.completamento.month, self.completamento.year)
        return ret
    info.allow_tags = True

    def esegui(self):
        url_base = "/ordini/%s/%d"%({'Prelievo':'prelievo', 'Deposito':'deposito'}[self.tipo],self.id)
        return u"<a href='%s'>Letture</a>"%url_base
    esegui.allow_tags = True

class DettaglioOrdine(models.Model):
    ordine = models.ForeignKey(Ordine)
    articolo = models.ForeignKey(articoli_db.Articolo)
    richiesto = models.IntegerField(blank=False, null=False)
    numero = models.IntegerField(blank=True, null=True)

@receiver(pre_save, sender=Ordine)
def update_ordine(sender, instance, *args, **kwargs):
    if not instance.annullamento is None:
        instance.stato = 'Annullato'
    elif not instance.completamento is None:
        instance.stato = 'Chiuso'
    else:
        instance.stato = 'Aperto'
