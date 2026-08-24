from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from base.mixins import BrokerageRequiredMixin
from commissions.forms import CommissionForm
from commissions.models import Commission


class CommissionListView(BrokerageRequiredMixin, ListView):
    model = Commission
    template_name = 'commissions/commission_list.html'
    context_object_name = 'commissions'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('q', '').strip()
        if search:
            queryset = queryset.filter(
                Q(policy__number__icontains=search)
                | Q(client__name__icontains=search)
            )
        return queryset.select_related('policy', 'client', 'insurer', 'agent', 'producer')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('q', '')
        return context


class CommissionDetailView(BrokerageRequiredMixin, DetailView):
    model = Commission
    template_name = 'commissions/commission_detail.html'
    context_object_name = 'commission'


class CommissionCreateView(BrokerageRequiredMixin, SuccessMessageMixin, CreateView):
    model = Commission
    form_class = CommissionForm
    template_name = 'commissions/commission_form.html'
    success_message = 'Comissão registrada com sucesso.'

    def get_initial(self):
        initial = super().get_initial()
        policy_id = self.request.GET.get('policy')
        if policy_id:
            from policies.models import Policy
            policy = Policy.all_objects.filter(
                pk=policy_id, brokerage=self.request.brokerage
            ).first()
            if policy:
                initial['policy'] = policy.pk
        return initial

    def get_success_url(self):
        return reverse('commissions:detail', args=[self.object.pk])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.brokerage
        return kwargs

    def form_valid(self, form):
        form.instance.brokerage = self.request.brokerage
        return super().form_valid(form)


class CommissionUpdateView(BrokerageRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Commission
    form_class = CommissionForm
    template_name = 'commissions/commission_form.html'
    success_message = 'Comissão atualizada com sucesso.'

    def get_success_url(self):
        return reverse('commissions:detail', args=[self.object.pk])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.brokerage
        return kwargs


class CommissionDeleteView(BrokerageRequiredMixin, DeleteView):
    model = Commission
    template_name = 'commissions/commission_confirm_delete.html'
    success_url = reverse_lazy('commissions:list')
