from django.contrib import admin
from django.contrib.admin import register

from managebook.models import Book, Genre


class BookAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ['title', 'publish_date']
    search_fields = ['title']
    list_filter = ['publish_date', 'author', 'genre']


admin.site.register(Book, BookAdmin)
admin.site.register(Genre)
# Register your models here.
