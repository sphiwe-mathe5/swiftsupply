from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from core.project.settings import ADMIN_PATH

from core import views 


urlpatterns = [

    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('documents/', views.team, name='team'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
