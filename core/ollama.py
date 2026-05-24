import requests
import subprocess
import time
import os

from core.config import (
    OLLAMA_BASE_URL,
    OLLAMA_GENERATE_URL,
    MODEL,
    SYSTEM_PROMPT_PATH,
    REQUEST_TIMEOUT,
    MODEL_OPTIONS,
    KEEP_ALIVE,
    WARMUP_MESSAGE
)

from core.logger import logger


MAX_TENTATIVAS = 3
INTERVALO_TENTATIVA = 1  # segundos


# =========================
# 🚀 INICIAR OLLAMA
# =========================
def iniciar_ollama():
    try:
        requests.get(OLLAMA_BASE_URL, timeout=2)
        print("✅ Ollama já está rodando")
    except:
        print("🚀 Iniciando Ollama...")

        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        for _ in range(15):
            try:
                requests.get(OLLAMA_BASE_URL, timeout=2)
                print("✅ Ollama iniciado")
                break
            except:
                time.sleep(1)
        else:
            print("❌ Não consegui iniciar o Ollama")
            exit()

    # 🔥 Warm-up sempre roda (mesmo se já estiver ativo)
    warmup_model()


# =========================
# 🔥 WARM-UP
# =========================
def warmup_model():
    try:
        print("🔥 Aquecendo modelo...")

        requests.post(
            OLLAMA_GENERATE_URL,
            json={
                "model": MODEL,
                "prompt": WARMUP_MESSAGE,
                "stream": False,
                "keep_alive": KEEP_ALIVE,
                "options": {
                    **MODEL_OPTIONS,
                    "temperature": 0
                }
            },
            timeout=10
        )

        print("✅ Modelo aquecido")

    except Exception as e:
        logger.warning(f"Warmup falhou: {e}")


# =========================
# 📄 PROMPT SISTEMA
# =========================
def carregar_prompt_sistema():
    if os.path.exists(SYSTEM_PROMPT_PATH):
        with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read()
    return "Você é um assistente."


# =========================
# 🧠 PERGUNTAR OLLAMA
# =========================
def perguntar_ollama(texto_usuario: str) -> str:
    prompt_sistema = carregar_prompt_sistema()
    prompt_final = f"{prompt_sistema}\nUsuário: {texto_usuario}"

    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            response = requests.post(
                OLLAMA_GENERATE_URL,
                json={
                    "model": MODEL,
                    "prompt": prompt_final,
                    "stream": False,
                    "keep_alive": KEEP_ALIVE,  # 🔥 chave da performance
                    "options": MODEL_OPTIONS
                },
                timeout=REQUEST_TIMEOUT
            )

            data = response.json()
            return data.get("response", "")

        except requests.exceptions.Timeout:
            logger.warning(
                f"Ollama timeout tentativa {tentativa}/{MAX_TENTATIVAS}"
            )

        except requests.exceptions.ConnectionError:
            logger.warning(
                f"Ollama conexão falhou tentativa {tentativa}/{MAX_TENTATIVAS}"
            )

        except Exception as e:
            logger.error(f"Ollama erro inesperado: {e}")
            break

        if tentativa < MAX_TENTATIVAS:
            time.sleep(INTERVALO_TENTATIVA)

    logger.error("Ollama falhou após todas as tentativas")

    return '{"tipo":"chat","resposta":"Não consegui processar isso agora. O modelo demorou demais."}'