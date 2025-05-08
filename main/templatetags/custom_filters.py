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
