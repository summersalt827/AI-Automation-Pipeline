---
name: 风格参考提取
description: 用户在小红书或其他平台看到好的卡片/封面样式，截图发给你并说「参考这个样式」时，提取设计 Token → 识别组件 → 生成参考 HTML → 套用到实际内容。触发词："参考这个样式"、"学习这个风格"、"提取这个设计"。
---

# Style Reference Skill

当用户在小红书或其他平台看到好的卡片/封面样式，截图发给你并说「参考这个样式」时，执行以下流程。

## 触发词

- "参考这个样式"
- "学习这个风格"
- "用这个风格套到 X 内容上"
- "提取这个设计"

## 工作流

### Step 1: 提取设计 Token

从截图中提取 CSS 变量：
```css
:root {
  --bg: #xxx; --card: #xxx; --ink: #xxx;
  --soft: #xxx; --accent: #xxx; --line: #xxx;
}
```

同时提取：字号阶梯、间距阶梯、圆角、字体。

### Step 2: 识别组件

从截图中识别每个 UI 组件，命名并描述。

### Step 3: 生成设计参考 HTML

在 `xiaohongshu/design-refs/` 创建 390px 宽度的参考 HTML，用 placeholder 还原组件。

### Step 4: 套用到实际内容

Canvas → 1080×1440px（铁律），字号按比例放大 2.5-2.8x，用实际内容数据填充组件，渲染 @2x PNG。

## 设计参考目录

```
xiaohongshu/design-refs/
├── claude-fable-style.html
├── claude-fable-style.png
```
