#!/usr/bin/env python3
"""Render AI Skills cards — purple template, step-card layout, podcast/tutorial style.

Usage:
    from render_skills import render_skills_cards, render_skills_cover, screenshot_htmls

    paths = render_skills_cards(cards, output_dir, date_str,
                                 guest_photo="dianne-penn.png",
                                 source_info={"show": "Lenny's Podcast", "episode": "..."})
"""

from __future__ import annotations

from pathlib import Path

# ═══════════════════════════════════════════════════════════════════
# AI Skills CSS — purple #5B4FE9, cream #F6F2E9, Inter font
# ═══════════════════════════════════════════════════════════════════

CARD_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{
  width:1080px;
  background:#F6F2E9;
  font-family:'Inter',-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;
  display:flex;justify-content:center;
  -webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;
}
.canvas{width:1080px;background:#F6F2E9;position:relative;overflow:hidden;padding-bottom:80px}
.topbar{height:8px;background:#5B4FE9;width:100%}
.deco-circle{position:absolute;border:1px solid #E3DDCB;border-radius:50%}
.deco-1{width:500px;height:500px;top:-260px;right:-190px}
.deco-2{width:310px;height:310px;top:-70px;right:70px}
.deco-3{width:360px;height:360px;bottom:-210px;left:-190px}
.dots{position:absolute;top:56px;right:72px;display:grid;grid-template-columns:repeat(6,10px);grid-gap:12px;z-index:2}
.dots span{width:6px;height:6px;border-radius:50%;background:#CFC9B8}
.content{position:relative;z-index:3;padding:80px 80px 0 80px}
.eyebrow{display:flex;align-items:center;gap:12px;color:#5B4FE9;font-weight:700;font-size:18px;letter-spacing:0.5px;margin-bottom:20px}
.eyebrow .dash{width:26px;height:3px;background:#5B4FE9;display:inline-block}
.header-row{display:flex;align-items:center;gap:24px;margin-bottom:30px}
.guest-badge{flex-shrink:0;display:flex;align-items:center;gap:10px;background:#FFF;border:1px solid #ECE7DA;border-radius:100px;padding:8px 16px 8px 8px;box-shadow:0 2px 8px rgba(0,0,0,0.03)}
.guest-badge img{width:40px;height:40px;border-radius:50%;object-fit:cover}
.guest-badge .name{font-size:16px;font-weight:700;color:#6B6B6B}
.guest-badge .role{font-size:13px;font-weight:600;color:#B4AEA0}
.headline{font-size:60px;font-weight:900;line-height:1.12;color:#C9C4B8;letter-spacing:-1px}
.headline .accent{color:#5B4FE9}
.highlight-wrap{margin-top:10px}
.highlight{display:inline-block;background:#5B4FE9;color:#fff;font-size:46px;font-weight:800;padding:8px 26px 12px 26px;line-height:1.1;border-radius:4px}
.steps{margin-top:60px;display:flex;flex-direction:column;gap:20px}
.step-card{background:#FFF;border:1px solid #ECE7DA;border-radius:16px;padding:26px 30px;display:flex;align-items:flex-start;gap:22px;box-shadow:0 2px 8px rgba(0,0,0,0.03)}
.step-num{flex:0 0 auto;width:40px;height:40px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:20px;color:#fff;margin-top:2px}
.step-num.c1{background:#5B4FE9}
.step-num.c2{background:#3B82C4}
.step-num.c3{background:#2FA37A}
.step-num.c4{background:#E0A93B}
.step-num.c5{background:#E0679B}
.step-text{flex:1;min-width:0}
.step-title{font-size:24px;font-weight:800;color:#2A2A2A;margin-bottom:6px}
.step-desc{font-size:17px;color:#9A9689;font-weight:500;line-height:1.5}
.insight-box{margin-top:60px;background:#FFF;border:2px solid #5B4FE9;border-radius:16px;padding:32px 36px;text-align:center}
.insight-label{font-size:14px;font-weight:700;color:#9A9689;letter-spacing:1.5px;margin-bottom:10px}
.insight-text{font-size:26px;font-weight:800;color:#2A2A2A;line-height:1.4}
.insight-text .hl{color:#5B4FE9}
.footer-note{text-align:center;margin-top:36px;font-size:16px;color:#B4AEA0;font-weight:600}
.github-bar{{text-align:center;margin-top:12px;padding:10px 0;font-size:14px;font-weight:600;font-family:'Space Mono','SF Mono',monospace;color:#6B6B6B;letter-spacing:0.3px}}
.github-bar .gh{{color:#5B4FE9;font-weight:700}}
"""

COVER_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{
  width:1080px;height:1440px;overflow:hidden;
  background:#F6F2E9;
  font-family:'Inter',-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;
  -webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;
}
.canvas{width:1080px;height:1440px;background:#F6F2E9;position:relative;display:flex;flex-direction:column;align-items:center;justify-content:center}
.topbar{position:absolute;top:0;left:0;height:8px;background:#5B4FE9;width:100%;z-index:4}
.deco-circle{position:absolute;border:1px solid #E3DDCB;border-radius:50%}
.deco-1{width:500px;height:500px;top:-260px;right:-190px}
.deco-2{width:310px;height:310px;top:-70px;right:70px}
.deco-3{width:360px;height:360px;bottom:-210px;left:-190px}
.dots{position:absolute;top:44px;right:72px;display:grid;grid-template-columns:repeat(6,10px);grid-gap:12px;z-index:2}
.dots span{width:6px;height:6px;border-radius:50%;background:#CFC9B8}
.content{position:relative;z-index:3;padding:90px 70px 70px;display:flex;flex-direction:column;align-items:center;justify-content:center}
.eyebrow{display:flex;align-items:center;gap:12px;color:#5B4FE9;font-weight:700;font-size:18px;letter-spacing:0.5px;margin-bottom:20px}
.eyebrow .dash{width:26px;height:3px;background:#5B4FE9;display:inline-block}
.guest-photo{width:340px;height:340px;border-radius:50%;object-fit:cover;border:5px solid #5B4FE9;box-shadow:0 12px 48px rgba(91,79,233,0.25);margin-bottom:28px}
.headline{font-size:64px;font-weight:900;line-height:1.1;color:#C9C4B8;letter-spacing:-1px;text-align:center;margin-bottom:4px}
.headline .accent{color:#5B4FE9}
.subtitle{font-size:20px;font-weight:600;color:#9A9689;margin-bottom:6px;text-align:center}
.source-tag{display:inline-flex;align-items:center;gap:8px;background:#FFF;border:1px solid #ECE7DA;border-radius:100px;padding:10px 20px;font-size:15px;font-weight:700;color:#6B6B6B;margin-bottom:30px}
.source-tag .dot{width:8px;height:8px;border-radius:50%;background:#5B4FE9}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px;width:100%;margin-bottom:30px}
.icard{background:#FFF;border:1px solid #ECE7DA;border-radius:16px;padding:26px 28px;display:flex;align-items:center;gap:18px;box-shadow:0 2px 8px rgba(0,0,0,0.03)}
.ic-emoji{font-size:40px;flex-shrink:0}
.ic-title{font-size:22px;font-weight:800;color:#2A2A2A;line-height:1.3;word-break:break-word}
.caption-pill{padding:16px 38px;background:#5B4FE9;color:#fff;border-radius:100px;font-size:20px;font-weight:800;text-align:center;flex-shrink:0}
.github-bar{{text-align:center;margin-top:14px;padding:8px 0;font-size:14px;font-weight:600;font-family:'Space Mono','SF Mono',monospace;color:#6B6B6B;letter-spacing:0.3px}}
.github-bar .gh{{color:#5B4FE9;font-weight:700}}
"""


# ═══════════════════════════════════════════════════════════════════
# Card HTML generation
# ═══════════════════════════════════════════════════════════════════

def _make_card_html(card: dict, idx: int, guest_photo: str | None = None,
                    guest_name: str = "", guest_role: str = "",
                    eyebrow: str = "PODCAST NOTES") -> str:
    """Generate a single AI Skills card HTML from card data dict.

    card dict keys: emoji, title, summary, detail, why_care, key_points, source_note
    """
    emoji = card.get('emoji', '📌')
    title = card.get('title', '')
    summary = card.get('summary', '')
    detail = card.get('detail', '')
    why_care = card.get('why_care', '')
    key_points = card.get('key_points', [])
    source = card.get('source_note', 'YouTube')

    # Split title: last ~3 chars as accent (purple)
    if len(title) > 3:
        headline_gray = title[:-3]
        headline_accent = title[-3:]
    else:
        headline_gray = ""
        headline_accent = title

    steps_data = [
        ('💬', '发生了什么？', summary, 'c1'),
        ('🔍', '深入了解一下', detail, 'c2'),
        ('💡', '为什么值得关注', why_care, 'c3'),
    ]
    steps_html = ""
    for icon_char, label, text, color in steps_data:
        steps_html += f"""<div class="step-card">
  <div class="step-num {color}">{icon_char}</div>
  <div class="step-text">
    <div class="step-title">{label}</div>
    <div class="step-desc">{text}</div>
  </div>
</div>"""

    kp_text = ' · '.join(key_points[:3])

    # Guest badge
    guest_html = ""
    if guest_photo and guest_name:
        guest_html = f"""<div class="header-row">
  <div class="guest-badge">
    <img src="{guest_photo}" alt="{guest_name}">
    <div>
      <div class="name">{guest_name}</div>
      <div class="role">{guest_role}</div>
    </div>
  </div>
</div>"""

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | AI Skills</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap" rel="stylesheet">
<style>
{CARD_CSS}
</style>
</head>
<body>
<div class="canvas">
<div class="topbar"></div>
<div class="deco-circle deco-1"></div>
<div class="deco-circle deco-2"></div>
<div class="deco-circle deco-3"></div>
<div class="dots">{'<span></span>' * 12}</div>
<div class="content">
<div class="eyebrow"><span class="dash"></span>{eyebrow} · 0{idx+1}</div>
{guest_html}
<div class="headline">{headline_gray}<span class="accent">{headline_accent}</span></div>
<div class="highlight-wrap"><span class="highlight">{emoji} {title}</span></div>
<div class="steps">
{steps_html}
</div>
<div class="insight-box">
  <div class="insight-label">KEY TAKEAWAYS</div>
  <div class="insight-text">{kp_text}</div>
</div>
<div class="footer-note">{source} · 2026.07.30</div>
<div class="github-bar">GitHub: <span class="gh">summersalt827/AI-Automation-Pipeline</span></div>
</div>
</div>
</body>
</html>"""


def _make_cover_html(cards: list[dict], date_str: str,
                     guest_photo: str | None = None,
                     headline_gray: str = "播客", headline_accent: str = "笔记",
                     subtitle: str = "", source_label: str = "",
                     eyebrow: str = "PODCAST NOTES",
                     caption_pill: str = "精选 4 条核心洞察") -> str:
    """Generate the AI Skills cover HTML with 2x2 grid of card titles."""
    grid_items = ""
    for c in cards:
        grid_items += f'<div class="icard"><div class="ic-emoji">{c.get("emoji","")}</div><div class="ic-title">{c.get("title","")}</div></div>\n'

    # Guest photo block
    photo_html = ""
    if guest_photo:
        photo_html = f'<img class="guest-photo" src="{guest_photo}" alt="Guest">\n'

    subtitle_html = ""
    if subtitle:
        subtitle_html = f'<div class="subtitle">{subtitle}</div>\n'

    source_html = ""
    if source_label:
        source_html = f'<div class="source-tag"><span class="dot"></span>{source_label}</div>\n'

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Skills | {date_str}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap" rel="stylesheet">
<style>
{COVER_CSS}
</style>
</head>
<body>
<div class="canvas">
<div class="topbar"></div>
<div class="deco-circle deco-1"></div>
<div class="deco-circle deco-2"></div>
<div class="deco-circle deco-3"></div>
<div class="dots"><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span></div>
<div class="content">
<div class="eyebrow"><span class="dash"></span>{eyebrow}</div>
{photo_html}
<div class="headline">{headline_gray}<span class="accent">{headline_accent}</span></div>
{subtitle_html}
{source_html}
<div class="grid">
{grid_items}
</div>
<div class="caption-pill">{caption_pill}</div>
<div class="github-bar">GitHub: <span class="gh">summersalt827/AI-Automation-Pipeline</span></div>
</div>
</div>
</body>
</html>"""


# ═══════════════════════════════════════════════════════════════════
# Main entry points
# ═══════════════════════════════════════════════════════════════════

def render_skills_cards(cards: list[dict], output_dir: Path, date_str: str,
                        guest_photo: str | None = None,
                        guest_name: str = "", guest_role: str = "",
                        eyebrow: str = "PODCAST NOTES",
                        prefix: str = "skills") -> list[Path]:
    """Generate AI Skills card HTML files. Returns list of HTML paths."""
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for i, card in enumerate(cards):
        html = _make_card_html(card, i, guest_photo=guest_photo,
                               guest_name=guest_name, guest_role=guest_role,
                               eyebrow=eyebrow)
        path = output_dir / f'{date_str}_{prefix}_card_{i+1:02d}.html'
        path.write_text(html, encoding='utf-8')
        paths.append(path)
    return paths


def render_skills_cover(cards: list[dict], output_dir: Path, date_str: str,
                        guest_photo: str | None = None,
                        headline_gray: str = "播客", headline_accent: str = "笔记",
                        subtitle: str = "", source_label: str = "",
                        eyebrow: str = "PODCAST NOTES",
                        caption_pill: str = "精选 4 条核心洞察",
                        prefix: str = "skills") -> Path:
    """Generate AI Skills cover HTML. Returns HTML path."""
    output_dir.mkdir(parents=True, exist_ok=True)
    html = _make_cover_html(cards, date_str, guest_photo=guest_photo,
                            headline_gray=headline_gray,
                            headline_accent=headline_accent,
                            subtitle=subtitle, source_label=source_label,
                            eyebrow=eyebrow, caption_pill=caption_pill)
    path = output_dir / f'{date_str}_{prefix}_cover.html'
    path.write_text(html, encoding='utf-8')
    return path


def screenshot_htmls(html_paths: list[Path], output_dir: Path) -> list[Path]:
    """Screenshot HTML files as PNG at 1080x1440 @2x = 2160x2880 (clipped, not full_page)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  [screenshot] playwright not installed, skip PNG")
        return []

    output_dir.mkdir(parents=True, exist_ok=True)
    png_paths: list[Path] = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"],
            )
            for html_path in html_paths:
                png_path = output_dir / html_path.with_suffix(".png").name
                file_uri = Path(html_path).resolve().as_uri()

                page = browser.new_page(
                    viewport={"width": 1080, "height": 1440},
                    device_scale_factor=2,
                )
                page.goto(file_uri, wait_until="networkidle", timeout=30000)
                page.screenshot(
                    path=str(png_path),
                    full_page=False,
                    clip={"x": 0, "y": 0, "width": 1080, "height": 1440},
                )
                page.close()
                png_paths.append(png_path)
            browser.close()
    except Exception as exc:
        print(f"  [screenshot] failed: {exc}")

    return png_paths


def render_and_screenshot(cards: list[dict], output_dir: Path, date_str: str,
                          **kwargs) -> dict:
    """Full pipeline: generate HTML + screenshot to PNG.

    Returns dict with keys: cover_html, cover_png, card_htmls, card_pngs, caption_path
    """
    prefix = kwargs.pop('prefix', 'skills')
    # Generate HTML
    cover_html = render_skills_cover(cards, output_dir, date_str, prefix=prefix, **kwargs)
    card_htmls = render_skills_cards(cards, output_dir, date_str, prefix=prefix, **kwargs)

    # Screenshot
    all_html = [cover_html] + card_htmls
    all_png = screenshot_htmls(all_html, output_dir)

    return {
        'cover_html': cover_html,
        'cover_png': all_png[0] if all_png else None,
        'card_htmls': card_htmls,
        'card_pngs': all_png[1:] if len(all_png) > 1 else [],
        'all_pngs': all_png,
    }
