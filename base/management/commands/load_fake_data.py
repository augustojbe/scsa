import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker

from base.tenant import set_current_brokerage
from base.utils import only_digits
from base.constants import (
    CLAIM_OPEN,
    CLAIM_TYPE_CHOICES,
    COMMISSION_PENDING,
    PROPOSAL_APPROVED,
    PROPOSAL_DRAFT,
    PROPOSAL_SUBMITTED,
    RENEWAL_CONTACTED,
    RENEWAL_PENDING,
)
from agents.models import Agent, Producer
from claims.models import Claim
from clients.models import Client
from commissions.models import Commission
from core.models import Brokerage, User
from crm.models import Deal, Pipeline, PipelineStage
from insurers.models import Branch, Insurer
from policies.models import (
    Coverage,
    CoveredItem,
    Endorsement,
    Policy,
    PolicyAttachment,
    Proposal,
    ProposalAttachment,
)
from policies.services import generate_policy_from_proposal
from renewals.models import Renewal

INSURERS = [
    ('Porto Seguro', 'POSG'),
    ('Bradesco Seguros', 'BRAD'),
    ('Itaú Seguros', 'ITAU'),
    ('SulAmérica', 'SULA'),
    ('Mapfre', 'MAPF'),
]

BRANCHES = ['Automóvel', 'Residencial', 'Vida', 'Viagem', 'Empresarial', 'Frota']

COVERAGES = {
    'Automóvel': ['Colisão', 'Roubo/Furto', 'Terceiros', 'Vidros', 'Assistência 24h'],
    'Residencial': ['Incêndio', 'Alagamento', 'Roubo', 'Responsabilidade Civil'],
    'Vida': ['Morte', 'Invalidez', 'Doenças Graves'],
    'Viagem': ['Médico', 'Bagagem', 'Cancelamento'],
    'Empresarial': ['Incêndio', 'Responsabilidade Civil', 'Equipamentos'],
    'Frota': ['Colisão', 'Roubo/Furto', 'Casco', 'Terceiros'],
}

BRANCH_ITEM_TYPE = {
    'Automóvel': 'vehicle', 'Residencial': 'property', 'Vida': 'life',
    'Viagem': 'travel', 'Empresarial': 'business', 'Frota': 'fleet_item',
}


class Command(BaseCommand):
    help = 'Carrega dados fake (Faker) realistas para demonstração.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.fake = Faker('pt_BR')

        cnpj = '12345678000190'
        brokerage = Brokerage.objects.filter(cnpj=cnpj).first()
        if brokerage is None:
            brokerage = Brokerage.objects.create(
                cnpj=cnpj,
                legal_name=self.fake.company() + ' Corretora Ltda',
                trade_name=self.fake.company_suffix(),
                email=self.fake.company_email(),
                phone=self.fake.phone_number(),
                street=self.fake.street_name(),
                number=str(self.fake.random_int(1, 9999)),
                neighborhood=self.fake.neighborhood(),
                city=self.fake.city(),
                state=self.fake.state_abbr(),
                zip_code=self.fake.postcode(),
            )
        set_current_brokerage(brokerage)

        self._reset(brokerage)
        self._create_user(brokerage)
        self._load_base(brokerage)
        self._load_commercial(brokerage)
        self._load_crm(brokerage)
        self.stdout.write(
            self.style.SUCCESS(f'Dados fake carregados para {brokerage.trade_name}.')
        )

    def _reset(self, brokerage):
        """Remove dados de domínio da corretora demo para regenerar do zero."""
        from base.models import Notification
        from ai.models import ChatMessage, ChatSession
        from django.contrib.auth import get_user_model

        models = [
            ChatMessage, ChatSession, Notification,
            Commission, Renewal, Endorsement, Claim,
            PolicyAttachment, ProposalAttachment,
            Policy, Proposal, Deal, PipelineStage, Pipeline,
            CoveredItem, Coverage, Producer, Agent,
            Branch, Insurer, Client,
        ]
        for model in models:
            if hasattr(model, 'all_objects'):
                model.all_objects.filter(brokerage=brokerage).delete()
        get_user_model().objects.filter(brokerage=brokerage).delete()

    def _create_user(self, brokerage):
        email = 'augustojbe@gmail.com'
        password = '1988jaguaribe'
        user, _ = User.objects.get_or_create(
            email=email,
            defaults={
                'full_name': self.fake.name(),
                'brokerage': brokerage,
                'role': 'owner',
                'is_staff': True,
            },
        )
        # Sempre garante credenciais de demonstração conhecidas.
        user.brokerage = brokerage
        user.role = 'owner'
        user.is_staff = True
        user.is_active = True
        user.set_password(password)
        user.save()
        self.stdout.write(f'Usuário demo: {email} / {password}')

    def _load_base(self, brokerage):
        today = timezone.localdate()

        insurers = []
        for name, code in INSURERS:
            insurer, _ = Insurer.all_objects.get_or_create(
                brokerage=brokerage, code=code, defaults={'name': name}
            )
            insurers.append(insurer)

        branches = []
        for name in BRANCHES:
            branch, _ = Branch.all_objects.get_or_create(
                brokerage=brokerage, name=name
            )
            branches.append(branch)
            for cov_name in COVERAGES[name]:
                Coverage.all_objects.get_or_create(
                    brokerage=brokerage, name=cov_name, defaults={'branch': branch}
                )

        clients = []
        for _ in range(25):
            is_pj = self.fake.boolean(chance_of_getting_true=25)
            client = Client.all_objects.create(
                brokerage=brokerage,
                name=self.fake.company() if is_pj else self.fake.name(),
                type='pj' if is_pj else 'pf',
                document=only_digits(self.fake.cnpj()) if is_pj else only_digits(self.fake.cpf()),
                email=self.fake.email(),
                phone=self.fake.phone_number(),
                street=self.fake.street_name(),
                number=str(self.fake.random_int(1, 9999)),
                complement=self.fake.word() if self.fake.boolean(30) else '',
                neighborhood=self.fake.neighborhood(),
                city=self.fake.city(),
                state=self.fake.state_abbr(),
                zip_code=self.fake.postcode(),
                created_at=self.fake.date_time_between(
                    start_date='-2y', end_date='-30d', tzinfo=timezone.get_current_timezone()
                ),
            )
            clients.append(client)

        self.insurers = insurers
        self.branches = branches
        self.clients = clients
        self.brokerage = brokerage

    def _money(self, low, high):
        return round(self.fake.random_int(int(low * 100), int(high * 100)) / 100, 2)

    def _load_commercial(self, brokerage):
        today = timezone.localdate()
        agents = []
        for _ in range(4):
            agents.append(
                Agent.all_objects.create(
                    brokerage=brokerage,
                    name=self.fake.name(),
                    document=only_digits(self.fake.cpf()),
                    type='person',
                    commission_rate=self.fake.random_element([10, 15, 20, 25]),
                )
            )

        producers = []
        for _ in range(6):
            producers.append(
                Producer.all_objects.create(
                    brokerage=brokerage,
                    agent=self.fake.random_element(agents) if self.fake.boolean(70) else None,
                    name=self.fake.name(),
                    document=only_digits(self.fake.cpf()),
                    commission_rate=self.fake.random_element([5, 8, 10, 12]),
                )
            )

        for client in self.clients:
            branch = self.fake.random_element(self.branches)
            insurer = self.fake.random_element(self.insurers)
            coverage = list(
                Coverage.all_objects.filter(branch=branch)
            )[:self.fake.random_int(1, 3)]
            item_type = BRANCH_ITEM_TYPE[branch.name]
            item = CoveredItem.all_objects.create(
                brokerage=brokerage,
                description=f'{item_type} de {client.name}',
                type=item_type,
                attributes={
                    'marca': self.fake.random_element(['Fiat', 'VW', 'GM', 'Toyota', 'Honda']),
                    'ano': self.fake.random_int(2015, 2024),
                    'placa': self.fake.license_plate(),
                } if item_type == 'vehicle' else {'detalhe': self.fake.text(20)},
            )

            premium = self._money(500, 5000)
            proposal = Proposal.all_objects.create(
                brokerage=brokerage,
                client=client,
                insurer=insurer,
                branch=branch,
                status=self.fake.random_element(
                    [PROPOSAL_DRAFT, PROPOSAL_SUBMITTED, PROPOSAL_APPROVED]
                ),
                premium=premium,
                notes=self.fake.sentence() if self.fake.boolean(40) else '',
                created_at=self.fake.date_time_between(
                    start_date='-8m', end_date='-1d', tzinfo=timezone.get_current_timezone()
                ),
            )
            proposal.coverages.set(coverage)
            proposal.covered_items.set([item])

            if self.fake.boolean(60):
                policy, created = generate_policy_from_proposal(proposal)
                if created:
                    policy.start_date = self.fake.date_between(
                        start_date='-1y', end_date='-1m'
                    )
                    policy.end_date = policy.start_date + timedelta(days=365)
                    policy.notes = self.fake.sentence() if self.fake.boolean(30) else ''
                    policy.save()

                    if self.fake.boolean(40):
                        Endorsement.all_objects.create(
                            brokerage=brokerage,
                            policy=policy,
                            type=self.fake.random_element(
                                ['inclusion', 'exclusion', 'alteration']
                            ),
                            description=self.fake.sentence(),
                            effective_date=self.fake.date_between(
                                start_date='-3m', end_date='today'
                            ),
                        )

                    if self.fake.boolean(50):
                        Claim.all_objects.create(
                            brokerage=brokerage,
                            policy=policy,
                            covered_item=item,
                            type=self.fake.random_element([c for c, _ in CLAIM_TYPE_CHOICES]),
                            status=CLAIM_OPEN,
                            description=self.fake.paragraph(),
                            reserved_amount=self._money(1000, 20000),
                            reported_at=self.fake.date_time_between(
                                start_date='-4m', end_date='-1d',
                                tzinfo=timezone.get_current_timezone(),
                            ),
                        )

                    if self.fake.boolean(70):
                        Renewal.all_objects.create(
                            brokerage=brokerage,
                            policy=policy,
                            client=client,
                            due_date=policy.end_date - timedelta(days=30),
                            status=self.fake.random_element(
                                [RENEWAL_PENDING, RENEWAL_CONTACTED]
                            ),
                            notes=self.fake.sentence() if self.fake.boolean(30) else '',
                        )

                    if self.fake.boolean(60):
                        total = self._money(200, 3000)
                        commission = Commission.all_objects.create(
                            brokerage=brokerage,
                            policy=policy,
                            insurer=insurer,
                            client=client,
                            total_amount=total,
                            status=COMMISSION_PENDING,
                        )
                        commission.compute_shares()
                        commission.computed_at = timezone.now()
                        commission.save()

    def _load_crm(self, brokerage):
        pipeline, _ = Pipeline.all_objects.get_or_create(
            brokerage=brokerage,
            is_default=True,
            defaults={'name': 'Funil Comercial'},
        )
        stage_specs = [
            ('Lead', '#0d6efd', 1),
            ('Qualificação', '#0dcaf0', 2),
            ('Proposta enviada', '#ffc107', 3),
            ('Negociação', '#fd7e14', 4),
            ('Fechado', '#198754', 5),
        ]
        stages = []
        for name, color, order in stage_specs:
            stage, _ = PipelineStage.all_objects.get_or_create(
                brokerage=brokerage,
                pipeline=pipeline,
                order=order,
                defaults={'name': name, 'color': color},
            )
            stages.append(stage)

        for i, client in enumerate(
            self.fake.random_elements(self.clients, length=12, unique=True)
        ):
            Deal.all_objects.create(
                brokerage=brokerage,
                pipeline=pipeline,
                stage=self.fake.random_element(stages),
                client=client,
                title=f'Negociação {client.name}',
                value=self._money(1000, 20000),
                expected_close_date=timezone.localdate()
                + timedelta(days=self.fake.random_int(1, 90)),
                order=i,
            )
