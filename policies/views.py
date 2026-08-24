from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, View

from base.mixins import BrokerageRequiredMixin
from base.views import AttachmentDownloadView
from policies.forms import (
    CoverageForm,
    CoveredItemForm,
    EndorsementForm,
    PolicyAttachmentForm,
    PolicyForm,
    ProposalAttachmentForm,
    ProposalForm,
)
from policies.models import (
    Coverage,
    CoveredItem,
    Endorsement,
    Policy,
    PolicyAttachment,
    Proposal,
    ProposalAttachment,
)
from policies.services import generate_policy_from_proposal


class CoverageListView(BrokerageRequiredMixin, ListView):
    model = Coverage
    template_name = 'policies/coverage_list.html'
    context_object_name = 'coverages'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('q', '').strip()
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('q', '')
        return context


class CoverageCreateView(BrokerageRequiredMixin, SuccessMessageMixin, CreateView):
    model = Coverage
    form_class = CoverageForm
    template_name = 'policies/coverage_form.html'
    success_url = reverse_lazy('policies:coverage_list')
    success_message = 'Cobertura criada com sucesso.'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.brokerage
        return kwargs

    def form_valid(self, form):
        form.instance.brokerage = self.request.brokerage
        return super().form_valid(form)


class CoverageUpdateView(BrokerageRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Coverage
    form_class = CoverageForm
    template_name = 'policies/coverage_form.html'
    success_url = reverse_lazy('policies:coverage_list')
    success_message = 'Cobertura atualizada com sucesso.'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.brokerage
        return kwargs


class CoverageDeleteView(BrokerageRequiredMixin, DeleteView):
    model = Coverage
    template_name = 'policies/coverage_confirm_delete.html'
    success_url = reverse_lazy('policies:coverage_list')


class CoveredItemListView(BrokerageRequiredMixin, ListView):
    model = CoveredItem
    template_name = 'policies/item_list.html'
    context_object_name = 'items'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('q', '').strip()
        if search:
            queryset = queryset.filter(description__icontains=search)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('q', '')
        return context


class CoveredItemCreateView(BrokerageRequiredMixin, SuccessMessageMixin, CreateView):
    model = CoveredItem
    form_class = CoveredItemForm
    template_name = 'policies/item_form.html'
    success_url = reverse_lazy('policies:item_list')
    success_message = 'Item coberto criado com sucesso.'

    def form_valid(self, form):
        form.instance.brokerage = self.request.brokerage
        return super().form_valid(form)


class CoveredItemUpdateView(BrokerageRequiredMixin, SuccessMessageMixin, UpdateView):
    model = CoveredItem
    form_class = CoveredItemForm
    template_name = 'policies/item_form.html'
    success_url = reverse_lazy('policies:item_list')
    success_message = 'Item coberto atualizado com sucesso.'


class CoveredItemDeleteView(BrokerageRequiredMixin, DeleteView):
    model = CoveredItem
    template_name = 'policies/item_confirm_delete.html'
    success_url = reverse_lazy('policies:item_list')


class ProposalListView(BrokerageRequiredMixin, ListView):
    model = Proposal
    template_name = 'policies/proposal_list.html'
    context_object_name = 'proposals'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('q', '').strip()
        if search:
            queryset = queryset.filter(client__name__icontains=search)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('q', '')
        return context


class ProposalDetailView(BrokerageRequiredMixin, DetailView):
    model = Proposal
    template_name = 'policies/proposal_detail.html'
    context_object_name = 'proposal'


class ProposalCreateView(BrokerageRequiredMixin, SuccessMessageMixin, CreateView):
    model = Proposal
    form_class = ProposalForm
    template_name = 'policies/proposal_form.html'
    success_message = 'Proposta criada com sucesso.'

    def get_success_url(self):
        return reverse_lazy('policies:proposal_detail', args=[self.object.pk])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.brokerage
        return kwargs

    def form_valid(self, form):
        form.instance.brokerage = self.request.brokerage
        return super().form_valid(form)


class ProposalUpdateView(BrokerageRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Proposal
    form_class = ProposalForm
    template_name = 'policies/proposal_form.html'
    success_message = 'Proposta atualizada com sucesso.'

    def get_success_url(self):
        return reverse_lazy('policies:proposal_detail', args=[self.object.pk])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.brokerage
        return kwargs


class ProposalDeleteView(BrokerageRequiredMixin, DeleteView):
    model = Proposal
    template_name = 'policies/proposal_confirm_delete.html'
    success_url = reverse_lazy('policies:proposal_list')


class ProposalAttachmentCreateView(
    BrokerageRequiredMixin, SuccessMessageMixin, CreateView
):
    model = ProposalAttachment
    form_class = ProposalAttachmentForm
    success_message = 'Anexo adicionado com sucesso.'

    def dispatch(self, request, *args, **kwargs):
        self.proposal = get_object_or_404(Proposal, pk=self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.brokerage = self.request.brokerage
        form.instance.proposal = self.proposal
        return super().form_valid(form)

    def form_invalid(self, form):
        for errors in form.errors.values():
            for error in errors:
                messages.error(self.request, error)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('policies:proposal_detail', args=[self.proposal.pk])


class ProposalAttachmentDownloadView(AttachmentDownloadView):
    model = ProposalAttachment


class ProposalGeneratePolicyView(BrokerageRequiredMixin, View):
    def post(self, request, pk):
        proposal = get_object_or_404(Proposal, pk=pk)
        policy, created = generate_policy_from_proposal(proposal)
        if created:
            messages.success(request, f'Apólice {policy.number} gerada com sucesso.')
        else:
            messages.info(
                request,
                f'Esta proposta já foi convertida na apólice {policy.number}.',
            )
        return redirect('policies:policy_detail', policy.pk)


class PolicyListView(BrokerageRequiredMixin, ListView):
    model = Policy
    template_name = 'policies/policy_list.html'
    context_object_name = 'policies'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('q', '').strip()
        if search:
            queryset = queryset.filter(
                Q(client__name__icontains=search) | Q(number__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('q', '')
        return context


class PolicyDetailView(BrokerageRequiredMixin, DetailView):
    model = Policy
    template_name = 'policies/policy_detail.html'
    context_object_name = 'policy'


class PolicyCreateView(BrokerageRequiredMixin, SuccessMessageMixin, CreateView):
    model = Policy
    form_class = PolicyForm
    template_name = 'policies/policy_form.html'
    success_message = 'Apólice criada com sucesso.'

    def get_success_url(self):
        return reverse('policies:policy_detail', args=[self.object.pk])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.brokerage
        return kwargs

    def form_valid(self, form):
        form.instance.brokerage = self.request.brokerage
        return super().form_valid(form)


class PolicyUpdateView(BrokerageRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Policy
    form_class = PolicyForm
    template_name = 'policies/policy_form.html'
    success_message = 'Apólice atualizada com sucesso.'

    def get_success_url(self):
        return reverse('policies:policy_detail', args=[self.object.pk])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.brokerage
        return kwargs


class PolicyDeleteView(BrokerageRequiredMixin, DeleteView):
    model = Policy
    template_name = 'policies/policy_confirm_delete.html'
    success_url = reverse_lazy('policies:policy_list')


class PolicyAttachmentCreateView(BrokerageRequiredMixin, SuccessMessageMixin, CreateView):
    model = PolicyAttachment
    form_class = PolicyAttachmentForm
    success_message = 'Anexo adicionado com sucesso.'

    def dispatch(self, request, *args, **kwargs):
        self.policy = get_object_or_404(Policy, pk=self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.brokerage = self.request.brokerage
        form.instance.policy = self.policy
        return super().form_valid(form)

    def form_invalid(self, form):
        for errors in form.errors.values():
            for error in errors:
                messages.error(self.request, error)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('policies:policy_detail', args=[self.policy.pk])


class PolicyAttachmentDownloadView(AttachmentDownloadView):
    model = PolicyAttachment


class EndorsementListView(BrokerageRequiredMixin, ListView):
    model = Endorsement
    template_name = 'policies/endorsement_list.html'
    context_object_name = 'endorsements'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('q', '').strip()
        if search:
            queryset = queryset.filter(
                Q(number__icontains=search)
                | Q(policy__number__icontains=search)
            )
        return queryset.select_related('policy')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('q', '')
        return context


class EndorsementDetailView(BrokerageRequiredMixin, DetailView):
    model = Endorsement
    template_name = 'policies/endorsement_detail.html'
    context_object_name = 'endorsement'


class EndorsementCreateView(BrokerageRequiredMixin, SuccessMessageMixin, CreateView):
    model = Endorsement
    form_class = EndorsementForm
    template_name = 'policies/endorsement_form.html'
    success_message = 'Endosso criado com sucesso.'

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
        return reverse('policies:endorsement_detail', args=[self.object.pk])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.brokerage
        return kwargs

    def form_valid(self, form):
        form.instance.brokerage = self.request.brokerage
        return super().form_valid(form)


class EndorsementUpdateView(BrokerageRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Endorsement
    form_class = EndorsementForm
    template_name = 'policies/endorsement_form.html'
    success_message = 'Endosso atualizado com sucesso.'

    def get_success_url(self):
        return reverse('policies:endorsement_detail', args=[self.object.pk])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.brokerage
        return kwargs


class EndorsementDeleteView(BrokerageRequiredMixin, DeleteView):
    model = Endorsement
    template_name = 'policies/endorsement_confirm_delete.html'
    success_url = reverse_lazy('policies:endorsement_list')
