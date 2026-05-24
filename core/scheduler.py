import threading
import time

from core.logger import logger


class Scheduler:
    def __init__(self):
        self.tarefas = []
        self.rodando = False
        self.thread = None

    def adicionar_tarefa(self, nome, intervalo_segundos, funcao):
        self.tarefas.append({
            "nome": nome,
            "intervalo": intervalo_segundos,
            "funcao": funcao,
            "ultima_execucao": 0
        })

        logger.info(f"Scheduler: tarefa registrada: {nome}")

    def iniciar(self):
        if self.rodando:
            return

        self.rodando = True

        self.thread = threading.Thread(
            target=self._loop,
            daemon=True
        )

        self.thread.start()
        logger.info("Scheduler iniciado")

    def parar(self):
        self.rodando = False
        logger.info("Scheduler parado")

    def _loop(self):
        while self.rodando:
            agora = time.time()

            for tarefa in self.tarefas:
                tempo_passado = agora - tarefa["ultima_execucao"]

                if tempo_passado >= tarefa["intervalo"]:
                    try:
                        tarefa["funcao"]()
                        tarefa["ultima_execucao"] = agora

                    except Exception as e:
                        logger.error(
                            f"Erro na tarefa agendada '{tarefa['nome']}': {e}"
                        )

            time.sleep(1)


scheduler = Scheduler()