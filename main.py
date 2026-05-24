import subprocess
import time
import os
import json

from core.ollama import iniciar_ollama, perguntar_ollama
from core.parser import parse_resposta
from core.thinking import iniciar_thinking, parar_thinking

from features.hora import ver_hora


# =========================
# 🌍 ANIMAÇÃO INICIAL
# =========================
def animacao_inicio():
    try:
        proc = subprocess.Popen(
            ["curl", "ascii.live/earth"],
            stdout=None,
            stderr=subprocess.DEVNULL
        )

        time.sleep(3)
        proc.terminate()

    except Exception:
        pass


# =========================
# 📂 CARREGAR TRIGGERS
# =========================
def carregar_triggers():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    triggers_path = os.path.join(base_dir, "triggers")

    mapa_acoes = {}

    if not os.path.exists(triggers_path):
        return mapa_acoes

    for arquivo in os.listdir(triggers_path):
        if not arquivo.endswith(".json"):
            continue

        caminho = os.path.join(triggers_path, arquivo)

        try:
            with open(caminho, "r", encoding="utf-8") as f:
                data = json.load(f)

                acao = data.get("acao")
                gatilhos = data.get("gatilhos", [])

                if acao and gatilhos:
                    mapa_acoes[acao] = gatilhos

        except Exception as e:
            print(f"⚠️ Erro ao carregar {arquivo}: {e}")

    return mapa_acoes


# =========================
# 🧠 DETECÇÃO DE AÇÃO
# =========================
def detectar_acao(texto, mapa_acoes):
    texto = texto.lower().strip()

    for acao, gatilhos in mapa_acoes.items():
        for gatilho in gatilhos:
            if gatilho in texto:
                return acao

    return None


# =========================
# ⚙️ EXECUÇÃO DE AÇÃO
# =========================
def executar_acao(acao):
    if acao == "ver_hora":
        return ver_hora()

    return {
        "ok": False,
        "acao": acao,
        "mensagem": "Ação não reconhecida",
        "dados": "",
        "erro": "Ação não cadastrada"
    }


# =========================
# 🗣️ RESPOSTA DE FEATURE
# =========================
def responder_resultado_feature(resultado):
    acao = resultado.get("acao")
    ok = resultado.get("ok")
    dados = resultado.get("dados")
    erro = resultado.get("erro")

    if acao == "ver_hora":
        if ok:
            return f"Agora são {dados}."
        return f"Não consegui ver a hora do sistema. Erro: {erro}"

    if ok:
        return "Pronto, fiz."

    return "Não consegui executar isso."


# =========================
# 🚀 MAIN
# =========================
def main():
    animacao_inicio()

    iniciar_ollama()

    mapa_acoes = carregar_triggers()

    print("\n🤖 Jarvis iniciado (digite 'sair')\n")

    while True:
        user_input = input("Você: ").strip()

        if user_input.lower() in ["sair", "exit"]:
            print("Jarvis: Fechou!")
            break

        # 🔍 tenta detectar ação
        acao = detectar_acao(user_input, mapa_acoes)

        if acao:
            resultado = executar_acao(acao)
            resposta = responder_resultado_feature(resultado)
            print("Jarvis:", resposta)
            continue

        # 🤖 fallback IA
        stop_event = iniciar_thinking()

        resposta_bruta = perguntar_ollama(user_input)

        parar_thinking(stop_event)

        data = parse_resposta(resposta_bruta)

        print("Jarvis:", data.get("resposta", "Entendi."))


if __name__ == "__main__":
    main()