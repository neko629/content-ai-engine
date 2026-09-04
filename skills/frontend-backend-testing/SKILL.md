---
name: frontend-backend-testing
version: 2.2.0
author: Krisxt Campbelluq
license: MIT
description: |
  前后端功能/UI 布局/接口契约/代码质量/状态流转/权限角色系统性测试 Skill。含 4 模式（全量速测/分项深测/增量回归/测试编排）、21 维度（17 业务质量+4 代码工程）、7 类测试设计方法、5 大常见 Bug 库、6 端到端示例，强制 agentic 工具实测（Read/Grep/Bash/Chrome/Pencil）而非纸上推理，输出测试范围/测试点/用例表/Bug 清单/复现步骤/修改建议/回归建议。
  【必须触发】用户明确表达系统性测试或评审意图：(1) 主动要求"做一次完整测试/QA/质量评审/代码审查/UI 走查/原型走查/接口验收/回归/上线前检查/安全/性能/兼容性/权限/边界值/异常/状态流转测试"；(2) 要求产出测试用例/测试点/检查清单/Bug 清单/缺陷报告/测试报告/测试计划/测试矩阵/回归建议；(3) 提供原型/UI 稿/Figma/接口文档/PRD/代码仓库/Bug 单/PR/运行环境并附"测/检查/验收/走查/评审/找 Bug"意图；(4) 描述 Bug 现象+希望整理或追根；(5) 出现"前后端联调/PR Review/迭代回归/冒烟/E2E"等关键词组合。
  【不应触发】(a) 只是写单测代码本身；(b) A/B 测试/灰度/内测公测等运营场景；(c) 概念问答（"什么是边界值"）；(d) 比喻性测试（测网速/心跳）；(e) 压测脚本/CI 配置等纯工程任务；(f) ML 模型评测；(g) 仅口头提一句但无材料无目标——先 AskUserQuestion 澄清。
  【触发承诺】按流程：确认输入→选模式→Read 维度文件→调方法库→工具实测→结构化输出→质量门禁自检。未实测项必须显式标"未实测，待验证"，绝不臆造。详细触发场景及示例见 SKILL.md 正文"二、何时触发本 Skill"。
---

# 前后端功能与 UI 测试 Skill v2

本 Skill 用于对 Web 系统、后台管理系统、移动端 H5、小程序等的页面、功能、接口、代码、数据进行系统性测试，输出测试范围、测试点、测试用例、问题清单、复现步骤、修改建议和回归建议。

---

## 一、Skill 入口流程（必读）

收到测试请求时，按以下顺序执行：

### 步骤 1：确认输入信息

参照下方"输入清单"快速盘点用户已提供的材料。任意一项缺失但非关键即可继续；信息严重缺失时一次性向用户问 1–3 个关键问题（不要逐条追问）。

### 步骤 2：选择测试模式

读取 `modes/` 下对应文件，按其流程推进。如不确定，默认走 **分项深测**（深度优先，逐项展开）。

| 模式 | 适用场景 | 对应文件 |
|---|---|---|
| 全量速测 | 项目上线前快速过一遍、时间紧 | `modes/full-scan.md` |
| **分项深测**（默认） | 用户要求"逐项测试"、单一维度深入 | `modes/deep-dive.md` |
| 增量回归 | Bug 修复 / 代码 diff / 迭代回归 | `modes/regression.md` |
| 测试编排 | 复杂项目、需先规划再执行 | `modes/orchestration.md` |

### 步骤 3：完成"测试输入分析"

在写任何测试用例之前，**必须**先把输入原料结构化提取，避免直接跳到用例输出。提取内容：

- 原型 → 交互节点 / 状态机 / 跳转图
- UI 稿 → 设计 token / 组件状态矩阵 / 断点表
- 接口文档 → 契约表 / 错误码全集
- 需求文档 → 业务规则表 / 验收标准
- 代码 → 路由表 / 组件树 / 接口调用关系（可选）

如分析阶段缺信息，输出"已知 vs 待补"两栏，再继续。

### 步骤 4：按选定模式 + 选定维度执行测试

对每个涉及的维度，Read `dimensions/<NN-name>.md`，按其 Checklist + 测试方法 + Bug 模式库 + 通过判定 执行。

### 步骤 5：按输出标准产出结果

参照 `templates/test-report.md` 标准结构输出。复杂场景调用 `methods/` 下的测试设计方法（等价类 / 边界值 / 状态迁移 / 判定表 / 错误推测 / 正交组合 / 场景法）。

### 步骤 6：质量门禁自检

输出前对照"完成标准"自检，未达标项要么补齐，要么显式标注"未覆盖原因"。

---

## 二、何时触发本 Skill

frontmatter 的 description 字段已给出压缩版触发判定（受 1024 字符限制），本节是**完整版判定细则**，触发前 Claude 必须按本节判断，避免误触发或漏触发。

### 2.1 必须触发的 5 类场景

只有当用户**明确表达系统性测试或质量评审意图**时才触发本 Skill：

**(1) 用户主动提出测试动作**
典型表达：
- "对这个页面/功能/接口/模块做一次完整测试"
- "帮我做产品功能测试"
- "做一次 QA / 质量评审 / 代码审查 / Code Review / PR Review"
- "做一次 UI 走查 / 原型走查 / 接口验收 / 接口联调"
- "做一次回归测试 / 上线前检查 / 灰度前检查"
- "做一次安全测试 / 性能测试 / 兼容性测试 / 权限测试"
- "做一次边界值测试 / 异常场景测试 / 状态流转测试"
- "做一次冒烟测试 / E2E 测试 / 端到端测试 / 白盒 / 黑盒测试"

**(2) 用户要求产出测试交付物**
典型表达：
- "帮我写测试用例 / 测试点 / 检查清单 / Bug 清单"
- "输出缺陷报告 / 问题记录 / 测试报告 / 测试计划 / 测试矩阵 / 回归建议"

**(3) 用户提供测试原料 + 测试意图**
原料：原型图、UI 设计稿、Figma 链接、Pencil / .pen 文件、接口文档、OpenAPI、Postman 集合、需求文档、PRD、代码仓库、Git 分支、Bug 单、PR / Commit、运行环境地址、测试账号  
+ 意图词：测一下 / 检查 / 验收 / 走查 / 评审 / 找 Bug / 看看有什么问题  
满足"原料 + 意图"组合即触发。

**(4) 用户描述具体 Bug 现象 + 希望整理或追根**
典型表达：
- "这个地方有问题，帮我整理成 Bug 单"
- "帮我看可能哪里出错"
- "帮我写复现步骤"
- "帮我评估这个 Bug 的影响面"

**(5) 出现明确的测试场景关键词组合**
任一明确出现即触发：
"前后端联调"、"页面验收"、"接口验收"、"UI 走查"、"原型走查"、"代码审查 / Code Review"、"PR Review"、"上线前检查"、"灰度前检查"、"迭代结束回归"、"冒烟测试"、"E2E 测试"、"端到端测试"、"白盒测试"、"黑盒测试"。

### 2.2 不应触发的 7 类场景

只是顺口提到"测试"二字或谈论与本 Skill 无关话题时**不要触发**，避免抢戏：

**(a) 用户在写单元测试代码本身**
例："帮我写一个 Jest 测试函数 / 一个 pytest 测试方法"——属于纯写代码任务，由通用编码处理。  
**例外**：用户明确说"我要对这个项目做单测覆盖率审查 / 单测质量评估"——此时触发，进入维度 19。

**(b) 用户在做 A/B 测试 / 灰度测试 / 用户测试 / 内测 / 公测**
属于产品运营或市场测试讨论，与软件质量测试无关，不触发。

**(c) 用户只是询问测试相关的概念性问题**
例："什么是边界值测试 / 黑盒和白盒的区别 / 测试金字塔是什么"——属科普问答，按对话答复即可，不要套用 Skill 模板。

**(d) 用户只是用了"测一下"做口头比喻**
例："测一下网速"、"测一下心跳"、"测一下我对你的爱"——非软件场景，不触发。

**(e) 用户在做压测脚本编写 / 自动化测试框架搭建 / CI 配置**
属于纯工程任务，不触发。  
**例外**：用户明确要求"按测试方法论检查我们的脚本是否覆盖足够"——此时触发，进入分项深测。

**(f) 用户在做机器学习模型评测 / 数据集质量评估 / 算法精度测试**
属于 ML 领域，不在本 Skill 范畴。

**(g) 用户只轻提一句但无材料无目标**
例："我想测一下 / 等会儿要测"但没有任何输入材料和明确目标——应**先按 AskUserQuestion 澄清范围与材料**，不要直接套 Skill 模板硬输出。

### 2.3 判定流程（建议 Claude 按此顺序）

```
收到请求
  ├─ 是否落入 2.2 不应触发的 (a)–(g)？
  │     是 → 按对话/编码处理，不触发
  │     否 → 下一步
  ├─ 是否落入 2.1 必须触发的 (1)–(5)？
  │     是 → 触发本 Skill，进入步骤 1（确认输入）
  │     否 → 模糊场景，判断关键词倾向
  └─ 模糊场景：含"测/质量/Bug/检查"但意图不明
        → 用 AskUserQuestion 澄清后再决定

---

## 三、Agentic 工具使用规约（重要）

本 Skill 严禁"纸上谈兵"。能用工具实测的部分必须实测，不能只靠推理。

| 测试动作 | 推荐工具 |
|---|---|
| 看代码 / 找定义 / 找引用 | Read · Glob · Grep |
| 跑 lint / 单测 / 构建 / 依赖扫描 | Bash（`npm run lint/test/build`，`npm audit`，`pip check`） |
| curl 接口 / 看日志 / 看端口 | Bash |
| 实测页面（点击、渲染、控制台、网络） | `mcp__Claude_in_Chrome__navigate` · `get_page_text` · `read_console_messages` · `read_network_requests` · `get_screenshot` |
| 读 .pen 设计稿 | `mcp__pencil__open_document` · `batch_get` · `get_screenshot` · `get_variables` |
| 输出测试用例表 | `xlsx` Skill |
| 输出测试报告 | `docx` Skill |
| 输出评审稿 | `pptx` Skill / `pdf` Skill |

**铁律**：

1. **未实测必标注**：任何未经工具实测的结论，必须在用例 / 问题清单的"实际结果"栏标注"未实测，待验证"。
2. **可执行优先**：如果有代码仓库或运行环境可用，先跑通工具链（lint/test/build/接口探测），再进入业务测试。
3. **不臆造**：信息缺失时不要臆造结论，标注"待用户补充"，并继续推进其他可测部分。
4. **每个用例可复现**：复现步骤必须具体到"点哪个按钮、填什么内容、走到哪一步"。

---

## 四、测试输入清单（开始前确认）

按需补齐，不必全部要求：

1. **产品原型 / 原型说明**：用于判断功能逻辑与交互
2. **UI 设计稿 / 页面截图 / .pen 文件路径**：用于检查样式
3. **接口文档 / OpenAPI / Postman 集合**：用于核对契约
4. **需求文档 / PRD / 验收标准**：用于理解业务规则
5. **代码仓库路径 / Git 分支**：用于代码层测试
6. **页面地址 / 运行环境**：用于实测
7. **角色与权限说明**：用于权限测试
8. **测试账号与数据**：用于功能测试
9. **已知问题 / 高风险点**：用于优先级判定
10. **此次测试目标 / 范围 / 时间盒**：用于选择模式

---

## 五、21 个测试维度索引

详细内容见 `dimensions/<NN-name>.md`，每个维度独立 Read。

**业务功能层（1–10）**
- 01 原型交互测试 — `dimensions/01-prototype-interaction.md`
- 02 页面 UI 布局测试 — `dimensions/02-ui-layout.md`
- 03 前后端接口联调 — `dimensions/03-api-integration.md`
- 04 数据传输与落库 — `dimensions/04-data-persistence.md`
- 05 输入校验与边界值 — `dimensions/05-input-validation.md`
- 06 异常场景与容错 — `dimensions/06-exception-handling.md`
- 07 权限与角色 — `dimensions/07-permission-role.md`
- 08 登录态与会话 — `dimensions/08-session-auth.md`
- 09 搜索/筛选/排序/分页 — `dimensions/09-list-operations.md`
- 10 状态流转 — `dimensions/10-state-transition.md`

**通用质量层（11–17）**
- 11 文件上传下载导入导出 — `dimensions/11-file-io.md`
- 12 兼容性 — `dimensions/12-compatibility.md`
- 13 性能与响应速度 — `dimensions/13-performance.md`
- 14 安全性 — `dimensions/14-security.md`
- 15 日志与可观测性 — `dimensions/15-observability.md`
- 16 回归测试 — `dimensions/16-regression.md`
- 17 用户体验 — `dimensions/17-ux.md`

**代码工程层（18–21，v2 新增）**
- 18 代码静态分析 — `dimensions/18-static-analysis.md`
- 19 单元 / 集成测试 — `dimensions/19-unit-integration-test.md`
- 20 代码可维护性 — `dimensions/20-code-maintainability.md`
- 21 依赖与构建 — `dimensions/21-dependencies-build.md`

每个维度文件统一结构：**Checklist · 测试方法 · 常见 Bug 模式 · 通过判定**。

---

## 六、测试设计方法库索引

复杂场景需调用方法库穷举测试条件：

- 等价类划分 — `methods/equivalence-partitioning.md`
- 边界值分析 — `methods/boundary-value.md`
- 判定表 — `methods/decision-table.md`
- 状态迁移图 — `methods/state-transition.md`
- 错误推测法 — `methods/error-guessing.md`
- 正交组合 — `methods/orthogonal-array.md`
- 场景法（端到端） — `methods/scenario-based.md`

---

## 七、模板与 Bug 库索引

- 测试报告模板 — `templates/test-report.md`
- 测试计划模板 — `templates/test-plan.md`
- 测试用例表模板 — `templates/test-case.md`
- Bug 报告模板 — `templates/bug-report.md`
- 测试矩阵模板 — `templates/test-matrix.md`
- UI 常见 Bug 库 — `checklists/ui-common-bugs.md`
- 接口常见 Bug 库 — `checklists/api-common-bugs.md`
- 状态流转常见 Bug — `checklists/state-common-bugs.md`
- 权限常见 Bug 库 — `checklists/permission-common-bugs.md`
- 性能常见 Bug 库 — `checklists/performance-common-bugs.md`

---

## 八、示例索引

调用前可 Read 对应示例对齐输出风格：

- 登录模块 — `examples/login.md`
- 表单 + 校验 — `examples/form-validation.md`
- 列表 + 筛选 + 分页 — `examples/list-filter-pagination.md`
- 文件上传 — `examples/file-upload.md`
- 权限角色 — `examples/permission-role.md`
- 状态流转（订单） — `examples/state-transition-order.md`

---

## 九、与其他 Skill 协作

本 Skill 负责"测试内容"，文件交付交给输出类 Skill：

- 测试报告 .docx → 结合 `docx` Skill
- 测试用例 .xlsx → 结合 `xlsx` Skill
- 测试 PDF → 结合 `pdf` Skill
- 评审 PPT → 结合 `pptx` Skill

---

## 十、质量门禁（完成标准）

测试视为"完成"必须满足：

1. 17 业务/质量维度每个至少 1 个测试点（不适用维度需显式说明原因）
2. 涉及代码访问的项目，代码工程层 4 维度至少跑过 lint + build + 已有单测
3. P0 路径（主流程 + 数据安全 + 权限控制）100% 覆盖
4. 每个 Bug 有可复现步骤
5. 每个用例可被客观判定（不写"显示正常"这种模糊描述）
6. 至少给出 1 条回归建议
7. 所有未实测项显式标注"未实测，待验证"

不满足上述任一条，必须在报告顶部"质量门禁状态"区域显式列出未达标项与原因。
