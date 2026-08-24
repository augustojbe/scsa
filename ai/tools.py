from clients.models import Client
from claims.models import Claim
from crm.models import Deal
from policies.models import Policy, Proposal


def _fmt_value(value):
    if value is None:
        return '—'
    return str(value)


def get_client_data(brokerage_id, client_id):
    client = Client.all_objects.filter(pk=client_id, brokerage_id=brokerage_id).first()
    if client is None:
        return None
    policies = client.policies.all()
    proposals = client.proposals.all()
    claims_count = Claim.all_objects.filter(policy__client_id=client.pk).count()
    return {
        'entity': 'Cliente',
        'name': client.name,
        'type': client.get_type_display(),
        'document': client.document or '—',
        'email': client.email or '—',
        'phone': client.phone or '—',
        'city': f'{client.city}/{client.state}' if client.city else '—',
        'apolices': len(policies),
        'propostas': len(proposals),
        'sinistros': claims_count,
        'premio_total': sum((p.premium for p in policies), 0),
    }


def get_policy_data(brokerage_id, policy_id):
    policy = Policy.all_objects.filter(pk=policy_id, brokerage_id=brokerage_id).first()
    if policy is None:
        return None
    return {
        'entity': 'Apólice',
        'number': policy.number,
        'client': policy.client.name,
        'insurer': policy.insurer.name,
        'branch': policy.branch.name,
        'status': policy.get_status_display(),
        'premium': f'R$ {policy.premium:.2f}',
        'start_date': policy.start_date.strftime('%d/%m/%Y') if policy.start_date else '—',
        'end_date': policy.end_date.strftime('%d/%m/%Y') if policy.end_date else '—',
        'coverages': ', '.join(c.name for c in policy.coverages.all()) or '—',
        'covered_items': ', '.join(i.description for i in policy.covered_items.all()) or '—',
        'sinistros': policy.claims.count(),
        'endossos': policy.endorsements.count(),
    }


def get_claim_data(brokerage_id, claim_id):
    claim = Claim.all_objects.filter(pk=claim_id, brokerage_id=brokerage_id).first()
    if claim is None:
        return None
    return {
        'entity': 'Sinistro',
        'number': claim.number,
        'policy': claim.policy.number,
        'client': claim.policy.client.name,
        'type': claim.get_type_display(),
        'status': claim.get_status_display(),
        'reported_at': claim.reported_at.strftime('%d/%m/%Y %H:%M'),
        'covered_item': claim.covered_item.description,
        'reserved_amount': f'R$ {claim.reserved_amount:.2f}',
    }


def get_proposal_data(brokerage_id, proposal_id):
    proposal = Proposal.all_objects.filter(
        pk=proposal_id, brokerage_id=brokerage_id
    ).first()
    if proposal is None:
        return None
    return {
        'entity': 'Proposta',
        'id': proposal.pk,
        'client': proposal.client.name,
        'insurer': proposal.insurer.name,
        'branch': proposal.branch.name,
        'status': proposal.get_status_display(),
        'premium': f'R$ {proposal.premium:.2f}',
        'coverages': ', '.join(c.name for c in proposal.coverages.all()) or '—',
        'converted': 'Sim' if proposal.status == 'converted' else 'Não',
    }


def get_deal_data(brokerage_id, deal_id):
    deal = Deal.all_objects.filter(pk=deal_id, brokerage_id=brokerage_id).first()
    if deal is None:
        return None
    return {
        'entity': 'Negociação',
        'title': deal.title,
        'client': deal.client.name if deal.client else '—',
        'pipeline': deal.pipeline.name,
        'stage': deal.stage.name,
        'value': f'R$ {deal.value:.2f}',
        'expected_close_date': (
            deal.expected_close_date.strftime('%d/%m/%Y')
            if deal.expected_close_date else '—'
        ),
    }


GETTERS = {
    'client': get_client_data,
    'policy': get_policy_data,
    'claim': get_claim_data,
    'proposal': get_proposal_data,
    'deal': get_deal_data,
}
