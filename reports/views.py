from django.http import Http404
from django.views.generic import TemplateView

from base.mixins import BrokerageRequiredMixin
from reports.exporters import REPORTS, build_csv, build_pdf


class ReportIndexView(BrokerageRequiredMixin, TemplateView):
    template_name = 'reports/report_index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reports'] = [
            {'slug': slug, 'title': title}
            for slug, (title, _) in REPORTS.items()
        ]
        return context


class ReportExportView(BrokerageRequiredMixin, TemplateView):
    fmt = 'csv'

    def get(self, request, slug):
        if slug not in REPORTS:
            raise Http404
        if self.fmt == 'pdf':
            return build_pdf(slug)
        return build_csv(slug)


class ReportCsvView(ReportExportView):
    fmt = 'csv'


class ReportPdfView(ReportExportView):
    fmt = 'pdf'
