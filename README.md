# NEXORA-AI

A local-first cybersecurity learning assistant for Android Termux.

NEXORA-AI uses an OpenAI-compatible chat API. It works with a local `llama.cpp` server for offline use or with a trusted online provider.

## Safety

NEXORA-AI is a learning assistant, not a hacking agent. It does not execute shell commands, scans, exploits, or network actions. Only discuss authorized, defensive, and educational cybersecurity work.

## Requirements

- Android device with Termux
- Git
- Python 3
- 4 GB RAM minimum is recommended for small quantized models
- Enough storage for a GGUF model

## Install on Termux

```bash
pkg update && pkg upgrade
pkg install git cmake clang make python
mkdir -p "$HOME/models"
```

Clone this project:

```bash
git clone https://github.com/BENZEX999/NEXORA-AI.git
cd NEXORA-AI
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Offline mode

Build `llama.cpp`:

```bash
git clone https://github.com/ggerganov/llama.cpp "$HOME/llama.cpp"
cmake -S "$HOME/llama.cpp" -B "$HOME/llama.cpp/build" -DGGML_NATIVE=ON
cmake --build "$HOME/llama.cpp/build" --config Release -j2
```

Place a licensed GGUF model in `$HOME/models/assistant.gguf`, then start the server:

```bash
"$HOME/llama.cpp/build/bin/llama-server" \
  --model "$HOME/models/assistant.gguf" \
  --ctx-size 2048 \
  --host 127.0.0.1 \
  --port 8080
```

Keep that session open. In another Termux session:

```bash
cd NEXORA-AI
python nexora.py
```

Use `/help`, `/reset`, or `/quit` in the chat.

## Online mode

Set the provider details in environment variables:

```bash
export NEXORA_ENDPOINT="https://YOUR-TRUSTED-PROVIDER/v1/chat/completions"
export NEXORA_MODEL="YOUR_MODEL_NAME"
export NEXORA_API_KEY="YOUR_API_KEY"
python nexora.py
```

Online mode sends prompts to the selected provider. Never send credentials, private keys, authentication cookies, or sensitive incident data.

## Configuration

- `NEXORA_ENDPOINT`: OpenAI-compatible chat-completions URL
- `NEXORA_MODEL`: provider or local model name
- `NEXORA_API_KEY`: optional bearer token
- `NEXORA_MAX_TURNS`: retained conversation turns; default `8`
- `NEXORA_HISTORY_FILE`: optional JSONL history path
- `NEXORA_SAVE_HISTORY`: set `1` to save conversation history

Example:

```bash
export NEXORA_SAVE_HISTORY=1
export NEXORA_HISTORY_FILE="$HOME/nexora-history.jsonl"
export NEXORA_MAX_TURNS=12
python nexora.py
```

## Security behavior

The assistant does not provide exploit instructions or operational intrusion guidance. If it detects suspicious intent, it redirects to defensive alternatives such as lab environments, threat modeling, detection engineering, hardening, or incident response.

## License

Add an OSI-approved license before publishing a software distribution.
