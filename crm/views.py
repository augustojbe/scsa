import json

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from base.mixins import BrokerageRequiredMixin
from crm.forms import DealForm, PipelineForm, PipelineStageForm
from crm.models import Deal, Pipeline, PipelineStage


class PipelineListView(BrokerageRequiredMixin, ListView):
    model = Pipeline
    template_name = 'crm/pipeline_list.html'
    context_object_name = 'pipelines'
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


class PipelineCreateView(BrokerageRequiredMixin, SuccessMessageMixin, CreateView):
    model = Pipeline
    form_class = PipelineForm
    template_name = 'crm/pipeline_form.html'
    success_url = reverse_lazy('crm:pipeline_list')
    success_message = 'Pipeline criado com sucesso.'

    def form_valid(self, form):
        form.instance.brokerage = self.request.brokerage
        return super().form_valid(form)


class PipelineUpdateView(BrokerageRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Pipeline
    form_class = PipelineForm
    template_name = 'crm/pipeline_form.html'
    success_url = reverse_lazy('crm:pipeline_list')
    success_message = 'Pipeline atualizado com sucesso.'


class PipelineDeleteView(BrokerageRequiredMixin, DeleteView):
    model = Pipeline
    template_name = 'crm/pipeline_confirm_delete.html'
    success_url = reverse_lazy('crm:pipeline_list')


class PipelineStageCreateView(BrokerageRequiredMixin, SuccessMessageMixin, CreateView):
    model = PipelineStage
    form_class = PipelineStageForm
    template_name = 'crm/stage_form.html'
    success_message = 'Etapa criada com sucesso.'

    def dispatch(self, request, *args, **kwargs):
        self.pipeline = get_object_or_404(Pipeline, pk=self.kwargs['pipeline_pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pipeline'] = self.pipeline
        return context

    def form_valid(self, form):
        form.instance.brokerage = self.request.brokerage
        form.instance.pipeline = self.pipeline
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('crm:pipeline_detail', args=[self.pipeline.pk])


class PipelineStageUpdateView(BrokerageRequiredMixin, SuccessMessageMixin, UpdateView):
    model = PipelineStage
    form_class = PipelineStageForm
    template_name = 'crm/stage_form.html'
    success_message = 'Etapa atualizada com sucesso.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pipeline'] = self.object.pipeline
        return context

    def get_success_url(self):
        return reverse('crm:pipeline_detail', args=[self.object.pipeline_id])


class PipelineStageDeleteView(BrokerageRequiredMixin, DeleteView):
    model = PipelineStage
    template_name = 'crm/stage_confirm_delete.html'
    success_message = 'Etapa excluída com sucesso.'

    def get_success_url(self):
        return reverse('crm:pipeline_detail', args=[self.object.pipeline_id])


class PipelineDetailView(BrokerageRequiredMixin, DetailView):
    model = Pipeline
    template_name = 'crm/pipeline_detail.html'
    context_object_name = 'pipeline'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stages'] = self.object.stages.all()
        return context


class DealListView(BrokerageRequiredMixin, ListView):
    model = Deal
    template_name = 'crm/deal_list.html'
    context_object_name = 'deals'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('q', '').strip()
        pipeline_id = self.request.GET.get('pipeline', '')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(client__name__icontains=search)
            )
        if pipeline_id:
            queryset = queryset.filter(pipeline_id=pipeline_id)
        return queryset.select_related('client', 'stage', 'pipeline')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('q', '')
        context['pipelines'] = Pipeline.all_objects.filter(
            brokerage=self.request.brokerage
        )
        return context


class DealDetailView(BrokerageRequiredMixin, DetailView):
    model = Deal
    template_name = 'crm/deal_detail.html'
    context_object_name = 'deal'


class DealCreateView(BrokerageRequiredMixin, SuccessMessageMixin, CreateView):
    model = Deal
    form_class = DealForm
    template_name = 'crm/deal_form.html'
    success_message = 'Negociação criada com sucesso.'

    def get_initial(self):
        initial = super().get_initial()
        stage_id = self.request.GET.get('stage')
        if stage_id:
            stage = PipelineStage.all_objects.filter(
                pk=stage_id, brokerage=self.request.brokerage
            ).first()
            if stage:
                initial['pipeline'] = stage.pipeline_id
                initial['stage'] = stage.pk
        return initial

    def get_success_url(self):
        return reverse('crm:deal_detail', args=[self.object.pk])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.brokerage
        return kwargs

    def form_valid(self, form):
        form.instance.brokerage = self.request.brokerage
        return super().form_valid(form)


class DealUpdateView(BrokerageRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Deal
    form_class = DealForm
    template_name = 'crm/deal_form.html'
    success_message = 'Negociação atualizada com sucesso.'

    def get_success_url(self):
        return reverse('crm:deal_detail', args=[self.object.pk])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.brokerage
        return kwargs


class DealDeleteView(BrokerageRequiredMixin, DeleteView):
    model = Deal
    template_name = 'crm/deal_confirm_delete.html'
    success_url = reverse_lazy('crm:deal_list')


class KanbanView(BrokerageRequiredMixin, TemplateView):
    template_name = 'crm/kanban.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pipeline_id = self.request.GET.get('pipeline')
        pipelines = Pipeline.all_objects.filter(brokerage=self.request.brokerage)
        pipeline = None
        if pipeline_id:
            pipeline = pipelines.filter(pk=pipeline_id).first()
        if pipeline is None:
            pipeline = pipelines.filter(is_default=True).first() or pipelines.first()
        context['pipelines'] = pipelines
        context['pipeline'] = pipeline
        stages = []
        if pipeline is not None:
            for stage in pipeline.stages.all():
                stages.append(
                    {
                        'stage': stage,
                        'deals': stage.deals.select_related('client'),
                    }
                )
        context['stages'] = stages
        return context


class DealMoveView(BrokerageRequiredMixin, View):
    def post(self, request, pk):
        deal = get_object_or_404(Deal, pk=pk)
        try:
            data = json.loads(request.body or b'{}')
        except ValueError:
            data = request.POST
        stage_id = data.get('stage_id') or data.get('stage')
        stage = PipelineStage.all_objects.filter(
            pk=stage_id,
            brokerage=request.brokerage,
            pipeline=deal.pipeline,
        ).first()
        if stage is None:
            return JsonResponse({'error': 'Etapa inválida.'}, status=400)
        deal.stage = stage
        deal.save(update_fields=['stage', 'updated_at'])
        return JsonResponse({'ok': True})
