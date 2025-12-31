from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from .views import page_view, article_view, blog_by_category_view

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += [
    path('', page_view, {"slug": "home"}, name="home"),
    path('blog/<slug:slug>/', article_view, name="article"),
    path('about/', page_view, {"slug": "about"}, name="about"),
    path('contact/', page_view, {"slug": "contact"}, name="contact"),
    path('blog/category/<slug:slug>/', blog_by_category_view, name="blog_category"),
    path('<slug:slug>/', page_view, name="page"),
    path("ckeditor/", include("ckeditor_uploader.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
