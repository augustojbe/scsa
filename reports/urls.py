from django.urls import path

from reports import views

app_name = 'reports'

urlpatterns = [
    path('', views.ReportIndexView.as_view(), name='index'),
    path('<slug:slug>/csv/', views.ReportCsvView.as_view(), name='csv'),
    path('<slug:slug>/pdf/', views.ReportPdfView.as_view(), name='pdf'),
]
