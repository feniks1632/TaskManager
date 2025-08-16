from django.contrib import admin
from django.urls import path, include
from tasks.views import login_view, logout_view, signup_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tasks.urls', namespace='tasks')),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('signup', signup_view, name='signup'),
]
