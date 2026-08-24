import os

from ai.tools import GETTERS


def _openai_available():
    if not os.getenv('OPENAI_API_KEY'):
        return False
    try:
        import openai  # noqa: F401
        return True
    except ImportError:
        return False


def _call_openai(system, user):
    import openai

    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    response = client.chat.completions.create(
        model=os.getenv('OPENAI_MODEL', 'gpt-5.5-mini'),
        messages=[
            {'role': 'system', 'content': system},
            {'role': 'user', 'content': user},
        ],
    )
    return response.choices[0].message.content


def _simulate_summary(data):
    lines = []
    lines.append(f'# Resumo — {data["entity"]}')
    lines.append('')
    for key, value in data.items():
        if key == 'entity':
            continue
        label = key.replace('_', ' ').capitalize()
        lines.append(f'- **{label}:** {value}')
    lines.append('')
    lines.append('## Insights')
    lines.append('')
    lines.append(
        '- Registro localizado no contexto da corretora, pronto para análise operacional.'
    )
    lines.append('- Consulte o detalhe completo na tela da entidade para mais informações.')
    return '\n'.join(lines)


def generate_summary(entity_type, brokerage_id, entity_id):
    getter = GETTERS[entity_type]
    data = getter(brokerage_id, entity_id)
    if data is None:
        raise ValueError('Entidade não encontrada para a corretora informada.')
    if _openai_available():
        user = '\n'.join(f'{k}: {v}' for k, v in data.items())
        return _call_openai(
            'Você é um assistente de uma corretora de seguros. '
            'Gere um resumo conciso, em português, com seções e insights.',
            user,
        )
    return _simulate_summary(data)


def chat_reply(session_title, user_message, context):
    if _openai_available():
        return _call_openai(
            'Você é um assistente da corretora de seguros SCSI. '
            'Responda em português com Markdown, apenas com base na base da corretora.',
            f'Sessão: {session_title}\nContexto do tenant:\n{context}\n\nUsuário: {user_message}',
        )
    return (
        f'## Resposta simulada\n\n'
        f'Entendi sua pergunta: **{user_message}**.\n\n'
        f'Esta é uma resposta de demonstração gerada porque não há '
        f'`OPENAI_API_KEY` configurada. Quando a chave for definida, '
        f'o agente responderá com base nos dados da corretora.\n\n'
        f'- **Tenant:** dados isolados por corretora\n'
        f'- **Sessão:** {session_title}'
    )
