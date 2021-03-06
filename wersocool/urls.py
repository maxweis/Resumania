from django.conf.urls import include
from django.urls import path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic.base import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from users import urls as users_urls
from users import views as users_views
from rso_manage import urls as rso_urls
from events import urls as events_urls
from analytics import urls as analytics_urls
from .views import home_view, github_redirect, youtube_video_redirect

urlpatterns = [
    path('', home_view, name='home'),
    path('signup', users_views.SignUp, name='signup'),
    path('login', auth_views.LoginView.as_view(), {'template_name': 'login.html'}, name='login'),
    path('logout', auth_views.LogoutView.as_view(), {'template_name': 'logged_out.html'}, name='logout'),
    path('admin', admin.site.urls),
    path('github', github_redirect),
    path('video', youtube_video_redirect),
    path('about_us', TemplateView.as_view(template_name='about_us.html'), name='about_us'),
    path('users/', include(users_urls)),
    path('rsos/', include(rso_urls)),
    path('analytics/', include(analytics_urls)),
    path('', include(events_urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
