from django.urls import path

from ai import views

app_name = 'ai'

urlpatterns = [
    path('chat/', views.ChatSessionListView.as_view(), name='chat_list'),
    path('chat/create/', views.ChatSessionCreateView.as_view(), name='chat_create'),
    path('chat/<int:pk>/', views.ChatDetailView.as_view(), name='chat_detail'),
    path('chat/<int:pk>/send/', views.ChatSendView.as_view(), name='chat_send'),
    path('notifications/mark-read/', views.NotificationsMarkReadView.as_view(), name='notifications_mark_read'),
    path('summarize/client/<int:pk>/', views.SummarizeClientView.as_view(), name='summarize_client'),
    path('summarize/policy/<int:pk>/', views.SummarizePolicyView.as_view(), name='summarize_policy'),
    path('summarize/claim/<int:pk>/', views.SummarizeClaimView.as_view(), name='summarize_claim'),
    path('summarize/proposal/<int:pk>/', views.SummarizeProposalView.as_view(), name='summarize_proposal'),
    path('summarize/deal/<int:pk>/', views.SummarizeDealView.as_view(), name='summarize_deal'),
]
