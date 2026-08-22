from django.urls import path

from policies import views

app_name = 'policies'

urlpatterns = [
    path('coverages/', views.CoverageListView.as_view(), name='coverage_list'),
    path('coverages/create/', views.CoverageCreateView.as_view(), name='coverage_create'),
    path('coverages/<int:pk>/edit/', views.CoverageUpdateView.as_view(), name='coverage_edit'),
    path('coverages/<int:pk>/delete/', views.CoverageDeleteView.as_view(), name='coverage_delete'),
    path('items/', views.CoveredItemListView.as_view(), name='item_list'),
    path('items/create/', views.CoveredItemCreateView.as_view(), name='item_create'),
    path('items/<int:pk>/edit/', views.CoveredItemUpdateView.as_view(), name='item_edit'),
    path('items/<int:pk>/delete/', views.CoveredItemDeleteView.as_view(), name='item_delete'),
    path('proposals/', views.ProposalListView.as_view(), name='proposal_list'),
    path('proposals/create/', views.ProposalCreateView.as_view(), name='proposal_create'),
    path('attachments/<int:pk>/download/', views.ProposalAttachmentDownloadView.as_view(), name='proposal_attachment_download'),
    path('proposals/<int:pk>/', views.ProposalDetailView.as_view(), name='proposal_detail'),
    path('proposals/<int:pk>/attachments/upload/', views.ProposalAttachmentCreateView.as_view(), name='proposal_attachment_create'),
    path('proposals/<int:pk>/edit/', views.ProposalUpdateView.as_view(), name='proposal_edit'),
    path('proposals/<int:pk>/delete/', views.ProposalDeleteView.as_view(), name='proposal_delete'),
]
