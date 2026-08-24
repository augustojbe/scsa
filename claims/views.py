from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from base.mixins import BrokerageRequiredMixin
from base.views import AttachmentDownloadView
from claims.forms import ClaimAttachmentForm, ClaimForm
from claims.models import Claim, ClaimAttachment


class ClaimListView(BrokerageRequiredMixin, ListView):
    model = Claim
    template_name = 'claims/claim_list.html'
    context_object_name = 'claims'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('q', '').strip()
        if search:
            queryset = queryset.filter(
                Q(number__icontains=search)
                | Q(policy__client__name__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('q', '')
        return context


class ClaimDetailView(BrokerageRequiredMixin, DetailView):
    model = Claim
    template_name = 'claims/claim_detail.html'
    context_object_name = 'claim'


class ClaimCreateView(BrokerageRequiredMixin, SuccessMessageMixin, CreateView):
    model = Claim
    form_class = ClaimForm
    template_name = 'claims/claim_form.html'
    success_message = 'Sinistro registrado com sucesso.'

    def get_initial(self):
        initial = super().get_initial()
        policy_id = self.request.GET.get('policy')
        if policy_id:
            policy = Policy.all_objects.filter(
                pk=policy_id, brokerage=self.request.brokerage
            ).first()
            if policy:
                initial['policy'] = policy.pk
        return initial

    def get_success_url(self):
        return reverse('claims:detail', args=[self.object.pk])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.brokerage
        return kwargs

    def form_valid(self, form):
        form.instance.brokerage = self.request.brokerage
        return super().form_valid(form)


class ClaimUpdateView(BrokerageRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Claim
    form_class = ClaimForm
    template_name = 'claims/claim_form.html'
    success_message = 'Sinistro atualizado com sucesso.'

    def get_success_url(self):
        return reverse('claims:detail', args=[self.object.pk])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.brokerage
        return kwargs


class ClaimDeleteView(BrokerageRequiredMixin, DeleteView):
    model = Claim
    template_name = 'claims/claim_confirm_delete.html'
    success_url = reverse_lazy('claims:list')


class ClaimAttachmentCreateView(BrokerageRequiredMixin, SuccessMessageMixin, CreateView):
    model = ClaimAttachment
    form_class = ClaimAttachmentForm
    success_message = 'Anexo adicionado com sucesso.'

    def dispatch(self, request, *args, **kwargs):
        self.claim = get_object_or_404(Claim, pk=self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.brokerage = self.request.brokerage
        form.instance.claim = self.claim
        return super().form_valid(form)

    def form_invalid(self, form):
        for errors in form.errors.values():
            for error in errors:
                messages.error(self.request, error)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('claims:detail', args=[self.claim.pk])


class ClaimAttachmentDownloadView(AttachmentDownloadView):
    model = ClaimAttachment
