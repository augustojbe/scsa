from django.http import FileResponse, Http404
from django.views import View

from base.mixins import BrokerageRequiredMixin


class AttachmentDownloadView(BrokerageRequiredMixin, View):
    model = None

    def get(self, request, pk):
        attachment = (
            self.model.all_objects.filter(pk=pk, brokerage=request.brokerage).first()
        )
        if attachment is None:
            raise Http404
        response = FileResponse(attachment.file.open('rb'))
        response['Content-Disposition'] = f'inline; filename="{attachment.filename}"'
        response['X-Content-Type-Options'] = 'nosniff'
        return response
