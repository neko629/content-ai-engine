# DEPENDENCIES · 依赖矩阵（机器可读）

> 本文档供 host agent 触发 skill 时自动解析依赖。人工可读，但格式严格。
> 严格模式下任一 `required: true` 的依赖缺失即报错退出。

---

## 核心元数据

```yaml
skill_name: prototype-replication
version: 1.2.0
strict_mode: true
min_claude_model: claude-4
min_host: cowork-latest | claude-code | claude-agent-sdk
```

---

## 基础工具依赖（always required）

```yaml
default_tools:
  - name: Read
    required: true
    purpose: 读取上传的截图 / 文档
  - name: Write
    required: true
    purpose: 输出原型文档落盘
  - name: AskUserQuestion
    required: true
    purpose: 素材不足时反问澄清
  - name: TaskCreate
    required: true
    purpose: 长任务进度追踪
  - name: TaskUpdate
    required: true
    purpose: 任务状态更新
  - name: Grep
    required: false
    purpose: 多文档对照
  - name: Glob
    required: false
    purpose: 批量素材定位
  - name: Bash
    required: false
    purpose: 处理压缩包 / 批量素材
```

---

## 按输入类型的条件依赖

```yaml
conditional_dependencies:

  # 当用户输入是 URL / 网页链接
  input_type: url
  required_tools:
    - name: mcp__Claude_in_Chrome__navigate
      install_url: https://docs.claude.com/cowork/claude-in-chrome
      cowork_setting: Settings > Capabilities > Enable Claude in Chrome
    - name: mcp__Claude_in_Chrome__get_page_text
    - name: mcp__Claude_in_Chrome__read_page
    - name: mcp__Claude_in_Chrome__get_screenshot
  on_missing: error  # 严格模式：不降级
  error_message: "URL 类输入需要 Claude in Chrome MCP。详见 INSTALL.md §2.1"

  ---

  # 当用户上传 .pdf
  input_type: pdf
  required_skills:
    - name: anthropic-skills:pdf
  on_missing: error
  error_message: "PDF 输入需要 anthropic-skills:pdf 已安装"

  ---

  # 当用户上传 .docx
  input_type: docx
  required_skills:
    - name: anthropic-skills:docx
  on_missing: error
  error_message: "Word 文档输入需要 anthropic-skills:docx 已安装"

  ---

  # 当用户上传 .xlsx
  input_type: xlsx
  required_skills:
    - name: anthropic-skills:xlsx
  on_missing: error
  error_message: "Excel 文档输入需要 anthropic-skills:xlsx 已安装"

  ---

  # 当用户上传截图 / 图片
  input_type: image
  required_capabilities:
    - claude_multimodal_vision: true
  on_missing: error
  error_message: "需要 Claude 4+ 多模态视觉能力"
```

---

## 按输出形态的条件依赖

```yaml
output_dependencies:

  # 输出为 .docx
  output_type: docx
  required_skills:
    - name: anthropic-skills:docx
  on_missing: error

  ---

  # 输出为 PDF
  output_type: pdf
  required_skills:
    - name: anthropic-skills:pdf
  on_missing: error

  ---

  # 输出含 SVG 流程图 / 状态机
  output_type: svg_diagram
  required_tools:
    - name: mcp__visualize__read_me
    - name: mcp__visualize__show_widget
  on_missing: error

  ---

  # 输出到 Pencil 设计文件
  output_type: pencil
  required_tools:
    - name: mcp__pencil__open_document
    - name: mcp__pencil__batch_design
  on_missing: error

  ---

  # 默认：聊天里直接显示 Markdown
  output_type: chat_markdown
  required: 无额外依赖
```

---

## Cowork 设置依赖

```yaml
cowork_settings:
  - name: Network Access
    required: true (URL 类输入时)
    path: Settings > Network > Enable
  - name: File System Access
    required: true (输出落盘时)
    path: Settings > Files > Connect folder
  - name: Claude in Chrome
    required: true (URL 类输入时)
    path: Settings > Capabilities > Enable Claude in Chrome
  - name: Computer Use
    required: false
    path: Settings > Desktop > Enable Computer use
    note: 本 skill 不需要，可禁用
```

---

## 安全约束

```yaml
security:
  api_keys_needed: false
  network_access:
    when: input_type == url
    targets: 用户提供的具体 URL
    no_third_party_calls: true
  data_persistence:
    where: host agent 工作文件夹
    encrypted: 按 host 自身策略
  sensitive_data_handling:
    rule: SKILL.md §四"涉密素材"
    behavior: 输出前自动脱敏（订单号→***，用户名→user_X）
```

---

## 已知冲突 skills

```yaml
conflicts_with:
  - skill: feature-breakdown
    when: 用户说 "拆功能 + 出原型"
    resolution: 本 skill 仅在"原型"意图明确时触发
  - skill: development-implementation
    when: 用户说 "复刻 + 实现"
    resolution: 本 skill 出原型说明，"实现"让位
  - skill: prd-generator
    when: 用户说 "复刻 + 写 PRD"
    resolution: 本 skill 出原型说明，PRD 让位
```

---

## 自检引用

```yaml
self_check_file: ./self-check.md
self_check_on: first_trigger
self_check_blocking: true  # 严格模式：失败即退出
```

---

## 版本兼容矩阵

```yaml
compatibility:
  - skill_version: 1.0.0
    min_claude_model: claude-3.5
    min_host: any
  - skill_version: 1.1.0
    min_claude_model: claude-3.5
    min_host: any
  - skill_version: 1.2.0       # current
    min_claude_model: claude-4
    min_host: cowork-latest
```

---

## 维护者

```yaml
maintainer: 用户自定义
license: 自定义（本 skill 包含 Anthropic skill format，使用前请确认许可）
```
