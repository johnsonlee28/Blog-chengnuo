---
title: "我让AI直接开我的电脑干活，没给密码"
slug: "ai-controls-my-mac-no-password"
date: 2026-03-19
author: "成诺"
tags: ["AI", "Tailscale", "Chrome", "自动化", "OpenClaw"]
description: "AI 用你的 Chrome、带你的登录态干活，不需要密码。踩了半天 IPv6 的坑，最后发现答案早就在那了。"
---

对 Openclaw 说一句"帮我在 podwise 上搜索最近比较火的 Top 20 信息，整理成科技朋克信息图"。

AI 就能用已经登录好的 Chrome，操作后台系统、读邮件、填表单。不需要把密码交出去，因为 Cookie（浏览器记住的登录状态）已经在那了。

从"想到"到"做到"，踩了半天坑。

Mac 的家庭宽带只有 IPv6 出口，没有公网 IPv4。简单说，就像你家门牌号只有新版格式，但对面那栋楼只认老版格式，互相找不到。

服务器在腾讯云，有公网 IPv4。

原计划 Mac 通过 SSH 反向隧道（把本地端口"投射"到远程服务器上的一种方法）连服务器，把本地 Chrome 的调试端口映射上去，结果连不上。

Mac（IPv6）打不到腾讯云服务器（IPv4）。

安全组里加了 IPv6 的 TCP 22 入站规则，没用。

检查 `sshd_config`，`AddressFamily any` 没问题，没用。

查 iptables（Linux 防火墙规则），规则正常，没用。

不是防火墙问题，不是 SSH 配置问题，不是安全组问题。腾讯云轻量应用服务器这个产品，**压根不给你分配 IPv6 地址**。安全组里的 IPv6 规则是个摆设，写了也白写。

半天时间，排查了一圈，结论：这条路走不通。

---

## Tailscale 一直都在

就在要放弃的时候，突然想起来，两台机器早就装了 Tailscale。

Tailscale 是什么？一句话：给你所有设备建一个虚拟内网。不管设备在哪、用 IPv4 还是 IPv6、在公司内网还是家里 WiFi，装上 Tailscale、登同一个账号，所有设备自动出现在同一个"虚拟局域网"里，直接通信。不用管什么端口转发、防火墙规则，装上就通。

查了下两台设备的 Tailscale IP：

- 服务器：`100.69.xxx.xx`
- Mac：`100.72.xxx.xx`

试了一下：

```
ssh root@100.69.xxx.xx
```

秒通。

半天的 iptables、sshd_config、安全组、IPv6……全白折腾，答案就在这里。

---

## 安装 Tailscale

Tailscale 四步搞定：注册账号、服务器装一个命令、Mac 装 App Store 版、登同一个账号，全部打通。

**第一步：注册账号**

去 [tailscale.com](https://tailscale.com) 注册，用 Google 或 GitHub 账号登录。免费版支持最多 100 台设备，够用。

**第二步：服务器（Linux）安装**

一行命令搞定：

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

终端会输出一个链接，浏览器打开授权，回来会看到 `Success.`

查服务器的 Tailscale IP：

```bash
tailscale ip -4
# 输出类似：100.69.xxx.xx
```

**第三步：Mac 安装**

App Store 搜 **Tailscale**，安装官方客户端，用同一个账号登录。

**第四步：验证连通**

服务器上 ping 一下 Mac 的 Tailscale IP，或直接 SSH，能通就行。

从这一刻起，IPv4 还是 IPv6，不再是你的问题。

> Tailscale 的 100.x.x.x 地址绑定账号，不会变。记下来当内网地址用。

---

## 4 步让 AI 控制远程 Chrome

这套链路依赖 **Chrome DevTools MCP**（一个把 Chrome 调试协议封装成标准接口的工具，让 AI 能像操作 API 一样操控真实浏览器）。

注：OpenClaw 从 **3.13 版本**开始正式支持。

安装方式很简单，在 OpenClaw 配置里加一行 MCP：

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest", "--autoConnect"]
    }
  }
}
```

加完重启 OpenClaw，AI 就能通过这个接口直接调用 Chrome 的所有调试能力。

**第 1 步：Mac 上启动 Chrome 调试模式**

让 Chrome 打开一扇"后门"，允许外部程序控制它：

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.chrome-ai-profile"
```

`--user-data-dir` 必须用专用 Profile（相当于给 AI 开一个独立的浏览器账号），原因后面说。

**第 2 步：Mac 上建 SSH 反向隧道**

把 Mac 本地的 Chrome 调试端口"投射"到服务器上，让服务器上的 AI 能碰到它：

```bash
ssh -N -R 19222:127.0.0.1:9222 root@<服务器Tailscale IP>
```

这个终端窗口"卡住"就是正常工作状态，别关。

**第 3 步：服务器上验证连通**

```bash
curl http://127.0.0.1:19222/json/version
```

返回包含 `webSocketDebuggerUrl` 的 JSON，说明链路通了。

**第 4 步：让 AI 开始干活**

直接在 OpenClaw 里下指令，AI 会通过 Chrome DevTools 操控你的浏览器，带着你的登录态去做事。

---

## Chrome DevTools MCP 能做什么

连上 Chrome 之后，AI 拿到的不是一个"模拟浏览器"，而是你正在用的那个，带登录态、带历史记录、带所有已装的扩展。

这个差别很重要。很多网站有反爬机制（检测到不是真人浏览器就直接拦截），陌生浏览器指纹一进来就被挡。你的 Chrome 进去，它以为是你本人在操作。

具体能帮你省什么时间：

**① 每天重复的网页操作**

每天早上打开 5 个网站、记录几个数字、填进表格。这种流程交给 AI，它循环执行，你只看结果。每天省 20 分钟，一个月省出 10 小时。

**② 需要登录才能进的后台系统**

公司 ERP、电商卖家后台、广告投放平台，这些系统没有 API，但有网页。AI 带着你的 Cookie 进去，能读数据、填表单、导出报表，不需要你手动一条条复制粘贴。这是跟普通爬虫最大的区别，普通爬虫进不去登录墙，AI 直接用你的登录态。

**③ 有反爬保护的内容**

知乎、小红书、LinkedIn，直接用程序去抓大概率被拒之门外。用 Chrome 去拿，和你本人刷网页没区别，内容直接返回。

**④ 截图 + 分析页面状态**

AI 截下当前页面，结合视觉理解判断"按钮有没有变灰""表单有没有报错""价格有没有变化"。比纯代码解析网页结构更稳定，因为它是"看"页面，不是"猜"页面。

**⑤ 跨页面信息整合**

打开十几个标签页，从每个页面抽取关键字段，整合成一份报告。手动要一小时，AI 三分钟。

Chrome DevTools MCP 让 AI 从"能聊天"变成"能干活"，干那些有界面、没 API、但每天都得做的活。

---

## 必读风险提示

**① Cookie 和 Session 全暴露**

CDP（Chrome 调试协议）能做的事跟你坐在电脑前一样。你登录了什么网站，AI 就能操作什么网站。

必须用专用 Chrome Profile，只登 AI 需要操作的网站。

**别装钱包插件，别登银行。**

**② 隧道用完即关**

隧道开着，19222 端口就是一扇门。用完就关（Ctrl+C），别让它常驻后台。

**③ Tailscale 账号 = 内网钥匙**

谁拿到你的 Tailscale 账号，谁就能进你的虚拟内网。开启两步验证，不要在不信任的设备上登录。

**④ `/tmp` 不是保险箱**

调试过程中可能在 /tmp 生成临时文件，服务器重启后会被清空。重要的配置、脚本、数据，别放在 /tmp 里。

---

## 最后

回头看这一天，最大的收获不是技术本身。

花了半天排查 IPv6、iptables、安全组，最后发现答案在 Tailscale，一个早就装好了的工具。问题出在网络层，解决方案在组网层。死盯着问题本身，反而看不到旁边的出口。

问题和答案经常不在同一个方向上。

至于 AI 控制真实浏览器这件事，现在只是起点。当 AI 能看到你看到的网页、能点你能点的按钮、能读你能读的数据，它就不再是一个只会聊天的对话框了。

它变成了一双手。

---

💡 更多 AI 实战经验，关注公众号「成诺的复利之旅」获取更多。

**📌 相关文章：**

- [如何给 AI 建立一个灵魂](/posts/how-to-give-ai-a-soul/) — AI能开你的电脑，但还得有灵魂才知道该干什么
- [OpenClaw团队有岗位没手艺？用了2个月的升级方案](/posts/openclaw-team-skill-upgrade-2-months/) — 远程控制是基础设施，团队协作才是核心
- [结构化输出：省掉70%的人工整理时间](/posts/structured-output-save-70-percent-time/) — AI开了电脑之后，怎么让它自动处理抓到的数据
