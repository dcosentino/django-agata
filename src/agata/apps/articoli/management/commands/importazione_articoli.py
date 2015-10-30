#-*- coding: utf-8 -*-

import csv
from django.core.management.base import BaseCommand, CommandError
from articoli.models import Articolo
from anagrafiche.models import Societa

class Command(BaseCommand):
    args = '<id_produttore, nome_del_file>'
    help = 'Aggiunge in anagrafica gli articoli'

    def handle(self, *args, **options):
        filename = args[1]
        id_produttore = int(args[0])
        tot_articoli = 0
        try:
            produttore = Societa.objects.get(id=id_produttore)
        except Produttore.DoesNotExist:
             self.stdout.write('Id produttore errato\n')
             return

        self.stdout.write('%s\n' % filename)
        with open(filename, 'rb') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=';', quotechar='"')
            for row in csvreader:
                try:
                    codice = row[0]
                    codice_ean = row[1]

                    self.stdout.write(u'%s', % codice_ean)
                    descrizione = row[2]

                    if codice_ean != '':
                        test = Articolo.objects.get(codice_ean=codice_ean)
                        self.stdout.write('Articolo EAN: %s già presente\n' % codice_ean)
                    else:
                        codice_ean = None # Serve a evitare casini con articoli con ean
                        test = Articolo.objects.get(codice=codice)
                        self.stdout.write('Articolo codice: %s già presente\n' % codice)
                except Articolo.DoesNotExist:
                    a = Articolo(
                        produttore=produttore,
                        codice=codice,
                        codice_ean=codice_ean,
                        descrizione=descrizione)
                    a.save()
                    tot_articoli += 1
        self.stdout.write('\nImportazione completata: aggiunti %d articoli in anagrafica\n\n' % tot_articoli)
