from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('shop/', include('managebook.urls'), name='managebook'),
    path('', include('social_django.urls', namespace='social')),
    path('accounts/', include('allauth.urls'))
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns
