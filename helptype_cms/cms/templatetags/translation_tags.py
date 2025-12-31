from django import template
from django.utils.safestring import mark_safe
from django.conf import settings
from django.template import engines, RequestContext
from django.template import TemplateSyntaxError
import html

from cms.models import BlockTranslation

register = template.Library()
django_engine = engines['django']


@register.simple_tag(takes_context=True)
def render_block(context, block):
    """
    - Dacă limba curentă este limba implicită (settings.LANGUAGE_CODE) -> afișează block.content
    - Altminteri -> afișează BlockTranslation (dacă există) sau mesaj de missing
    - Deblochează HTML escapet (html.unescape) și compilează conținutul ca template
    """
    request = context.get('request')
    if not block:
        return ''

    lang = getattr(request, 'LANGUAGE_CODE', settings.LANGUAGE_CODE) or settings.LANGUAGE_CODE
    lang_code = str(lang).split('-')[0].lower()
    default_code = str(settings.LANGUAGE_CODE).split('-')[0].lower()

    # Dacă cerem limba implicită, folosim întotdeauna block.content
    if lang_code == default_code:
        content = block.content or ""
    else:
        trans = BlockTranslation.objects.filter(block=block, language__code__iexact=lang_code).first()
        content = trans.content if trans and trans.content and trans.content.strip() else None

    if not content or not content.strip():
        return mark_safe(
            f"<div class='translation-missing'>Translation missing for block '{getattr(block, 'title', getattr(block, 'slug', ''))}' and language '{lang_code}'</div>"
        )

    # dacă conținutul e escapet (&lt; &gt;) -> unescape
    if '&lt;' in content or '&gt;' in content:
        content = html.unescape(content)

    # compilează și renderizează cu motorul Django (permite {% trans %}, {% load %}, etc.)
    try:
        tpl = django_engine.from_string(content)
        ctx = RequestContext(request, context.flatten()) if request is not None else context
        rendered = tpl.render(ctx)
    except TemplateSyntaxError:
        rendered = content
    except Exception:
        rendered = content

    return mark_safe(rendered)
