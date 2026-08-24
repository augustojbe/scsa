from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from base.constants import RENEWAL_PENDING
from base.mixins import BrokerageRequiredMixin
from renewals.forms import RenewalForm
from renewals.models import Renewal


class RenewalListView(BrokerageRequiredMixin, ListView):
    model = Renewal
    template_name = 'renewals/renewal_list.html'
    context_object_name = 'renewals'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('q', '').strip()
        status = self.request.GET.get('status', '')
        scope = self.request.GET.get('scope', '')
        if search:
            queryset = queryset.filter(
                Q(policy__number__icontains=search)
                | Q(client__name__icontains=search)
            )
        if status:
            queryset = queryset.filter(status=status)
        if scope == 'upcoming':
            queryset = queryset.filter(
                status=RENEWAL_PENDING,
                due_date__gte=timezone.localdate(),
            )
        elif scope == 'overdue':
            queryset = queryset.filter(
                status=RENEWAL_PENDING,
                due_date__lt=timezone.localdate(),
            )
        return queryset.select_related('policy', 'client')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('q', '')
        context['upcoming_count'] = Renewal.all_objects.filter(
            brokerage=self.request.brokerage,
            status=RENEWAL_PENDING,
            due_date__gte=timezone.localdate(),
        ).count()
        context['overdue_count'] = Renewal.all_objects.filter(
            brokerage=self.request.brokerage,
            status=RENEWAL_PENDING,
            due_date__lt=timezone.localdate(),
        ).count()
        return context


class RenewalDetailView(BrokerageRequiredMixin, DetailView):
    model = Renewal
    template_name = 'renewals/renewal_detail.html'
    context_object_name = 'renewal'


class RenewalCreateView(BrokerageRequiredMixin, SuccessMessageMixin, CreateView):
    model = Renewal
    form_class = RenewalForm
    template_name = 'renewals/renewal_form.html'
    success_message = 'Renovação criada com sucesso.'

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
        return reverse('renewals:detail', args=[self.object.pk])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.brokerage
        return kwargs

    def form_valid(self, form):
        form.instance.brokerage = self.request.brokerage
        return super().form_valid(form)


class RenewalUpdateView(BrokerageRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Renewal
    form_class = RenewalForm
    template_name = 'renewals/renewal_form.html'
    success_message = 'Renovação atualizada com sucesso.'

    def get_success_url(self):
        return reverse('renewals:detail', args=[self.object.pk])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.brokerage
        return kwargs


class RenewalDeleteView(BrokerageRequiredMixin, DeleteView):
    model = Renewal
    template_name = 'renewals/renewal_confirm_delete.html'
    success_url = reverse_lazy('renewals:list')
