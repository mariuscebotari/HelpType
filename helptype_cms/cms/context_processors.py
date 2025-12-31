from .models import Button, SiteSettings

def site_settings(request):
    settings = {s.key: s.value for s in SiteSettings.objects.all()}
    return {'site_settings': settings}

def global_buttons(request):
    return {
        'header_buttons': Button.objects.filter(locations__contains='header').order_by('order'),
        'footer_buttons': Button.objects.filter(locations__contains='footer').order_by('order'),
        'page_buttons': Button.objects.filter(locations__contains='page').order_by('order'),
    }