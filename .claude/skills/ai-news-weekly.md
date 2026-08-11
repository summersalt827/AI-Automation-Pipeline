# AI News 周报 — 全流程自动化 Skill

一句话：从邮箱拉取 AI 新闻邮件，全网聚合增强，Claude 精选 6-8 条 + 3 GitHub 项目，生成小红书卡片+封面+视频。

## 触发词

- "AI news"
- "跑 AI News"
- "生成周报"

## 全流程（10 步）

### Step 1: 拉取邮件
- IMAP 连接 163 邮箱，搜索近 7 天标题含 `[AINews]` 的邮件
- 如果没有当天邮件，自动往前追溯到最近一封未处理的
- 提取邮件正文（HTML → 纯文本）

### Step 2: 翻译
- Claude 翻译邮件正文，中英对照格式
- 保留原文关键术语不翻译

### Step 3: 外部增强
- Bing 搜索 + HN (Algolia API) + ArXiv (Atom) + Twitter/X (Nitter → Bing fallback)
- 5 层信源优先级：官方公告 → benchmark → KOL → 企业案例 → 反方声音
- 各源独立抓取，失败静默跳过

### Step 4: 精选 (Curation)
- Claude 从全源中精选 6-8 条，按分类组织：
  - 模型&研究 (2-3 条)
  - 产品&工具 (2 条)
  - 行业&政策 (1-2 条)
- 准入门槛：≥2 个独立信源，或 HN 50+ 分
- 去重：中英文关键词加权重叠检测，加权 ≥4 的不重复发
- 权重参考 `preferences.md`：Agent/MCP > Web3+AI > 工作流 > 开源模型 > AI 产品 UX

### Step 5: GitHub Trending
- GitHub Search API，近 7 天 star 增速最快
- 选出 3 条标记"本周必看"
- 权重最高（有代码 = 有真相）

### Step 6: 用户审核 ⚠️
- **必须停下来**，打印标题+摘要等待用户确认
- 用户确认后才进入渲染环节

### Step 7: 卡片生成
- 设计文档风（design-doc style），深蓝 `#124783` + 墨绿 `#1ca77a`
- 每张卡片 3 层 info-card：发生了什么 / 深入了解一下 / 为什么值得关注
- "记住三点" + Insight Box 收尾
- GitHub 类型用绿色系（`#e8f5e9` 背景）
- Chrome headless 截图：1080×1440 @2x = 2160×2880 PNG
- 输出到 `xiaohongshu/<YYYY-MM-DD>/`

### Step 8: 封面生成
- 2×2 网格封面
- 双平台：小红书 3:4 (1080×1440) + B站 16:9 (1920×1080)
- Sci-Fi Dark 风格（`#050510` 背景，青紫霓虹渐变）
- @2x 截图

### Step 9: 文案
- `combined_caption.txt` — 小红书文案
- `bilibili_caption.txt` — B站文案
- 标题取邮件原始 subject，内容大白话风格

### Step 10: 发布（当前手动）
- 小红书自动发布已禁用（账号被封）
- 卡片和文案输出到日期目录，手动上传

## 环境变量

| 变量 | 说明 |
|------|------|
| `EMAIL_163_USER` / `EMAIL_163_PASS` | 163 邮箱 IMAP |
| `ANTHROPIC_API_KEY` | API key |
| `ANTHROPIC_BASE_URL` | `https://api.deepseek.com/anthropic` |
| `ANTHROPIC_MODEL` | `deepseek-v4-pro[1m]` |
| `GITHUB_TOKEN` | GitHub API（可选，提频） |

## 运行

```bash
cd ~/Desktop/AI\ news\ \&\ skills/AI-news/ai-news-xiaohongshu
python3 news_pipeline/fetch_ai_news.py
```

## 视频（可选）

周报视频：纯录屏+旁白，真人不入镜，花叔v 风格。
裁剪→字幕→Zoom→BGM→9:16 转换，详见 `video-editing-sop` memory。
