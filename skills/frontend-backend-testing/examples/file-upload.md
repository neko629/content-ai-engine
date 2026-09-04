# 示例 · 文件上传（维度 11）

## 用户输入
> "上传头像功能，帮我测一下"

## 业务约定
- 格式：JPG / PNG / WebP
- 大小：≤ 2MB
- 尺寸：建议 ≥ 200×200
- 上传后裁剪为正方形

## 测试用例

| # | 维度 | 场景 | 文件 | 预期 |
|---|---|---|---|---|
| 1 | 11 | 标准 JPG | 100KB / 500×500 | PASS |
| 2 | 11 | 标准 PNG | 同上 | PASS |
| 3 | 11 | 不支持格式 | gif / svg / pdf | 拒绝 + 友好提示 |
| 4 | 11 | 假后缀 | exe 改 .jpg | 接口校验拒绝 |
| 5 | 11 | 0B 文件 | 空文件 | 拒绝 |
| 6 | 11 | 1B 文件 | 1 字节 | 拒绝（小于最小有效）或 PASS |
| 7 | 11 | 临界大小 | 1.99MB | PASS |
| 8 | 11 | 2MB | 正好 2MB | PASS（含等于） |
| 9 | 11 | 超限 | 2.01MB | 拒绝 + 提示 |
| 10 | 11 | 超大 | 10MB | 拒绝 + 提示（不应上传中才报错） |
| 11 | 11 | 极小尺寸 | 10×10 | 业务定（一般提示但允许） |
| 12 | 11 | 极大尺寸 | 10000×10000 | 服务端限制 |
| 13 | 11 | 中文文件名 | "头像.jpg" | 名称落库无损 |
| 14 | 11 | 超长文件名 | 300 字符 | 截断或拒绝 |
| 15 | 11 | 特殊字符 | `a/b.jpg`、`con.jpg`、`..\..\evil.jpg` | 拒绝路径穿越 |
| 16 | 06 异常 | 上传中断网 | 大文件中途断网 | 提示失败，可重试 |
| 17 | 06 异常 | 上传中关页面 | | 不留临时垃圾 |
| 18 | 06 异常 | 重复点上传 | 快速点 3 次 | 只发 1 个请求 |
| 19 | 02 UI | 进度条 | 慢网 | 实时显示进度 |
| 20 | 02 UI | Loading 态 | | 上传中按钮 disabled |
| 21 | 07 权限 | 未登录 | | 401 |
| 22 | 14 安全 | 病毒文件 | EICAR 测试文件 | 拒绝（如有病毒扫描）|
| 23 | 14 安全 | 含 XSS 的 SVG | SVG 含 script | 不渲染 / 转图片 |

## 工具实测

```bash
# 准备各种边界文件
dd if=/dev/zero of=/tmp/2mb.jpg bs=1M count=2
dd if=/dev/zero of=/tmp/over.jpg bs=1M count=3
echo "fake jpg" > /tmp/fake.jpg.exe
mv /tmp/fake.jpg.exe /tmp/fake.jpg

# 上传测试
curl -X POST https://api.example.com/v1/avatar \
  -H 'Authorization: Bearer xxx' \
  -F 'file=@/tmp/2mb.jpg'

curl -X POST https://api.example.com/v1/avatar \
  -H 'Authorization: Bearer xxx' \
  -F 'file=@/tmp/over.jpg'
```

## 常见 Bug
- 只校验前端后缀
- 大文件超限提示在上传完成后才报
- 临时文件未清理（关页面后 /tmp 有残留）
- 中文文件名落库变 ???
- 上传成功但 URL 可被遍历（递增 ID）

## 通过判定
- 格式 + 大小双层校验（前端 + 接口）
- 边界文件齐备
- 中断 / 重复点 / 安全文件 已测
- 文件命名 / 存储路径 安全
