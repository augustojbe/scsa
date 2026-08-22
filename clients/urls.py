from django.urls import path

from clients import views

app_name = 'clients'

urlpatterns = [
    path('', views.ClientListView.as_view(), name='list'),
    path('create/', views.ClientCreateView.as_view(), name='create'),
    path('attachments/<int:pk>/download/', views.ClientAttachmentDownloadView.as_view(), name='attachment_download'),
    path('<int:pk>/', views.ClientDetailView.as_view(), name='detail'),
    path('<int:pk>/attachments/upload/', views.ClientAttachmentCreateView.as_view(), name='attachment_create'),
    path('<int:pk>/edit/', views.ClientUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.ClientDeleteView.as_view(), name='delete'),
]
