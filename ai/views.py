import json
import time

from django.contrib import messages
from django.http import Http404, JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, RedirectView, TemplateView

from ai.models import ChatMessage, ChatSession
from ai.tasks import (
    summarize_claim,
    summarize_client,
    summarize_deal,
    summarize_policy,
    summarize_proposal,
)
from base.mixins import BrokerageRequiredMixin
from base.models import Notification


class SummarizeView(BrokerageRequiredMixin, View):
    task = None
    entity_url_name = None
    label = 'entidade'

    def post(self, request, pk):
        try:
            self.task.delay(request.brokerage.pk, pk)
            messages.info(
                request,
                f'Análise de {self.label} iniciada. Você será notificado quando ficar pronta.',
            )
        except Exception:
            self.task.run(request.brokerage.pk, pk)
            messages.success(request, f'Resumo de {self.label} gerado com sucesso.')
        return redirect(self.entity_url_name, pk)


class SummarizeClientView(SummarizeView):
    task = summarize_client
    entity_url_name = 'clients:detail'
    label = 'cliente'


class SummarizePolicyView(SummarizeView):
    task = summarize_policy
    entity_url_name = 'policies:policy_detail'
    label = 'apólice'


class SummarizeClaimView(SummarizeView):
    task = summarize_claim
    entity_url_name = 'claims:detail'
    label = 'sinistro'


class SummarizeProposalView(SummarizeView):
    task = summarize_proposal
    entity_url_name = 'policies:proposal_detail'
    label = 'proposta'


class SummarizeDealView(SummarizeView):
    task = summarize_deal
    entity_url_name = 'crm:deal_detail'
    label = 'negociação'


class ChatSessionListView(BrokerageRequiredMixin, ListView):
    model = ChatSession
    template_name = 'ai/chat_list.html'
    context_object_name = 'sessions'
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class ChatSessionCreateView(BrokerageRequiredMixin, View):
    def post(self, request):
        session = ChatSession.all_objects.create(
            brokerage=request.brokerage,
            user=request.user,
            title=request.POST.get('title', '').strip() or 'Nova conversa',
        )
        return redirect('ai:chat_detail', session.pk)


class ChatDetailView(BrokerageRequiredMixin, DetailView):
    model = ChatSession
    template_name = 'ai/chat_detail.html'
    context_object_name = 'session'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class ChatSendView(BrokerageRequiredMixin, View):
    def post(self, request, pk):
        session = get_object_or_404(
            ChatSession, pk=pk, user=request.user, brokerage=request.brokerage
        )
        user_message = request.POST.get('message', '').strip()
        if not user_message:
            return JsonResponse({'error': 'Mensagem vazia.'}, status=400)

        ChatMessage.all_objects.create(
            brokerage=request.brokerage, session=session, role='user', content=user_message
        )

        from ai.services import chat_reply

        reply = chat_reply(request.brokerage.pk, session.title, user_message, '')

        def stream():
            for i in range(0, len(reply), 4):
                chunk = reply[i:i + 4]
                yield f'data: {json.dumps({"token": chunk})}\n\n'
                time.sleep(0.01)
            yield 'data: [DONE]\n\n'

        # Save the assistant message after the generator finishes.
        def save_and_stream():
            try:
                yield from stream()
            finally:
                ChatMessage.all_objects.create(
                    brokerage=request.brokerage,
                    session=session,
                    role='assistant',
                    content=reply,
                )

        response = StreamingHttpResponse(save_and_stream(), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response


class NotificationsMarkReadView(BrokerageRequiredMixin, RedirectView):
    url = reverse_lazy('dashboard:index')

    def post(self, request):
        Notification.all_objects.filter(
            brokerage=request.brokerage, user=request.user, is_read=False
        ).update(is_read=True)
        return super().post(request)
