import bleach
import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

ALLOWED_TAGS = [
    'p', 'h1', 'h2', 'h3', 'h4', 'ul', 'ol', 'li', 'strong', 'em', 'b', 'i',
    'code', 'pre', 'blockquote', 'br', 'hr', 'a', 'table', 'thead', 'tbody',
    'tr', 'th', 'td',
]

ALLOWED_ATTRS = {'a': ['href', 'title']}


@register.filter
def render_markdown(value):
    if not value:
        return ''
    html = markdown.markdown(
        value,
        extensions=['extra', 'fenced_code', 'sane_lists', 'nl2br'],
    )
    cleaned = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        strip=True,
    )
    return mark_safe(cleaned)
