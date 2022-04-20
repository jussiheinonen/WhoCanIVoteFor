from datetime import datetime

from django import template
from django.template.defaultfilters import stringfilter
import re

register = template.Library()


@register.filter(name="ni_postcode")
@stringfilter
def ni_postcode(postcode):
    if re.match("^BT.*", postcode):
        return True


@register.filter(name="todate")
def convert_str_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()


@register.filter(name="totime")
def convert_str_time(value):
    return datetime.strptime(value, "%H:%M:%S").time()
