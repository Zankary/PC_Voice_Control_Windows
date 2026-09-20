# PC Voice Control — Windows

Assistente de voz local em Python para executar comandos no computador.

## O que esta versão faz

Depois de iniciar o programa, fale:

- `PC, mute Discord`
- `PC, desmute Discord`
- `PC, pausa`
- `PC, play`
- `PC, aumenta o volume`
- `PC, diminui o volume`
- `PC, mutar volume`

O programa usa **faster-whisper** para reconhecer a voz localmente.

### Importante sobre o Discord

O programa envia ` ' `.

No Discord, configure esse atalho em:

**Configurações → Atalhos de teclado → Adicionar um atalho → Silenciar**

Escolha ` ' ` como atalho global.

Assim, o comando de voz não depende de o Discord estar com o foco.

## Instalação

Recomenda-se Python 3.11 ou 3.12 no Windows.

Abra o PowerShell dentro desta pasta:

```powershell
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Depois execute:

```powershell
python pc_voice_control.py
```

Na primeira execução, o faster-whisper poderá baixar o modelo `tiny`.
Isso é normal. Depois o modelo fica armazenado localmente.

## Microfone

O programa usa o microfone padrão do Windows.

Se quiser verificar qual dispositivo está sendo usado:

```powershell
python -c "import sounddevice as sd; print(sd.query_devices())"
```

## Como funciona

```text
Microfone
   ↓
faster-whisper
   ↓
"PC, mute Discord"
   ↓
palavra de ativação = PC
   ↓
comando = mute Discord
   ↓
Ctrl + Shift + M
   ↓
Discord mutado
```

## Melhorias futuras

Esta é a primeira versão. Dá para adicionar:

- palavra de ativação dedicada ("Jarvis", "Computador", etc.)
- resposta por voz ("Discord mutado")
- abrir/fechar programas
- comandos para jogos
- atalhos personalizados
- controle de Spotify/YouTube
- executar scripts Python
- comandos com parâmetros ("volume 30%")
- interface gráfica
- iniciar automaticamente com o Windows
- reconhecimento mais rápido usando GPU
- modo de escuta contínua com menos consumo de CPU

## Observação sobre privacidade

O reconhecimento é feito localmente pelo faster-whisper depois que o modelo está instalado. O script não envia o áudio para uma API de reconhecimento de voz.
