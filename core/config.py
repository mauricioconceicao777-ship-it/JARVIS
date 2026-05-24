import os

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_GENERATE_URL = f"{OLLAMA_BASE_URL}/api/generate"

MODEL = "phi3:latest"

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPTS_DIR = os.path.join(PROJECT_ROOT, "prompts")
SYSTEM_PROMPT_PATH = os.path.join(PROMPTS_DIR, "system.txt")

REQUEST_TIMEOUT = 80

# Mantém o modelo carregado no Ollama por mais tempo
KEEP_ALIVE = "30m"

# Mensagem pequena usada para aquecer o modelo ao iniciar
WARMUP_MESSAGE = "ok"

MODEL_OPTIONS = {
    "temperature": 0.2,
    "num_predict": 120
}

THINKING_DELAY_SECONDS = 2.5

THINKING_PHRASES = [
    "Hmm... deixa eu pensar...",
    "Só um instante...",
    "Pensando aqui...",
    "Boa pergunta...",
    "Calma aí..."
]