from django.db import transaction

from base.constants import POLICY_ACTIVE, PROPOSAL_CONVERTED
from policies.models import Policy


@transaction.atomic
def generate_policy_from_proposal(proposal):
    existing = proposal.policies.first()
    if existing is not None:
        return existing, False
    policy = Policy.objects.create(
        brokerage_id=proposal.brokerage_id,
        proposal=proposal,
        client=proposal.client,
        insurer=proposal.insurer,
        branch=proposal.branch,
        status=POLICY_ACTIVE,
        premium=proposal.premium,
    )
    policy.coverages.set(proposal.coverages.all())
    policy.covered_items.set(proposal.covered_items.all())
    if proposal.status != PROPOSAL_CONVERTED:
        proposal.status = PROPOSAL_CONVERTED
        proposal.save(update_fields=['status', 'updated_at'])
    return policy, True
