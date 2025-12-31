from django.contrib.sitemaps import Sitemap
from .models import Page, BlogPost

class PageSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Page.objects.all()

    def location(self, obj):
        if getattr(obj, "slug", "") == "home":
            return "/"
        return f"/{obj.slug}/"

class BlogSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return BlogPost.objects.all()

    def location(self, obj):
        return f"/blog/{obj.slug}/"

    def lastmod(self, obj):
        return getattr(obj, "created_at", None)