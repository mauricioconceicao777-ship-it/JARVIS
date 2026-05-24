import time
import threading
import random
import sys

from core.config import THINKING_DELAY_SECONDS, THINKING_PHRASES


SPINNER_FRAMES = ["🌍", "🌎", "🌏"]


def _animar_pensando(delay, stop_event):
    time.sleep(delay)

    if stop_event.is_set():
        return

    frase = random.choice(THINKING_PHRASES)
    i = 0

    while not stop_event.is_set():
        frame = SPINNER_FRAMES[i % len(SPINNER_FRAMES)]
        sys.stdout.write(f"\rJarvis: {frame} {frase}")
        sys.stdout.flush()

        i += 1
        time.sleep(0.35)

    # limpa a linha antes da resposta final
    sys.stdout.write("\r" + " " * 80 + "\r")
    sys.stdout.flush()


def iniciar_thinking():
    stop_event = threading.Event()

    thread = threading.Thread(
        target=_animar_pensando,
        args=(THINKING_DELAY_SECONDS, stop_event),
        daemon=True
    )

    thread.start()

    return {
        "stop_event": stop_event,
        "thread": thread
    }


def parar_thinking(thinking_control):
    if not thinking_control:
        return

    stop_event = thinking_control.get("stop_event")
    thread = thinking_control.get("thread")

    if stop_event:
        stop_event.set()

    if thread:
        thread.join(timeout=0.5)