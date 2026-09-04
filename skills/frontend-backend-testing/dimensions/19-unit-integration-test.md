# 维度 19 · 单元 / 集成测试（v2 新增）

> 检查代码自身的测试覆盖、关键路径有无测试、mock 是否合理。

## Checklist

### 覆盖率
- 单测覆盖率达基线（行 / 分支 / 函数 / 语句）
- 关键模块 / 核心算法 / 工具函数有专项测试
- 异常路径有测试（不只测 happy path）

### 测试质量
- 测试名描述清晰（"应该返回 X 当 Y"）
- 每个测试只测一件事
- 无相互依赖（测试可独立运行 / 乱序）
- mock 不过度（mock 太多 = 测了寂寞）
- 集成测试覆盖关键链路

### 接口契约测试
- 后端接口有契约测试（schema 校验）
- 前端 mock 与真实接口一致（避免上线翻车）

### 端到端
- E2E（Playwright / Cypress）覆盖主流程
- E2E 用例稳定（避免 flaky test）

## 测试方法

```bash
# 跑测试 + 看覆盖率
npm run test -- --coverage
npm run test:e2e
pytest --cov

# 看覆盖率报告
open coverage/lcov-report/index.html

# 找未测的关键文件
git diff --name-only HEAD~5 | grep -E '\.(ts|js|tsx|jsx)$' | \
  xargs -I{} sh -c 'test -f "{}.test.ts" || test -f "{}.spec.ts" || echo "no test: {}"'
```

## 常见 Bug 模式

- 覆盖率 30% 还自称"有测试"
- 只测 happy path
- 测试与实现耦合（改实现一定改测试）
- mock 过深，测试 = 测 mock 不是测代码
- E2E 不稳定，被禁用了
- 关键模块（鉴权、支付、状态机）零测试

## 通过判定

- 覆盖率达团队基线（典型：行 ≥ 70%、分支 ≥ 60%、关键模块 ≥ 90%）
- 关键模块异常路径有测试
- 测试稳定（无 flaky）
- 接口契约测试存在
