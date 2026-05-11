from django import template

register = template.Library()


@register.filter
def formato_pesos(value):
    if value is None or value == '':
        return '0'

    try:
        numero = int(value)
    except (ValueError, TypeError):
        return '0'

    return f'{numero:,}'.replace(',', '.')


@register.filter
def formato_numero(value):
    if value is None or value == '':
        return '0'

    try:
        numero = int(value)
    except (ValueError, TypeError):
        return '0'

    return f'{numero:,}'.replace(',', '.')