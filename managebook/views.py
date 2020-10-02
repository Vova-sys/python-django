from django.contrib.auth import authenticate, login, logout
from django.db.models import Count, Q, CharField, Value
from django.db.models.functions import Cast
from django.http import HttpResponse
from django.shortcuts import render, redirect
from managebook.models import BookLike, Book, CommentLike
from django.views import View
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages

class BookView(View):
    def get(self, request):
        response = {}
        if request.user.is_authenticated:
            quary = Q(book_like__user_id=request.user.id)
            sub_quary = Book.objects.filter(quary). \
                annotate(user_rate=Cast('book_like__rate', CharField())). \
                prefetch_related("author", 'genre', 'comment', 'comment__user')
            result = Book.objects.filter(~quary).annotate(user_rate=Value(-1, CharField())). \
                prefetch_related("author", 'genre', 'comment', 'comment__user').union(sub_quary)
            response['content'] = result.all()
        else:
            response['content'] = Book.objects. \
                prefetch_related("author", 'genre', 'comment', 'comment__user').all()
        return render(request, 'index.html', response)


class AddRateBook(View):
    def get(self, request, rate, book_id):
        if request.user.is_authenticated:
            BookLike.objects.create(book_id=book_id, rate=rate, user_id=request.user.id)
        return redirect('hello')

class AddLike (View):
    def get(self, request, comment_id):
        if request.user.is_authenticated:
            CommentLike.objects.create(comment_id=comment_id, user_id=request.user.id)
        return redirect('hello')


class RegisterView(View):
    def get(self, request):
        form = UserCreationForm()
        return render(request, 'register.html', {'form':form})

    def post(self, request):
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('hello')
        messages.error(request, "This Username already exist")
        return redirect('register')

class LoginView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'login.html', {'form':form})

    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('hello')
        messages.error(request, message='User does not exist')
        return redirect('login')

class LogoutView(View):
    def get(self,request):
        logout(request)
        return redirect('hello')
