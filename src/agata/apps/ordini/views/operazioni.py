#-*- coding: utf-8 -*-


from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.context_processors import csrf

import datetime

import magazzino.models as magazzino_db
import articoli.models as articoli_db
import ordini.models as ordini_db


def prelievo(request, idordine):
    idordine = int(idordine,10)
    ordine = get_object_or_404(ordini_db.Ordine, id = idordine) 

    if ordine.stato == "Aperto":
        c = {
            'articoli': ordine.lista_articoli(),    
            'idordine': idordine,
            'letture': ordine.lista_letture(),
            'operazione': "Prelievo"
            }
        c.update(csrf(request))
    
        return render_to_response('ordini/prelievo.html', c)
    else:
        return render_to_response('ordini/visualizza_prelievo.html', {"ordine": ordine})


def verifica_prelievo(request, idordine):
    idordine = int(idordine,10)
    ordine = get_object_or_404(ordini_db.Ordine, id = idordine) 

    if request.method != "POST":
        # non accetto altri metodi
        print "ARG!"
        return redirect(reverse('prelievo', args=[idordine]))

    # prendiamo le letture
    letture = request.POST['codici']
    # salviamole
    ordine.letture = letture
    ordine.save()
    # verifichiamo
    dati = [ v for k,v in ordine.lista_articoli(False).items() ]

    sconosciuti = [ v for v in dati if v['sconosciuto'] ]
    incompleti =  [ v for v in dati if v['letti'] < v['qta'] ]
    completi = [ v for v in dati if v['letti'] == v['qta'] ]
    esubero =  [ v for v in dati if v['letti'] > v['qta'] and not v['sconosciuto'] ]

    ok_salva = True if len(esubero)==0 and len(sconosciuti)==0 else False
    warn_salva = True if len(incompleti)!=0 else False
    
    c = {
        'ordine': ordine,
        'idordine': idordine,
        'sconosciuti': sconosciuti,
        'incompleti': incompleti,
        'completi': completi,
        'esubero': esubero,
        'nsconosciuti': len(sconosciuti),
        'nincompleti': len(incompleti),
        'ncompleti': len(completi),
        'nesubero': len(esubero),
        'ok_salva': ok_salva,
        'warn_salva': warn_salva,
        }
    c.update(csrf(request))
    return render_to_response('ordini/verifica_prelievo.html',c)
    


def chiudi_prelievo(request, idordine):
    idordine = int(idordine,10)
    ordine = get_object_or_404(ordini_db.Ordine, id = idordine) 

    # verifica
    dati = [ v for k,v in ordine.lista_articoli(False).items() ]

    sconosciuti = [ v for v in dati if v['sconosciuto'] ]
    incompleti =  [ v for v in dati if v['letti'] < v['qta'] ]
    completi = [ v for v in dati if v['letti'] == v['qta'] ]
    esubero =  [ v for v in dati if v['letti'] > v['qta'] and not v['sconosciuto'] ]

    ok_salva = True if len(esubero)==0 and len(sconosciuti)==0 else False

    if not ok_salva:
        # non accetto la chiusura
        return redirect(reverse('prelievo', args=[idordine]))

    passa = completi + incompleti
    for art in passa:
        dett = ordine.dettaglioordine_set.filter(articolo__codice = art['bcr'])
        n = art['letti']
        for d in dett:
            if n == 0:
                break
            rimuovere = min(n, d.richiesto)
            n-=rimuovere
            if d.numero is None:
                d.numero = 0
            d.numero+=rimuovere
            d.save()
    ordine.completamento = datetime.datetime.now()
    ordine.save()

    return redirect("/admin/")
