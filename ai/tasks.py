import logging

from celery import shared_task

from base.tenant import set_current_brokerage
from base.models import Notification

logger = logging.getLogger(__name__)


def _run_summary(entity_type, brokerage_id, entity_id, model, url_name):
    set_current_brokerage(brokerage_id)
    from ai.services import generate_summary
    from ai.tools import GETTERS

    from django.urls import reverse
    from django.contrib.auth import get_user_model

    data = GETTERS[entity_type](brokerage_id, entity_id)
    if data is None:
        return None

    obj = model.all_objects.get(pk=entity_id, brokerage_id=brokerage_id)
    summary = generate_summary(entity_type, brokerage_id, entity_id)
    obj.ai_summary = summary
    obj.save(update_fields=['ai_summary', 'updated_at'])

    user = get_user_model().objects.filter(
        brokerage_id=brokerage_id, is_superuser=False
    ).first()
    if user is not None:
        Notification.all_objects.create(
            brokerage_id=brokerage_id,
            user=user,
            message=f'Resumo com IA pronto para {data["entity"]}.',
            url=reverse(url_name, args=[obj.pk]),
        )
    return obj.pk


@shared_task
def summarize_client(brokerage_id, client_id):
    from clients.models import Client
    return _run_summary('client', brokerage_id, client_id, Client, 'clients:detail')


@shared_task
def summarize_policy(brokerage_id, policy_id):
    from policies.models import Policy
    return _run_summary('policy', brokerage_id, policy_id, Policy, 'policies:policy_detail')


@shared_task
def summarize_claim(brokerage_id, claim_id):
    from claims.models import Claim
    return _run_summary('claim', brokerage_id, claim_id, Claim, 'claims:detail')


@shared_task
def summarize_proposal(brokerage_id, proposal_id):
    from policies.models import Proposal
    return _run_summary('proposal', brokerage_id, proposal_id, Proposal, 'policies:proposal_detail')


@shared_task
def summarize_deal(brokerage_id, deal_id):
    from crm.models import Deal
    return _run_summary('deal', brokerage_id, deal_id, Deal, 'crm:deal_detail')
