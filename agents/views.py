from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from agents.forms import AgentForm, ProducerForm
from agents.models import Agent, Producer
from base.mixins import BrokerageRequiredMixin


class AgentListView(BrokerageRequiredMixin, ListView):
    model = Agent
    template_name = 'agents/agent_list.html'
    context_object_name = 'agents'
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


class AgentCreateView(BrokerageRequiredMixin, SuccessMessageMixin, CreateView):
    model = Agent
    form_class = AgentForm
    template_name = 'agents/agent_form.html'
    success_url = reverse_lazy('agents:list')
    success_message = 'Agente criado com sucesso.'

    def form_valid(self, form):
        form.instance.brokerage = self.request.brokerage
        return super().form_valid(form)


class AgentUpdateView(BrokerageRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Agent
    form_class = AgentForm
    template_name = 'agents/agent_form.html'
    success_url = reverse_lazy('agents:list')
    success_message = 'Agente atualizado com sucesso.'


class AgentDeleteView(BrokerageRequiredMixin, DeleteView):
    model = Agent
    template_name = 'agents/agent_confirm_delete.html'
    success_url = reverse_lazy('agents:list')


class AgentDetailView(BrokerageRequiredMixin, DetailView):
    model = Agent
    template_name = 'agents/agent_detail.html'
    context_object_name = 'agent'


class ProducerListView(BrokerageRequiredMixin, ListView):
    model = Producer
    template_name = 'agents/producer_list.html'
    context_object_name = 'producers'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('q', '').strip()
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset.select_related('agent')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('q', '')
        return context


class ProducerCreateView(BrokerageRequiredMixin, SuccessMessageMixin, CreateView):
    model = Producer
    form_class = ProducerForm
    template_name = 'agents/producer_form.html'
    success_url = reverse_lazy('agents:producer_list')
    success_message = 'Produtor criado com sucesso.'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.brokerage
        return kwargs

    def form_valid(self, form):
        form.instance.brokerage = self.request.brokerage
        return super().form_valid(form)


class ProducerUpdateView(BrokerageRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Producer
    form_class = ProducerForm
    template_name = 'agents/producer_form.html'
    success_url = reverse_lazy('agents:producer_list')
    success_message = 'Produtor atualizado com sucesso.'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.brokerage
        return kwargs


class ProducerDeleteView(BrokerageRequiredMixin, DeleteView):
    model = Producer
    template_name = 'agents/producer_confirm_delete.html'
    success_url = reverse_lazy('agents:producer_list')


class ProducerDetailView(BrokerageRequiredMixin, DetailView):
    model = Producer
    template_name = 'agents/producer_detail.html'
    context_object_name = 'producer'
