# from django import template
# from django.contrib.humanize.templatetags.humanize import intcomma as original_intcomma

# register = template.Library()

# @register.filter(name="intcomma")
# def intcomma(value):
#     """Global override of intcomma: use space instead of comma."""
#     result = original_intcomma(value)
#     return result.replace(",", " ")
