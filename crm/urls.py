from django.urls import path

from crm import views

app_name = 'crm'

urlpatterns = [
    path('', views.KanbanView.as_view(), name='kanban'),
    path('grid/', views.DealListView.as_view(), name='deal_list'),
    path('deals/create/', views.DealCreateView.as_view(), name='deal_create'),
    path('deals/<int:pk>/move/', views.DealMoveView.as_view(), name='deal_move'),
    path('deals/<int:pk>/', views.DealDetailView.as_view(), name='deal_detail'),
    path('deals/<int:pk>/edit/', views.DealUpdateView.as_view(), name='deal_edit'),
    path('deals/<int:pk>/delete/', views.DealDeleteView.as_view(), name='deal_delete'),
    path('pipelines/', views.PipelineListView.as_view(), name='pipeline_list'),
    path('pipelines/create/', views.PipelineCreateView.as_view(), name='pipeline_create'),
    path('pipelines/<int:pk>/', views.PipelineDetailView.as_view(), name='pipeline_detail'),
    path('pipelines/<int:pk>/edit/', views.PipelineUpdateView.as_view(), name='pipeline_edit'),
    path('pipelines/<int:pk>/delete/', views.PipelineDeleteView.as_view(), name='pipeline_delete'),
    path('pipelines/<int:pipeline_pk>/stages/create/', views.PipelineStageCreateView.as_view(), name='stage_create'),
    path('stages/<int:pk>/edit/', views.PipelineStageUpdateView.as_view(), name='stage_edit'),
    path('stages/<int:pk>/delete/', views.PipelineStageDeleteView.as_view(), name='stage_delete'),
]
