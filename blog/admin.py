from django.contrib import admin

from .models import Post, Tag


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    date_hierarchy = 'published_at'
    list_display = ('title', 'author', 'published_at')
    filter_horizontal = ('tags',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    filter_horizontal = ('posts',)

