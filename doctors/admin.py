from django.contrib import admin
from .models import Category, Blogs, Comments


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id_category", "name")
    search_fields = ("name",)


@admin.register(Blogs)
class BlogsAdmin(admin.ModelAdmin):
    list_display = ("blog_id", "title", "doctor", "id_category", "is_published", "posted_at")
    list_filter = ("is_published", "id_category", "posted_at")
    search_fields = ("title", "summary", "description")
    list_editable = ("is_published",)


@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_display = ("comment_id", "blog", "user", "commented_at")
    list_filter = ("commented_at",)
    search_fields = ("comment",)