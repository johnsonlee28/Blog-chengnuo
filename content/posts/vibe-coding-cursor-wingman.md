---
title: "Vibe Coding 实战：我用 Cursor 做了一个 AI 情感僚机"
slug: "vibe-coding-cursor-wingman"
date: 2026-04-01
author: "成诺"
categories: [产品实战]
tags: [Vibe Coding, AI工具, 实战]
description: "不会写代码，但用 Cursor 从零搭出了 Wingman——一个帮你分析聊天氛围、生成回复的 AI 工具。这是完整的实战过程。"
canonicalURL: "https://blog.zhixingshe.cc/posts/vibe-coding-cursor-wingman/"
cover:
  image: "/images/covers/vibe-coding-cursor-wingman.png"
  alt: ""
  relative: false
---

去年这时候，我对「Vibe Coding」这个词的理解还停在：「就是 AI 帮你写代码嘛，有啥了不起的。」

现在我的想法是：这玩意儿把独立开发的门槛炸平了一半。

---

## 从一个具体的痛点开始

事情的起点很普通——

身边有朋友跟人暧昧期发消息，发完截图给我：「你帮我看看，这条回的是什么意思？」

这种事发生的次数多了，我开始想：**为什么没有一个工具专门干这件事？**

不是泛泛的「AI聊天助手」，而是：

- 你把聊天截图丢进去
- 它告诉你现在的对话温度是热还是冷
- 根据你的性格风格，给你几条可以发的回复

这就是 [Wingman](https://wingman.zhixingshe.cc) 的起点。

---

## Cursor 是怎么介入的

说清楚一点——做 Wingman 之前，我写代码的水平是：

- 能看懂 Python 基础语法
- 改改别人的脚本没问题
- 从零搭一个有前端的完整产品？没戏

然后我开始用 Cursor。

Cursor 不是「你说需求它生成代码」那么简单。更准确的描述是：**它是一个能参与你思考过程的结对程序员**。你不需要先把需求写清楚，你可以边想边说，它边理解边写，有问题它问你，你觉得不对你推翻重来。

整个过程更像是跟一个有代码能力的人对话，而不是填表单。

---

## 实际做了什么

**第一步：把产品逻辑说清楚**

跟 Cursor 描述：用户上传聊天截图，识别文字，输出「对话温度」（1-10分），再根据用户的风格偏好（幽默/温柔/直接）生成3条回复建议。

Cursor 直接给了技术方案：Next.js 前端 + FastAPI 后端 + 通义千问 (Qwen) 做截图识别与分析。

**第二步：逐模块推进**

没有一口气把所有代码生成出来。而是：

1. 先做「截图上传+文字识别」这一块
2. 跑通了，再做「温度分析」逻辑
3. 再接「回复生成」
4. 最后做 UI

每一步 Cursor 写完，我在浏览器里验证，发现问题告诉它，它修。这个循环大概持续了3天。

**第三步：遇到了什么麻烦**

- 截图识别偶尔出错 → 换成先用本地 OCR 提取文字，再喂给千问分析
- 「温度」这个概念太主观，模型输出不稳定 → 在 prompt 里加了详细的评分标准和示例
- 移动端排版垮了 → 让 Cursor 专门跑一轮「只修移动端样式，不动逻辑」

这些问题在以前对我来说是「卡死」，现在变成了「多花一个小时」。

---

## Vibe Coding 真正改变了什么

不是「不用学编程了」——这个说法是错的。

真正改变的是：**你需要学的东西变了**。

以前做产品，卡点在「实现」：想清楚了但写不出来。

现在卡点在「想清楚」：你对产品的理解有多深，Cursor 就能帮你走多远。

> 换句话说，Vibe Coding 放大的不是你的技术能力，而是你的产品思维。

如果你有一个具体的痛点，能把它说清楚，知道「好的结果」是什么样，Cursor 能帮你把这件事做出来。

---

## 工具组合参考

我做 Wingman 用的完整工具链：

| 环节 | 工具 |
|------|------|
| 代码编写 | Cursor (Claude Opus) |
| 前端框架 | Next.js + Tailwind |
| 后端 | FastAPI (Python) |
| AI 能力 | 通义千问 (Qwen) |
| 部署 | Vercel (前端) + Railway (后端) |
| 版本管理 | GitHub |

整个过程没有外包，没有找程序员，自己一个人完成。

---

## 相关延伸

如果你对「AI 工具怎么真正融入工作流」感兴趣，可以看这几篇：

- [结构化输出：省掉70%的人工整理时间](/posts/structured-output-save-70-percent-time/) — 让 AI 直接输出可处理的格式，而不是一堆文字
- [我以为派出去了，其实一个都没到——多 Agent 派单的正确姿势](/posts/openclaw-multi-agent-dispatch) — 多个 AI 协作时踩过的坑
- [如何给 AI 建立一个灵魂](/posts/how-to-give-ai-a-soul/) — 为什么同一个问题，不同的 AI 助手给出完全不同的回答

Wingman 现在可以直接用：[wingman.zhixingshe.cc](https://wingman.zhixingshe.cc)

---

*有在用 Cursor 做东西的，欢迎告诉我你遇到的最大卡点。*

---

## 延伸阅读

- [用 AI 工具把「冷场率」降到了个位数](/posts/wingman-ai-chat-assistant/)
- [跟喜欢的人聊天，为什么总是你先没话说？](/posts/why-you-run-out-of-things-to-say/)
- [AI帮你到了终点，但路上的风景只能自己看](/posts/helicopter-era-ai-cant-replace-experience/)
