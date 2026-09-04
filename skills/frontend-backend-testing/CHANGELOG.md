# Changelog

本 Skill 遵循 [Semantic Versioning](https://semver.org/)。

## [2.2.0] — 2026-06-04

### 修复
- **重大**：description 字段超出 Cowork 1024 字符上限导致安装失败。压缩至 780 字符。
- 详细触发条件 (5 类必触发 + 7 类不应触发) 从 description 搬到正文 §2.1 / §2.2，并新增 §2.3 判定流程图。
- frontmatter 加入 version / author / license 元信息。

### 新增
- VERSION、README.md、CHANGELOG.md、INSTALL.md、LICENSE 5 个发行文件。
- 多 Agent 安装指南（Cowork / Claude Code / Claude Agent SDK）。

### 影响
- 功能能力 0 变化；仅触发判定精度提升 + 元信息规范化。

## [2.1.0] — 2026-06-03（已废弃）

### 新增
- description 中加入 5 类必触发场景 + 7 类不应触发场景 + 触发后工作风格承诺。

### 已知问题
- description 长度 2050 字符超过 Cowork 1024 限制，无法安装。请用 v2.2.0。

## [2.0.0] — 2026-06-03

### 重大变更
- 从单文件 SKILL.md（12.5KB）重构为目录型 Skill（204KB / 49 文件）。
- 4 种测试模式分流（全量速测 / 分项深测 / 增量回归 / 测试编排）。
- 21 个测试维度统一结构（Checklist + 测试方法 + Bug 模式库 + 通过判定）。
- 新增代码工程层 4 维度（静态分析 / 单测 / 可维护性 / 依赖构建）。
- 引入 7 类测试设计方法库。
- 引入 5 大常见 Bug 模式库。
- 6 个端到端测试示例。
- Agentic 工具使用规约 + "未实测必标注"铁律。
- 7 条质量门禁完成标准。

## [1.0.0] — 2026-05-14（初版）

### 初版
- 单文件 SKILL.md。
- 17 个测试维度（每维度一句话描述）。
- 测试用例 / Bug 报告模板。
- 1 个登录示例。

### 局限
- 维度只是"清单"，缺方法论；
- 一次性输出 21 维度报告，无法逐项深入；
- 没有代码层测试；
- 没有 agentic 工具规约。

[2.2.0]: https://semver.org/
[2.1.0]: https://semver.org/
[2.0.0]: https://semver.org/
[1.0.0]: https://semver.org/
