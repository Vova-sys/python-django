from django.urls import path

from managebook import views

urlpatterns = [
    path('hello/', views.BookView.as_view(), name='hello'),
    path('add_rate/<int:rate>/<int:book_id>', views.AddRateBook.as_view(), name='add_rate'),
    path('add_like2comment/<int:comment_id>', views.AddLike.as_view(), name='add_like2comment'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]
