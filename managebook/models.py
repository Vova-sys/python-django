from django.contrib.auth.models import User
from django.db import models


class Genre(models.Model):
    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    title = models.CharField(max_length=50, verbose_name='название')

    def __str__(self):
        return self.title


class Book(models.Model):
    class Meta:
        verbose_name = 'Книги'
        verbose_name_plural = 'Книги'

    def __str__(self):
        if self.title is not None:
            return self.title
        else:
            return "name is not defined"

    title = models.CharField(
        max_length=50,
        verbose_name='название',
        help_text="help text",
        db_index=True,
    )
    slug = models.SlugField(verbose_name='Слаг')
    text = models.TextField(verbose_name='текст')
    author = models.ManyToManyField(User, verbose_name='автор')
    publish_date = models.DateField(auto_now_add=True)
    genre = models.ManyToManyField('managebook.Genre', verbose_name='жанр')
    rate = models.ManyToManyField(User, through='managebook.BookLike', related_name='rate')



class Comment(models.Model):
    text = models.TextField(verbose_name='текст')
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='пользователь')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name='Книга')
    like = models.ManyToManyField(User, related_name='like')


class BookLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rate = models.PositiveBigIntegerField(default=0)
