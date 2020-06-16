from django.urls import path

from . import views
app_name = 'social'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    # path('profile/<str:username>/', views.user_profile, name='profile'), #HOW IT SHOULD BE
    path('profile/', views.user_profile, name='profile'), #Old School, using GET Parameters to select the user
    path('upload_file/', views.upload_file, name='upload_file'), 
    path('edit_file/', views.edit_file, name='edit_file'), 
    path('delete_file/', views.delete_file, name='delete_file'), 
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('static/', views.static, name='static_files'),
]