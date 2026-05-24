import os
import subprocess


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")


SCRIPTS_PERMITIDOS = {
    "limpar_cache": {
        "caminho": os.path.join(SCRIPTS_DIR, "sistema", "limpar_cache.sh"),
        "descricao": "Limpeza simples de cache do sistema"
    },
    "status_sistema": {
        "caminho": os.path.join(SCRIPTS_DIR, "sistema", "status_basico.sh"),
        "descricao": "Status básico do sistema"
    }
}


def executar_script(nome_script):
    script = SCRIPTS_PERMITIDOS.get(nome_script)

    if not script:
        return {
            "ok": False,
            "acao": "executar_script",
            "script": nome_script,
            "mensagem": "Script não permitido",
            "dados": "",
            "erro": "Script não cadastrado na whitelist"
        }

    caminho = script["caminho"]

    if not os.path.exists(caminho):
        return {
            "ok": False,
            "acao": "executar_script",
            "script": nome_script,
            "mensagem": "Script não encontrado",
            "dados": "",
            "erro": f"Arquivo não existe: {caminho}"
        }

    try:
        resultado = subprocess.run(
            ["bash", caminho],
            capture_output=True,
            text=True,
            timeout=60
        )

        if resultado.returncode == 0:
            return {
                "ok": True,
                "acao": "executar_script",
                "script": nome_script,
                "mensagem": "Script executado com sucesso",
                "dados": resultado.stdout.strip(),
                "erro": ""
            }

        return {
            "ok": False,
            "acao": "executar_script",
            "script": nome_script,
            "mensagem": "Script retornou erro",
            "dados": resultado.stdout.strip(),
            "erro": resultado.stderr.strip()
        }

    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "acao": "executar_script",
            "script": nome_script,
            "mensagem": "Script demorou demais",
            "dados": "",
            "erro": "Timeout ao executar script"
        }

    except Exception as e:
        return {
            "ok": False,
            "acao": "executar_script",
            "script": nome_script,
            "mensagem": "Falha inesperada ao executar script",
            "dados": "",
            "erro": str(e)
        }