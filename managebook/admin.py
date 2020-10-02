from django.contrib import admin
from django.contrib.admin import register

from managebook.models import Book, Comment, Genre


class CommentAdmin(admin.StackedInline):  # класс StackedInLine используется для того, чтобы в админке показывать
    model = Comment  # какой-нибулдь класс вместе с моделью, который имеет некторое отношение к этой модели. Например ForeignKey
    extra = 2  # сколько дополнительных полей для коментов отображается
    readonly_fields = ['like']  # Поля только для чтения


class BookAdmin(admin.ModelAdmin):
    inlines = [CommentAdmin]
    prepopulated_fields = {'slug': ('title',)}
    list_display = ['title', 'publish_date']
    search_fields = ['title']
    list_filter = ['publish_date', 'author', 'genre']


admin.site.register(Book, BookAdmin)
admin.site.register(Genre)
# Register your models here.
