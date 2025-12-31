from django.contrib import admin
from django.db import models

try:
    from adminsortable2.admin import SortableAdminBase, SortableInlineAdminMixin
except Exception:
    class SortableAdminBase: pass
    class SortableInlineAdminMixin: pass

from .models import Block, BlockTranslation, Page, PageBlock, Language, Category, Button, SiteSettings, BlogPost, Testimonial
from .widgets import CodeMirrorWidget 
try:
    from ckeditor_uploader.widgets import CKEditorUploadingWidget
except Exception:
    CKEditorUploadingWidget = None
from django import forms
from django.shortcuts import redirect
from django.contrib import messages



class BlockTranslationInline(admin.TabularInline):
    model = BlockTranslation
    extra = 0
    fields = ('language', 'content')
    formfield_overrides = {
        models.TextField: {'widget': CodeMirrorWidget},
    }


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ('title',)
    inlines = [BlockTranslationInline]
    search_fields = ('title',)
    formfield_overrides = {
        models.TextField: {'widget': CodeMirrorWidget},
    }


@admin.register(BlockTranslation)
class BlockTranslationAdmin(admin.ModelAdmin):
    list_display = ('block', 'language')
    fields = ('block', 'language', 'content')
    formfield_overrides = {
        models.TextField: {'widget': CodeMirrorWidget},
    }


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'created_at')
    search_fields = ('title', 'body')
    list_filter = ('categories', 'created_at')
    filter_horizontal = ('categories',)
    prepopulated_fields = {'slug': ('title',)}
    if CKEditorUploadingWidget:
        formfield_overrides = {
            models.TextField: {'widget': CKEditorUploadingWidget()},
        }
    else:
        formfield_overrides = {
            models.TextField: {'widget': CodeMirrorWidget},
        }
    # Inline editing for categories using the through model so editors can
    # add/remove category relations directly from the BlogPost edit page.

    # Use a custom changelist template so we can render a "Add category" form
    change_list_template = 'admin/cms/blogpost/change_list.html'

    # Small form to allow quick creation of Category from the BlogPost changelist
    class CategoryForm(forms.ModelForm):
        class Meta:
            model = Category
            fields = ['name', 'slug']

    def changelist_view(self, request, extra_context=None):
        """Override to handle quick category creation form on the changelist."""
        extra_context = extra_context or {}
        if request.method == 'POST' and 'add_category' in request.POST:
            form = self.CategoryForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Category created successfully.")
                return redirect(request.path)
            else:
                messages.error(request, "Please fix the errors in the category form.")
                extra_context['category_form'] = form
        else:
            extra_context['category_form'] = self.CategoryForm()

        # include full categories list so we can render management table
        try:
            extra_context['categories'] = Category.objects.all()
        except Exception:
            extra_context['categories'] = []

        return super().changelist_view(request, extra_context=extra_context)


# Tabular inline for the ManyToMany through table between BlogPost and Category
class CategoryInline(admin.TabularInline):
    model = BlogPost.categories.through
    extra = 1




@admin.register(SiteSettings)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')
    search_fields = ('key', 'value')
    formfield_overrides = {
        models.TextField: {'widget': CodeMirrorWidget},
    }


class PageBlockInline(SortableInlineAdminMixin, admin.TabularInline):
    model = PageBlock
    extra = 1
    sortable_field_name = "order"
    autocomplete_fields = ['block']


@admin.register(Page)
class PageAdmin(SortableAdminBase, admin.ModelAdmin):
    inlines = [PageBlockInline]
    list_display = ('title', 'slug')
    search_fields = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Button)
class ButtonAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'order', 'color')
    list_editable = ('order',)
    list_display_links = ('name',)


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'active')
    list_editable = ('active',)                
    search_fields = ('code', 'name')



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    
    def get_model_perms(self, request):
        """Hide Category from the app index while keeping admin views accessible via direct links.

        Returning an empty dict prevents the model from showing in the admin app list,
        but the change/add/delete views remain available if you link to them directly
        (which the BlogPost changelist does).
        """
        return {}


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("author_name", "title", "author_role")
    search_fields = ("author_name", "title", "author_role")

