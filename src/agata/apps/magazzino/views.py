#-*- coding: utf-8 -*-
import re

from django.shortcuts import render_to_response, HttpResponseRedirect, get_object_or_404
from django.conf import settings
from django.template import RequestContext
from django.core.urlresolvers import reverse

from magazzino.models import *

import articoli.models as articoli_db
import anagrafiche.models as anagrafiche_db


def parse_barcodes(text):
    d = {}
    tokens = [ t.strip() for t in re.split(r'\s+', text) if t != "" ]
    for t in tokens:
        if t.find(';') != -1:
            try:
                barcode, qta, ubicazione = t.split(';')
            except ValueError:
                barcode, qta = t.split(';')
            qta = int(qta)
        else:
            barcode, qta, ubicazione = t, 1, None
        d[barcode] = qta + d.setdefault(barcode, 0)
    return d

def parse_barcodes_con_ubicazioni(text):
    d = {} 
    tokens = [ t.strip() for t in re.split(r'\s+', text) if t != "" ]
    ubicazione = None
    for t in tokens:
        #print t
        if t.find(';') != -1:
            try:
                barcode, qta, ubicazione = t.split(';')
            except ValueError:
                barcode, qta = t.split(';')
                ubicazione = None
            qta = int(qta)
        else:
            barcode, qta, ubicazione = t, 1, None
        
        d.setdefault(barcode, {'tot':0, 'ubicazioni':{}})

        # TODO: gestire correttamente ubicazione
        try:
            prev = d[barcode]['ubicazioni'][ubicazione]
        except:
            prev = 0
        d[barcode]['ubicazioni'][ubicazione] = qta+prev
        d[barcode]['tot']+=qta
    #print d
    return d
 
def verifica_letture(letture, tipo, magazzino, richiesta=None, completata=False, id_cliente=None, manuale=False, modifica_richiesta=False):

    import custom.soedis.models as soedis_db

    letture_pulite = parse_barcodes_con_ubicazioni(letture)
    tot_richiesta = 0
    if richiesta:
        richiesta_pulita = parse_barcodes_con_ubicazioni(richiesta)
        for k, dati in richiesta_pulita.iteritems():
            qta = dati['tot']
            ubicazioni = dati['ubicazioni']
            tot_richiesta += qta

    retval = []
    ok = True

    tot = 0

    totali = {
        'ok': 0,
        'unknown': 0,
        'missing': 0,
        'missing_giacenza': 0,
        'some': 0,
        'more': 0,
        'not_requested': 0,
        'articoli': 0
        }


    #print letture_pulite

    for k, dati in letture_pulite.iteritems():
        qta = dati['tot']
        ubicazioni = dati['ubicazioni']
        
        totali['articoli'] += 1
        dato = {
            'codice_ean': k,
            'quantita': qta,
            'ubicazioni': ubicazioni
            }
        tot += qta

        print dato, id_cliente, k
        try:
            if k != '':
                if not manuale:
                    test = articoli_db.Articolo.objects.get(codice_ean=k)
                else:
                    # Sto facendo un operazione manuale, uso il codice articolo e non il barcode a seconda del cliente
                    if id_cliente in [settings.ID_PRODUTTORE_STARLINE]:#, settings.ID_PRODUTTORE_ARNETTA]:
                        test = articoli_db.Articolo.objects.get(produttore__id=id_cliente, codice_ean=k)
                    else:
                        test = articoli_db.Articolo.objects.get(produttore__id=id_cliente, codice=k)
                    print 'test', test
            else:
                continue
            dato['articolo'] = test
            if tipo == 'deposito':
                if richiesta:
                    # Non richiesto
                    # qta_richiesta = richiesta_pulita.get(k, '')  # PRIMA ERA COSÌ
                    qta_richiesta = richiesta_pulita.get(dato['codice_ean'], {'tot':''})['tot']
                    #qta_richiesta = qta_richiesta['tot']
                    dato['richiesta'] = qta_richiesta
                    if qta_richiesta == '':
                        ok = False
                        dato['res'] = 'not_requested'
                        totali['not_requested'] += qta
                    elif qta_richiesta < qta:
                        ok = False
                        dato['res'] = 'more'
                        totali['more'] += qta - qta_richiesta
                    elif qta_richiesta > qta:
                        ok = False
                        dato['res'] = 'missing'
                        totali['missing'] += qta_richiesta - qta
                    else:
                        dato['res'] = 'ok'
                        totali['ok'] += qta
                else:
                    # Si tratta di un operazione di magazzino senza la verifica, quindi è tutto ok
                    dato['res'] = 'ok'
                    totali['ok'] += qta
            elif tipo == 'prelievo':
                if richiesta:
                    qta_richiesta = richiesta_pulita.get(dato['codice_ean'], {'tot':''})['tot']
                    dato['richiesta'] = qta_richiesta
                    #print '-->', qta_richiesta, qta
                    if qta_richiesta == '':
                        #print 'vuoto'
                        ok = False
                        dato['res'] = 'not_requested'
                        totali['not_requested'] += qta
                    elif qta_richiesta < qta:
                        ok = False
                        dato['res'] = 'more'
                        totali['more'] += qta - qta_richiesta
                    elif qta_richiesta > qta:
                        ok = False
                        dato['res'] = 'missing'
                        totali['missing'] += qta_richiesta - qta
                    else:
                        dato['res'] = 'ok'
                        totali['ok'] += qta
                if completata:
                    # Non devo verificare la giacenza
                    dato['res'] = 'ok'
                else:
                    # verifico se la quantita da prelevare è disponibile
                    if dato['ubicazioni']:
                        for ubicazione, qta in dato['ubicazioni'].iteritems():
                            #print ubicazione, qta
                            giacenze = Giacenza.objects.filter(magazzino=magazzino, articolo=test, ubicazione=ubicazione)
                            giacenza = Giacenza(magazzino=magazzino, articolo=test, ubicazione=ubicazione)
                            giacenza.quantita = 0
                            for g in giacenze:
                                giacenza.quantita += g.quantita
                                g.delete()
                            if giacenza.quantita > 0:
                                giacenza.save()
                                #print dato['articolo']
                            try:
                                giacenza = Giacenza.objects.get(magazzino=magazzino, articolo=test, ubicazione=ubicazione)
                                if giacenza.quantita < qta:
                                    dato['res'] = 'missing_giacenza'
                                    totali['missing_giacenza'] += qta - giacenza.quantita
                                    dato['ubicazioni'][ubicazione] = giacenza.quantita - qta
                                    ok = False
                                elif not richiesta or richiesta is None:
                                    dato['res'] = 'ok'
                            except Giacenza.DoesNotExist:
                                dato['res'] = 'missing_giacenza'
                                totali['missing_giacenza'] += qta
                                dato['ubicazioni'][ubicazione] = -qta
                                ok = False
                            except Giacenza.MultipleObjectsReturned:
                                print test.codice_ean
                    else:
                        try:
                            giacenza = Giacenza.objects.get(magazzino=magazzino, articolo=test, ubicazione=None)

                            if giacenza.quantita < qta and not richiesta:
                                dato['res'] = 'missing_giacenza'
                                totali['missing_giacenza'] += qta - giacenza.quantita
                                ok = False
                            elif not richiesta or richiesta is None:
                                dato['res'] = 'ok'
                        except Giacenza.DoesNotExist:
                            #print 'non presente'
                            dato['res'] = 'missing_giacenza'
                            totali['missing_giacenza'] += qta
                            ok = False
        except articoli_db.Articolo.DoesNotExist:
            dato['res'] = 'unknown'
            totali['unknown'] += qta
            ok = False
        except articoli_db.Articolo.MultipleObjectsReturned:
            dato['res'] = 'unknown'
            totali['unknown'] += qta
            dato['codice_ean'] += u'<br/>Più di un articolo per questo barcode'
            ok = False
        #print 'dato',  dato, richiesta
        retval.append(dato)
    if tot == 0:
        ok = False
    if richiesta and tot != tot_richiesta:
        # verifico i mancanti rispetto alla richiesta
        for k,v in richiesta_pulita.iteritems():
            if letture_pulite.get(k, None) is None:
                dato = {
                    'codice_ean': k,
                    'quantita': 0,
                    'res': 'missing',
                    'richiesta': richiesta_pulita.get(k, '???').get('tot', '???'),
                    'ubicazioni': None
                    }

                try:
                    if k != '' and k != None:
                        if not manuale:
                            test = articoli_db.Articolo.objects.get(codice_ean=k)
                        else:
                            # Sto facendo un operazione manuale, uso il codice articolo e non il barcode
                            test = articoli_db.Articolo.objects.get(produttore__id=id_cliente, codice=k)          
                    else:
                        continue
                    dato['articolo'] = test
                    #totali['missing'] += qta
                    if id_cliente == settings.ID_PRODUTTORE_SOEDIS and tipo == 'deposito' and False:
                        # Verifico che non si agià stato sparato qualche barcode per master carton di quell'articolo
                        articolo_soedis = soedis_db.Articolo.objects.get(codice_ean=k)
                        if letture_pulite.get(articolo_soedis.barcode_master_carton, None) is None:
                            dato['articolo'] = test
                            totali['missing'] += qta
                            retval.append(dato)
                    else:
                        dato['articolo'] = test
                        totali['missing'] += qta
                        retval.append(dato)
                except:
                    pass
                    #print 'barcode con problemi:', k
                #ok = False
        ok = False
        if modifica_richiesta:
            ok = True
    #print 'retval', retval
    return ok, tot, retval, totali


def operazioni(request, tipo, id_operazione='', tutto=None, manuale=False):
    completata = False
    modifica_richiesta = False
    if id_operazione != '':
        operazione = get_object_or_404(OperazioneMagazzino, id=id_operazione)

        try:
            id_cliente = operazione.ordine.societa.id
        except:
            id_cliente = None

        if id_cliente == settings.ID_PRODUTTORE_GEOWORLD:
            manuale = True

        if operazione.stato in ['Annullata','Completata']:
            # Devo solo visualizzare i risultati
            completata = True
            ok, tot_pezzi, verifica, totali = verifica_letture(operazione.letture, tipo, None, operazione.richiesta, completata, id_cliente, manuale, modifica_richiesta)

            return render_to_response('magazzino/operazione_magazzino.html', {
                    'tipo': tipo,
                    'verifica': verifica,
                    'lettura_ok': ok,
                    'tot_pezzi': tot_pezzi,
                    'totali': totali,
                    'id_operazione': id_operazione,
                    'completata': completata,
                    'operazione': operazione
                    }, context_instance=RequestContext(request))

        form = OperazioneMagazzinoForm(instance=operazione)
        richiesta = operazione.ordine.richiesta

    else:
        form = OperazioneMagazzinoForm()
        richiesta = None
    verifica = None
    ok = False
    tot_pezzi = 0
    totali = None
    id_cliente = None

            
    if request.method == 'POST':
        if request.POST.get('modifica_richiesta', 'FALSE') == 'TRUE':
            modifica_richiesta = True


        form = OperazioneMagazzinoForm(request.POST)
        try:
            id_magazzino_ingresso = int(request.POST.get('magazzino_ingresso'))
            magazzino_ingresso = Magazzino.objects.get(id=id_magazzino_ingresso)
        except ValueError:
            magazzino_ingresso = None
        try:
            id_magazzino_uscita = int(request.POST.get('magazzino_uscita'))
            magazzino_uscita = Magazzino.objects.get(id=id_magazzino_uscita)
        except ValueError:
            magazzino_uscita = None

        if tipo == 'deposito':
            magazzino = magazzino_ingresso
        elif tipo == 'prelievo':
            magazzino = magazzino_uscita
        if manuale:
            id_cliente = int(request.POST.get('cliente', -1))
        else:
            try:
                id_cliente = operazione.ordine.societa.id
            except:
                id_cliente = None
            
        #print 'id_cliente, manuale, modifica_richiesta ', id_cliente, manuale, modifica_richiesta
        ok, tot_pezzi, verifica, totali = verifica_letture(request.POST.get('letture', ''), tipo, magazzino, richiesta, completata, id_cliente, manuale, modifica_richiesta)

        if request.POST.get('completa', 'False') == 'True' or modifica_richiesta:
            # Salvo l'operazione
            if id_operazione != '':
                operazione.richiesta = richiesta
                operazione.letture = request.POST['letture']
                operazione.note = request.POST['note']
                operazione.stato = 'Completata'
                operazione.pezzi = tot_pezzi
                operazione.save()

                operazione.ordine.stato = 'Completata'
                operazione.ordine.richiesta_modificata = modifica_richiesta
                operazione.ordine.save()

            else:
                op = OperazioneMagazzino(
                    tipo = tipo,
                    magazzino_ingresso = magazzino_ingresso,
                    magazzino_uscita = magazzino_uscita,
                    letture = request.POST['letture'],
                    note = request.POST['note'],
                    stato = 'Completata',
                    pezzi = tot_pezzi
                    )
                op.save()
            # Aggiorno la giacenza di magazzino
            for v in verifica:
                #print 'v=', v
                if tipo == 'deposito':
                    # TODO: ciclo for sulle ubicazioni per prelievi e depositi
                    if v['ubicazioni']:
                        for ubicazione, qta in v['ubicazioni'].iteritems():
                            try:
                                giacenza = Giacenza.objects.get(magazzino=magazzino_ingresso,
                                                                articolo=v['articolo'], 
                                                                ubicazione=ubicazione
                                                            )
                            except Giacenza.DoesNotExist:
                                giacenza = Giacenza(magazzino=magazzino_ingresso,
                                                    articolo=v['articolo'],
                                                    ubicazione=ubicazione,
                                                    quantita = 0)
                            giacenza.quantita += qta
                            giacenza.save()
                                
                    else:
                        try:
                            giacenza = Giacenza.objects.get(magazzino=magazzino_ingresso,
                                                            articolo=v['articolo'], ubicazione=None)
                        except Giacenza.DoesNotExist:
                            giacenza = Giacenza(magazzino=magazzino_ingresso,
                                                articolo=v['articolo'],
                                                ubicazione=None,
                                                quantita = 0)
                        giacenza.quantita += v['quantita']                            
                        giacenza.save()
                        # Aggiunto per gestire i casi in cui abbiamo i depositi con modifica rispetto alla richiesta
                        if giacenza.quantita == 0:
                            giacenza.delete()

                elif tipo == 'prelievo':
                    if v['ubicazioni']:
                        for ubicazione, qta in v['ubicazioni'].iteritems():
                            giacenza = Giacenza.objects.get(magazzino=magazzino_uscita,
                                                            articolo=v['articolo'],
                                                            ubicazione=ubicazione)
                            giacenza.quantita -= qta
                            giacenza.save()
                            
                            if giacenza.quantita == 0:
                                giacenza.delete()
                    else:
                        try:
                            giacenza = Giacenza.objects.get(magazzino=magazzino_uscita,
                                                        articolo=v['articolo'],
                                                        ubicazione=None
                                                        )
                            giacenza.quantita -= v['quantita']
                            giacenza.save()

                            if giacenza.quantita == 0:
                                giacenza.delete()
                        except Giacenza.DoesNotExist:
                            pass

            return HttpResponseRedirect(reverse('operazione_completata'))

    return render_to_response('magazzino/operazione_magazzino.html', {
        'form': form,
        'tipo': tipo,
        'verifica': verifica,
        'lettura_ok': ok,
        'tot_pezzi': tot_pezzi,
        'totali': totali,
        'id_operazione': id_operazione,
        'id_cliente': id_cliente,
        'clienti': anagrafiche_db.Societa.objects.all().order_by('ragione_sociale'),
        'completata': completata, 'manuale': manuale
            }, context_instance=RequestContext(request))


def operazioni_ubicazioni(request, tipo):
    form = GiacenzaForm()
    verifica = None
    ok = False
    tot_pezzi = 0
    totali = None
    msg = None
    msg_class = None
    if request.method == 'POST':
        form = GiacenzaForm(request.POST)
        if form.is_valid():
            codice = form.cleaned_data['codice_articolo']
            articolo = articoli_db.Articolo.objects.get(codice=codice)
            magazzino = form.cleaned_data['magazzino']
            quantita=form.cleaned_data['quantita']
            ubicazione=form.cleaned_data['ubicazione']
            note=form.cleaned_data['note']

            if tipo == 'deposito':
                try:
                    giacenza = Giacenza.objects.get(magazzino=magazzino,
                                                    ubicazione=ubicazione,
                                                    articolo=articolo)
                    giacenza.quantita += quantita
                except Giacenza.DoesNotExist:
                        """
                        try:
                    if ubicazione != '' and ubicazione is not None:
                        # Verifico se c'è qualcos'altro nella stessa ubicazione
                            giacenza = Giacenza.objects.get(magazzino=magazzino,
                                                            ubicazione=ubicazione
                                                            )
                            msg = u"Deposito non disponibile: l'ubicazione %s è già occupata dall'articolo %s" % (ubicazione, giacenza.articolo.codice)
                            msg_class = "err"
                            return render_to_response('magazzino/operazione_magazzino_ubicazioni.html', {
                                    'form': form,
                                    'operazione': tipo,
                                    'verifica': verifica,
                                    'lettura_ok': ok,
                                    'tot_pezzi': tot_pezzi,
                                    'totali': totali,
                                    'msg': msg,
                                    'msg_class': msg_class
                                    }, context_instance=RequestContext(request))
                        except Giacenza.DoesNotExist:
                            giacenza = Giacenza(magazzino=magazzino,
                                                ubicazione=ubicazione,
                                                articolo=articolo,
                                                quantita=quantita)
                    else:
                        giacenza = Giacenza(magazzino=magazzino,
                                            ubicazione=ubicazione,
                                            articolo=articolo,
                                            quantita=quantita)
                       """
                        # Non esiste, la creo
                        giacenza = Giacenza(magazzino=magazzino,
                                            ubicazione=ubicazione,
                                            articolo=articolo,
                                            quantita=quantita)
                        

                giacenza.save()

                # Salvo l'operazione
                op = OperazioneMagazzino(
                    tipo = tipo,
                    magazzino_ingresso = magazzino,
                    letture = u"%s;%d;%s" % (articolo, quantita, ubicazione),
                    stato = 'Completata',
                    note=note,
                    pezzi=quantita
                    )
                op.save()

                msg = u"Operazione %d<br/>Articolo %s depositato nel magazzino %s" % (op.id, articolo, magazzino)
                msg_class = "ok"

                initial = {
                    'magazzino': magazzino
                    }
                form = GiacenzaForm(initial=initial)

            elif tipo == 'prelievo':
                try:
                    giacenza = Giacenza.objects.get(magazzino=magazzino,
                                                    ubicazione=ubicazione,
                                                    articolo=articolo)
                    if  giacenza.quantita < quantita:
                        msg = u"Prelievo non disponibile: la quantità presente (%d) è minore di quella richiesta (%s)" % (giacenza.quantita, quantita)
                        msg_class = "err"
                    else:
                        giacenza.quantita -= quantita
                        giacenza.save()

                        # Salvo l'operazione
                        op = OperazioneMagazzino(
                            tipo = tipo,
                            magazzino_uscita = magazzino,
                            letture = u"%s;%d;%s" % (articolo, quantita, ubicazione),
                            stato = 'Completata',
                            note=note,
                            pezzi=quantita
                            )
                        op.save()

                        msg = u"Operazione %d<br/>Articolo %s prelevato dal magazzino %s" % (op.id, articolo, magazzino)
                        msg_class = "ok"

                        initial = {
                            'magazzino': magazzino
                            }
                        form = GiacenzaForm(initial=initial)

                except Giacenza.DoesNotExist:
                    elenco = Giacenza.objects.filter(magazzino=magazzino,
                                                     articolo=articolo)
                    if ubicazione:
                        msg = u"Articolo %s non presente nell'ubicazione %s del magazzino %s" % (articolo, ubicazione, magazzino)
                    else:
                        msg = u""
                    if elenco.count() > 0:
                        msg += u"""<br/>Articolo presente nelle seguenti ubicazioni:<br/>"""
                        for e in elenco:
                            if e.ubicazione:
                                msg += u"%s - %d pezzi<br/>" % (e.ubicazione, e.quantita)
                            else:
                                msg += u"Ubicazione senza nome<br/>"
                    else:
                        altri = Giacenza.objects.filter(articolo=articolo)
                        if altri.count() > 0:
                            msg = u"Articolo %s non presente nel magazzino %s, ma presente nei seguenti magazzini:<br/>" % (articolo, magazzino)
                            for a in altri:
                                msg += u'%s<br/>' % a.magazzino.nome
                        else:
                            msg = u"Articolo %s non presente nel magazzino %s" % (articolo, magazzino)
                    msg_class = "err"


    return render_to_response('magazzino/operazione_magazzino_ubicazioni.html', {
            'form': form,
            'operazione': tipo,
            'verifica': verifica,
            'lettura_ok': ok,
            'tot_pezzi': tot_pezzi,
            'totali': totali,
            'msg': msg,
            'msg_class': msg_class
            }, context_instance=RequestContext(request))


def operazione_completata(request):
    return render_to_response('magazzino/operazione_completata.html', {}, context_instance=RequestContext(request))




def apri_ordine(request, id_ordine):
    ordine = get_object_or_404(Ordine, id=id_ordine)

    if ordine.operazione is None:
        op = OperazioneMagazzino(
            tipo = ordine.tipo,
            magazzino_ingresso = ordine.magazzino_ingresso,
            magazzino_uscita = ordine.magazzino_uscita,
            richiesta = ordine.richiesta,
            stato=ordine.stato,
            note=ordine.note,
            )
        op.save()
        ordine.operazione = op
        ordine.save()

    else:
        op = ordine.operazione

    return HttpResponseRedirect(reverse('operazione_magazzino', args=[op.tipo, op.id]))

def vedi_ordine(request, id_ordine):
    ordine = get_object_or_404(Ordine, id=id_ordine)
    th_aggiuntive = []
    td_aggiuntive = []
    # Personalizzazioni
    if ordine.societa.id == settings.ID_PRODUTTORE_SOEDIS:
        th_aggiuntive.append('Barcode Master Carton') 

    return render_to_response('magazzino/dettaglio_ordine.html', {'ordine': ordine, 'settings': settings}, context_instance=RequestContext(request))


def storico_articoli(request):
    elenco = []
    giacenze = None
    clienti = anagrafiche_db.Societa.objects.all().order_by('ragione_sociale')
    codice_articolo = ''
    if request.method == 'POST':
        codice_articolo = request.POST.get('codice', '')
        """cliente = request.POST.get('cliente', '')
        try:
            cliente = anagrafiche_db.Societa.objects.get(id=cliente)
            articolo = articoli_db.Articolo.objects.get(fornitore=cliente, codice=codice)
        except:
            pass
        """
        dati = OperazioneMagazzino.objects.filter(stato='Completata', letture__icontains=codice_articolo).order_by('ts_operazione')
        for d in dati:
            letture_pulite = parse_barcodes(d.letture)
            elenco.append((
                d.ts_operazione, d.tipo, d.magazzino_ingresso, d.magazzino_uscita, codice_articolo, letture_pulite[codice_articolo], d.note
            )
                      )
        giacenze = Giacenza.objects.filter(articolo__codice=codice_articolo)
        #print '---', codice_articolo, giacenze

    return render_to_response('magazzino/storico_articoli.html', {'elenco': elenco, 'giacenze':giacenze, 'clienti': clienti, 'codice':codice_articolo}, context_instance=RequestContext(request))

def str_or_empty(string):
    if string is None:
        return ''
    else:
        return string


def storico_articoli_download(request, codice):
    
    import tempfile, os, zipfile
    from django.http import HttpResponse
    from django.utils.html import strip_tags

    output = [u"Data operazione;Tipo operazione;Magazzino Ingresso;Magazzino Uscita;Codice Articolo;Quantità;Note"]
    dati = OperazioneMagazzino.objects.filter(stato='Completata', letture__icontains=codice).order_by('ts_operazione')
    for d in dati:
        letture_pulite = parse_barcodes(d.letture)
        output.append("%s;%s;%s;%s;%s;%s;%s;" % (
            d.ts_operazione.strftime("%d/%m/%Y %H:%M:%S"), 
            d.tipo, 
            str_or_empty(d.magazzino_ingresso), 
            str_or_empty(d.magazzino_uscita), 
            codice, 
            letture_pulite[codice], 
            d.note.replace('\n', ' ').replace('\r', ' ')
        )
        )

    fd, fname = tempfile.mkstemp(suffix='.zip', text=False)
    os.close(fd)
    zipf = zipfile.ZipFile(fname,'w')
    zipf.writestr('storico_operazioni.csv', "\n".join(output).encode('utf8'))
    zipf.close()
    zipfname = "storico_operazioni.zip"

    temp = open(fname,'r')

    response = HttpResponse(temp.read(),mimetype='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s'%zipfname
    response['Content-Length'] = temp.tell()

    return response
