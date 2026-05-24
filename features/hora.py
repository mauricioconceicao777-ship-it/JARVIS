from datetime import datetime


def ver_hora():
    try:
        agora = datetime.now()

        hora_formatada = agora.strftime("%H:%M")

        return {
            "ok": True,
            "acao": "ver_hora",
            "mensagem": "Hora obtida com sucesso",
            "dados": hora_formatada,
            "erro": ""
        }

    except Exception as e:
        return {
            "ok": False,
            "acao": "ver_hora",
            "mensagem": "Falha ao obter hora",
            "dados": "",
            "erro": str(e)
        }