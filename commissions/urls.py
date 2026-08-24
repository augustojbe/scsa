from django.urls import path

from commissions import views

app_name = 'commissions'

urlpatterns = [
    path('', views.CommissionListView.as_view(), name='list'),
    path('create/', views.CommissionCreateView.as_view(), name='create'),
    path('<int:pk>/', views.CommissionDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.CommissionUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.CommissionDeleteView.as_view(), name='delete'),
]
