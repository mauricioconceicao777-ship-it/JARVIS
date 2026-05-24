from flask import Flask, render_template, request, jsonify
import sys
import os
import requests
import json

# 🔧 permite importar o core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.ollama import iniciar_ollama, perguntar_ollama
from core.parser import parse_resposta
from core.logger import logger
from core.interpreter import interpretar_resultado_feature
from core.scheduler import scheduler

from features.hora import ver_hora
from features.scripts import executar_script
from features.monitoramento import verificar_status_sistema

app = Flask(__name__)


# =========================
# 🔥 CARREGAR TRIGGERS
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRIGGERS_PATH = os.path.join(BASE_DIR, "triggers", "scripts.json")

try:
    with open(TRIGGERS_PATH, "r", encoding="utf-8") as f:
        TRIGGERS_SCRIPTS = json.load(f)
except Exception as e:
    logger.warning(f"Erro ao carregar triggers: {e}")
    TRIGGERS_SCRIPTS = {}


# =========================
# 🧠 DETECÇÃO DE AÇÃO
# =========================
def detectar_acao(texto):
    texto = texto.lower().strip()

    # 🔹 scripts
    for nome_script, gatilhos in TRIGGERS_SCRIPTS.items():
        for gatilho in gatilhos:
            if gatilho in texto:
                return ("script", nome_script)

    # 🔹 hora
    if "hora" in texto:
        return ("hora", None)

    return (None, None)


# =========================
# ⚙️ EXECUÇÃO DE AÇÃO
# =========================
def executar_acao(tipo, valor):
    if tipo == "hora":
        return ver_hora()

    if tipo == "script":
        return executar_script(valor)

    return {
        "ok": False,
        "acao": tipo,
        "mensagem": "Ação não reconhecida",
        "dados": "",
        "erro": "Ação não cadastrada"
    }


def responder_resultado_feature(resultado):
    """
    Fallback antigo mantido por segurança.
    Se o interpretador falhar, ainda temos uma resposta simples.
    """
    if resultado.get("ok"):

        if resultado.get("acao") == "ver_hora":
            return f"Agora são {resultado['dados']}."

        if resultado.get("acao") == "executar_script":
            if resultado.get("dados"):
                return resultado["dados"]

            return "Script executado com sucesso."

        return "Pronto."

    if resultado.get("erro"):
        return f"Deu problema: {resultado['erro']}"

    return "Não consegui executar isso."


# =========================
# 🌐 ROTAS
# =========================
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json or {}
    mensagem = data.get("mensagem", "")

    tipo, valor = detectar_acao(mensagem)

    if tipo:
        resultado = executar_acao(tipo, valor)

        try:
            resposta = interpretar_resultado_feature(resultado)
        except Exception as e:
            logger.warning(f"Falha no interpretador, usando fallback: {e}")
            resposta = responder_resultado_feature(resultado)

        return jsonify({"resposta": resposta})

    resposta_bruta = perguntar_ollama(mensagem)
    parsed = parse_resposta(resposta_bruta)

    return jsonify({"resposta": parsed.get("resposta", "Entendi.")})


# =========================
# 📍 LOCALIZAÇÃO SERVIDOR
# =========================
@app.route("/api/localizacao/servidor", methods=["GET"])
def localizacao_servidor():
    try:
        response = requests.get(
            "https://ipinfo.io/json",
            timeout=8
        )

        data = response.json()

        return jsonify({
            "ok": True,
            "cidade": data.get("city", ""),
            "estado": data.get("region", ""),
            "pais": data.get("country", ""),
            "mensagem": "Localização do servidor obtida"
        })

    except Exception as e:
        logger.warning(f"Falha ao resolver localização do servidor: {e}")

        return jsonify({
            "ok": False,
            "cidade": "",
            "estado": "",
            "pais": "",
            "mensagem": "Não consegui resolver a localização do servidor"
        })


# =========================
# 📍 LOCALIZAÇÃO DISPOSITIVO
# =========================
@app.route("/api/localizacao/dispositivo", methods=["POST"])
def localizacao_dispositivo():
    data = request.json or {}

    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if latitude is None or longitude is None:
        return jsonify({
            "ok": False,
            "cidade": "",
            "estado": "",
            "pais": "",
            "mensagem": "Localização não recebida"
        })

    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={
                "format": "jsonv2",
                "lat": latitude,
                "lon": longitude,
                "zoom": 10,
                "addressdetails": 1
            },
            headers={
                "User-Agent": "JarvisLocal/1.0"
            },
            timeout=8
        )

        data = response.json()
        address = data.get("address", {})

        cidade = (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or address.get("municipality")
            or ""
        )

        estado = address.get("state", "")
        pais = address.get("country", "")

        return jsonify({
            "ok": True,
            "cidade": cidade,
            "estado": estado,
            "pais": pais,
            "mensagem": "Localização do dispositivo obtida"
        })

    except Exception as e:
        logger.warning(f"Falha ao resolver localização do dispositivo: {e}")

        return jsonify({
            "ok": False,
            "cidade": "",
            "estado": "",
            "pais": "",
            "mensagem": "Não consegui resolver a cidade do dispositivo"
        })


# =========================
# 🚀 START
# =========================
if __name__ == "__main__":
    iniciar_ollama()

    scheduler.adicionar_tarefa(
        nome="monitoramento_sistema",
        intervalo_segundos=30,
        funcao=verificar_status_sistema
    )

    scheduler.iniciar()

    app.run(host="0.0.0.0", port=5000, debug=False)