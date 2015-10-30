#-*- coding: utf-8 -*-

import csv
from django.core.management.base import BaseCommand, CommandError
from articoli.models import Articolo
from magazzino.models import Magazzino, Giacenza

class Command(BaseCommand):
    args = '<id_magazzino, nome_del_file>'
    help = 'Carica gli articoli nel magazzino specificato'

    def handle(self, *args, **options):
        filename = args[1]
        id_magazzino = int(args[0])
        tot_articoli = 0
        try:
            magazzino = Magazzino.objects.get(id=id_magazzino)
        except Magazzino.DoesNotExist:
             self.stdout.write('Id magazzino errato\n')
             return

        self.stdout.write('%s\n' % filename)
        with open(filename, 'rb') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=';', quotechar='"')
            for row in csvreader:
                try:
                    codice = row[0]
                    articolo = Articolo.objects.get(codice=codice)
                    quantita = int(row[1])
                    ubicazione = row[2]
                    giacenza = Giacenza(magazzino=magazzino,
                                        articolo=articolo,
                                        quantita=quantita,
                                        ubicazione=ubicazione)
                    giacenza.save()
                    tot_articoli += quantita

                except Articolo.DoesNotExist:
                    self.stdout.write('Articolo %s non presente in anagrafica\n' % articolo)
        self.stdout.write('\nImportazione completata: depositati %d articoli\n\n' % tot_articoli)
