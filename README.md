# Local Meeting Summary Tools

Local meeting transcription and summarization tool - Real-time meeting recording with AI-powered meeting minutes generation.

## Features

- Real-time audio capture and transcription
- AI-powered automatic generation of meeting summaries, key points, and action items
- Multiple LLM support (Ollama / Gemini / Qwen)
- Bilingual interface (Chinese / English)

## Quick Start

### 1. Install System Dependencies (Raspberry Pi OS)

```bash
# Install Node.js
sudo apt update
sudo apt install -y nodejs npm

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # Reload environment variables, or reopen terminal
```

### 2. Install Project Dependencies

```bash
uv sync
```

### 3. Configuration

```bash
cp config.example.yaml config.yaml
```

Edit `config.yaml` to configure database connection and LLM API keys.

### 4. Start the Application

```bash
./dev.sh
```

Visit http://localhost:5173

## API Documentation

After starting, visit http://localhost:5173/docs

## License

MIT License
