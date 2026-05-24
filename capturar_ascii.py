import subprocess
import time
import json
import re

DURACAO = 12
URL = "ascii.live/earth"
SAIDA = "earth_frames.json"

print("Capturando animação...")

proc = subprocess.Popen(
    ["curl", "-s", URL],
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL
)

inicio = time.time()
buffer = b""

while time.time() - inicio < DURACAO:
    chunk = proc.stdout.read(4096)
    if not chunk:
        break
    buffer += chunk

proc.kill()

texto = buffer.decode("utf-8", errors="ignore")

partes = re.split(r"\x1b\[2J|\x1b\[H|\x1bc", texto)

frames = []

for parte in partes:
    limpo = re.sub(r"\x1b\[[0-9;?]*[A-Za-z]", "", parte)

    linhas = limpo.splitlines()

    # remove só linhas totalmente vazias no começo/fim,
    # mas preserva espaços laterais importantes
    while linhas and linhas[0].strip() == "":
        linhas.pop(0)

    while linhas and linhas[-1].strip() == "":
        linhas.pop()

    if not linhas:
        continue

    frame = "\n".join(linhas)

    if len(frame) > 100:
        frames.append(frame)

frames_unicos = []
vistos = set()

for frame in frames:
    if frame not in vistos:
        frames_unicos.append(frame)
        vistos.add(frame)

with open(SAIDA, "w", encoding="utf-8") as f:
    json.dump(frames_unicos, f, ensure_ascii=False, indent=2)

print(f"Frames capturados: {len(frames_unicos)}")
print(f"Salvo em: {SAIDA}")