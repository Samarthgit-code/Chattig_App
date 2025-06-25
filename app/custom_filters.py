from django import template

register = template.Library()

@register.filter
def humanize_views(value):
    try:
        value = int(value)
        if value >= 1_000_000:
            return f"{value/1_000_000:.1f}M".rstrip('0').rstrip('.')
        elif value >= 1_000:
            return f"{value/1_000:.1f}K".rstrip('0').rstrip('.')
        else:
            return str(value)
    except (ValueError, TypeError):
        return value
