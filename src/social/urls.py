from django.urls import path

from . import views
app_name = 'social'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    # path('profile/<str:username>/', views.user_profile, name='profile'), #HOW IT SHOULD BE
    path('profile/', views.user_profile, name='profile'), #Old School, using GET Parameters to select the user
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
]