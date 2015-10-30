#-*- coding: utf-8 -*-
import os, datetime
from django.core.management.base import BaseCommand, CommandError

from contabilita.models import Servizio

from django.conf import settings

class Command(BaseCommand):
    args = ''
    help = '''Invia le mail relative ai servizi in scadenza'''

    option_list = BaseCommand.option_list

    def handle(self,*args,**options):
        # TODO: impostare la mail con le scadenze e inviarla
        self.stdout.write("FATTO", ending='')

