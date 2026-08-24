from django.urls import path

from renewals import views

app_name = 'renewals'

urlpatterns = [
    path('', views.RenewalListView.as_view(), name='list'),
    path('create/', views.RenewalCreateView.as_view(), name='create'),
    path('<int:pk>/', views.RenewalDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.RenewalUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.RenewalDeleteView.as_view(), name='delete'),
]
