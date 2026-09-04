# 维度 18 · 代码静态分析（v2 新增）

> 用工具检查代码层问题：lint、类型、复杂度、未使用代码、安全模式。

## Checklist

### Lint
- ESLint / TSLint / Stylelint / Prettier 配置存在且严格
- 无 disable 滥用（`eslint-disable` 大段）
- CI 中 lint 是 blocking

### 类型
- TypeScript strict 模式开启
- 无 `any` 滥用（统计占比）
- 无 `@ts-ignore` 滥用
- 接口 / API 响应有类型定义

### 复杂度
- 函数行数 / 圈复杂度 / 嵌套深度
- 文件行数（单文件 < 500 行参考线）
- 重复代码率（jscpd / sonar）

### 死代码
- 未使用变量 / 函数 / 导入 / 文件
- 未引用的路由 / 组件

### 安全模式
- 用 `eval` / `Function` 构造器
- innerHTML / dangerouslySetInnerHTML 未过滤
- 硬编码密钥 / Token
- console.log 泄露敏感信息（生产环境）

## 测试方法

```bash
# Node
npm run lint
npx eslint . --max-warnings=0
npx tsc --noEmit
npx jscpd src/ --min-lines 5

# Python
ruff check .
mypy .
bandit -r src/

# 通用
git grep -nE 'TODO|FIXME|HACK' src/
git grep -nE 'console\.(log|debug)' src/
git grep -nE 'eslint-disable' src/
git grep -nE '\bany\b' --include='*.ts' --include='*.tsx' src/ | wc -l
```

## 常见 Bug 模式

- TS strict 关闭，类型形同虚设
- `any` 占比 > 10%
- 大量 `@ts-ignore` 掩盖问题
- ESLint 一片 disable
- 单文件 1000+ 行未拆分
- 重复代码率 > 5%
- 硬编码密钥被提交到仓库
- 死代码 / 未引用导出
- console.log 留在生产代码

## 通过判定

- lint / type-check / build 三连 PASS
- `any` 占比 ≤ 5%（或符合团队基线）
- 无硬编码密钥（git-secrets / trufflehog 扫过）
- 重复代码率 ≤ 团队基线
- 无未使用导出（dead code 扫描）
