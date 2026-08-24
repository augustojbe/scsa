import os

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from agents.models import Agent, Producer
from claims.models import Claim
from clients.models import Client
from commissions.models import Commission
from crm.models import Deal, PipelineStage
from insurers.models import Insurer
from policies.models import Policy, Proposal
from renewals.models import Renewal


def _rows_label(rows, limit=20):
    if not rows:
        return 'Nenhum registro encontrado.'
    return '\n'.join(
        ' - ' + ' | '.join(f'{k}: {v}' for k, v in row.items()) for row in rows[:limit]
    )


def _fmt(value):
    return str(value) if value not in (None, '') else '—'


def build_tools(brokerage_id):
    """Retorna tools de leitura filtradas pelo brokerage (nunca aceita do LLM)."""

    @tool
    def list_clients(query: str = '') -> str:
        """Lista clientes da corretora, opcionalmente filtrando por nome/documento."""
        qs = Client.all_objects.filter(brokerage_id=brokerage_id)
        if query:
            qs = qs.filter(name__icontains=query)
        return _rows_label([
            {
                'id': c.pk, 'nome': c.name, 'tipo': c.get_type_display(),
                'documento': _fmt(c.document), 'email': _fmt(c.email),
            }
            for c in qs
        ])

    @tool
    def get_client_detail(client_id: int) -> str:
        """Retorna o detalhe de um cliente da corretora pelo id."""
        c = Client.all_objects.filter(pk=client_id, brokerage_id=brokerage_id).first()
        if c is None:
            return 'Cliente não encontrado.'
        return _rows_label([{
            'id': c.pk, 'nome': c.name, 'tipo': c.get_type_display(),
            'email': _fmt(c.email), 'telefone': _fmt(c.phone),
            'apolices': c.policies.count(), 'propostas': c.proposals.count(),
        }])

    @tool
    def list_policies(query: str = '') -> str:
        """Lista apólices da corretora, opcionalmente filtrando por número/cliente."""
        qs = Policy.all_objects.filter(brokerage_id=brokerage_id)
        if query:
            qs = qs.filter(number__icontains=query)
        return _rows_label([
            {
                'id': p.pk, 'numero': p.number, 'cliente': p.client.name,
                'status': p.get_status_display(), 'premio': f'{p.premium:.2f}',
            }
            for p in qs
        ])

    @tool
    def get_policy_detail(policy_id: int) -> str:
        """Retorna o detalhe de uma apólice da corretora pelo id."""
        p = Policy.all_objects.filter(pk=policy_id, brokerage_id=brokerage_id).first()
        if p is None:
            return 'Apólice não encontrada.'
        return _rows_label([{
            'id': p.pk, 'numero': p.number, 'cliente': p.client.name,
            'seguradora': p.insurer.name, 'ramo': p.branch.name,
            'status': p.get_status_display(), 'premio': f'{p.premium:.2f}',
            'inicio': _fmt(p.start_date), 'fim': _fmt(p.end_date),
            'sinistros': p.claims.count(),
        }])

    @tool
    def list_claims(query: str = '') -> str:
        """Lista sinistros da corretora."""
        qs = Claim.all_objects.filter(brokerage_id=brokerage_id)
        if query:
            qs = qs.filter(number__icontains=query)
        return _rows_label([
            {
                'id': cl.pk, 'numero': cl.number, 'apolice': cl.policy.number,
                'tipo': cl.get_type_display(), 'status': cl.get_status_display(),
            }
            for cl in qs
        ])

    @tool
    def list_proposals(query: str = '') -> str:
        """Lista propostas da corretora."""
        qs = Proposal.all_objects.filter(brokerage_id=brokerage_id)
        if query:
            qs = qs.filter(client__name__icontains=query)
        return _rows_label([
            {
                'id': pr.pk, 'cliente': pr.client.name, 'status': pr.get_status_display(),
                'premio': f'{pr.premium:.2f}',
            }
            for pr in qs
        ])

    @tool
    def list_deals(query: str = '') -> str:
        """Lista negociações (CRM) da corretora."""
        qs = Deal.all_objects.filter(brokerage_id=brokerage_id)
        if query:
            qs = qs.filter(title__icontains=query)
        return _rows_label([
            {
                'id': d.pk, 'titulo': d.title, 'cliente': d.client.name if d.client else '—',
                'etapa': d.stage.name, 'valor': f'{d.value:.2f}',
            }
            for d in qs
        ])

    @tool
    def get_renewals() -> str:
        """Lista renovações da corretora."""
        return _rows_label([
            {
                'id': r.pk, 'apolice': r.policy.number, 'cliente': r.client.name,
                'vencimento': _fmt(r.due_date), 'status': r.get_status_display(),
            }
            for r in Renewal.all_objects.filter(brokerage_id=brokerage_id)
        ])

    @tool
    def get_commissions_summary() -> str:
        """Resumo das comissões e repasses da corretora."""
        qs = Commission.all_objects.filter(brokerage_id=brokerage_id)
        total = sum((c.total_amount for c in qs), 0)
        agent_share = sum((c.agent_share for c in qs), 0)
        producer_share = sum((c.producer_share for c in qs), 0)
        brokerage_share = sum((c.brokerage_share for c in qs), 0)
        return (
            f'Total: {total:.2f}\n'
            f'Repasse agente: {agent_share:.2f}\n'
            f'Repasse produtor: {producer_share:.2f}\n'
            f'Líquido corretora: {brokerage_share:.2f}\n'
            f'Registros: {qs.count()}'
        )

    return [
        list_clients,
        get_client_detail,
        list_policies,
        get_policy_detail,
        list_claims,
        list_proposals,
        list_deals,
        get_renewals,
        get_commissions_summary,
    ]


def build_chat_agent(brokerage_id):
    """Compila o agente LangGraph (ReAct) com tools do tenant. Retorna None sem chave."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return None
    model = ChatOpenAI(
        model=os.getenv('OPENAI_MODEL', 'gpt-5.5-mini'),
        temperature=0.3,
    )
    return create_react_agent(model, build_tools(brokerage_id))
