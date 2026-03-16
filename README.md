# 日语学习每日推送系统 🇯🇵

自动化日语学习内容生成与推送系统，结合二次元文化和日本旅行场景，让学习更有趣！

## 功能特性

- 📚 **自动读取课程大纲**：从 `syllabus.json` 读取每日学习内容
- 🤖 **AI 生成教学内容**：调用 LLM API 生成生动的 Markdown 学习资料
- 📱 **飞书群组推送**：自动推送到飞书群组 Webhook
- 📊 **学习进度追踪**：自动维护当前学习天数
- ⚙️ **GitHub Actions 自动化**：每日定时自动推送
- 🛡️ **健壮的错误处理**：失败时不累加天数，保证进度准确

## 项目结构

```
japanese_daily/
├── syllabus.json          # 课程大纲（90天内容）
├── daily_push.py          # 主推送脚本
├── config.example.py      # 配置文件示例
├── config.py              # 实际配置文件（需自行创建）
├── current_day.txt        # 当前学习天数（自动维护）
├── requirements.txt       # Python 依赖
├── daily_push.log         # 运行日志
└── .github/
    └── workflows/
        └── daily_push.yml # GitHub Actions 配置
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置设置

复制配置文件模板并填入你的配置：

```bash
cp config.example.py config.py
```

编辑 `config.py`，填入以下信息：

```python
# LLM API 配置
LLM_API_BASE = "https://api.openai.com/v1"  # 你的 API Base URL
LLM_API_KEY = "your-api-key-here"           # 你的 API Key
LLM_MODEL = "gpt-4o-mini"                   # 使用的模型

# 飞书 Webhook 配置
FEISHU_WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
```

### 3. 手动测试运行

```bash
python daily_push.py
```

### 4. GitHub Actions 自动推送

#### 4.1 设置 Secrets

在你的 GitHub 仓库中设置以下 Secrets（Settings → Secrets and variables → Actions）：

| Secret 名称 | 说明 | 示例 |
|------------|------|------|
| `LLM_API_BASE` | LLM API Base URL | `https://api.openai.com/v1` |
| `LLM_API_KEY` | LLM API Key | `sk-xxxxx` |
| `LLM_MODEL` | 使用的模型 | `gpt-4o-mini` |
| `FEISHU_WEBHOOK_URL` | 飞书群组 Webhook URL | `https://open.feishu.cn/...` |

#### 4.2 启用 Actions

推送代码到 GitHub 后，Actions 将自动按照配置的定时任务执行。

默认：每天 UTC 0:00（北京时间 8:00）自动推送。

修改推送时间，编辑 `.github/workflows/daily_push.yml` 中的 `cron` 表达式。

## 课程大纲格式

`syllabus.json` 格式示例：

```json
[
  {
    "day": 1,
    "lesson": 0,
    "words": ["あ", "い", "う", "え", "お"],
    "grammar": "五十音图（元音）"
  },
  {
    "day": 2,
    "lesson": 0,
    "words": ["か", "き", "く", "け", "こ"],
    "grammar": "五十音图（清音与浊音）"
  }
]
```

## 教学内容示例

生成的学习内容包括：

- 📅 **今日语法点**
- 🎯 **词汇讲解**（带二次元/旅行场景例句）
- 📝 **语法详解**（动漫/旅行实际应用）
- 🎮 **实战演练**（趣味小题）
- 💡 **知识点**（文化小知识或学习技巧）

## 状态管理

- `current_day.txt` 记录当前学习天数
- 只有推送成功后才更新天数
- 失败时不累加，保证学习进度准确
- 完成所有课程后会发送完成提醒

## 日志

运行日志保存在 `daily_push.log`，包含：
- ✓ 配置加载状态
- ✓ API 调用详情
- ✓ 推送结果
- ✗ 错误信息

## 飞书推送效果

推送消息以飞书卡片形式展示，包含：
- 蓝色标题栏
- Markdown 格式的学习内容
- 推送时间戳

## 故障排查

### 问题：API 调用失败
- 检查 `LLM_API_KEY` 是否正确
- 确认 `LLM_API_BASE` 可访问
- 查看日志文件了解详细错误

### 问题：飞书推送失败
- 确认 Webhook URL 有效
- 检查飞书机器人是否有权限
- 查看日志文件了解详细错误

### 问题：GitHub Actions 失败
- 确认所有 Secrets 已正确设置
- 查看 Actions 运行日志
- 检查代码语法是否正确

## 自定义配置

### 修改推送时间

编辑 `.github/workflows/daily_push.yml`：

```yaml
schedule:
  - cron: '0 0 * * *'  # 修改此处的 cron 表达式
```

### 修改 Prompt 模板

编辑 `config.py` 中的 `SYSTEM_PROMPT`，自定义教学内容格式。

### 手动触发推送

在 GitHub Actions 页面，点击 "Run workflow" 手动执行。

## License

MIT
