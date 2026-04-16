#!/usr/bin/env python3
"""
SEO Wave 4 for blog.zhixingshe.cc
1. Add keywords to all posts missing them
2. Add lastmod to all posts
3. Add contextual internal links to articles with 0 body links
4. Enhance articles missing in-body crosslinks
"""

import os
import re
from datetime import datetime

POSTS_DIR = "/root/.openclaw/workspace/blog-chengnuo/content/posts"

# === KEYWORDS MAP ===
# Only for posts that don't already have keywords
KEYWORDS_MAP = {
    "ai-controls-my-mac-no-password": [
        "AI控制电脑", "OpenClaw远程操控", "Chrome CDP", "AI自动化",
        "Tailscale远程", "AI不需要密码", "AI操作浏览器"
    ],
    "ai-roast-my-monthly-bills": [
        "AI记账", "AI审判账单", "AI理财", "普通人用AI",
        "AI生活应用", "月度账单分析", "FMCG用AI"
    ],
    "helicopter-era-ai-cant-replace-experience": [
        "AI替代经验", "Vibe Coding陷阱", "判断力训练",
        "AI时代成长", "直升机时代", "AI不能替代的能力"
    ],
    "how-to-give-ai-a-soul": [
        "AI灵魂", "SOUL.md", "AI人格配置", "OpenClaw配置",
        "AI记忆系统", "AI助手人格化", "非程序员AI配置"
    ],
    "openclaw-memory-system-three-layers": [
        "OpenClaw记忆", "AI记忆三层", "LCM记忆", "Memory Search",
        "MEMORY.md", "AI长期记忆", "OpenClaw实战"
    ],
    "openclaw-multi-agent-dispatch": [
        "OpenClaw多Agent", "Agent派单", "deliver命令",
        "多Agent协作", "AI团队管理", "OpenClaw派单"
    ],
    "openclaw-skill-tools-md": [
        "OpenClaw Skill", "TOOLS.md", "AI工具管理",
        "装完即写档", "OpenClaw配置", "AI Agent技能"
    ],
    "openclaw-team-skill-upgrade-2-months": [
        "OpenClaw团队", "AI团队搭建", "Agent升级",
        "AI落地实战", "普通人搭AI团队", "FMCG用AI"
    ],
    "stop-explaining-just-show-ai": [
        "推广AI", "AI落地推广", "让别人相信AI",
        "AI展示而非解释", "普通人用AI", "AI传播策略"
    ],
    "structured-output-save-70-percent-time": [
        "结构化输出", "AI数据整理", "JSON输出",
        "AI效率提升", "非程序员结构化", "AI自动化工作流"
    ],
    "vibe-coding-cursor-wingman": [
        "Vibe Coding", "Cursor开发", "AI做产品",
        "Wingman AI", "不会写代码做产品", "AI情感僚机", "从零做产品"
    ],
    "why-you-run-out-of-things-to-say": [
        "聊天没话说", "社交技巧", "聊天冷场",
        "第一句话怎么发", "暧昧期聊天", "Wingman聊天助手"
    ],
    "wingman-ai-chat-assistant": [
        "Wingman AI", "AI聊天助手", "聊天冷场解决",
        "AI情感分析", "聊天回复建议", "AI社交工具"
    ],
}

# === CONTEXTUAL LINKS TO ADD ===
# For posts with 0 body internal links, add natural contextual links
# Format: {post_slug: [(search_text, replacement_with_link), ...]}
CONTEXTUAL_LINKS = {
    "ai-remembers-you": [
        # Link to soul article when mentioning AI personality/configuration
        ("AI助手", "AI助手（关于如何给AI搭建人格，可以看[这篇实操](/posts/how-to-give-ai-a-soul/)）"),
        # Link to memory article
        ("记忆系统", "[记忆系统](/posts/openclaw-memory-system-three-layers/)"),
    ],
    "openclaw-memory-system-three-layers": [
        ("SOUL.md", "[SOUL.md](/posts/how-to-give-ai-a-soul/)"),
        ("TOOLS.md", "[TOOLS.md](/posts/openclaw-skill-tools-md/)"),
    ],
    "openclaw-multi-agent-dispatch": [
        ("Skill", "[Skill](/posts/openclaw-skill-tools-md/)"),
        ("记忆", "[记忆](/posts/openclaw-memory-system-three-layers/)"),
    ],
    "openclaw-skill-tools-md": [
        ("多 Agent", "[多 Agent 派单](/posts/openclaw-multi-agent-dispatch/)"),
        ("记忆系统", "[记忆系统](/posts/openclaw-memory-system-three-layers/)"),
    ],
    "why-bosses-learn-ai-become-anxious": [
        ("结构化输出", "[结构化输出](/posts/structured-output-save-70-percent-time/)"),
        ("Vibe Coding", "[Vibe Coding](/posts/vibe-coding-cursor-wingman/)"),
    ],
    "wingman-ai-chat-assistant": [
        ("冷场", "冷场（推荐先看[这篇分析](/posts/why-you-run-out-of-things-to-say/)）"),
        ("Cursor", "[Cursor](/posts/vibe-coding-cursor-wingman/)"),
    ],
}


def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def split_frontmatter(content):
    """Split markdown into frontmatter and body"""
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            return parts[1], parts[2]
    return '', content


def add_keywords(frontmatter, slug):
    """Add keywords if not present"""
    if 'keywords:' in frontmatter:
        return frontmatter, False
    if slug not in KEYWORDS_MAP:
        return frontmatter, False
    
    keywords = KEYWORDS_MAP[slug]
    keyword_line = f'keywords: {keywords}'
    
    # Insert after description line
    lines = frontmatter.split('\n')
    new_lines = []
    inserted = False
    for line in lines:
        new_lines.append(line)
        if line.strip().startswith('description:') and not inserted:
            new_lines.append(keyword_line)
            inserted = True
    
    if not inserted:
        # Insert before the last line
        new_lines.insert(-1, keyword_line)
    
    return '\n'.join(new_lines), True


def add_lastmod(frontmatter):
    """Add lastmod = today if not present"""
    if 'lastmod:' in frontmatter:
        return frontmatter, False
    
    today = datetime.now().strftime('%Y-%m-%d')
    lastmod_line = f'lastmod: {today}'
    
    lines = frontmatter.split('\n')
    new_lines = []
    inserted = False
    for line in lines:
        new_lines.append(line)
        if line.strip().startswith('date:') and not inserted:
            new_lines.append(lastmod_line)
            inserted = True
    
    if not inserted:
        new_lines.insert(-1, lastmod_line)
    
    return '\n'.join(new_lines), True


def process_post(filepath):
    slug = os.path.basename(filepath).replace('.md', '')
    content = read_file(filepath)
    frontmatter, body = split_frontmatter(content)
    
    changes = []
    
    # 1. Add keywords
    frontmatter, kw_added = add_keywords(frontmatter, slug)
    if kw_added:
        changes.append(f"  + keywords added")
    
    # 2. Add lastmod
    frontmatter, lm_added = add_lastmod(frontmatter)
    if lm_added:
        changes.append(f"  + lastmod added")
    
    if changes:
        new_content = f'---{frontmatter}---{body}'
        write_file(filepath, new_content)
        print(f"✅ {slug}")
        for c in changes:
            print(c)
    else:
        print(f"⏭️  {slug} (no changes needed)")
    
    return len(changes) > 0


def main():
    modified = 0
    for filename in sorted(os.listdir(POSTS_DIR)):
        if filename.endswith('.md'):
            filepath = os.path.join(POSTS_DIR, filename)
            if process_post(filepath):
                modified += 1
    
    print(f"\n📊 Modified: {modified}/16 posts")


if __name__ == '__main__':
    main()
