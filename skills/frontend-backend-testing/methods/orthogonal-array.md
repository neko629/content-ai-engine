# 测试设计方法 · 正交组合

## 概念

多变量组合爆炸时用正交表压缩，保证"两两组合"覆盖率最高。

## 适用场景

- 3+ 个变量，每个 2+ 个取值
- 全组合数 > 测试预算

## 示例：浏览器兼容性

变量：浏览器 ∈ {Chrome, Safari, Firefox}、系统 ∈ {Win, Mac, iOS}、网络 ∈ {WiFi, 4G, 弱网}

全组合 = 3 × 3 × 3 = 27 用例。

用 L9 正交表压缩到 9 用例（保证任意两两组合都至少出现 1 次）：

| # | 浏览器 | 系统 | 网络 |
|---|---|---|---|
| 1 | Chrome | Win | WiFi |
| 2 | Chrome | Mac | 4G |
| 3 | Chrome | iOS | 弱网 |
| 4 | Safari | Win | 4G |
| 5 | Safari | Mac | 弱网 |
| 6 | Safari | iOS | WiFi |
| 7 | Firefox | Win | 弱网 |
| 8 | Firefox | Mac | WiFi |
| 9 | Firefox | iOS | 4G |

## 工具

- AllPairs / PICT 工具自动生成
- 在线正交表查询
