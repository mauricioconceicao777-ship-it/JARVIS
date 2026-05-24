from core.logger import logger
from features.scripts import executar_script


def verificar_status_sistema():
    resultado = executar_script("status_sistema")

    if not resultado.get("ok"):
        logger.warning(
            f"Monitoramento: falha ao verificar sistema: {resultado.get('erro')}"
        )
        return

    dados = resultado.get("dados", "")

    logger.info(f"Monitoramento: status do sistema verificado | {dados}")