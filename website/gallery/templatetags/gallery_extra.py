from django import template

register = template.Library()

@register.filter(name="col")
def column(num, val):
    return (num % val) + 1

@register.filter(name="row")
def row(num, val):
    return (num / val) + 1
