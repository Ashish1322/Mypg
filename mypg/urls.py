"""mypg URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

# For authentication urls in case of forgeeten password
# accounts/logout/ [name='logout']
# accounts/password_change/ [name='password_change']
# accounts/password_change/done/ [name='password_change_done']
# accounts/password_reset/ [name='password_reset']
# accounts/password_reset/done/ [name='password_reset_done']
# accounts/reset/<uidb64>/<token>/ [name='password_reset_confirm']
# accounts/reset/done/ [name='password_reset_complete']

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home,name="home"),
    path('login-apna-thikana/', views.login_user,name="login"),
    path('signup-apna-thikana/', views.signup_user,name="signup"),
    path('logout/', views.logout_user,name="logout"),
    path('about-us/', views.about,name="about"),
    path('privacy-policy/', views.policy,name="policy"),
    path('terms-conditions/', views.conditions,name="conditions"),
    path('pg/', include('pg.urls')),
    # Password forgeeten urls
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='mypg/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="mypg/password_reset_confirm.html"), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='mypg/password_reset_complete.html'), name='password_reset_complete'),  
    path("password_reset", views.password_reset_request, name="password_reset"),
    path("activate/<uidb64>/<token>",views.get, name="activate"), # Account activation url


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)