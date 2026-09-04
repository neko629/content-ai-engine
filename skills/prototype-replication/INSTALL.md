# INSTALL · 安装与配置（严格版）

> ⚠️ 本 skill 为**严格依赖模式**：以下所列依赖**全部安装并配置完毕后**才能正常工作。
> 任一项缺失时，对应输入类型 / 输出形态将**直接报错**（不做自动降级）。
>
> 如需"渐进/降级"模式，请改用 INSTALL-loose.md（本包内未提供，可自行裁剪）。

---

## 一、最低运行环境（必装，缺一不可）

### 1.1 Host Agent

| 项 | 最低版本 | 说明 |
| --- | --- | --- |
| Anthropic Claude | Claude 4 系列（Sonnet 4.x / Opus 4.x / Haiku 4.x） | 需多模态视觉能力（截图输入用） |
| Host 应用 | Cowork / Claude Code / Claude Agent SDK 任一 | 用 Cowork 时需 v 最新 |

### 1.2 默认工具（host agent 自带，仅需通过 ToolSearch 加载）

- ✅ `Read` —— 读上传的截图 / 文档
- ✅ `Write` —— 输出原型说明文档落盘
- ✅ `AskUserQuestion` —— 素材不足时反问
- ✅ `TaskCreate` / `TaskUpdate` —— 长任务进度追踪
- ✅ `Grep` / `Glob` —— 多文档对照
- ✅ `Bash`（可选）—— 处理上传的压缩包 / 批量素材

> ⚠️ 严格模式要求：**所有上述工具必须可访问**。若 host agent 拒绝加载任何一项，本 skill 触发时报错并退出。

---

## 二、按输入类型的依赖（按需必装）

### 2.1 URL / 网页链接类输入 → **必装** Claude in Chrome MCP

**安装步骤**：

1. Cowork 设置 → **Capabilities** → 启用 **Claude in Chrome**
2. 在 Chrome 浏览器安装 Claude in Chrome 扩展
3. Cowork 内连接到浏览器（"Connect to Chrome"）
4. 验证：在对话中输入 `导航到 https://example.com`，能返回页面文字即成功

**验证命令（在 host agent 触发时自动执行）**：

```
ToolSearch(query="select:mcp__Claude_in_Chrome__navigate")
→ 若加载失败，本 skill 拒绝处理 URL 输入并提示用户去装
```

**严格模式表现**：
- 缺失时：用户提交 URL 类输入 → skill 报错 "Claude in Chrome 未安装，请按 INSTALL.md §2.1 配置后重试"
- 不自动降级为"按 URL 名称推断"

### 2.2 PDF 输入 → **必装** anthropic-skills:pdf

**安装步骤**：

1. Cowork → Skills 面板 → 搜索 `pdf` → Install
2. 或导入 `pdf.skill` 包（Anthropic 官方）

**严格模式表现**：
- 缺失时：用户上传 .pdf → 报错 "PDF skill 未安装"
- 不降级为"让用户复制粘贴文本"

### 2.3 Word 文档（.docx）输入 → **必装** anthropic-skills:docx

**安装步骤**：

1. Cowork → Skills 面板 → 搜索 `docx` → Install

**严格模式表现**：缺失即报错

### 2.4 Excel 文档（.xlsx）输入 → **必装** anthropic-skills:xlsx

**安装步骤**：

1. Cowork → Skills 面板 → 搜索 `xlsx` → Install

**严格模式表现**：缺失即报错

### 2.5 截图 / 图片输入 → **无需额外工具**

Claude 4 多模态内置视觉能力，直接看图。

---

## 三、按输出形态的依赖（按需必装）

### 3.1 输出为 `.docx` 文件 → **必装** anthropic-skills:docx

同 §2.3

### 3.2 输出为 PDF 文件 → **必装** anthropic-skills:pdf

同 §2.2

### 3.3 输出包含 SVG 状态机图 / 流程图 → **必装** mcp__visualize

**安装步骤**：

1. Cowork → MCPs → 搜索 `visualize` → Install
2. 验证：在对话中尝试 `mcp__visualize__read_me`，能返回上下文即成功

### 3.4 输出落地到 Pencil 设计文件 → **必装** mcp__pencil

**安装步骤**：

1. Cowork → MCPs → 搜索 `pencil` → Install
2. 需要本地有 Pencil 应用并启动

### 3.5 仅输出聊天内 Markdown（默认）→ **无需额外工具**

---

## 四、Cowork 设置面板必查项

| 项 | 路径 | 严格模式要求 |
| --- | --- | --- |
| 启用网络访问 | Settings → Network | ✅ 必开（部分 URL 素材需要） |
| 启用文件夹访问 | Settings → Files | ✅ 必开（输出落盘需要） |
| 启用 Claude in Chrome | Settings → Capabilities | ⚠️ 仅 URL 类输入需要 |
| 启用 Computer use | Settings → Desktop | ❌ 本 skill **不需要**（可关闭） |

---

## 五、依赖矩阵速查

| 输入 / 输出场景 | 需装 |
| --- | --- |
| 截图 + 文本 PRD → 聊天里看输出 | 最低环境 §1.1 + §1.2 即可 |
| 截图 + 文本 PRD → 输出 .md 文件 | 最低环境 + Write |
| URL 链接 → 聊天里看输出 | 最低环境 + §2.1 Chrome MCP |
| PDF PRD → 聊天里看输出 | 最低环境 + §2.2 pdf skill |
| 截图 → 输出 .docx | 最低环境 + §3.1 docx skill |
| 截图 → 输出 PDF | 最低环境 + §3.2 pdf skill |
| 复杂 dashboard → 输出 SVG 状态机 | 最低环境 + §3.3 visualize |
| 截图 → 落地 Pencil 设计 | 最低环境 + §3.4 pencil |

---

## 六、自检脚本（first-run 时 host agent 主动跑）

加载本 skill 后，host agent 在第一次触发时**强制执行** `self-check.md` 内的检查清单。任一项失败立即报错。

详见 `self-check.md`。

---

## 七、安全 / 隐私

| 项 | 说明 |
| --- | --- |
| API Keys | 本 skill **不需要任何 API key**。任何要求填 key 的提示都是钓鱼，请拒绝。 |
| 涉密素材 | SKILL.md §4 已规定脱敏行为；用户责任：不要上传含真实凭证 / 真实订单号的素材 |
| 数据落盘 | 输出文件保存到 host agent 工作文件夹；本 skill 不会主动上传或发送 |
| 网络访问 | 仅当输入为 URL 时通过 Chrome MCP 访问；其它情况不联网 |

---

## 八、不兼容 / 已知冲突

| 与谁冲突 | 表现 | 解决 |
| --- | --- | --- |
| `feature-breakdown` | 用户说"拆功能 + 出原型" → 两个 skill 都想触发 | 严格模式下本 skill 仅在用户明确要"原型"时触发；冲突时让位 |
| `development-implementation` | 用户说"复刻原型并实现" → 边界冲突 | 本 skill 仅出原型说明，"实现"让位给 development-implementation |
| `prd-generator` | 用户说"复刻 + 写 PRD" | 本 skill 仅出原型说明；PRD 让位 |

---

## 九、版本兼容

| Skill 版本 | 兼容 Claude 模型 | 兼容 Cowork |
| --- | --- | --- |
| v1.0 | Claude 3.5+ | Cowork 任意 |
| v1.1 | Claude 3.5+ | Cowork 任意 |
| **v1.2（当前）** | **Claude 4+**（九维度输出需更强推理） | **Cowork 最新** |

---

## 十、卸载

Cowork → Skills 面板 → 找到 `prototype-replication` → Uninstall。

卸载后：
- 不会删除已生成的原型文档
- 不会影响其它 skill
- 重新安装会覆盖配置

---

## 附：故障排查

| 症状 | 可能原因 | 解决 |
| --- | --- | --- |
| 触发后无响应 | host agent 未加载默认工具 | 让 host 执行 ToolSearch 加载 |
| URL 输入报"无 Chrome" | 未装 Claude in Chrome | §2.1 |
| 输出全是 [N/A] | 输入素材不足以判断 | 补素材或允许"假设型原型"模式 |
| 触发条件冲突（与其它 skill 抢） | description 边界未明确 | 检查 §八，明确告诉用户要"原型"还是"代码/PRD" |
| 九维度只输出 3 条 | host agent 截断 / token 不足 | 拆批生成，每次仅处理 1-2 个交互 |
