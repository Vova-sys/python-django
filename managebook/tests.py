from django.db.models import Avg
from django.test import TestCase
from managebook.models import Book, BookLike, Comment
from django.contrib.auth.models import User


class TestModel(TestCase):
    def test_rate(self):
        user_1 = User.objects.create(username='user_1')
        user_2 = User.objects.create(username='user_2')
        book = Book.objects.create(text='text', slug='slug')
        BookLike.objects.create(book=book, user=user_1, rate=4)
        BookLike.objects.create(book=book, user=user_2, rate=6)
        rate__avg = book.book_like.aggregate(Avg('rate'))['rate__avg']
        self.assertEqual(rate__avg, 5)

    def test_cached_rate(self):
        user_1 = User.objects.create(username='user_1')
        user_2 = User.objects.create(username='user_2')
        book = Book.objects.create(text='text', slug='slug')
        BookLike.objects.create(book=book, user=user_1, rate=4)
        BookLike.objects.create(book=book, user=user_2, rate=6)
        self.assertEqual(book.cached_rate, 5)

    def test_comment_like(self):
        user_1 = User.objects.create(username='user_1')
        user_2 = User.objects.create(username='user_2')
        book = Book.objects.create(text='text', slug='slug')
        comment = Comment.objects.create(text='text', user=user_1, book=book)
        comment.like.add(user_2)
        comment.like.add(user_1)
        comment.save()
        like = comment.like.count()
        self.assertEqual(like, 2)
