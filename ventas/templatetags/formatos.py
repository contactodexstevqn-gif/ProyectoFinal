from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


def limpiar_numero(value):
    if value is None or value == '':
        return 0

    try:
        numero = Decimal(str(value))
        return int(numero)
    except (InvalidOperation, ValueError, TypeError):
        return 0


@register.filter
def formato_pesos(value):
    numero = limpiar_numero(value)
    return f'{numero:,}'.replace(',', '.')


@register.filter
def formato_numero(value):
    numero = limpiar_numero(value)
    return f'{numero:,}'.replace(',', '.')