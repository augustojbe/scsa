from django.urls import path

from insurers import views

app_name = 'insurers'

urlpatterns = [
    path('', views.InsurerListView.as_view(), name='list'),
    path('create/', views.InsurerCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.InsurerUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.InsurerDeleteView.as_view(), name='delete'),
    path('branches/', views.BranchListView.as_view(), name='branch_list'),
    path('branches/create/', views.BranchCreateView.as_view(), name='branch_create'),
    path('branches/<int:pk>/edit/', views.BranchUpdateView.as_view(), name='branch_edit'),
    path('branches/<int:pk>/delete/', views.BranchDeleteView.as_view(), name='branch_delete'),
]
