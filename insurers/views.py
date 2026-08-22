from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from base.mixins import BrokerageRequiredMixin
from insurers.forms import BranchForm, InsurerForm
from insurers.models import Branch, Insurer


class InsurerListView(BrokerageRequiredMixin, ListView):
    model = Insurer
    template_name = 'insurers/insurer_list.html'
    context_object_name = 'insurers'
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


class InsurerCreateView(BrokerageRequiredMixin, SuccessMessageMixin, CreateView):
    model = Insurer
    form_class = InsurerForm
    template_name = 'insurers/insurer_form.html'
    success_url = reverse_lazy('insurers:list')
    success_message = 'Seguradora criada com sucesso.'

    def form_valid(self, form):
        form.instance.brokerage = self.request.brokerage
        return super().form_valid(form)


class InsurerUpdateView(BrokerageRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Insurer
    form_class = InsurerForm
    template_name = 'insurers/insurer_form.html'
    success_url = reverse_lazy('insurers:list')
    success_message = 'Seguradora atualizada com sucesso.'


class InsurerDeleteView(BrokerageRequiredMixin, DeleteView):
    model = Insurer
    template_name = 'insurers/insurer_confirm_delete.html'
    success_url = reverse_lazy('insurers:list')


class BranchListView(BrokerageRequiredMixin, ListView):
    model = Branch
    template_name = 'insurers/branch_list.html'
    context_object_name = 'branches'
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


class BranchCreateView(BrokerageRequiredMixin, SuccessMessageMixin, CreateView):
    model = Branch
    form_class = BranchForm
    template_name = 'insurers/branch_form.html'
    success_url = reverse_lazy('insurers:branch_list')
    success_message = 'Ramo criado com sucesso.'

    def form_valid(self, form):
        form.instance.brokerage = self.request.brokerage
        return super().form_valid(form)


class BranchUpdateView(BrokerageRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Branch
    form_class = BranchForm
    template_name = 'insurers/branch_form.html'
    success_url = reverse_lazy('insurers:branch_list')
    success_message = 'Ramo atualizado com sucesso.'


class BranchDeleteView(BrokerageRequiredMixin, DeleteView):
    model = Branch
    template_name = 'insurers/branch_confirm_delete.html'
    success_url = reverse_lazy('insurers:branch_list')
