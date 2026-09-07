# content-ai-engine

> 把大模型/多模态能力做成「**可运营、可治理、可计量**」的内容 AI 加工链 —— 一个**零第三方依赖、离线即可运行**的参考实现。

一条内容从「裸标题/裸正文」到「**审核通过 + AI 改写标题 + AI 生成封面**」的完整加工链，附一套把 LLM 输出当**可靠工程**对待的模式：

- **多模型统一网关**：供应商与模型全部数据化（config），业务按**用途**调用；候选逐个尝试、失败自动降级（fallback）到兜底模型。
- **质量工程**：标题改写 → 强清洗 → 拒答检测 → 降温度重试；SD 提示词带缓存、失败不写缓存。
- **内容治理**：LLM 文本审核（固定类别 + JSON 输出）+ **fail-open** 取舍。
- **结构化输出**：容错 JSON 解析（代码围栏 / 单引号 / 尾逗号 / 大写布尔）→ 结构校验 → **带错误反馈重试**。
- **可观测可计量**：每次调用记审计（谁 / 哪个模型 / 多少 token / 成败），用量计数防热点、支持定时回刷语义。

默认 **Mock 模型**让整条链无需任何 key 就能跑通（顺便演示"供应商挂了自动降级"）；配置两个环境变量即切换到任意 **OpenAI 兼容**端点。

完整生产系统的背景、设计过程、关键取舍和问题改进见 [设计与改进文档](docs/design-process.md)。

---

## 目录结构

```
content-ai-engine/
├── aiengine/                # 参考实现核心（Python 3.10+ 标准库）
│   ├── config.py            #   模型/用途配置加载（数据化、无硬编码）
│   ├── gateway.py           #   LLM 统一网关：候选挑选/负载均衡/降级/mock
│   ├── usage.py             #   用量计量与调用审计
│   ├── moderation.py        #   文本内容审核（fail-open）
│   ├── title.py             #   AI 标题改写（清洗/拒答检测/降温度重试）
│   ├── cover.py             #   封面：SD 提示词(缓存) → 文生图 → 标记回写
│   ├── json_repair.py       #   容错 JSON 解析 + 结构校验 + 带反馈重试
│   ├── images.py            #   占位图生成（纯标准库）/ 可选真文生图端点
│   ├── pipeline.py          #   编排：审核→标题→封面 / 批量 / 分镜演示
│   ├── webserver.py         #   零依赖 HTTP demo 服务
│   └── cli.py               #   命令行入口
├── config/models.json       # 模型候选与用途映射（改这里即可切模型/供应商）
├── web/index.html           # 交互演示页
├── server.py                # 快捷入口：python3 server.py
├── tests/smoke.py           # 离线冒烟测试
├── skills/                  # 附：AI 驱动研发工作流 Skill 集（详见 README 末尾）
├── requirements.txt
└── LICENSE
```

## 架构

```
业务/页面                    编排( pipeline )                LLM 统一网关( gateway )
─────────────              ───────────────               ─────────────────────────
一条内容标题/正文   →   ① 文本审核 moderation  ───►  purpose=moderation ┐
                       ② 标题改写 title      ───►  purpose=title      ├─► 候选逐个尝试
                       ③ 封面 cover           ───►  purpose=sd_prompt  │   失败自动 fallback
                       (结构化输出 storyboard)──►  purpose=storyboard ┘      ↓ 兜底
                                                                      config/models.json
   输出：审核结果 + 改写标题 + 封面(data-uri)         每次调用写入 ──► usage.py（审计+计量）
```

---

## 快速开始

**要求**：Python 3.10+（**无任何第三方依赖**）。

```bash
# 1) 命令行跑一条加工链（离线、Mock 模型）
python3 -m aiengine.cli run "雨夜逆袭：少年觉醒异能" --text "正文用于审核"

# 2) 批量（含空标题 → skipped 语义）
python3 -m aiengine.cli batch

# 3) 演示「脏 JSON → 容错解析/校验/重试」
python3 -m aiengine.cli storyboard "深夜书店"

# 4) 起网页 demo
python3 server.py                 # 打开 http://127.0.0.1:8010
python3 -m aiengine.cli serve     # 同上

# 5) 离线自检 / 冒烟
python3 -m aiengine.cli selftest
python3 tests/smoke.py
```

### 接真实模型（任意 OpenAI 兼容端点）

```bash
export LLM_BASE_URL=https://api.openai.com/v1   # 或任意兼容网关
export LLM_API_KEY=sk-...
python3 server.py
```

未配置时，`primary`（openai_compatible）会失败并自动降级到 `fallback`（mock），
调用审计里能看到 `status=fallback` —— 这正是网关降级设计的一次现场演示。

---

## API

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/` | 交互演示页 |
| GET | `/api/health` | 健康检查 |
| GET | `/api/usage` | 用量快照 + 最近调用审计 |
| POST | `/api/pipeline` | `{"title": "...", "text": "..."}` 单条加工链 |
| POST | `/api/batch` | `{"titles": ["..."]}` 批量（ok/skipped/failed） |
| POST | `/api/storyboard` | `{"theme": "..."}` 脏 JSON 容错解析演示 |

## 与生产的对应关系（设计来源）

本项目是**参考实现**：从一套服务真实内容的"内容生产运营中台"中提炼出的可运行骨架。
生产中的对应做法（本仓库不含业务实现，仅保留模式）：

| 参考实现 | 生产形态 |
|---|---|
| `gateway` 候选/降级 | DB 化的模型配置 + 负载均衡/回退 + key 加密存储 |
| `usage` 内存计数 + 审计 | Redis 热 key 计数（避免 DB 热行）+ 定时批量回刷 |
| `images` 占位图 | 文生图供应商任务：提交 → 轮询(45s×80) → 自愈兜底 → 完成写回 |
| `cover` SD 缓存 | Redis 提示词缓存（24h，失败不写） |
| `pipeline` 单条/批量 | Celery 异步投递 + 批量 max_concurrency + 业务级 ok/skipped/failed |

> 一句话：**模型来自外部商业能力，工程价值在上层** —— 把"不稳定的 LLM 输出"变成
> "可配置、可编排、可审计、可计费、可兜底"的生产能力，并接到真实业务闭环。

---

## 附：AI 驱动研发工作流 Skill（`skills/`）

仓库还附带一套可复用的 **AI 研发工作流 Skill**（在 Claude Code / Codex 等 Agent 环境中运行），
把"一句话需求 → 交付物"沉淀成一条可预期流水线：

```
feature-breakdown → prd-generator → prototype-replication → development-implementation → frontend-backend-testing
   需求拆解             PRD              高保真原型               代码实现                   系统测试/验收
```

每个 Skill 的要点是**把方法论文本化**：触发门禁、防臆测（材料缺失先反问）、一致性自检、
强制 agentic 实测而非纸上推理。用法（以 Claude Code 为例）：
在任一项目中用 `/prd-generator …` 一类触发词调用；或直接阅读各 `SKILL.md` 了解方法体系。

---

## License

MIT
