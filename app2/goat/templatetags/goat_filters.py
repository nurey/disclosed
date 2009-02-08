import utils

from django import template
import locale
locale.setlocale(locale.LC_ALL, '')
register = template.Library()
 
 
@register.filter()
def currency(value):
    return utils.currency(value)