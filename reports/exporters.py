from io import BytesIO

import csv as csv_module

from django.db.models import Sum
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from agents.models import Agent, Producer
from claims.models import Claim
from clients.models import Client
from commissions.models import Commission
from crm.models import Deal, PipelineStage
from insurers.models import Insurer
from policies.models import Policy, Proposal
from renewals.models import Renewal


def _client_rows():
    headers = ['Nome', 'Tipo', 'Documento', 'E-mail', 'Telefone', 'Cidade/UF']
    rows = []
    for c in Client.all_objects.select_related('brokerage'):
        rows.append([
            c.name,
            c.get_type_display(),
            c.document or '',
            c.email or '',
            c.phone or '',
            f'{c.city}/{c.state}' if c.city else '',
        ])
    return headers, rows


def _insurer_rows():
    headers = ['Seguradora', 'Código', 'Apólices', 'Prêmio emitido']
    rows = []
    for i in Insurer.all_objects:
        total = i.policies.aggregate(_sum=Sum('premium'))['_sum'] or 0
        rows.append([
            i.name,
            i.code or '',
            i.policies.count(),
            f'{total:.2f}',
        ])
    return headers, rows


def _policy_rows():
    headers = ['Número', 'Cliente', 'Seguradora', 'Ramo', 'Status', 'Prêmio', 'Início', 'Fim']
    rows = []
    for p in Policy.all_objects.select_related('client', 'insurer', 'branch'):
        rows.append([
            p.number,
            p.client.name,
            p.insurer.name,
            p.branch.name,
            p.get_status_display(),
            f'{p.premium:.2f}',
            p.start_date.strftime('%d/%m/%Y') if p.start_date else '',
            p.end_date.strftime('%d/%m/%Y') if p.end_date else '',
        ])
    return headers, rows


def _proposal_rows():
    headers = ['#', 'Cliente', 'Seguradora', 'Ramo', 'Status', 'Prêmio']
    rows = []
    for p in Proposal.all_objects.select_related('client', 'insurer', 'branch'):
        rows.append([
            str(p.pk),
            p.client.name,
            p.insurer.name,
            p.branch.name,
            p.get_status_display(),
            f'{p.premium:.2f}',
        ])
    return headers, rows


def _claim_rows():
    headers = ['Número', 'Apólice', 'Cliente', 'Tipo', 'Status', 'Reportado', 'Reserva']
    rows = []
    for c in Claim.all_objects.select_related('policy', 'policy__client'):
        rows.append([
            c.number,
            c.policy.number,
            c.policy.client.name,
            c.get_type_display(),
            c.get_status_display(),
            c.reported_at.strftime('%d/%m/%Y %H:%M'),
            f'{c.reserved_amount:.2f}',
        ])
    return headers, rows


def _renewal_rows():
    headers = ['Apólice', 'Cliente', 'Vencimento', 'Status']
    rows = []
    for r in Renewal.all_objects.select_related('policy', 'client'):
        rows.append([
            r.policy.number,
            r.client.name,
            r.due_date.strftime('%d/%m/%Y'),
            r.get_status_display(),
        ])
    return headers, rows


def _commission_rows():
    headers = [
        'Apólice', 'Cliente', 'Total', 'Agente', 'Produtor', 'Corretora', 'Status',
    ]
    rows = []
    for c in Commission.all_objects.select_related('policy', 'client'):
        rows.append([
            c.policy.number,
            c.client.name,
            f'{c.total_amount:.2f}',
            f'{c.agent_share:.2f}',
            f'{c.producer_share:.2f}',
            f'{c.brokerage_share:.2f}',
            c.get_status_display(),
        ])
    return headers, rows


def _portfolio_rows():
    headers = ['Métrica', 'Valor']
    clients_total = Client.all_objects.count()
    clients_pf = Client.all_objects.filter(type='pf').count()
    clients_pj = Client.all_objects.filter(type='pj').count()
    policies_total = Policy.all_objects.count()
    policies_active = Policy.all_objects.filter(status='active').count()
    premium_total = Policy.all_objects.aggregate(s=Sum('premium'))['s'] or 0
    commission_total = Commission.all_objects.aggregate(s=Sum('total_amount'))['s'] or 0
    commission_brokerage = Commission.all_objects.aggregate(s=Sum('brokerage_share'))['s'] or 0
    rows = [
        ['Total de clientes', str(clients_total)],
        ['Clientes PF', str(clients_pf)],
        ['Clientes PJ', str(clients_pj)],
        ['Total de apólices', str(policies_total)],
        ['Apólices ativas', str(policies_active)],
        ['Prêmio total (R$)', f'{premium_total:.2f}'],
        ['Comissões totais (R$)', f'{commission_total:.2f}'],
        ['Líquido da corretora (R$)', f'{commission_brokerage:.2f}'],
        ['Seguradoras', str(Insurer.all_objects.count())],
        ['Agentes', str(Agent.all_objects.count())],
        ['Produtores', str(Producer.all_objects.count())],
        ['Negociações abertas', str(Deal.all_objects.count())],
        ['Renovações', str(Renewal.all_objects.count())],
    ]
    return headers, rows


REPORTS = {
    'clientes': ('Clientes', _client_rows),
    'seguradoras': ('Seguradoras', _insurer_rows),
    'apolices': ('Apólices', _policy_rows),
    'propostas': ('Propostas', _proposal_rows),
    'sinistros': ('Sinistros', _claim_rows),
    'renovacoes': ('Renovações', _renewal_rows),
    'comissoes': ('Comissões', _commission_rows),
    'carteira': ('Carteira', _portfolio_rows),
}


def build_csv(slug):
    title, getter = REPORTS[slug]
    headers, rows = getter()
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{slug}.csv"'
    writer = csv_module.writer(response)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    return response


def build_pdf(slug):
    title, getter = REPORTS[slug]
    headers, rows = getter()
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=10 * mm,
        leftMargin=10 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
    )
    styles = getSampleStyleSheet()
    story = [Paragraph(f'SCSI — Relatório: {title}', styles['Title']), Spacer(1, 6 * mm)]
    table_data = [headers] + rows
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f1f3f5')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(table)
    doc.build(story)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{slug}.pdf"'
    return response
