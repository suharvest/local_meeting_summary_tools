# Local Meeting Summary Tools

本地会议转录与摘要工具 - 一个用于实时会议录音、转录和 AI 驱动会议纪要生成的 Web 应用。

## 功能特点

- **实时音频采集** - 支持选择麦克风设备进行会议录音
- **AI 会议摘要** - 自动生成会议总结、要点和行动项
- **多 LLM 支持** - 支持 Ollama、Google Gemini、阿里云通义千问
- **流式输出** - 实时显示 AI 生成内容
- **双语支持** - 中文/英文界面切换
- **会议历史** - 保存和查看历史会议记录

## 技术栈

**后端:**
- Python 3.12+
- FastAPI
- aiomysql
- uv (包管理)

**前端:**
- Vue.js 3
- Tailwind CSS
- Vite

**LLM 提供商:**
- Ollama (本地部署)
- Google Gemini
- 阿里云通义千问 (Qwen)

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/suharvest/local_meeting_summary_tools.git
cd local_meeting_summary_tools
```

### 2. 安装依赖

确保已安装 [uv](https://github.com/astral-sh/uv) 和 [Node.js](https://nodejs.org/)。

```bash
# 安装 Python 依赖
uv sync

# 安装前端依赖
cd frontend && npm install && cd ..
```

### 3. 配置

复制配置模板并填写你的配置：

```bash
cp config.example.yaml config.yaml
```

编辑 `config.yaml`，配置数据库连接和 LLM API 密钥：

```yaml
database:
  host: "your_database_host"
  port: 3306
  user: "your_username"
  password: "your_password"
  database: "your_database_name"

llm:
  default_provider: "qwen"  # 可选: gemini, qwen, ollama
  providers:
    gemini:
      api_key: "YOUR_GEMINI_API_KEY"
    qwen:
      api_key: "YOUR_QWEN_API_KEY"
    ollama:
      base_url: "http://localhost:11434"
      model: "llama3.2"
```

### 4. 启动服务

使用开发脚本一键启动：

```bash
./dev.sh
```

或手动启动：

```bash
# 构建前端
cd frontend && npm run build && cd ..

# 启动服务
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 5173
```

### 5. 访问应用

- **Web 界面:** http://localhost:5173
- **API 文档:** http://localhost:5173/docs

## 项目结构

```
local_meeting_summary_tools/
├── backend/                 # 后端代码
│   ├── api/                # API 路由
│   │   ├── devices.py      # 设备管理接口
│   │   └── meetings.py     # 会议管理接口
│   ├── llm/                # LLM 集成
│   │   ├── factory.py      # LLM 工厂类
│   │   ├── gemini.py       # Gemini 实现
│   │   ├── ollama.py       # Ollama 实现
│   │   └── qwen.py         # 通义千问实现
│   ├── services/           # 业务服务
│   ├── config.py           # 配置加载
│   ├── database.py         # 数据库连接
│   └── main.py             # 应用入口
├── frontend/               # 前端代码 (Vue.js)
│   ├── src/
│   │   ├── components/     # Vue 组件
│   │   ├── composables/    # 组合式函数
│   │   ├── locales/        # 国际化文件
│   │   └── api/            # API 调用
│   └── ...
├── prompts/                # LLM 提示词模板
├── output/                 # 会议纪要输出目录
├── config.example.yaml     # 配置模板
├── dev.sh                  # 开发启动脚本
└── pyproject.toml          # Python 项目配置
```

## API 接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/devices` | GET | 获取音频设备列表 |
| `/api/meetings` | GET | 获取会议列表 |
| `/api/meetings` | POST | 创建新会议 |
| `/api/meetings/{id}` | GET | 获取会议详情 |
| `/api/meetings/{id}/summary` | POST | 生成会议摘要 |

完整 API 文档请访问 `/docs`。

## 许可证

MIT License
