#-*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User, Group

class WithDateAndOwner(models.Model):
    created         = models.DateTimeField(auto_now_add=True)
    updated         = models.DateTimeField(auto_now=True)
    owner           = models.ForeignKey(User, related_name="%(app_label)s_%(class)s_related", null=True, blank=True)
    class Meta:
        abstract = True
