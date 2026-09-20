"""
PC Voice Control - assistente de voz local para Windows.

Comandos:
    "PC, mute Discord"
    "PC, desmute Discord"
    "PC, pausa"
    "PC, play"
    "PC, volume mais"
    "PC, volume menos"
    "PC, mutar volume"
    "PC, desmutar volume"

O reconhecimento usa faster-whisper e roda localmente depois que o modelo
é baixado na primeira execução.
"""

import ctypes
import queue
import re
import sys
import time
from threading import Thread

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel


# =========================
# CONFIGURAÇÃO
# =========================

WAKE_WORDS = ("pc", "p c")
MODEL_SIZE = "tiny"       # tiny = mais leve; base = melhor reconhecimento
SAMPLE_RATE = 16000
CHUNK_SECONDS = 3.0
COMMAND_TIMEOUT = 5.0

# Atalho configurado no Discord para "Mute/Unmute":
DISCORD_MUTE_HOTKEY = ("'")


# =========================
# WINDOWS / TECLAS
# =========================

user32 = ctypes.windll.user32

VK_MEDIA_PLAY_PAUSE = 0xB3
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF

KEYEVENTF_KEYUP = 0x0002


def press_vk(vk):
    user32.keybd_event(vk, 0, 0, 0)
    user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)


def media_play_pause():
    press_vk(VK_MEDIA_PLAY_PAUSE)


def volume_up():
    press_vk(VK_VOLUME_UP)


def volume_down():
    press_vk(VK_VOLUME_DOWN)


def volume_mute():
    press_vk(VK_VOLUME_MUTE)


def hotkey_ctrl_shift_m():
    # Envia Ctrl+Shift+M para a janela ativa.
    # Para o Discord, o ideal é configurar esse mesmo atalho como
    # atalho global de mute.
    import keyboard
    keyboard.press_and_release("ctrl+shift+m")


# =========================
# INTERPRETAÇÃO
# =========================

def normalize(text):
    text = text.lower().strip()
    text = text.replace("-", " ")
    text = re.sub(r"\s+", " ", text)
    return text


def has_wake_word(text):
    text = normalize(text)
    return any(
        re.search(rf"\b{re.escape(word)}\b", text)
        for word in WAKE_WORDS
    )


def command_after_wake_word(text):
    text = normalize(text)
    for word in WAKE_WORDS:
        match = re.search(rf"\b{re.escape(word)}\b", text)
        if match:
            return text[match.end():].strip()
    return ""


def execute_command(command):
    command = normalize(command)

    # Discord
    if ("discord" in command and
        any(x in command for x in ("mute", "mutar", "silenciar", "mudo"))):
        print("  -> Discord: MUTE")
        hotkey_ctrl_shift_m()
        return True

    if ("discord" in command and
        any(x in command for x in ("desmute", "desmutar", "ativar microfone",
                                    "tirar do mudo"))):
        print("  -> Discord: DESMUTE")
        hotkey_ctrl_shift_m()
        return True

    # Play / pause
    if any(x in command for x in (
        "pausa", "pause", "parar vídeo", "parar video",
        "pausar", "play", "continuar", "continua"
    )):
        print("  -> PLAY/PAUSE")
        media_play_pause()
        return True

    # Volume
    if any(x in command for x in (
        "aumentar volume", "volume mais", "volume acima",
        "aumenta o volume", "mais volume"
    )):
        print("  -> VOLUME +")
        volume_up()
        return True

    if any(x in command for x in (
        "diminuir volume", "volume menos", "volume abaixo",
        "diminui o volume", "menos volume"
    )):
        print("  -> VOLUME -")
        volume_down()
        return True

    if any(x in command for x in (
        "mutar volume", "mute volume", "silenciar computador",
        "mutar computador"
    )):
        print("  -> VOLUME MUTE")
        volume_mute()
        return True

    return False


# =========================
# ÁUDIO
# =========================

audio_queue = queue.Queue()


def audio_callback(indata, frames, time_info, status):
    if status:
        print(f"[áudio] {status}", file=sys.stderr)
    audio_queue.put(indata[:, 0].copy())


def record_chunk():
    pieces = []
    required = int(SAMPLE_RATE * CHUNK_SECONDS)
    total = 0

    while total < required:
        try:
            piece = audio_queue.get(timeout=CHUNK_SECONDS + 1)
        except queue.Empty:
            return None

        pieces.append(piece)
        total += len(piece)

    return np.concatenate(pieces).astype(np.float32)


def transcribe(model, audio):
    segments, _ = model.transcribe(
        audio,
        language="pt",
        beam_size=1,
        best_of=1,
        temperature=0,
        vad_filter=True,
        condition_on_previous_text=False,
    )
    return " ".join(segment.text for segment in segments).strip()


# =========================
# LOOP PRINCIPAL
# =========================

def main():
    print("=" * 60)
    print(" PC VOICE CONTROL")
    print("=" * 60)
    print(f"Modelo: {MODEL_SIZE}")
    print("Diga: 'PC, mute Discord' ou 'PC, pausa'")
    print("Ctrl+C para sair.")
    print()
    print("Carregando modelo... (na primeira vez pode baixar alguns arquivos)")

    model = WhisperModel(
        MODEL_SIZE,
        device="cpu",
        compute_type="int8",
    )

    print("Modelo carregado.")
    print("Microfone ativo.")
    print()

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        blocksize=1600,
        callback=audio_callback,
    ):
        while True:
            audio = record_chunk()

            if audio is None:
                continue

            text = transcribe(model, audio)

            if not text:
                continue

            print(f"[ouvi] {text}")

            if has_wake_word(text):
                command = command_after_wake_word(text)

                if command:
                    print(f"[comando] {command}")

                    if not execute_command(command):
                        print("  -> Comando não reconhecido.")

            time.sleep(0.05)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nEncerrado.")
    except Exception as exc:
        print("\nERRO:")
        print(exc)
        print("\nConfira o README.txt para instalação.")
        input("\nPressione ENTER para sair...")
