from django import template
from api.models import Chiqim, Kirim

register = template.Library()

@register.filter
def is_instance_of(obj, class_name):
    class_name = class_name.lower()
    
    if class_name == "chiqim" and isinstance(obj, Chiqim):
        return True
    elif class_name == "kirim" and isinstance(obj, Kirim):
        return True
    return False


@register.filter
def comma_to_dot(value):
    return str(value).replace(',', '.')


@register.filter
def replace(value, arg):
    """ {{ value|replace:"old,new" }} """
    try:
        old, new = arg.split(',')
        return str(value).replace(old, new)
    except ValueError:
        return value
