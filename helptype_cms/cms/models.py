from django.db import models
try:
    from ckeditor_uploader.fields import RichTextUploadingField
except Exception:
    RichTextUploadingField = None

class Language(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Block(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class BlockTranslation(models.Model):
    block = models.ForeignKey(Block, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.block.title} ({self.language.code})"


class Page(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.title


class PageBlock(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    block = models.ForeignKey(Block, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    # Use CKEditor RichTextUploadingField when available so editors can add
    # headings, images and other rich content. Fall back to TextField.
    if RichTextUploadingField:
        body = RichTextUploadingField(blank=True, null=True)
    else:
        body = models.TextField(blank=True, null=True)
    # optional featured image
    image = models.ImageField(upload_to='blog/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, blank=True)

    def __str__(self):
        return self.title



class Button(models.Model):
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    color = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name


class SiteSettings(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=500)

    def __str__(self):
        return self.key

class Testimonial(models.Model):
    title = models.CharField(max_length=200)
    comment = models.TextField()
    author_name = models.CharField(max_length=100)
    author_role = models.CharField(max_length=100)
    image = models.ImageField(upload_to="testimonials")

    class Meta:
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"

    def __str__(self):
        return f"{self.author_name} – {self.title}"
    

