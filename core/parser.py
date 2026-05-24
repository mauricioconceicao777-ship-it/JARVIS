import json

def extrair_json(texto: str) -> str:
    if not texto:
        return ""

    texto = texto.strip()
    texto = texto.replace("```json", "").replace("```", "").strip()

    inicio = texto.find("{")
    fim = texto.rfind("}")

    if inicio == -1 or fim == -1 or fim <= inicio:
        return ""

    return texto[inicio:fim + 1]


def parse_resposta(texto: str) -> dict:
    """
    Tenta extrair e parsear o JSON.
    Nunca quebra o fluxo: sempre retorna um dict válido.
    """
    bruto = extrair_json(texto)

    if not bruto:
        return {
            "tipo": "chat",
            "resposta": "Não consegui entender direito 😅"
        }

    try:
        data = json.loads(bruto)

        if "tipo" not in data:
            data["tipo"] = "chat"

        if "resposta" not in data:
            data["resposta"] = "Entendi."

        return data

    except Exception:
        return {
            "tipo": "chat",
            "resposta": "Deu um erro ao interpretar 😅"
        }