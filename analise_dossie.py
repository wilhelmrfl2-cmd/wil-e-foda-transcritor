import os
from dotenv import load_dotenv
load_dotenv()

import anthropic

def gerar_dossie(transcricao: str, observacao: str = "") -> str:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    instrucao_extra = f"\n\nOBSERVAÇÃO ESPECIAL DO USUÁRIO (priorize isso):\n{observacao}" if observacao.strip() else ""
    prompt = f"""Você é um analista de conteúdo especialista em marketing digital.
Com base na transcrição abaixo, gere um dossiê completo contendo:
1. RESUMO EXECUTIVO — O que o vídeo fala em 3 linhas
2. TEMA PRINCIPAL — Qual o assunto central
3. GANCHOS UTILIZADOS — Quais técnicas de atenção o criador usou
4. ESTRUTURA DO VÍDEO — Como ele organizou o conteúdo
5. PALAVRAS-CHAVE — As 10 principais
6. PÚBLICO-ALVO — Para quem esse conteúdo foi feito
7. PONTOS FORTES — O que funcionou bem
8. OPORTUNIDADES — O que poderia ser melhorado ou explorado
9. IDEIAS DE CONTEÚDO — 5 ideias de vídeos baseadas nesse conteúdo
{instrucao_extra}
TRANSCRIÇÃO:
{transcricao}
Responda em português brasileiro, de forma clara e direta."""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text
