# 维度 21 · 依赖与构建（v2 新增）

> 依赖漏洞、构建产物、环境配置一致性。

## Checklist

### 依赖
- 依赖项版本锁定（lock 文件提交）
- 无已知 CVE 高危漏洞
- 无未维护的依赖（最近一次更新 > 2 年）
- 无重复依赖（多版本共存）
- 生产依赖 vs 开发依赖区分正确
- 许可证合规（GPL / 商用限制）

### 构建
- 构建可重现（同代码同 lock 文件，结果一致）
- 产物大小符合预期
- 产物无源码泄露（无 sourceMap 上线 / 已混淆）
- 环境变量正确注入
- 构建警告无遗漏

### 环境配置
- dev / staging / prod 配置隔离
- 配置不含明文密钥（用环境变量 / secrets manager）
- 配置变更有审计
- 多环境差异可对照

### CI/CD
- CI 跑全部检查（lint / test / build / audit）
- CI 失败阻塞合入
- 部署有回滚能力
- 灰度 / 蓝绿 / 金丝雀策略

## 测试方法

```bash
# 依赖漏洞
npm audit
yarn audit
pip-audit
trivy fs .

# 重复依赖
npm ls --all | grep -E 'deduped|UNMET'
npx depcheck

# 产物大小
ls -lah dist/
du -sh dist/
npx source-map-explorer dist/*.js

# 许可证
npx license-checker --summary

# 环境配置
git grep -nE '(password|token|secret)\s*=' . | grep -v '\.env\.example'
```

## 常见 Bug 模式

- package-lock.json 没提交 → 不可重现
- 依赖有高危 CVE 但没人盯
- 死依赖（未使用但还在 deps）
- sourceMap 上线 → 源码泄露
- 配置文件含明文密钥
- 没有 CI / CI 不阻塞
- 灰度策略缺失，全量上线

## 通过判定

- audit / scan 无高危漏洞
- lock 文件已提交
- 构建可重现
- 配置无明文密钥
- CI/CD 链路完整
