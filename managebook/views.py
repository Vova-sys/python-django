from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Count, Q, CharField, Value, OuterRef, Subquery, Exists, Prefetch
from django.db.models.functions import Cast
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_page
from pytils.translit import slugify
from managebook.forms import BookForm, CommentForm, CustomUserCreateForm, CustomAuthenticationForm
from managebook.models import BookLike, Book, CommentLike, Comment, Genre
from django.views import View
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from datetime import datetime
from django.utils.decorators import method_decorator
from json import dumps, loads


class BookView(View):
    @method_decorator(cache_page(5))
    def get(self, request, num_page=1):
        response = {'form': CommentForm}
        if request.user.is_authenticated:
            sub_query_1 = Subquery(BookLike.objects.filter(user=request.user, book=OuterRef('pk')).values('rate'))
            sub_query_2 = Exists(User.objects.filter(id=request.user.id, book=OuterRef('pk')))
            sub_query_3 = Exists(User.objects.filter(id=request.user.id, comment=OuterRef('pk')))
            sub_query_4 = Exists(User.objects.filter(id=request.user.id, like=OuterRef('pk')))
            comment = Comment.objects.annotate(is_owner=sub_query_3, is_liked=sub_query_4). \
                select_related('user').prefetch_related('like')
            comment_prefetch = Prefetch('comment', comment)
            result = Book.objects.annotate(user_rate=Cast(sub_query_1, CharField()),
                                           is_owner=sub_query_2)\
                .prefetch_related(comment_prefetch, 'author', 'genre', 'rate')
        else:
            result = Book.objects. \
                prefetch_related("author", 'genre', 'comment', 'comment__user').all()
        pag = Paginator(result, 5)
        response['content'] = pag.page(num_page)
        response['count_page'] = list(range(1, pag.num_pages + 1))
        response['book_form'] = BookForm()
        return render(request, 'index.html', response)


class AddRateBook(View):
    def get(self, request, rate, book_id):
        if request.user.is_authenticated:
            BookLike.objects.create(book_id=book_id, rate=rate, user_id=request.user.id)
        return redirect('hello')


class AddLike(View):
    def get(self, request, comment_id):
        if request.user.is_authenticated:
            CommentLike.objects.create(comment_id=comment_id, user_id=request.user.id)
        return redirect('hello')


class RegisterView(View):
    def get(self, request):
        form = CustomUserCreateForm()
        return render(request, 'register.html', {'form': form})

    def post(self, request):
        form = CustomUserCreateForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('hello')
        messages.error(request, "This Username already exist")
        return redirect('register')


class LoginView(View):
    def get(self, request):
        form = CustomAuthenticationForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('hello')
        messages.error(request, message='User does not exist')
        return redirect('login')


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('hello')


class AddNewBook(View):
    def get(self, request):
        form = BookForm()
        return render(request, 'create_book.html', {'form': form})

    def post(self, request):
        book = BookForm(data=request.POST)
        if book.is_valid():
            nb = book.save(commit=False)
            nb.slug = slugify(nb.title)
            try:
                nb.save()
            except IntegrityError:
                datetime.now().strftime('%Y:%m:%d:%H:%M:%S:%f')
                nb.save()
            nb.author.add(request.user)
            book.save_m2m()
            return redirect('hello')
        return redirect('add_book')


class DeleteBook(View):
    def get(self, request, book_id):
        if request.user.is_authenticated:
            book = Book.objects.get(id=book_id)
            if request.user in book.author.all():
                book.delete()
            return redirect('hello')



class UpdateBook(View):
    def get(self, request, book_slug):
        if request.user.is_authenticated:
            book = Book.objects.get(slug=book_slug)
            if request.user in book.author.all():
                bf = BookForm(instance=book)
                return render(request, 'update_book.html', {'form': bf, 'slug': book_slug})
        return redirect('hello')

    def post(self, request, book_slug):
        book = Book.objects.get(slug=book_slug)
        bf = BookForm(instance=book, data=request.POST)
        if bf.is_valid():
            bf.save()
        return redirect('hello')


class AddComment(View):
    def post(self, request, book_id):
        if request.user.is_authenticated:
            cf = CommentForm(data=request.POST)
            comment = cf.save(commit=False)
            comment.user = request.user
            comment.book_id = book_id
            comment.save()
        return redirect('hello')


class DeleteComment(View):
    def get(self, request, comment_id):
        if request.user.is_authenticated:
            try:
                Comment.objects.get(id=comment_id, user=request.user).delete()
            except Comment.DoesNotExist:
                pass
        return redirect('hello')

class UpdateComment(View):
    def get(self, request, comment_id):
            if request.user.is_authenticated:
                comment = Comment.objects.get(id=comment_id)
                if comment.user == request.user:
                    cf = CommentForm(instance=comment)
                    return render(request, 'update_comment.html', {'form': cf, 'id': comment.id})
            return redirect('hello')

    def post(self, request, comment_id):
        comment = Comment.objects.get(id=comment_id)
        cf = CommentForm(instance=comment, date=request.POST)
        if cf.is_valid():
            cf.save
        return redirect('hello')

class AddLikeAjax(View):
    def post(self, request):
        if request.user.is_authenticated:
            cl_id = request.POST['cl_id'][3:]
            flag = CommentLike(user=request.user, comment_id=cl_id).save()
            comment = Comment.objects.get(id=cl_id)
            return JsonResponse({
                'ok': True,
                'count_like': comment.cached_like,
                'flag': flag,
                'user': request.user.username
            })
        return JsonResponse({'ok': False})

class AddBookRateAjax(View):
    def post(self, request):
        if request.user.is_authenticated:
            bl = BookLike(
                user=request.user, book_id=request.POST["book_id"], rate=request.POST['book_rate'])
            flag = bl.save()
            bl.book.refresh_from_db()
            return JsonResponse({
                "flag": flag,
                "cached_rate": bl.book.cached_rate,
                "rate": bl.rate,
                "user": request.user.username})
        return JsonResponse({"ok": False})

class DeleteCommentAjax(View):
    def delete(self, request, comment_id):
        if request.user.is_authenticated:
            Comment.objects.filter(id=comment_id, user=request.user).delete()
        return JsonResponse({"ok": True})

class AddNewBookAjax(View):
    def post(self, request):
        if request.user.is_authenticated:
            b = Book(title=request.POST['title'], text=request.POST['text'], slug=slugify(request.POST['title']))
            try:
                b.save()
            except IntegrityError:
                b.slug += datetime.now().strftime('%Y:%m:%d:%H:%M:%S:%f')
                b.title += datetime.now().strftime('%Y:%m:%d:%H:%M:%S:%f')
                b.save()
            b.author.add(request.user)

            for g in loads(request.POST['genre']):
                req_g = Genre.objects.get(id=g)
                b.genre.add(req_g)
            b.save()



        return JsonResponse({"ok": True})