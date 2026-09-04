# 维度 08 · 登录态与会话测试

> 检查未登录、登录过期、Token 失效、退出登录、重复登录等场景下的行为。

## Checklist

- 未登录访问需登录页 → 跳登录页 + 记录原 URL → 登录后回跳
- Token 即将过期 → 静默刷新（refresh_token）
- Token 已过期 → 跳登录页 + 友好提示
- 退出登录 → 清 Token / Cookie / 缓存 / Service Worker
- 多标签页登录态同步（一个 tab 退出，其他 tab 同步）
- 同账号多端登录策略：互踢 / 并存 / 二次确认
- 记住密码：勾选 vs 不勾选 行为差异
- 自动登录：明文存密码 vs 长期 Token
- Token 存储位置：localStorage（XSS 风险）vs httpOnly Cookie（CSRF 风险）
- 登录失败次数限制（防暴力破解）
- 验证码 / OTP / 二次验证
- 第三方登录：OAuth 回调、错误处理、绑定/解绑

## 测试方法

1. 修改本地 Token 为过期值/无效值，看接口行为
2. 模拟 Token 即将过期，看是否触发 refresh
3. 多标签页同时操作，验证同步
4. Bash 直接调登录接口，测错误次数限制
5. 抓 Chrome 网络请求看 Token 实际怎么传（Header / Cookie）

## 常见 Bug 模式

- Token 过期接口报 500 不报 401
- 退出登录只清前端 Token，服务端 Session 仍有效
- 多 tab 不同步，一个 tab 退出后另一个 tab 还能操作
- Refresh Token 与 Access Token 同寿命（白搞）
- localStorage 存 Token 但页面有 XSS 漏洞
- 登录失败提示泄露"账号不存在"vs"密码错误"
- 无失败次数限制，被暴力破解
- OAuth 回调的 state 参数没校验（CSRF）
- 第三方登录失败无降级

## 通过判定

- 未登录拦截 + 回跳完整
- Token 过期与刷新链路稳定
- 退出真正退出（前后端都清）
- 失败次数有限制
- Token 存储方式有明确安全策略
