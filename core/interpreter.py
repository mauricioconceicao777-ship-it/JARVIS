import json
import requests
import re

from core.config import (
    OLLAMA_GENERATE_URL,
    MODEL,
    MODEL_OPTIONS
)

from core.parser import parse_resposta
from core.logger import logger


INTERPRETER_TIMEOUT = 20


# =========================
# 🔹 INTERPRETAÇÃO LOCAL
# =========================
def interpretar_status_sistema(dados: str) -> str:
    cpu = None
    memoria = None
    disco = None

    cpu_match = re.search(r"CPU:\s*\n([0-9]+)%", dados)
    memoria_match = re.search(r"Memória:\s*\n([0-9]+)%", dados)
    disco_match = re.search(r"Disco:\s*\n([0-9]+)%", dados)

    if cpu_match:
        cpu = int(cpu_match.group(1))

    if memoria_match:
        memoria = int(memoria_match.group(1))

    if disco_match:
        disco = int(disco_match.group(1))

    partes = []

    if cpu is not None:
        if cpu < 50:
            partes.append(f"CPU tranquila, em {cpu}%.")
        elif cpu < 80:
            partes.append(f"CPU moderada, em {cpu}%.")
        else:
            partes.append(f"CPU alta, em {cpu}%.")

    if memoria is not None:
        if memoria < 60:
            partes.append(f"Memória confortável, em {memoria}%.")
        elif memoria < 85:
            partes.append(f"Memória moderada, em {memoria}%.")
        else:
            partes.append(f"Memória alta, em {memoria}%.")

    if disco is not None:
        if disco < 75:
            partes.append(f"Disco ok, {disco}% usado.")
        elif disco < 90:
            partes.append(f"Disco ficando cheio, {disco}% usado.")
        else:
            partes.append(f"Disco crítico, {disco}% usado.")

    if not partes:
        return dados or "Status obtido, mas não consegui interpretar."

    return " ".join(partes)


# =========================
# 🔹 FALLBACK
# =========================
def fallback_interpretacao(resultado):
    acao = resultado.get("acao", "")
    dados = resultado.get("dados", "")
    erro = resultado.get("erro", "")

    if resultado.get("ok"):

        # 🔥 HORA → resposta imediata
        if acao == "ver_hora":
            return f"Agora são {dados}."

        # 🔥 SCRIPT → resposta direta
        if acao == "executar_script":
            if dados:
                return dados
            return "Pronto."

        return "Pronto."

    if erro:
        return f"Não consegui executar. {erro}"

    return "Não consegui executar isso."


# =========================
# 🧠 INTERPRETADOR PRINCIPAL
# =========================
def interpretar_resultado_feature(resultado):
    acao = resultado.get("acao")
    script = resultado.get("script")

    # 🔥 PRIORIDADE 1 — respostas instantâneas (sem IA)
    if acao == "ver_hora":
        return fallback_interpretacao(resultado)

    # 🔥 PRIORIDADE 2 — scripts específicos (local)
    if acao == "executar_script" and script == "status_sistema":
        return interpretar_status_sistema(resultado.get("dados", ""))

    # 🔥 PRIORIDADE 3 — script simples (sem IA)
    if acao == "executar_script":
        return fallback_interpretacao(resultado)

    # 🔥 PRIORIDADE 4 — IA (somente quando necessário)
    prompt = f"""
Você é o Jarvis, um assistente brasileiro.

Interprete o resultado abaixo e responda de forma curta, clara e natural.

Regras:
- Resposta curta
- Não invente dados
- Não use markdown
- Se deu erro, explique simples
- JSON válido obrigatório

Formato:
{{
  "tipo": "chat",
  "resposta": "texto"
}}

Resultado:
{json.dumps(resultado, ensure_ascii=False)}
"""

    try:
        response = requests.post(
            OLLAMA_GENERATE_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    **MODEL_OPTIONS,
                    "temperature": 0.1,
                    "num_predict": 80
                }
            },
            timeout=INTERPRETER_TIMEOUT
        )

        bruto = response.json().get("response", "")
        parsed = parse_resposta(bruto)

        resposta = parsed.get("resposta", "").strip()

        if resposta:
            return resposta

        return fallback_interpretacao(resultado)

    except Exception as e:
        logger.warning(f"Falha no interpretador IA: {e}")
        return fallback_interpretacao(resultado)