from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from base.mixins import BrokerageRequiredMixin
from base.views import AttachmentDownloadView
from clients.forms import ClientAttachmentForm, ClientForm
from clients.models import Client, ClientAttachment


class ClientListView(BrokerageRequiredMixin, ListView):
    model = Client
    template_name = 'clients/client_list.html'
    context_object_name = 'clients'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('q', '').strip()
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(document__icontains=search)
                | Q(email__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('q', '')
        return context


class ClientDetailView(BrokerageRequiredMixin, DetailView):
    model = Client
    template_name = 'clients/client_detail.html'
    context_object_name = 'client'


class ClientCreateView(BrokerageRequiredMixin, SuccessMessageMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_message = 'Cliente criado com sucesso.'

    def get_success_url(self):
        return reverse_lazy('clients:detail', args=[self.object.pk])

    def form_valid(self, form):
        form.instance.brokerage = self.request.brokerage
        return super().form_valid(form)


class ClientUpdateView(BrokerageRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_message = 'Cliente atualizado com sucesso.'

    def get_success_url(self):
        return reverse_lazy('clients:detail', args=[self.object.pk])


class ClientDeleteView(BrokerageRequiredMixin, DeleteView):
    model = Client
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('clients:list')


class ClientAttachmentCreateView(
    BrokerageRequiredMixin, SuccessMessageMixin, CreateView
):
    model = ClientAttachment
    form_class = ClientAttachmentForm
    success_message = 'Anexo adicionado com sucesso.'

    def dispatch(self, request, *args, **kwargs):
        self.client = get_object_or_404(Client, pk=self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.brokerage = self.request.brokerage
        form.instance.client = self.client
        return super().form_valid(form)

    def form_invalid(self, form):
        for errors in form.errors.values():
            for error in errors:
                messages.error(self.request, error)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('clients:detail', args=[self.client.pk])


class ClientAttachmentDownloadView(AttachmentDownloadView):
    model = ClientAttachment
