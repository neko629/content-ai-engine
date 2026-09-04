# 完整示例

## 示例 1：新增功能（带冲突裁决与自检）

**Input**
```
需求：用户登录模块
功能清单：F-01 账号密码登录 / F-02 验证码(4位数字) / F-03 成功跳首页 / F-04 失败提示
PRD：R-01 连续失败5次锁定10分钟
原型：登录页含"记住我"勾选；未画锁定提示
架构：Vue3 + Element Plus，views/api/services 分层，接口走统一 request 封装
```

**Output（节选）**
```
【冲突裁决】
- "记住我"：原型有、功能清单无 → 范围以原型为准 → 纳入实现(P)
- 锁定逻辑(R-01)：PRD 有、原型未画提示 → 规则以 PRD 为准，实现锁定；锁定后的 UI 提示文案原型缺失 → 待确认

【对齐矩阵】
F-01 → views/login/LoginForm.vue + api/auth.js   已完成
F-02 → LoginForm.vue (captcha len=4)              已完成
F-03 → views/login/index.vue (router.push('/'))   已完成
F-04 → LoginForm.vue (ElMessage.error)            已完成
R-01 → services/auth.js (失败计数+锁定)            已完成
P-记住我 → LoginForm.vue (rememberMe)             已完成

【可运行性验证】vite build 通过；vitest 主流程用例 3/3 通过
【覆盖率自检】
完整性：F-01~04、R-01、原型"记住我"均已覆盖
一致性：无清单外新增；目录遵循 views/api/services
待确认：①锁定提示文案 ②验证码来源(图形/短信) ③token 刷新不在清单内，未实现
```

## 示例 2：修改已有代码

**Input**：在现有订单列表加"按状态筛选"，PRD：R-07 状态枚举 待付款/已付款/已取消；原型：筛选为下拉单选，放列表顶部右侧。

**Output（节选）**
```
【对齐矩阵】F-12 状态筛选 → views/order/List.vue(顶部右侧下拉) + api/order.js(status 入参)；R-07 枚举 → constants/orderStatus.js
【修改范围】
- views/order/List.vue: 新增 <el-select> 第 24~31 行；query 增加 status
- api/order.js: getOrderList 入参增加 status
【变更代码】// Diff ...（文件头注释 // 覆盖 F-12, R-07）
【可运行性验证】lint 通过；列表筛选组件测试 2/2 通过
【覆盖率自检】F-12、R-07 已覆盖；无清单外新增；待确认：默认是否选中"全部"原型未注明
```

## 示例 3：材料缺失拦截（步骤 0 硬门禁）

**Input**："帮我实现这个功能：做个数据看板。"（无功能清单/原型/架构/字段）

**Output**
```
关键材料缺失，先确认再开发（不臆造）：
1. 看板要展示哪些指标/图表？（功能范围——需功能清单或原型）
2. 技术栈与项目结构？（前端框架/是否已有项目/目录规范——需架构）
3. 数据来源与字段结构？（接口还是静态数据/字段定义）
补齐后即按对齐流程开发。
```
