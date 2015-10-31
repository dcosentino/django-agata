import decimal 
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def euro(value):
    return '%.2f' % decimal.Decimal(value)
