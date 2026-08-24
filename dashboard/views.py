import json

from django.core.cache import cache
from django.db.models import Count, Sum
from django.utils import timezone
from django.views.generic import TemplateView

from base.mixins import BrokerageRequiredMixin
from claims.models import Claim
from clients.models import Client
from commissions.models import Commission
from crm.models import Deal, Pipeline
from insurers.models import Insurer
from policies.models import Policy, Proposal
from renewals.models import Renewal


class DashboardView(BrokerageRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'
    cache_timeout = 300

    def _compute(self, brokerage):
        total_clients = Client.all_objects.filter(brokerage=brokerage).count()
        clients_pf = Client.all_objects.filter(brokerage=brokerage, type='pf').count()
        clients_pj = Client.all_objects.filter(brokerage=brokerage, type='pj').count()

        total_policies = Policy.all_objects.filter(brokerage=brokerage).count()
        active_policies = Policy.all_objects.filter(
            brokerage=brokerage, status='active'
        ).count()
        premium_total = (
            Policy.all_objects.filter(brokerage=brokerage)
            .aggregate(s=Sum('premium'))['s']
            or 0
        )

        total_proposals = Proposal.all_objects.filter(brokerage=brokerage).count()
        total_claims = Claim.all_objects.filter(brokerage=brokerage).count()
        total_insurers = Insurer.all_objects.filter(brokerage=brokerage).count()

        commission_total = (
            Commission.all_objects.filter(brokerage=brokerage)
            .aggregate(s=Sum('total_amount'))['s']
            or 0
        )
        brokerage_share = (
            Commission.all_objects.filter(brokerage=brokerage)
            .aggregate(s=Sum('brokerage_share'))['s']
            or 0
        )

        policies_by_branch = list(
            Policy.all_objects.filter(brokerage=brokerage)
            .values('branch__name')
            .annotate(value=Count('id'))
            .order_by('-value')
        )
        policies_by_insurer = list(
            Policy.all_objects.filter(brokerage=brokerage)
            .values('insurer__name')
            .annotate(value=Count('id'))
            .order_by('-value')
        )

        # Funil de negociações (pipeline padrão ou primeiro)
        pipeline = (
            Pipeline.all_objects.filter(brokerage=brokerage, is_default=True).first()
            or Pipeline.all_objects.filter(brokerage=brokerage).first()
        )
        funnel = []
        max_deals = 1
        if pipeline is not None:
            stages = pipeline.stages.annotate(deal_count=Count('deals'))
            for stage in stages:
                funnel.append(
                    {
                        'name': stage.name,
                        'color': stage.color,
                        'count': stage.deal_count,
                    }
                )
            if funnel:
                max_deals = max(f['count'] for f in funnel) or 1
        for f in funnel:
            f['width'] = round((f['count'] / max_deals) * 100) if f['count'] else 8

        renewals_upcoming = Renewal.all_objects.filter(
            brokerage=brokerage,
            status='pending',
            due_date__gte=timezone.localdate(),
        ).count()
        renewals_overdue = Renewal.all_objects.filter(
            brokerage=brokerage,
            status='pending',
            due_date__lt=timezone.localdate(),
        ).count()

        return {
            'total_clients': total_clients,
            'clients_pf': clients_pf,
            'clients_pj': clients_pj,
            'total_policies': total_policies,
            'active_policies': active_policies,
            'premium_total': premium_total,
            'total_proposals': total_proposals,
            'total_claims': total_claims,
            'total_insurers': total_insurers,
            'commission_total': commission_total,
            'brokerage_share': brokerage_share,
            'renewals_upcoming': renewals_upcoming,
            'renewals_overdue': renewals_overdue,
            'policies_by_branch': json.dumps(policies_by_branch),
            'policies_by_insurer': json.dumps(policies_by_insurer),
            'clients_by_type': json.dumps(
                [
                    {'name': 'Pessoa Física', 'value': clients_pf},
                    {'name': 'Pessoa Jurídica', 'value': clients_pj},
                ]
            ),
            'funnel': funnel,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        brokerage = self.request.brokerage
        cache_key = f'dashboard:{brokerage.pk}'
        data = cache.get(cache_key)
        if data is None:
            data = self._compute(brokerage)
            cache.set(cache_key, data, self.cache_timeout)
        context.update(data)
        return context
