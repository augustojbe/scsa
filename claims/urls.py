from django.urls import path

from claims import views

app_name = 'claims'

urlpatterns = [
    path('', views.ClaimListView.as_view(), name='list'),
    path('create/', views.ClaimCreateView.as_view(), name='create'),
    path('attachments/<int:pk>/download/', views.ClaimAttachmentDownloadView.as_view(), name='claim_attachment_download'),
    path('<int:pk>/', views.ClaimDetailView.as_view(), name='detail'),
    path('<int:pk>/attachments/upload/', views.ClaimAttachmentCreateView.as_view(), name='claim_attachment_create'),
    path('<int:pk>/edit/', views.ClaimUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.ClaimDeleteView.as_view(), name='delete'),
]
