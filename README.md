# Local Meeting Summary Tools

本地会议转录与摘要工具 - 实时会议录音、AI 驱动会议纪要生成。

## 功能特点

- 实时音频采集与转录
- AI 自动生成会议摘要、要点和行动项
- 多 LLM 支持（Ollama / Gemini / 通义千问）
- 中英文双语界面

## 快速开始

### 1. 安装系统依赖（Raspberry Pi OS）

```bash
# 安装 Node.js
sudo apt update
sudo apt install -y nodejs npm

# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.local/bin/env
```

### 2. 安装项目依赖

```bash
uv sync
```

### 3. 配置

```bash
cp config.example.yaml config.yaml
```

编辑 `config.yaml`，填写数据库连接和 LLM API 密钥。

### 4. 启动

```bash
./dev.sh
```

访问 http://localhost:5173

## API 文档

启动后访问 http://localhost:5173/docs

## 许可证

MIT License
