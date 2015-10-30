#-*- coding: utf-8 -*-
from decimal import Decimal
from collections import OrderedDict
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.conf import settings

from agata.apps.contabilita.models import Fattura, FatturaFornitore, Spesa, Tassa, Stipendio, Dividendo

def tipologia_clientela(request, anno, chi):

    output = {}

    totale_anno = Decimal('0.0')
    totale_verifica = Decimal('0.0')

    if chi == 'snc':
        fatture = Fattura.objects.filter(origine='4Sigma Snc', data__year=anno)
    else:
        fatture = Fattura.objects.filter(origine='Studio Associato 4Sigma', data__year=anno)
    for f in fatture:
        totale_anno += f.importo


    for k,v in settings.TIPOLOGIA_CLIENTELA:
        totale = Decimal('0.0')
        numero_incarichi = 0
        if chi == 'snc':
            fatture = Fattura.objects.filter(origine='4Sigma Snc', cliente__tipo=k, data__year=anno)
        else:
            fatture = Fattura.objects.filter(origine='Studio Associato 4Sigma', cliente__tipo=k, data__year=anno)
        for f in fatture:
            totale += f.importo
            numero_incarichi += 1
        res = Decimal(totale / totale_anno) * Decimal('100.0')
        output[k] = {
            'totale': res,
            'numero_incarichi': numero_incarichi
            }
        totale_verifica += res


    return render_to_response('tipologia_clientela.html', {
            'output':output,
            'anno': anno,
            'verifica': {'importo_totale': totale_verifica,
                         'numero_incarichi': numero_incarichi }
            }, context_instance=RequestContext(request))


def ritenute_acconto(request, anno):

    fatture = Fattura.objects.filter(origine='Studio Associato 4Sigma', data__year=anno, ra_ricevuta=False).order_by('cliente__ragione_sociale', 'data')

    return render_to_response('ritenute_acconto.html', {
            'fatture':fatture,
            'anno': anno,
            }, context_instance=RequestContext(request))



def tipologia_compensi(request, anno, chi):

    output = {}

    totale_anno = Decimal('0.0')
    totale_verifica = Decimal('0.0')

    if chi == 'snc':
        fatture = Fattura.objects.filter(origine='4Sigma Snc', data__year=anno)
    else:
        fatture = Fattura.objects.filter(origine='Studio Associato 4Sigma', data__year=anno)

    for f in fatture:
        totale_anno += f.importo


    for k,v in settings.TIPI_ATTIVITA:
        totale = Decimal('0.0')
        numero_incarichi = 0
        if chi == 'snc':
            fatture = Fattura.objects.filter(origine='4Sigma Snc', tipo_attivita=k, data__year=anno)
        else:
            fatture = Fattura.objects.filter(origine='Studio Associato 4Sigma', tipo_attivita=k, data__year=anno)

        for f in fatture:
            totale += f.importo
            numero_incarichi += 1
        res = Decimal(totale / totale_anno) * Decimal('100.0')
        output[k] = {
            'totale': res,
            'numero_incarichi': numero_incarichi
            }
        totale_verifica += res


    return render_to_response('tipologia_compensi.html', {
            'output':output,
            'anno': anno,
            'verifica': {'importo_totale': totale_verifica,
                         'numero_incarichi': numero_incarichi }
            }, context_instance=RequestContext(request))



def area_di_mercato(request, anno, chi):

    output = {}

    totale_anno = Decimal('0.0')
    totale_verifica = Decimal('0.0')
    if chi == 'snc':
        fatture = Fattura.objects.filter(origine='4Sigma Snc', data__year=anno)
    else:
        fatture = Fattura.objects.filter(origine='Studio Associato 4Sigma', data__year=anno)

    numero_incarichi = 0
    # Calcolo i totali
    for f in fatture:
        totale_anno += f.importo
        numero_incarichi += 1


    comunale = {
        'numero_incarichi': 0,
        'totale': Decimal('0.0')
        }

    regionale = {
        'numero_incarichi': 0,
        'totale': Decimal('0.0')
        }

    nazionale = {
        'numero_incarichi': 0,
        'totale': Decimal('0.0')
        }

    internazionale = {
        'numero_incarichi': 0,
        'totale': Decimal('0.0')
        }

    for f in fatture:
        if f.cliente.sede_legale().provincia.sigla == settings.PROVINCIA_SEDE_LEGALE:
            comunale['numero_incarichi'] += 1
            comunale['totale'] += f.importo

        elif f.cliente.sede_legale().provincia.sigla in settings.PROVINCE_REGIONE:
            regionale['numero_incarichi'] += 1
            regionale['totale'] += f.importo

        elif f.cliente.sede_legale().provincia.sigla not in settings.PROVINCE_REGIONE and f.cliente.sede_legale().provincia.sigla != settings.PROVINCIA_SEDE_LEGALE and f.cliente.sede_legale().nazione.sigla == 'IT':
            nazionale['numero_incarichi'] += 1
            nazionale['totale'] += f.importo

        elif f.cliente.sede_legale().nazione.sigla != 'IT':
            internazionale['numero_incarichi'] += 1
            internazionale['totale'] += f.importo

    comunale['totale'] = Decimal(comunale['totale'] / totale_anno) * Decimal('100.0')
    regionale['totale'] = Decimal(regionale['totale'] / totale_anno) * Decimal('100.0')
    nazionale['totale'] = Decimal(nazionale['totale'] / totale_anno) * Decimal('100.0')
    internazionale['totale'] = Decimal(internazionale['totale'] / totale_anno) * Decimal('100.0')


    totale_verifica = comunale['totale']+regionale['totale'] + nazionale['totale']+internazionale['totale']


    return render_to_response('area_di_mercato.html', {
            'comunale': comunale,
            'regionale': regionale,
            'nazionale': nazionale,
            'internazionale': internazionale,
            'anno': anno,
            'verifica': {'importo_totale': totale_verifica,
                         'numero_incarichi': numero_incarichi }
            }, context_instance=RequestContext(request))


def statistiche(request, which, chi):

    output = []

    if which == 'fatturato':
        for anno in settings.ANNI:
            totale_anno = Decimal('0.0')
            totale_incassato = Decimal('0.0')
            da_incassare = Decimal('0.0')
            if chi == 'snc':
                fatture = Fattura.objects.filter(origine='4Sigma Snc', data__year=anno)
            elif chi == 'studio':
                fatture = Fattura.objects.filter(origine='Studio Associato 4Sigma', data__year=anno)
            else: # ALL
                fatture = Fattura.objects.filter(data__year=anno)
            num_fatture = fatture.count()
            for f in fatture:
                totale_anno += f.importo
                if f.pagata_bool():
                    totale_incassato += f.importo
                else:
                    da_incassare += f.importo
            if totale_anno > Decimal('0.0'):
                percentuale_incasso = Decimal(totale_incassato / totale_anno) * Decimal('100.0')
                fattura_media = Decimal(totale_anno / num_fatture)
            else:
                percentuale_incasso = Decimal('0.0')
                fattura_media = Decimal('0.0')
            output.append({'anno':anno, 'totale_anno':totale_anno, 'percentuale_incasso': percentuale_incasso,
                           'num_fatture':num_fatture, 'fattura_media':fattura_media, 'da_incassare':da_incassare})

        return render_to_response('contabilita/fatturato.html', {
                'output': output }, context_instance=RequestContext(request))

    elif which == 'entrate_uscite':
        for anno in settings.ANNI:
            totale_anno = Decimal('0.0')
            totale_incassato = Decimal('0.0')
            da_incassare = Decimal('0.0')

            totale_spese = Decimal('0.0')
            spese_da_pagare = Decimal('0.0')

            totale_tasse = Decimal('0.0')
            tasse_da_pagare = Decimal('0.0')

            totale_stipendi = Decimal('0.0')
            stipendi_da_pagare = Decimal('0.0')
            totale_dividendi = Decimal('0.0')

            if chi == 'snc':
                fatture = Fattura.objects.filter(origine='4Sigma Snc', data__year=anno)
                fatture_fornitori = FatturaFornitore.objects.filter(origine='4Sigma Snc', data__year=anno)
                spese = Spesa.objects.filter(origine='4Sigma Snc', data__year=anno)
                tasse = Tassa.objects.filter(origine='4Sigma Snc', data__year=anno)
                stipendi = Stipendio.objects.filter(origine='4Sigma Snc', data__year=anno)
                dividendi = Dividendo.objects.filter(origine='4Sigma Snc', data__year=anno)
            elif chi == 'studio':
                fatture = Fattura.objects.filter(origine='Studio Associato 4Sigma', data__year=anno)
                fatture_fornitori = FatturaFornitore.objects.filter(origine='Studio Associato 4Sigma', data__year=anno)
                spese = Spesa.objects.filter(origine='Studio Associato 4Sigma', data__year=anno)
                tasse = Tassa.objects.filter(origine='Studio Associato 4Sigma', data__year=anno)
                stipendi = Stipendio.objects.filter(origine='Studio Associato 4Sigma', data__year=anno)
                dividendi = Dividendo.objects.filter(origine='Studio Associato 4Sigma', data__year=anno)
            else: # ALL
                fatture = Fattura.objects.filter(data__year=anno)
                fatture_fornitori = FatturaFornitore.objects.filter(data__year=anno)
                spese = Spesa.objects.filter(data__year=anno)
                tasse = Tassa.objects.filter(data__year=anno)
                stipendi = Stipendio.objects.filter(data__year=anno)
                dividendi = Dividendo.objects.filter(data__year=anno)

            for f in fatture:
                totale_anno += f.importo
                if f.pagata_bool():
                    totale_incassato += f.importo
                else:
                    da_incassare += f.da_incassare()

            for ff in fatture_fornitori:
                totale_spese += ff.importo
                if not ff.pagata_bool():
                    spese_da_pagare += ff.importo
                    # Rimuovo gli importi già pagati
                    for p in ff.pagamentofatturafornitore_set.all():
                        spese_da_pagare -= p.importo

            for ff in spese:
                totale_spese += ff.importo
                if not ff.pagata_bool():
                    spese_da_pagare += ff.importo
                    # Rimuovo gli importi già pagati
                    for p in ff.pagamentospesa_set.all():
                        spese_da_pagare -= p.importo


            for ff in tasse:
                totale_tasse += ff.importo
                if not ff.pagata_bool():
                    tasse_da_pagare += ff.importo
                    for p in ff.pagamentotassa_set.all():
                        tasse_da_pagare -= p.importo

            for s in stipendi:
                totale_stipendi += s.importo
                if not s.pagata_bool():
                    stipendi_da_pagare += s.importo
                    for p in ff.pagamentostipendio_set.all():
                        stipendi_da_pagare -= p.importo

            for d in dividendi:
                totale_dividendi += d.importo

            utile = totale_anno - totale_spese - totale_tasse - totale_stipendi
            cassa = totale_anno - totale_spese - totale_tasse - totale_stipendi - da_incassare
            output.append({'anno':anno, 'totale_anno':totale_anno, 'da_incassare':da_incassare,
                           'totale_spese': totale_spese, 'totale_tasse': totale_tasse, 'tasse_da_pagare': tasse_da_pagare, 'spese_da_pagare': spese_da_pagare,
                           'utile':utile, 'totale_stipendi': totale_stipendi, 'stipendi_da_pagare': stipendi_da_pagare, 'totale_dividendi': totale_dividendi, 'cassa': cassa })

        return render_to_response('contabilita/entrate_uscite.html', {
                'output': output, 'chi':chi }, context_instance=RequestContext(request))


def debitori(request, chi='all'):
    if chi == 'snc':
        fatture = Fattura.objects.filter(origine='4Sigma Snc').order_by('data')
    elif chi == 'studio':
        fatture = Fattura.objects.filter(origine='Studio Associato 4Sigma').order_by('data')
    else:
        fatture = Fattura.objects.filter().order_by('data')

    elenco = []
    torta = {}
    totale =  Decimal('0.0')
    for f in fatture:
        if not f.pagata_bool():
            elenco.append(f)
            if f.cliente.ragione_sociale not in torta:
                torta[f.cliente.ragione_sociale]  = f.da_incassare()
            else:
                torta[f.cliente.ragione_sociale]  += f.da_incassare()
            totale += f.da_incassare()
    ordinato = sorted(torta.items(), key=lambda t: t[1], reverse=True)
    torta = OrderedDict(ordinato)
    vincitore = ordinato[0]
    return render_to_response('contabilita/debitori.html', {
        'elenco':elenco,
        'chi': chi,
        'torta': torta,
        'vincitore': vincitore,
        'totale': totale
            }, context_instance=RequestContext(request))


