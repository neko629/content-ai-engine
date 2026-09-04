# 安装指南 · frontend-backend-testing v2.2.0

本 Skill 兼容所有支持 Claude Agent Skill 规范的 Agent。下面给出 3 种主流 Agent 的安装方式。

---

## 1️⃣ Cowork（Claude 桌面应用）

### 方式 A：拖拽安装（推荐）

1. 找到 `frontend-backend-testing-v2.2.0.skill` 文件
2. 在 Cowork 对话框拖入或双击
3. 出现 "Save skill" 卡片 → 点击安装
4. 如有同名旧版 → 选 **覆盖**
5. **⌘ + Q 完全退出 Cowork**，重新打开
6. 新开对话生效

### 方式 B：手动安装

1. 解压 `frontend-backend-testing-v2.2.0.zip`
2. 把 `frontend-backend-testing/` 整个文件夹复制到：
   ```
   ~/Library/Application Support/Claude/skills/  (macOS)
   %APPDATA%\Claude\skills\                       (Windows)
   ```
3. 重启 Cowork

### 验证

新会话发：
> 列出可用 skills

或

> 对登录页做一次完整测试

应看到 skill 被触发。

---

## 2️⃣ Claude Code（CLI / IDE 插件）

### 用户级安装（全局可用）

```bash
# 1. 解压
unzip frontend-backend-testing-v2.2.0.zip -d /tmp/

# 2. 复制到用户 skills 目录
mkdir -p ~/.claude/skills/
cp -r /tmp/frontend-backend-testing ~/.claude/skills/

# 3. 验证
ls ~/.claude/skills/frontend-backend-testing/SKILL.md
```

### 项目级安装（仅当前项目可用）

```bash
# 在项目根目录执行
mkdir -p .claude/skills/
unzip frontend-backend-testing-v2.2.0.zip -d .claude/skills/
```

### 验证

```bash
# 在 Claude Code 里
/skills
# 应看到 frontend-backend-testing 列出
```

---

## 3️⃣ Claude Agent SDK（自定义 Agent）

### Python SDK

```python
from claude_agent_sdk import Agent

agent = Agent(
    model="claude-sonnet-4-6",
    skills_path="./skills/",  # 解压到这个目录
)
```

把 `frontend-backend-testing/` 文件夹放到 `./skills/` 即可。

### TypeScript SDK

```typescript
import { Agent } from "@anthropic-ai/claude-agent-sdk";

const agent = new Agent({
  model: "claude-sonnet-4-6",
  skillsPath: "./skills/",
});
```

### 通用约定

任何遵循 Anthropic Agent Skill 规范的 Agent 都支持本 Skill。规范要求：

- 目录入口为 `SKILL.md`
- `SKILL.md` 含 YAML frontmatter（必含 `name` 和 `description`）
- 子文件可被 Agent 按需 Read

---

## 4️⃣ 验证 Skill 是否激活

### 触发测试

发以下任一句，应看到 Skill 被使用：

| 句式 | 期望 |
|---|---|
| "对登录页做一次完整测试" | ✅ 触发 → 进入分项深测 |
| "帮我写 XX 的测试用例" | ✅ 触发 |
| "做一次代码审查 / PR Review" | ✅ 触发 |
| "什么是边界值测试" | ❌ 不应触发（概念问答）|
| "测一下我的网速" | ❌ 不应触发（比喻）|

### 故障排查

| 症状 | 原因 | 处理 |
|---|---|---|
| Cowork 报 "description must be at most 1024 characters" | 装到了 v2.1 或更早版本 | 用 v2.2.0 重装 |
| 找不到 skill | 路径错 | 检查 SKILL.md 是否在 `frontend-backend-testing/` 直接子级 |
| 不触发 | 旧会话工具列表锁定 | 完全退出 Agent 重开新会话 |
| 触发但行为像 v1 | 旧版未卸载 | 删除旧目录，只保留 v2.2.0 |

---

## 5️⃣ 推荐配套工具

完整功能需要的可选工具：

| 工具 | 解决 | 必要性 |
|---|---|---|
| Claude in Chrome | 实测页面、抓控制台、抓网络 | ⭐ 强烈建议 |
| pencil MCP | 读 .pen 设计稿 | 按需 |
| GitHub / GitLab MCP | 拉代码、PR、commit | 测代码层时建议 |
| Jira / Linear MCP | Bug 单对接 | 做回归测试时建议 |
| Sentry MCP | 错误聚合 | 测可观测性时建议 |

不装这些也能跑，但维度 02 / 03 / 13 / 14 / 17 大量结论会标 "未实测，待验证"。

---

## 6️⃣ 升级与卸载

### 升级

直接覆盖旧目录即可，无需特殊操作。

### 卸载

| Agent | 操作 |
|---|---|
| Cowork | Settings → Customize / Skills → 找到 frontend-backend-testing → 卸载 |
| Claude Code | `rm -rf ~/.claude/skills/frontend-backend-testing` |
| Agent SDK | 删 `skills/frontend-backend-testing` 目录 |

---

## 7️⃣ 支持与反馈

- 版本：v2.2.0
- 更新日志：见 `CHANGELOG.md`
- 详细使用：见 `SKILL.md`
