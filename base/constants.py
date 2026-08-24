PLAN_FREE = 'free'
PLAN_PRO = 'pro'
PLAN_BUSINESS = 'business'

PLAN_CHOICES = [
    (PLAN_FREE, 'Free'),
    (PLAN_PRO, 'Pro'),
    (PLAN_BUSINESS, 'Business'),
]

ROLE_OWNER = 'owner'
ROLE_ADMIN = 'admin'
ROLE_AGENT = 'agent'
ROLE_PRODUCER = 'producer'
ROLE_OPERATIONAL = 'operational'

ROLE_CHOICES = [
    (ROLE_OWNER, 'Owner'),
    (ROLE_ADMIN, 'Admin'),
    (ROLE_AGENT, 'Agent'),
    (ROLE_PRODUCER, 'Producer'),
    (ROLE_OPERATIONAL, 'Operational'),
]

MANAGEMENT_ROLES = [ROLE_OWNER, ROLE_ADMIN]

CLIENT_TYPE_PERSON = 'pf'
CLIENT_TYPE_COMPANY = 'pj'

CLIENT_TYPE_CHOICES = [
    (CLIENT_TYPE_PERSON, 'Pessoa Física'),
    (CLIENT_TYPE_COMPANY, 'Pessoa Jurídica'),
]

COVERED_ITEM_VEHICLE = 'vehicle'
COVERED_ITEM_PROPERTY = 'property'
COVERED_ITEM_FLEET = 'fleet_item'
COVERED_ITEM_TRAVEL = 'travel'
COVERED_ITEM_LIFE = 'life'
COVERED_ITEM_BUSINESS = 'business'
COVERED_ITEM_OTHER = 'other'

COVERED_ITEM_TYPE_CHOICES = [
    (COVERED_ITEM_VEHICLE, 'Automóvel'),
    (COVERED_ITEM_PROPERTY, 'Imóvel'),
    (COVERED_ITEM_FLEET, 'Item de Frota'),
    (COVERED_ITEM_TRAVEL, 'Viagem'),
    (COVERED_ITEM_LIFE, 'Vida'),
    (COVERED_ITEM_BUSINESS, 'Empresarial'),
    (COVERED_ITEM_OTHER, 'Outro'),
]

POLICY_PENDING = 'pending'
POLICY_ACTIVE = 'active'
POLICY_CANCELLED = 'cancelled'
POLICY_EXPIRED = 'expired'

POLICY_STATUS_CHOICES = [
    (POLICY_PENDING, 'Pendente'),
    (POLICY_ACTIVE, 'Ativa'),
    (POLICY_CANCELLED, 'Cancelada'),
    (POLICY_EXPIRED, 'Expirada'),
]

CLAIM_TYPE_COLLISION = 'collision'
CLAIM_TYPE_THEFT = 'theft'
CLAIM_TYPE_FIRE = 'fire'
CLAIM_TYPE_FLOOD = 'flood'
CLAIM_TYPE_THIRD_PARTY = 'third_party'
CLAIM_TYPE_GLASS = 'glass'
CLAIM_TYPE_OTHER = 'other'

CLAIM_TYPE_CHOICES = [
    (CLAIM_TYPE_COLLISION, 'Colisão'),
    (CLAIM_TYPE_THEFT, 'Roubo/Furto'),
    (CLAIM_TYPE_FIRE, 'Incêndio'),
    (CLAIM_TYPE_FLOOD, 'Alagamento'),
    (CLAIM_TYPE_THIRD_PARTY, 'Terceiro'),
    (CLAIM_TYPE_GLASS, 'Vidros'),
    (CLAIM_TYPE_OTHER, 'Outro'),
]

CLAIM_OPEN = 'open'
CLAIM_IN_ANALYSIS = 'in_analysis'
CLAIM_APPROVED = 'approved'
CLAIM_PAID = 'paid'
CLAIM_DENIED = 'denied'
CLAIM_CLOSED = 'closed'

CLAIM_STATUS_CHOICES = [
    (CLAIM_OPEN, 'Aberto'),
    (CLAIM_IN_ANALYSIS, 'Em análise'),
    (CLAIM_APPROVED, 'Aprovado'),
    (CLAIM_PAID, 'Indenizado'),
    (CLAIM_DENIED, 'Recusado'),
    (CLAIM_CLOSED, 'Concluído'),
]

PROPOSAL_DRAFT = 'draft'
PROPOSAL_SUBMITTED = 'submitted'
PROPOSAL_APPROVED = 'approved'
PROPOSAL_REJECTED = 'rejected'
PROPOSAL_CONVERTED = 'converted'

PROPOSAL_STATUS_CHOICES = [
    (PROPOSAL_DRAFT, 'Rascunho'),
    (PROPOSAL_SUBMITTED, 'Enviada'),
    (PROPOSAL_APPROVED, 'Aprovada'),
    (PROPOSAL_REJECTED, 'Recusada'),
    (PROPOSAL_CONVERTED, 'Convertida em apólice'),
]

RENEWAL_PENDING = 'pending'
RENEWAL_CONTACTED = 'contacted'
RENEWAL_RENEWED = 'renewed'
RENEWAL_LOST = 'lost'

RENEWAL_STATUS_CHOICES = [
    (RENEWAL_PENDING, 'Pendente'),
    (RENEWAL_CONTACTED, 'Contatado'),
    (RENEWAL_RENEWED, 'Renovado'),
    (RENEWAL_LOST, 'Perdido'),
]

ENDORSEMENT_INCLUSION = 'inclusion'
ENDORSEMENT_EXCLUSION = 'exclusion'
ENDORSEMENT_ALTERATION = 'alteration'
ENDORSEMENT_CANCELLATION = 'cancellation'
ENDORSEMENT_OTHER = 'other'

ENDORSEMENT_TYPE_CHOICES = [
    (ENDORSEMENT_INCLUSION, 'Inclusão'),
    (ENDORSEMENT_EXCLUSION, 'Exclusão'),
    (ENDORSEMENT_ALTERATION, 'Alteração'),
    (ENDORSEMENT_CANCELLATION, 'Cancelamento'),
    (ENDORSEMENT_OTHER, 'Outro'),
]

PIPELINE_STAGE_COLORS = [
    ('#0d6efd', 'Azul'),
    ('#198754', 'Verde'),
    ('#ffc107', 'Amarelo'),
    ('#dc3545', 'Vermelho'),
    ('#6f42c1', 'Roxo'),
    ('#0dcaf0', 'Ciano'),
    ('#6c757d', 'Cinza'),
    ('#fd7e14', 'Laranja'),
    ('#20c997', 'Teal'),
]

AGENT_PERSON = 'person'
AGENT_COMPANY = 'company'

AGENT_TYPE_CHOICES = [
    (AGENT_PERSON, 'Pessoa'),
    (AGENT_COMPANY, 'Empresa'),
]

COMMISSION_PENDING = 'pending'
COMMISSION_PAID = 'paid'

COMMISSION_STATUS_CHOICES = [
    (COMMISSION_PENDING, 'Pendente'),
    (COMMISSION_PAID, 'Paga'),
]
