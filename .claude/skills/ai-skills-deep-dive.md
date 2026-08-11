# AI Skills 深度内容 — 单主题长图文 Skill

一句话：选一个 AI 深度话题，生成 6 张紫色 AI Skills 风格小红书长图文卡片。

## 触发词

- "AI Skills"
- "做一个深度选题"
- "生成 AI Skills 卡片"
- "生成 AI 内容工厂卡片"

## AI Skills vs AI News

| | AI News 周报 | AI Skills 深度 |
|------|------------|-------------|
| 频率 | 每周日 | 手动触发 |
| 内容 | 6-8 条新闻精选 | 单主题深度展开 |
| 风格 | 设计文档风（深蓝+墨绿） | 紫色 AI Skills（`#5B4FE9`） |
| 卡片数 | 6-8 张 + 封面 | 6 张（cover + p1~p5） |
| 模板 | `render_combined.py` | `template-ai-skills.html` |

## 全流程（7 步）

### Step 1: 选题
- Claude 从全网抓取 + 邮件内容中选一个深度话题
- 标准：有实操价值、可拆解为步骤、单篇能讲透
- 话题方向参考 `preferences.md`：Agent/MCP > Web3+AI > 工作流 > 开源 > UX

### Step 2: 内容结构设计
按 6 张卡片结构组织内容：

| 卡片 | 内容 | 目的 |
|------|------|------|
| cover | 主题标题 + 一句话 hook + 管道预览 | 吸引点击 |
| p1 | 概念解释 (What + Why) | 建立认知 |
| p2 | 步骤拆解 (How, 3-5 步) | 实操引导 |
| p3 | 关键要素 (架构/对比/选择) | 加深理解 |
| p4 | 实战经验 + 案例 | 建立信任 |
| p5 | 总结 + 金句 + 行动建议 | 收尾转化 |

### Step 3: 卡片生成
- 紫色 AI Skills 风格：主色 `#5B4FE9`，暖白底 `#faf9f5`，Inter 字体
- 组件库：steps-box、compare-row、insight-box、code-block、choices 等
- Chrome headless 截图：1080×1440 @2x = 2160×2880 PNG
- **尺寸铁律**：永远 1080×1440，不接受其他尺寸

### Step 4: 封面
- AI Skills 标准封面：1080×1440，紫色顶条，圆形头像居中，2×2 grid
- 与 AI News 日报封面风格完全不同

### Step 5: 文案
- Markdown 格式 `xhs-skill-caption.md`
- 结构：hook → 概念解释 → 步骤拆解 → 关键要素 → 实战经验 → 金句收尾 → 关注引导 → 标签

### Step 6: 发布
- 卡片在 `xiaohongshu/<YYYY-MM-DD>/` 目录
- 文件名：`xhs-skill-cover.png` + `xhs-skill-p1.png` ~ `p5.png`
- 文案：`xhs-skill-caption.md` + `xhs-skill-caption.txt`

### Step 7: 产出物输出
- 所有 PNG/PDF 自动 copy 到 Desktop 带日期的文件夹

## 设计系统

```css
:root {
  --bg: #faf9f5;           /* 暖白底 */
  --card: #ffffff;         /* 卡片底 */
  --ink: #1a1a1a;          /* 主文字 */
  --soft: #6b6b6b;         /* 辅助文字 */
  --accent: #5B4FE9;       /* 紫色强调 */
  --line: #e7e4de;         /* 分割线 */
}
字体: Inter (标题), PingFang SC (正文)
卡片尺寸: 1080×1440px, 截图 @2x = 2160×2880px
```

## 组件库（按需拼装）

| 组件 | 用途 |
|------|------|
| `title-block` | 英文大标题 + 下划线 |
| `cn-block` | 中文副标题，关键词 accent 色高亮 |
| `compare-row` | 双栏对比（浅色 / accent 实色） |
| `steps-list` | 圆形编号 + 步骤文字 |
| `layers` | 编号圆 + 标题 + 灰色描述 |
| `insight-box` | 顶部分割线 + 金句 |
| `engines` | 双栏引擎预览 |
| `code-block` | 深色底代码块 |
| `choices` | 双栏选择卡片 |

## YouTube/播客蒸馏变体

触发：提供 YouTube URL 或播客链接。

```bash
python3 news_pipeline/youtube_to_xhs.py "<url>"
```

流程：yt-dlp 下载 → Whisper 转录 → Claude 蒸馏为 4 张卡片 → 渲染 PNG。

**必须用紫色 AI Skills 模板**，不能混用 AI News 日报风格。

## 品牌收尾

所有卡片/文案结尾统一用 IP 名：**小H的AI进化论**
