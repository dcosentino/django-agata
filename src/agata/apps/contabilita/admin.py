#-*- coding: utf-8 -*-

from django.contrib import admin
from models import *
from django.conf import settings
    
FIELDSETS_ATTIVITA = (
    (None, {
        'fields': [('tipo', 'importo', 'iva'), 'descrizione'],
    }),
    ('Ordine', {
        'fields': [('quantita', 'prezzo_unitario', 'rif_ordine')],
        'classes': ('collapse',),
        'description': u'Informazioni legate all\'ordine emesso dal cliente',
    }),
    ('Project management', {
        'fields': [('data_inizio', 'data_fine')],
        'classes': ('collapse',),
        'description': u'Informazioni legate alla durata dell\'attività',
    }),
)

FIELDSETS_ATTIVITA_MT_SERVICE = (
    (None, {
        'fields': [('tipo', 'importo', 'iva'), 'descrizione'],
    }),
)

class TipoServizioAdmin(admin.ModelAdmin):
    list_display = ['nome']
    list_display_links = ['nome']

class ServizioAdmin(admin.ModelAdmin):
    list_display = ['fattura', 'tipo', 'data_inizio', 'data_fine', 'fatturato']
    list_display_links = ['tipo']
    list_filter = [ 'data_inizio', 'data_fine']

class TipoAttivitaAdmin(admin.ModelAdmin):
    list_display = ['nome']
    list_display_links = ['nome']

class AttivitaAdmin(admin.ModelAdmin):
    list_display = ['fattura', 'tipo', 'data_inizio', 'data_fine', 'fatturato']
    list_display_links = ['tipo']
    list_filter = [ 'data_inizio', 'data_fine']
    raw_id_fields = ['rif_ordine']
    if settings.AGATA_INSTANCE == 'MT Service':
        fieldsets = FIELDSETS_ATTIVITA_MT_SERVICE
    else:
        fieldsets = FIELDSETS_ATTIVITA

class TipoPagamentoAdmin(admin.ModelAdmin):
    list_display = ['nome']
    list_display_links = ['nome']

class PagamentoAdmin(admin.ModelAdmin):
    raw_id_fields = ['fattura']
    list_display = ['origine_fattura', 'cliente_fattura', 'fattura', 'data', 'importo', 'tipo']
    list_filter = ['fattura__origine', 'fattura__cliente']
    search_fields = ['fattura__numero']
    date_hierarchy = 'data'
    ordering = ['-data']
    list_display_links = ['tipo']

class PagamentoInline(admin.TabularInline):
    model = Pagamento
    extra = 1

class ServizioInline(admin.StackedInline):
    model = Servizio
    extra = 1
    fieldsets = (
        (None, {
            'fields': [('tipo', 'importo', 'iva'), ('data_inizio', 'data_fine'), 'descrizione'],
        }),
    )

class AttivitaInline(admin.StackedInline):
    template = 'admin/edit_inline/stacked.html'

    model = Attivita
    raw_id_fields = ['rif_ordine']
    extra = 1
    if settings.AGATA_INSTANCE == 'MT Service':
        fieldsets = FIELDSETS_ATTIVITA_MT_SERVICE
    else:
        fieldsets = FIELDSETS_ATTIVITA


def esporta_debitori(modeladmin, request, queryset):
    import tempfile, os, zipfile
    from django.http import HttpResponse


    dati = ['Cliente;Data fattura;Importo;']

    for data in Fattura.objects.all().order_by('data'):
        if not data.pagata_bool():
            dati.append(
                "%s;%s;%s;" % (
                    data.cliente.ragione_sociale,
                    data.data.strftime("%d/%m/%Y"),
                    data.importo,
                )
            )

    fd, fname = tempfile.mkstemp(suffix='.zip', text=False)
    os.close(fd)
    zipf = zipfile.ZipFile(fname,'w')
    zipf.writestr('debitori.csv', "\n".join(dati).encode('utf8'))
    zipf.close()
    zipfname = "debitori.zip"

    temp = open(fname,'r')

    response = HttpResponse(temp.read(),mimetype='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s'%zipfname
    response['Content-Length'] = temp.tell()

    return response

esporta_debitori.short_description = "Esporta elenco debitori"


class FatturaAdmin(admin.ModelAdmin):
    raw_id_fields = ['cliente']
    list_display = ['origine', 'cliente', 'data', 'numero', 'importo', 'file_fattura', 'tipo', 'tipo_attivita', 'pagata', 'ra_ricevuta']
    list_display_links = ['cliente', 'data', 'numero']
    list_filter = ['origine', 'data', 'tipo', 'cliente', 'tipo_attivita']
    search_fields = ['numero', 'cliente__ragione_sociale']
    date_hierarchy = 'data'
    ordering = ['-data', '-numero']
    inlines = [AttivitaInline, ServizioInline, PagamentoInline]
    actions = [esporta_debitori]
    save_as = True
    if settings.AGATA_INSTANCE == 'MT Service':
        list_display = ['cliente', 'data', 'numero', 'importo', 'file_fattura', 'pagata']
        exclude = ['origine', 'tipo', 'tipo_attivita', 'ra_ricevuta']
        inlines = [AttivitaInline, PagamentoInline]

class TipoFatturaFornitoreAdmin(admin.ModelAdmin):
    list_display = ['nome']
    list_display_links = ['nome']

class PagamentoFatturaFornitoreAdmin(admin.ModelAdmin):
    raw_id_fields = ['fattura']
    list_display = ['origine_fattura', 'fattura', 'data', 'importo', 'tipo']
    list_filter = ['fattura__origine', 'fattura__fornitore']
    search_fields = ['fattura__numero']
    date_hierarchy = 'data'
    ordering = ['-data']
    list_display_links = ['tipo']

class PagamentoFatturaFornitoreInline(admin.TabularInline):
    model = PagamentoFatturaFornitore
    extra = 1


class FatturaFornitoreAdmin(admin.ModelAdmin):
    raw_id_fields = ['fornitore']
    list_display = ['origine', 'fornitore', 'data', 'numero', 'importo', 'file_fattura', 'tipo', 'pagata']
    list_display_links = ['fornitore', 'data', 'numero']
    list_filter = ['origine', 'data', 'tipo', 'fornitore']
    search_fields = ['numero', 'fornitore__ragione_sociale']
    date_hierarchy = 'data'
    ordering = ['-data', '-numero']
    inlines = [PagamentoFatturaFornitoreInline]
    save_as = True


class TipoSpesaAdmin(admin.ModelAdmin):
    list_display = ['nome']
    list_display_links = ['nome']

class PagamentoSpesaAdmin(admin.ModelAdmin):
    raw_id_fields = ['spesa']
    list_display = ['origine_spesa', 'spesa', 'data', 'importo', 'tipo']
    list_filter = ['spesa__origine', 'spesa__fornitore']
    search_fields = ['spesa__numero']
    date_hierarchy = 'data'
    ordering = ['-data']
    list_display_links = ['tipo']

class PagamentoSpesaInline(admin.TabularInline):
    model = PagamentoSpesa
    extra = 1


class SpesaAdmin(admin.ModelAdmin):
    raw_id_fields = ['fornitore']
    list_display = ['origine', 'fornitore', 'data', 'numero', 'importo', 'file_spesa', 'tipo', 'pagata']
    list_display_links = ['fornitore', 'data', 'numero']
    list_filter = ['origine', 'data', 'tipo', 'fornitore']
    search_fields = ['numero', 'fornitore__ragione_sociale']
    date_hierarchy = 'data'
    ordering = ['-data', '-numero']
    inlines = [PagamentoSpesaInline]
    save_as = True

class TipoTassaAdmin(admin.ModelAdmin):
    list_display = ['nome']
    list_display_links = ['nome']

class PagamentoTassaAdmin(admin.ModelAdmin):
    raw_id_fields = ['tassa']
    list_display = ['origine_tassa', 'tassa', 'data', 'importo', 'tipo']
    list_filter = ['tassa__origine']
    search_fields = ['tassa__numero']
    date_hierarchy = 'data'
    ordering = ['-data']
    list_display_links = ['tipo']

class PagamentoTassaInline(admin.TabularInline):
    model = PagamentoTassa
    extra = 1


class TassaAdmin(admin.ModelAdmin):
    list_display = ['origine', 'user', 'data', 'numero', 'importo', 'file_tassa', 'tipo', 'pagata']
    list_display_links = ['data', 'numero']
    list_filter = ['origine', 'data', 'tipo', 'user']
    search_fields = ['numero']
    date_hierarchy = 'data'
    ordering = ['-data', '-numero']
    inlines = [PagamentoTassaInline]

class PagamentoStipendioInline(admin.TabularInline):
    model = PagamentoStipendio

class StipendioAdmin(admin.ModelAdmin):
    list_display = ['origine', 'data', 'user', 'importo']
    list_display_links = ['data', 'user']
    list_filter = ['origine', 'data', 'user']
    search_fields = ['user']
    date_hierarchy = 'data'
    ordering = ['-data', 'user']
    inlines = [PagamentoStipendioInline]

class DividendoAdmin(admin.ModelAdmin):
    list_display = ['origine', 'data', 'user', 'importo']
    list_display_links = ['data', 'user']
    list_filter = ['origine', 'data', 'user']
    search_fields = ['user']
    date_hierarchy = 'data'
    ordering = ['-data', 'user']

class RigaOrdineAcquistoAdmin(admin.ModelAdmin):
    list_display = ['ragione_sociale', 'ordine', 'ordine_data', 'indice_riga',
                    'quantita', 'quantita_fornita', 'prezzo_unitario']
    list_display_links = ['ragione_sociale', 'ordine', 'indice_riga']
    search_fields = ['ordine__cliente__ragione_sociale']
    ordering = ['-ordine__data', 'indice_riga']
    readonly_fields = ['ordine']
    list_editable = ['quantita_fornita']

class RigaOrdineAcquistoInline(admin.TabularInline):
    model = RigaOrdineAcquisto
    extra = 1

class OrdineAcquistoAdmin(admin.ModelAdmin):
    raw_id_fields = ['cliente']
    list_display = ['destinatario', 'cliente', 'data', 'numero', 'file_ordine_cartaceo']
    list_display_links = ['cliente', 'data', 'numero']
    list_filter = ['destinatario', 'data', 'cliente']
    search_fields = ['data', 'numero', 'cliente__ragione_sociale']
    date_hierarchy = 'data'
    ordering = ['-data', '-numero']
    inlines = [RigaOrdineAcquistoInline]

admin.site.register(Dividendo, DividendoAdmin)
admin.site.register(Stipendio, StipendioAdmin)
admin.site.register(TipoTassa, TipoTassaAdmin)
admin.site.register(Tassa, TassaAdmin)
admin.site.register(PagamentoTassa, PagamentoTassaAdmin)

admin.site.register(Servizio, ServizioAdmin)
admin.site.register(TipoServizio, TipoServizioAdmin)
admin.site.register(Attivita, AttivitaAdmin)
admin.site.register(TipoAttivita, TipoAttivitaAdmin)
admin.site.register(Fattura, FatturaAdmin)
admin.site.register(Pagamento, PagamentoAdmin)
admin.site.register(TipoPagamento, TipoPagamentoAdmin)
admin.site.register(TipoSpesa, TipoSpesaAdmin)
admin.site.register(Spesa, SpesaAdmin)
admin.site.register(PagamentoSpesa, PagamentoSpesaAdmin)
admin.site.register(TipoFatturaFornitore, TipoFatturaFornitoreAdmin)
admin.site.register(FatturaFornitore, FatturaFornitoreAdmin)
admin.site.register(OrdineAcquisto, OrdineAcquistoAdmin)
admin.site.register(RigaOrdineAcquisto, RigaOrdineAcquistoAdmin)
