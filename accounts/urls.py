from django.urls import path

from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('home/', views.HomeView.as_view(), name='home'),
]
