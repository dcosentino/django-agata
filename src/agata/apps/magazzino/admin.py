#-*- coding: utf-8 -*-

from django.contrib import admin
from models import *


class MagazzinoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'giacenza']
    list_display_links = ['nome']

def str_or_empty(string):
    if string is None:
        return ''
    else:
        return string

def int_or_empty(numero):
    if numero is None:
        return ''
    else:
        return '%d'% numero


def esporta_giacenze(modeladmin, request, queryset):
    import tempfile, os, zipfile
    from django.http import HttpResponse


    dati = ['Magazzino;Produttore;Codice Articolo;Codice EAN;Descrizione;Quantita;Ubicazione;']

    for data in queryset:
        dati.append(
            "%s;%s;%s;%s;%s;%d;%s;" % (
                str_or_empty(data.magazzino.nome),
                str_or_empty(data.articolo.produttore.ragione_sociale),
                str_or_empty(data.articolo.codice),
                str_or_empty(data.articolo.codice_ean),
                str_or_empty(data.articolo.descrizione),
                data.quantita,
                str_or_empty(data.ubicazione)
                )
            )

    fd, fname = tempfile.mkstemp(suffix='.zip', text=False)
    os.close(fd)
    zipf = zipfile.ZipFile(fname,'w')
    zipf.writestr('giacenze.csv', "\n".join(dati).encode('utf8'))
    zipf.close()
    zipfname = "giacenze.zip"

    temp = open(fname,'r')

    response = HttpResponse(temp.read(),mimetype='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s'%zipfname
    response['Content-Length'] = temp.tell()

    return response

esporta_giacenze.short_description = "Esporta giacenze selezionate"


def esporta_giacenze_starline(modeladmin, request, queryset):
    import tempfile, os, zipfile
    from django.http import HttpResponse


    dati = ['Magazzino;Marca;Tipologia;Codice Articolo;Codice EAN;Descrizione;Taglia;Colore;Tessuto;Drop;Quantita;Ubicazione;']

    for data in queryset:
        try:
            test = data.articolo.starline_articolo_related

            dati.append(
                "%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%d;%s;" % (
                    str_or_empty(data.magazzino.nome),
                    str_or_empty(data.articolo.starline_articolo_related.marca),
                    str_or_empty(data.articolo.starline_articolo_related.tipologia),
                    str_or_empty(data.articolo.codice),
                    str_or_empty(data.articolo.codice_ean),
                    str_or_empty(data.articolo.descrizione),
                    str_or_empty(data.articolo.starline_articolo_related.taglia),
                    str_or_empty(data.articolo.starline_articolo_related.colore),
                    str_or_empty(data.articolo.starline_articolo_related.tessuto),
                    int_or_empty(data.articolo.starline_articolo_related.drop),
                    data.quantita,
                    str_or_empty(data.ubicazione),
                )
            )
        except:
            pass

    fd, fname = tempfile.mkstemp(suffix='.zip', text=False)
    os.close(fd)
    zipf = zipfile.ZipFile(fname,'w')
    zipf.writestr('giacenze_starline.csv', "\n".join(dati).encode('utf8'))
    zipf.close()
    zipfname = "giacenze_starline.zip"

    temp = open(fname,'r')

    response = HttpResponse(temp.read(),mimetype='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s'%zipfname
    response['Content-Length'] = temp.tell()

    return response

esporta_giacenze_starline.short_description = "Esporta giacenze Starline selezionate"



class GiacenzaAdmin(admin.ModelAdmin):
    list_display = ['magazzino', 'produttore', 'articolo', 'codice_ean', 'quantita', 'ubicazione']
    list_display_links = ['articolo']
    list_filter = ['magazzino']
    readonly_fields = ['magazzino', 'articolo','quantita', 'ubicazione', 'in_prelievo', 'in_deposito']
    search_fields = ['articolo__codice_ean', 'articolo__codice']
    actions = [esporta_giacenze, esporta_giacenze_starline]


def esporta_movimenti(modeladmin, request, queryset):
    import tempfile, os, zipfile
    from django.http import HttpResponse


    dati = ['Tipo;Magazzino ingresso;Magazzino uscita;Data e ora operazione;Stato;Pezzi']

    for data in queryset:
        if data.magazzino_ingresso:
            magazzino_ingresso = data.magazzino_ingresso.nome
        else:
            magazzino_ingresso = ''
        if data.magazzino_uscita:
            magazzino_uscita = data.magazzino_uscita.nome
        else:
            magazzino_uscita = ''
        dati.append(
            "%s;%s;%s;%s;%s;%s;" % (
                str_or_empty(data.tipo),
                magazzino_ingresso,
                magazzino_uscita,
                str_or_empty(data.ts_operazione.strftime("%d/%m/%Y %H:%M:%S")),
                str_or_empty(data.stato),
                int_or_empty(data.pezzi),
                )
            )

    fd, fname = tempfile.mkstemp(suffix='.zip', text=False)
    os.close(fd)
    zipf = zipfile.ZipFile(fname,'w')
    zipf.writestr('movimenti.csv', "\n".join(dati).encode('utf8'))
    zipf.close()
    zipfname = "movimenti.zip"

    temp = open(fname,'r')

    response = HttpResponse(temp.read(),mimetype='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s'%zipfname
    response['Content-Length'] = temp.tell()

    return response

esporta_movimenti.short_description = "Esporta movimenti selezionati"

class OperazioneMagazzinoAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'magazzino_ingresso', 'magazzino_uscita', 'ts_operazione', 'stato', 'pezzi', 'note']
    list_display_links = ['ts_operazione']
    list_filter = ['tipo', 'magazzino_ingresso', 'magazzino_uscita',]
    readonly_fields = ['tipo', 'magazzino_ingresso', 'magazzino_uscita', 'ts_operazione', 'stato', 'letture', 'richiesta', 'pezzi']
    date_hierarchy = 'ts_operazione'
    actions = [esporta_movimenti]


def esporta_ordini(modeladmin, request, queryset):
    import tempfile, os, zipfile
    from django.http import HttpResponse
    #out = open(settings.EXPORT_ORDINI_GEOWORLD_PATH+'/PROVA.TXT', 'a')
    tot = 0
    for record in queryset:
        if record.societa.id == settings.ID_PRODUTTORE_GEOWORLD and not record.esportato and record.stato == 'Completata' and record.peso_netto and record.peso_lordo and record.numero_colli:
            out = open(settings.EXPORT_ORDINI_GEOWORLD_PATH+'/'+record.numero_documento.strip()+'.out', 'w')
            record_AS400 = ['TESTA ']
            record_AS400.append(record.numero_documento.strip().encode('ascii').ljust(10)) 
            record_AS400.append(' ')
            record_AS400.append(record.data_documento.strftime('%d%m%Y'))
            record_AS400.append(' ')
            record_AS400.append(record.codice_cliente_fornitore.strip().encode('ascii').rjust(8)) 
            record_AS400.append(' ')
            record_AS400.append(record.ragione_sociale_anagrafica.strip().encode('ascii').ljust(180)) 
            record_AS400.append(record.note.replace('\r', ' ').replace('\n', '').strip().encode('ascii').ljust(72)) 
            #record_AS400.append(' ')
            if record.peso_lordo:
                record_AS400.append('%09.2f' % record.peso_lordo)          
            else:
                record_AS400.append('%09.2f' % 0.0)
            record_AS400.append(' ')
            if record.peso_netto:
                record_AS400.append('%09.2f' % record.peso_netto)          
            else:
                record_AS400.append('%09.2f' % 0.0)
            record_AS400.append(' ')
            if record.numero_colli:
                record_AS400.append('%09d' % record.numero_colli)            
            else:
                record_AS400.append('%09d' % 0)            
            record_AS400.append(' ')
            record_AS400.append(record.note_logistica.replace('\r', ' ').replace('\n', '').strip().encode('ascii')) 
            riga = ''.join(record_AS400)
            out.write(riga)
            out.write('\r\n')
            for art in record.richiesta_hr():
                record_AS400 = ['CORPO ']
                record_AS400.append(art['articolo'].codice.encode('ascii').ljust(20))
                record_AS400.append(' ')
                record_AS400.append(art['articolo'].descrizione[:50].encode('ascii').ljust(52))
                record_AS400.append('pz. ')
                record_AS400.append('%013d' % art['quantita'])
                record_AS400.append(' ')
                if art['articolo'].codice_ean:
                    record_AS400.append(art['articolo'].codice_ean.encode('ascii').ljust(40))
                else:
                    record_AS400.append(' '.ljust(40))
                riga = ''.join(record_AS400)
                out.write(riga)
                out.write('\r\n')
            out.flush()
            record.esportato = True
            record.save()
            out.close()
            tot += 1
    return HttpResponse('Esportazione completata<br/>Esportati %d ordini' % tot)
esporta_ordini.short_description = "Esporta ordini selezionati"


class OrdineAdmin(admin.ModelAdmin):
    list_display = ['societa', 'tipo', 'magazzino_ingresso', 'magazzino_uscita',
                    'ts_ordine',  'ragione_sociale_anagrafica', 'numero_documento', 'stato', 'pezzi', 'stampa_lista', 'apri_ordine', 'peso_lordo', 'peso_netto', 'numero_colli', 'esportato', 'richiesta_modificata']
    list_display_links = ['ts_ordine']
    list_filter = ['tipo', 'magazzino_ingresso', 'magazzino_uscita', 'esportato', 'richiesta_modificata']
    readonly_fields = ['societa', 'tipo', 'magazzino_ingresso', 'magazzino_uscita', 'ts_ordine', 'numero_documento', 'stato', 'operazione', 'richiesta', 'pezzi', 'note', 'numero_documento', 'data_documento', 'codice_cliente_fornitore', 'ragione_sociale_anagrafica', 'file_originale', 'richiesta_modificata']
    date_hierarchy = 'ts_ordine'
    actions = [esporta_ordini]

admin.site.register(OperazioneMagazzino, OperazioneMagazzinoAdmin)
admin.site.register(Ordine, OrdineAdmin)
admin.site.register(Giacenza, GiacenzaAdmin)
admin.site.register(Magazzino, MagazzinoAdmin)
