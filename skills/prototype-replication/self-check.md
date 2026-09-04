# SELF-CHECK · 加载时自检指令

> 本文档供 host agent 在首次触发本 skill 时**强制执行**。
> 严格模式下任一项失败立即报错退出。

---

## host agent 必须按以下顺序执行

### Step 1 · 基础工具检查

```
检查并加载（ToolSearch）：
- Read
- Write
- AskUserQuestion
- TaskCreate
- TaskUpdate

若任一加载失败 → 报错：
"严格模式下，本 skill 需要 Read / Write / AskUserQuestion / TaskCreate / TaskUpdate 全部可用。
请确认 host agent 已正确配置默认工具集。详见 INSTALL.md §1.2"
→ 退出
```

### Step 2 · 多模态视觉检查

```
若用户上传了图片素材：
  确认 Claude 模型版本 ≥ Claude 4

若 < Claude 4 → 报错：
"本 skill 严格模式要求 Claude 4+ 多模态视觉能力。当前模型版本不足。
请升级模型或改用纯文本素材输入。详见 INSTALL.md §1.1"
→ 退出
```

### Step 3 · 按输入类型条件检查

```
根据用户输入类型，执行对应检查：

if input_type == 'url':
  ToolSearch(query="select:mcp__Claude_in_Chrome__navigate")
  若加载失败 → 报错：
    "URL 输入需要 Claude in Chrome MCP。
    安装路径：Cowork → Settings → Capabilities → Enable Claude in Chrome。
    详见 INSTALL.md §2.1"
  → 退出

elif input_type == 'pdf':
  检查 anthropic-skills:pdf 已安装
  若未安装 → 报错：
    "PDF 输入需要 anthropic-skills:pdf 已安装。详见 INSTALL.md §2.2"
  → 退出

elif input_type == 'docx':
  检查 anthropic-skills:docx 已安装
  若未安装 → 报错并退出

elif input_type == 'xlsx':
  检查 anthropic-skills:xlsx 已安装
  若未安装 → 报错并退出

elif input_type == 'image':
  视觉能力已在 Step 2 检查，跳过

elif input_type == 'text' / 'markdown':
  无额外检查
```

### Step 4 · 按输出形态条件检查

```
若用户明确要求输出 .docx：
  检查 anthropic-skills:docx → 缺失则报错

若用户明确要求输出 PDF：
  检查 anthropic-skills:pdf → 缺失则报错

若用户明确要求输出 SVG 流程图：
  ToolSearch(query="select:mcp__visualize__show_widget")
  缺失则报错

若用户明确要求落地 Pencil：
  ToolSearch(query="select:mcp__pencil__open_document")
  缺失则报错

若仅输出聊天 Markdown：跳过此 step
```

### Step 5 · 触发意图二次校验

```
本 skill 触发后必须满足以下硬条件之一：

A. 用户素材包含以下任一：
   - 图片素材（截图、UI 设计稿）
   - URL 链接
   - .pdf / .docx / .xlsx 文件
   - 结构化文本（PRD、功能清单、页面分析）

B. 用户明确表示"按你的理解假设生成"

若两者都不满足：
  调用 AskUserQuestion 反问：
    "请提供以下任一素材以触发原型复刻：
     1. 截图 / UI 设计稿
     2. 页面链接
     3. PRD 或功能清单文档
     或明确告诉我『按你的理解假设生成』。"
  → 暂停本 skill，等用户回复
```

### Step 6 · meta 问询识别

```
若用户消息为以下任一格式 → **不触发** skill：
- "复刻原型这个 skill 是什么"
- "复刻原型会触发哪个 skill"
- "这句话会触发吗"
- "怎么使用复刻原型"
- "复刻原型有什么用"
- "skill 文档在哪"

→ 正常回答 meta 问题，不调用 skill 流程
```

### Step 7 · 边界冲突检查

```
若用户消息同时包含以下意图组合 → 提示让位：

- "复刻 + 写代码" / "复刻 + 实现" → 让位 development-implementation
  回复："本 skill 仅出原型说明文档。如需可运行代码，
        请用 development-implementation skill。是否继续按原型输出？"

- "复刻 + 写 PRD" → 让位 prd-generator
  回复："本 skill 仅出原型说明。如需 PRD，请用 prd-generator skill。"

- "复刻 + 拆功能" → 让位 feature-breakdown
  回复："本 skill 仅出原型说明。如需功能清单，请用 feature-breakdown skill。"

用户确认仅要原型 → 继续；否则 → 让位
```

---

## 执行流程总结

```
触发 skill
  ↓
Step 1 默认工具检查
  ↓
Step 2 模型版本检查
  ↓
Step 3 输入类型依赖检查
  ↓
Step 4 输出形态依赖检查
  ↓
Step 5 触发意图二次校验
  ↓
Step 6 meta 问询识别
  ↓
Step 7 边界冲突检查
  ↓
（全部通过）→ 进入 SKILL.md 主流程
  ↓
（任一失败）→ 报错退出 + 引用 INSTALL.md 对应章节
```

---

## 缓存策略

```
self-check 结果可缓存到本次 host agent session：
- 默认工具检查：缓存
- 模型版本检查：缓存
- 输入类型依赖：每次输入检查
- 输出形态依赖：每次输出选择检查
- 触发意图校验：每次触发执行
- meta 问询识别：每次触发执行
- 边界冲突检查：每次触发执行
```

---

## 调试模式

若用户加 `--debug` 或 `调试模式` → host agent 输出所有 self-check 步骤的详细结果（哪些 pass / 哪些 fail / 哪些 cache hit），方便排查。
