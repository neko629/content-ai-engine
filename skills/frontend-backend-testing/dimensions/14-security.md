# 维度 14 · 安全性测试

> 检查是否存在越权访问、敏感信息泄露、XSS、SQL 注入、恶意文件上传等风险。

## Checklist

### 认证与授权
- 越权（横向 / 纵向）→ 见维度 07
- Token 安全（存储 / 传输 / 时效）→ 见维度 08
- 密码策略（长度 / 复杂度 / 历史 / 锁定）

### 输入安全
- XSS：富文本 / 用户名 / 评论 / URL 参数
- SQL 注入：搜索 / 排序参数 / ID
- 命令注入：上传文件名 / 配置项
- SSRF：用户提供的 URL 被服务端访问
- XXE：XML 解析
- 反序列化：JSON / pickle
- 模板注入：邮件模板 / 富文本

### 输出安全
- 错误信息泄露内部栈
- 接口返回敏感字段（密码 hash / 内部 ID）
- 日志记录密码 / Token / 个人信息
- 报错回显 SQL 语句

### 传输安全
- HTTPS 强制 / HSTS
- TLS 版本（≥ 1.2）
- 混合内容（HTTPS 页面加载 HTTP 资源）
- Cookie：HttpOnly / Secure / SameSite

### CSRF
- POST 是否带 CSRF Token
- SameSite Cookie 策略

### 其他
- 点击劫持（X-Frame-Options / CSP frame-ancestors）
- 内容安全策略（CSP）
- 子资源完整性（SRI）
- CORS 配置不过松
- 依赖漏洞（npm audit）

## 测试方法

1. 用 OWASP ZAP / Burp Suite（如允许）
2. 手动构造 payload：`<script>alert(1)</script>`、`' OR 1=1--`、`{{7*7}}`
3. Bash 跑 `npm audit` / `pip-audit` / `trivy`
4. 检查响应头：`curl -I`
5. 检查 Cookie 属性：DevTools / Bash + grep

## 常见 Bug 模式

- 富文本未过滤 → 存储型 XSS
- 搜索拼接 SQL → 注入
- 错误页直接打印异常栈
- API 返回 password_hash 字段
- Cookie 缺 HttpOnly
- 内部接口未鉴权（认为内网安全）
- 文件上传未校验后缀，可上传 webshell
- 依赖有已知 CVE

## 通过判定

- OWASP Top 10 主要项已检查
- 无明显敏感字段泄露
- HTTPS + 安全头齐备
- 依赖漏洞扫描无高危
- 高风险输入点（富文本、URL 参数、文件上传）有专项测试
