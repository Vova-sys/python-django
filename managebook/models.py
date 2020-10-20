from django.contrib.auth.models import User
from django.db import models, IntegrityError
from django.db.models import Avg


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
    author = models.ManyToManyField(User, verbose_name='автор', db_index=True, related_name='book')
    publish_date = models.DateField(auto_now_add=True)
    genre = models.ManyToManyField('managebook.Genre', verbose_name='жанр')
    rate = models.ManyToManyField(User, through='managebook.BookLike', related_name='rate')
    cached_rate = models.DecimalField(max_digits=3, decimal_places=2, default=0)


class Comment(models.Model):
    text = models.TextField(verbose_name='текст')
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='пользователь', related_name='comment')
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, verbose_name='Книга', related_name='comment')
    like = models.ManyToManyField(
        User,through='CommentLike', related_name='like', blank=True, null=True)
    cached_like = models.PositiveIntegerField(default=0)


class BookLike(models.Model):
    class Meta:
        unique_together = ['user', 'book']
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='book_like')
    rate = models.PositiveBigIntegerField(default=0)

    def save(self, **kwargs):
        try:
            super().save(**kwargs)
        except IntegrityError:
            bl = BookLike.objects.get(user=self.user, book=self.book)
            bl.rate =self.rate
            bl.save()
        else:
            self.book.cached_rate = self.book.book_like.aggregate(Avg('rate'))['rate__avg']
            self.book.save()


class CommentLike(models.Model):
    class Meta:
        unique_together = ['comment', 'user']

    comment = models.ForeignKey(Comment, on_delete=models.CASCADE,related_name='comment_like')
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='comment_like')

    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs)
        except IntegrityError:
            CommentLike.objects.get(comment_id=self.comment.id, user_id=self.user.id).delete()
            self.comment.cached_like -= 1
            flag = False
        else:
            self.comment.cached_like += 1
            flag = True
        self.comment.save()
        return flag