# frontend-backend-testing · Skill

![Version](https://img.shields.io/badge/version-2.2.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Format](https://img.shields.io/badge/format-Claude_Skill-orange)

> 工程化前后端测试 Skill —— 4 测试模式 × 21 测试维度 × 7 测试设计方法 × 5 大 Bug 模式库 × 6 端到端示例。

## 📦 这是什么

一个为 Claude（Cowork / Claude Code / Claude Agent SDK）设计的 **完整测试 Skill**，把"清单型 QA"升级为"工程化测试 Agent"。

收到测试请求时，自动按以下顺序工作：

```
① 确认输入 → ② 选定模式 → ③ 结构化提取测试要素 → ④ 按维度逐项展开
→ ⑤ 调用测试设计方法穷举场景 → ⑥ 用工具实测（Read / Grep / Bash / Chrome / Pencil）
→ ⑦ 按模板结构化输出 → ⑧ 质量门禁自检
```

## ✨ 核心能力

### 4 种测试模式
- **全量速测** — 上线前快速过 21 维度
- **分项深测**（默认） — 单维度穷举式深入
- **增量回归** — 基于 Git diff / Bug 修复的影响面测试
- **测试编排** — 复杂项目分批规划

### 21 个测试维度
- **业务功能层（1–10）**：原型交互 / UI 布局 / 接口契约 / 数据落库 / 输入校验 / 异常容错 / 权限角色 / 会话登录 / 列表操作 / 状态流转
- **通用质量层（11–17）**：文件 IO / 兼容性 / 性能 / 安全 / 可观测性 / 回归 / UX
- **代码工程层（18–21，v2 新增）**：静态分析 / 单测 / 可维护性 / 依赖构建

### 7 类测试设计方法
等价类 · 边界值 · 判定表 · 状态迁移 · 错误推测 · 正交组合 · 场景法

### 强制 Agentic 工具实测
铁律：**未实测必标注 "未实测，待验证"**，杜绝纸上谈兵。

## 🚀 快速开始

详细安装见 `INSTALL.md`，简版：

| Agent | 安装方式 |
|---|---|
| **Cowork** | 双击 `.skill` 文件 → 点 Save skill |
| **Claude Code** | 解压到 `~/.claude/skills/frontend-backend-testing/` → 重启 |
| **Claude Agent SDK** | 解压到项目 `.claude/skills/` 或 SDK 配置的 skills 目录 |

安装后，对 Claude 说：
- "对登录页做一次完整测试"
- "帮我写 XX 功能的测试用例"
- "分析这个项目的代码质量"
- "PR 合入前做一次回归"
均会触发本 Skill。

## 📂 包结构

```
frontend-backend-testing/
├── SKILL.md                    # 入口 + 触发判定 + 模式分流
├── VERSION                     # 2.2.0
├── README.md                   # 你正在看的文件
├── CHANGELOG.md                # 版本演进
├── INSTALL.md                  # 多 Agent 安装指南
├── LICENSE                     # MIT
├── modes/                      # 4 种测试模式
├── dimensions/                 # 21 个测试维度
├── methods/                    # 7 类测试设计方法
├── templates/                  # 5 个交付模板
├── checklists/                 # 5 个 Bug 模式库
└── examples/                   # 6 个端到端示例
```

## 🔧 推荐配套工具

| 工具 | 必要性 | 说明 |
|---|---|---|
| Claude in Chrome | ⭐ 强烈建议 | 实测页面、抓控制台、抓网络 |
| pencil MCP | 按需 | 仅当用 .pen 设计稿时 |
| GitHub / Jira / Sentry | 按需 | 代码 / Bug 单 / 错误聚合 |

## 📜 License

MIT
