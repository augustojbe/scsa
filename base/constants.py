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
