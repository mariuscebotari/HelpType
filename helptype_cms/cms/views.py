from django.shortcuts import render, get_object_or_404
from django.template import RequestContext, Template
from django.utils.safestring import mark_safe
import requests
from django.conf import settings
from .models import BlogPost, Page, Button, PageBlock, SiteSettings, Category, Block, Language, BlockTranslation, Testimonial
from .forms import ContactForm

def get_site_settings():
    """Return site settings as a dictionary."""
    return {s.key: s.value for s in SiteSettings.objects.all()}

def article_view(request, slug):
    blog_post = get_object_or_404(BlogPost, slug=slug)
    buttons = Button.objects.all().order_by('order')
    site_settings = get_site_settings()
    categories = Category.objects.all()

    try:
        lang_code = getattr(request, 'LANGUAGE_CODE', settings.LANGUAGE_CODE)
        language = Language.objects.filter(code=lang_code, active=True).first()
        article_block = Block.objects.get(title="Article Layout")

        translation = None
        if language:
            translation = BlockTranslation.objects.filter(block=article_block, language=language).first()

        content_src = translation.content if (translation and translation.content) else article_block.content

        rendered_article = Template(content_src).render(RequestContext(request, {
            'blog_post': blog_post,
            'site_settings': site_settings,
            'buttons': buttons,
            'categories': categories,
        }))
        page_blocks = [{'title': blog_post.title, 'content': rendered_article}]
    except Block.DoesNotExist:
        page_blocks = []

    return render(request, "cms/page.html", {
        "page_blocks": page_blocks,
        "buttons": buttons,
        "site_settings": site_settings,
        "blog_posts": [],
        "show_blog_list": False,
        "blog_post": blog_post,
    })


def page_view(request, slug="home"):
    page = get_object_or_404(Page, slug=slug)
    buttons = Button.objects.all().order_by('order')
    site_settings = get_site_settings()
    blog_posts = BlogPost.objects.all().order_by('-created_at')
    categories = Category.objects.all()
    testimonials = Testimonial.objects.all()

    sent = False
    error = None
    form = ContactForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        cd = form.cleaned_data
        try:
            text = (
                f"📩 Mesaj nou de pe site:\n\n"
                f"👤 Nume: {cd['name']}\n"
                f"📞 Telefon: {cd.get('phone','')}\n"
                f"✉️ Email: {cd['email']}\n"
                f"📌 Subiect: {cd.get('subject','')}\n"
                f"💬 Mesaj: {cd['message']}"
            )

            url = f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage"
            payload = {"chat_id": settings.TELEGRAM_CHAT_ID, "text": text}

            requests.post(url, data=payload)
            sent = True
        except Exception as e:
            error = str(e)

    page_blocks = []
    context = {
        "site_settings": site_settings,
        "buttons": buttons,
        "page": page,
        "blog_posts": blog_posts,
        "form": form,
        "sent": sent,
        "error": error,
        "request": request,
        "categories": categories,
        "testimonials": testimonials,
    }

    for pb in PageBlock.objects.filter(page=page).select_related('block').order_by('order'):
        lang_code = getattr(request, 'LANGUAGE_CODE', settings.LANGUAGE_CODE)
        language = Language.objects.filter(code=lang_code, active=True).first()
        translation = None
        if language:
            translation = BlockTranslation.objects.filter(block=pb.block, language=language).first()

        src = translation.content if (translation and translation.content) else pb.block.content

        try:
            rendered = Template(src).render(RequestContext(request, context))
        except Exception:
            rendered = src

        page_blocks.append({'title': pb.block.title, 'content': mark_safe(rendered)})

    return render(request, "cms/page.html", {
        "page": page,
        "page_blocks": page_blocks,
        "site_settings": site_settings,
        "buttons": buttons,
        "blog_posts": blog_posts,
        "form": form,
        "sent": sent,
        "error": error,
    })



def blog_by_category_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    blog_posts = BlogPost.objects.filter(categories=category).order_by('-created_at')
    buttons = Button.objects.all().order_by('order')
    site_settings = get_site_settings()
    categories = Category.objects.all()

    try:
        block = Block.objects.get(title="Blog Category")
        rendered_content = Template(block.content).render(RequestContext(request, {
            "current_category": category,
            "category": category,
            "blog_posts": blog_posts,
            "categories": categories,
        }))
    except Block.DoesNotExist:
        rendered_content = f"<h2>Posts in category: {category.name}</h2>"

    page_blocks = [{
        "title": f"Category: {category.name}",
        "content": mark_safe(rendered_content),
    }]

    return render(request, "cms/page.html", {
        "page_blocks": page_blocks,
        "buttons": buttons,
        "site_settings": site_settings,
        "categories": categories,
        "current_category": category,
        "show_blog_list": True,
    })
