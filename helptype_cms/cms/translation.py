from modeltranslation.translator import register, TranslationOptions
from .models import Button

@register(Button)
class ButtonTranslationOptions(TranslationOptions):
    fields = ('name',)
