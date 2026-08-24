import os

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from ai.agent import build_chat_agent
from ai.tools import GETTERS


def _ai_available():
    if not os.getenv('OPENAI_API_KEY'):
        return False
    return True


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
    if _ai_available():
        try:
            llm = ChatOpenAI(model=os.getenv('OPENAI_MODEL', 'gpt-5.5-mini'))
            user = '\n'.join(f'{k}: {v}' for k, v in data.items())
            messages = [
                HumanMessage(
                    content=(
                        'Você é um assistente de uma corretora de seguros. Gere um resumo '
                        'conciso, em português, com seções e insights, a partir dos dados '
                        'fornecidos (já filtrados pelo tenant).\n\nDados:\n' + user
                    )
                )
            ]
            return llm.invoke(messages).content
        except Exception:
            # fallback: modelo/configuração indisponível -> resumo simulado
            pass
    return _simulate_summary(data)


def chat_reply(brokerage_id, session_title, user_message, context):
    if _ai_available():
        try:
            agent = build_chat_agent(brokerage_id)
            if agent is not None:
                result = agent.invoke(
                    {
                        'messages': [
                            HumanMessage(
                                content=(
                                    f'Sessão: {session_title}\n'
                                    f'Contexto do tenant:\n{context}\n\n'
                                    f'Usuário: {user_message}'
                                )
                            )
                        ]
                    },
                    {'configurable': {'thread_id': f'scsi-{session_title}'}},
                )
                return result['messages'][-1].content
        except Exception:
            # fallback: erro na chamada do agente -> resposta simulada
            pass
    return (
        f'## Resposta simulada\n\n'
        f'Entendi sua pergunta: **{user_message}**.\n\n'
        f'Esta é uma resposta de demonstração gerada porque não foi possível '
        f'completar a chamada ao agente (verifique `OPENAI_API_KEY`/`OPENAI_MODEL`). '
        f'Quando o modelo estiver configurado corretamente, o agente LangGraph '
        f'responderá usando as tools da corretora.\n\n'
        f'- **Tenant:** dados isolados por corretora\n'
        f'- **Sessão:** {session_title}'
    )
