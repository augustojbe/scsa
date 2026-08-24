import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from base.tenant import set_current_brokerage
from base.constants import (
    CLAIM_OPEN,
    CLAIM_TYPE_CHOICES,
    COMMISSION_PENDING,
    POLICY_ACTIVE,
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
    Proposal,
)
from policies.services import generate_policy_from_proposal
from renewals.models import Renewal

CLIENT_NAMES = [
    'Ana Paula Ribeiro', 'Bruno Carvalho', 'Carla Mendes', 'Diego Almeida',
    'Elisa Farias', 'Fábio Nogueira', 'Gabriela Rocha', 'Heitor Lima',
    'Isabela Castro', 'João Pedro Souza', 'Larissa Duarte', 'Marcos Vinícius',
    'Natália Barros', 'Otávio Ramos', 'Patrícia Freitas', 'Rafael Teixeira',
    'Sofia Martins', 'Thiago Correia', 'Vanessa Prado', 'William Ferreira',
]

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


class Command(BaseCommand):
    help = 'Carrega dados fake realistas para demonstração.'

    @transaction.atomic
    def handle(self, *args, **options):
        cnpj = '12.345.678/0001-90'
        brokerage = Brokerage.objects.filter(cnpj='12345678000190').first()
        if brokerage is None:
            brokerage = Brokerage.objects.create(
                cnpj='12345678000190',
                legal_name='Corretora Demo Ltda',
                trade_name='Demo Corretora',
                email='contato@demo.scsi.digital',
                phone='(11) 4002-8922',
                city='São Paulo',
                state='SP',
            )
        set_current_brokerage(brokerage)

        user, _ = User.objects.get_or_create(
            email='admin@demo.scsi.digital',
            defaults={
                'full_name': 'Admin Demo',
                'brokerage': brokerage,
                'role': 'owner',
                'is_staff': True,
            },
        )
        if not user.has_usable_password():
            user.set_password('admin123')
            user.save()

        self.stdout.write(f'Brokerage: {brokerage.legal_name}')
        self._load_base(brokerage)
        self._load_commercial(brokerage)
        self._load_crm(brokerage)
        self.stdout.write(self.style.SUCCESS('Dados fake carregados com sucesso.'))

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
                    brokerage=brokerage,
                    name=cov_name,
                    defaults={'branch': branch},
                )

        clients = []
        for i, name in enumerate(CLIENT_NAMES):
            client, _ = Client.all_objects.get_or_create(
                brokerage=brokerage,
                name=name,
                defaults={
                    'type': 'pf' if i % 4 else 'pj',
                    'document': f'{i:011d}' if i % 4 else f'{i:014d}',
                    'email': f'cliente{i}@email.com',
                    'phone': f'(11) 9{i:08d}',
                    'city': random.choice(['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Curitiba']),
                    'state': random.choice(['SP', 'RJ', 'MG', 'PR']),
                    'created_at': today - timedelta(days=random.randint(30, 700)),
                },
            )
            clients.append(client)

        self.insurers = insurers
        self.branches = branches
        self.clients = clients
        self.brokerage = brokerage

    def _load_commercial(self, brokerage):
        today = timezone.localdate()
        agents = []
        for i in range(4):
            agent, _ = Agent.all_objects.get_or_create(
                brokerage=brokerage,
                name=random.choice(['Agente Alfa', 'Agente Beta', 'Agente Gama', 'Agente Delta']),
                defaults={
                    'document': f'{i+1:011d}',
                    'commission_rate': random.choice([10, 15, 20, 25]),
                },
            )
            agents.append(agent)

        producers = []
        for i in range(6):
            producer, _ = Producer.all_objects.get_or_create(
                brokerage=brokerage,
                name=random.choice([
                    'Produtor 01', 'Produtor 02', 'Produtor 03',
                    'Produtor 04', 'Produtor 05', 'Produtor 06',
                ]),
                defaults={
                    'agent': random.choice(agents) if i % 3 else None,
                    'document': f'2{i:010d}',
                    'commission_rate': random.choice([5, 8, 10, 12]),
                },
            )
            producers.append(producer)

        for client in self.clients:
            branch = random.choice(self.branches)
            insurer = random.choice(self.insurers)
            coverage = list(Coverage.all_objects.filter(branch=branch))[:random.randint(1, 3)]
            item_type = {
                'Automóvel': 'vehicle', 'Residencial': 'property', 'Vida': 'life',
                'Viagem': 'travel', 'Empresarial': 'business', 'Frota': 'fleet_item',
            }[branch.name]
            item, _ = CoveredItem.all_objects.get_or_create(
                brokerage=brokerage,
                description=f'{item_type} de {client.name}',
                defaults={
                    'type': item_type,
                    'attributes': {
                        'marca': random.choice(['Fiat', 'VW', 'GM', 'Toyota']),
                        'ano': random.randint(2015, 2024),
                    },
                },
            )

            premium = round(random.uniform(500, 5000), 2)
            proposal = Proposal.all_objects.create(
                brokerage=brokerage,
                client=client,
                insurer=insurer,
                branch=branch,
                status=random.choice([PROPOSAL_DRAFT, PROPOSAL_SUBMITTED, PROPOSAL_APPROVED]),
                premium=premium,
                created_at=today - timedelta(days=random.randint(10, 200)),
            )
            proposal.coverages.set(coverage)
            proposal.covered_items.set([item])

            if random.random() < 0.6:
                policy, created = generate_policy_from_proposal(proposal)
                if created:
                    policy.start_date = today - timedelta(days=random.randint(30, 300))
                    policy.end_date = policy.start_date + timedelta(days=365)
                    policy.save()

                    if random.random() < 0.4:
                        Endorsement.all_objects.create(
                            brokerage=brokerage,
                            policy=policy,
                            type=random.choice(['inclusion', 'exclusion', 'alteration']),
                            description='Endosso de demonstração',
                            effective_date=today - timedelta(days=random.randint(1, 90)),
                        )

                    if random.random() < 0.5:
                        Claim.all_objects.create(
                            brokerage=brokerage,
                            policy=policy,
                            covered_item=item,
                            type=random.choice([c for c, _ in CLAIM_TYPE_CHOICES]),
                            status=CLAIM_OPEN,
                            description='Sinistro de demonstração',
                            reserved_amount=round(random.uniform(1000, 20000), 2),
                            reported_at=timezone.now() - timedelta(days=random.randint(1, 120)),
                        )

                    if random.random() < 0.7:
                        Renewal.all_objects.create(
                            brokerage=brokerage,
                            policy=policy,
                            client=client,
                            due_date=policy.end_date - timedelta(days=30),
                            status=random.choice([RENEWAL_PENDING, RENEWAL_CONTACTED]),
                        )

                    if random.random() < 0.6:
                        total = round(random.uniform(200, 3000), 2)
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
            brokerage=brokerage, is_default=True, defaults={'name': 'Funil Comercial'}
        )
        stage_names = [
            ('Lead', '#0d6efd', 1),
            ('Qualificação', '#0dcaf0', 2),
            ('Proposta enviada', '#ffc107', 3),
            ('Negociação', '#fd7e14', 4),
            ('Fechado', '#198754', 5),
        ]
        stages = []
        for name, color, order in stage_names:
            stage, _ = PipelineStage.all_objects.get_or_create(
                brokerage=brokerage, pipeline=pipeline, order=order,
                defaults={'name': name, 'color': color},
            )
            stages.append(stage)

        for i, client in enumerate(random.sample(self.clients, k=min(12, len(self.clients)))):
            stage = random.choice(stages)
            Deal.all_objects.create(
                brokerage=brokerage,
                pipeline=pipeline,
                stage=stage,
                client=client,
                title=f'Negociação {client.name}',
                value=round(random.uniform(1000, 20000), 2),
                expected_close_date=timezone.localdate() + timedelta(days=random.randint(1, 90)),
                order=i,
            )
