from django.urls import path

from agents import views

app_name = 'agents'

urlpatterns = [
    path('', views.AgentListView.as_view(), name='list'),
    path('create/', views.AgentCreateView.as_view(), name='create'),
    path('<int:pk>/', views.AgentDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.AgentUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.AgentDeleteView.as_view(), name='delete'),
    path('producers/', views.ProducerListView.as_view(), name='producer_list'),
    path('producers/create/', views.ProducerCreateView.as_view(), name='producer_create'),
    path('producers/<int:pk>/', views.ProducerDetailView.as_view(), name='producer_detail'),
    path('producers/<int:pk>/edit/', views.ProducerUpdateView.as_view(), name='producer_edit'),
    path('producers/<int:pk>/delete/', views.ProducerDeleteView.as_view(), name='producer_delete'),
]
