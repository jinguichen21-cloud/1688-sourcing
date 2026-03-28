---
name: 1688-sourcing
description: |
  1688 用照片筛同款 - 通过图像搜索从 1688 找相似商品。使用场景：亚马逊选品找1688 货源、以图搜图找供应商、批量查询同款商品。
  输入支持表格模式或URL 列表模式，输出自动创建「1688 同款选品」表格或写入指定表格。
---

# 1688 用照片筛同款v5.2

**核心原则：每次运行必须完整提取19 个字段，缺一不可**

## 严格禁止 (NEVER DO)

- ❌ 不要在不验证字段完整性的情况下继续执行（HARD-GATE）
- ❌ 不要跳过浏览器打开步骤直接使用缓存数据
- ❌ 不要在页面未加载完成时提取数据（必须wait_for 5000ms）
- ❌ 不要使用动态 class选择器，必须用nth-of-type固定选择器
- ❌ **不要在缺少1688 商品图链接的情况下强行处理** ← 必须从`<img>`标签提取src属性
- ❌ **不要在商品链接为空时不告知用户** → 采用搜索链接替代方案
- ❌ 不要在未确认目标表格的情况下写入数据
- ❌ 不要隐藏字段缺失错误，必须明确告知用户具体缺失字段
- ❌ **不要只返回 baseID，必须返回完整表格链接**：`https://alidocs.dingtalk.com/i/nodes/<BaseID>`

##必填字段清单（19个）

| # | 字段名 |来源|关键性|
|---|--------|-----|---------|
| 1-4 |原始图片链接、**1688 商品图链接**、商品链接、商品名称 |列1 | ⭐⭐⭐ |
| 5-11 | 价格、近 90 天销量、近 14 天销量、工厂年限、回头率、综合服务分、客服响应率 |列 2-8 | ⭐⭐ |
| 12-19 |起订量、发货履约率、48h 揽收率、首次上架时间、评价数、源头厂家、供应商名称、发货地|列 9-16 | ⭐⭐⭐ |

**商品链接构建规则**:使用商品名称生成1688站内搜索链接，详见 [references/product-link-solution.md](./references/product-link-solution.md)

## 意图判断决策树

```
用户提到"找同款"/"1688 货源"/"以图搜图":
├─ 已指定钉钉表格 → 表格模式：从表格读取商品图链接
├─ 直接提供 URL 列表 → URL模式：批量处理提供的图片链接
└─ 未指定 → HARD-GATE：询问用户采用哪种模式

用户提到"写入表格":
├─ 已指定表格名称 → 写入指定表格
└─ 未指定 → 自动创建「1688 同款选品」表格
```

## 核心工作流

```bash
# Step 1:确认输入源（HARD-GATE）
表格模式：dws aitable record list --base <BASE_ID> --table <TABLE_ID>
URL模式：直接使用用户提供的URL 列表

# Step 2:拼装 1688 搜索 URL
https://air.1688.com/app/1688-lp/landing-page/comparison-table.html?bizType=browser&currency=CNY&customerId=dingtalk&outImageAddress=<URL编码后的图片地址>

# Step 3:打开浏览器并提取数据
use_browser(action=navigate, url=<search_url>)
use_browser(action=wait_for, timeMs=5000)
use_browser(action=evaluate, fn=<JavaScript 提取脚本>)

# Step 4:字段完整性验证（HARD-GATE）
验证19 个字段是否全部存在，缺少任一字段则停止并报告

# Step 5:写入目标表格
检查表格存在：dws aitable doc search "1688 同款"
不存在则创建：dws aitable doc create "1688 同款选品"
写入数据：dws aitable record create --base <BASE_ID> --table <TABLE_ID> --data '[{"cells":{...}}]'

# Step 6:返回表格链接（HARD-GATE）
表格链接：https://alidocs.dingtalk.com/i/nodes/<BASE_ID>
```

## 上下文传递规则

|操作 | 从返回中提取 | 用于 |
|------|-------------|------|
| 表格读取| recordId,商品图链接 |构建搜索 URL+后续标记完成|
| 浏览器打开| targetId |后续evaluate/screenshot操作 |
| JS提取 | products数组（19字段） |写入目标表格的cells数据|
| 表格创建| base UUID |后续record create 的--base参数|
| 数据写入|成功记录数|向用户报告完成情况|

## HARD-GATE验证机制

**Gate 1:输入源确认** -已确认输入模式（表格 or URL），获取必要参数

**Gate 2:字段完整性** -验证19个必填字段是否全部存在，商品图链接不能为空

**Gate 3:写入前确认** -目标表格已确认，所有记录字段验证通过，数据格式符合要求

**Gate 4:交付确认** -必须返回完整表格链接`https://alidocs.dingtalk.com/i/nodes/<BASE_ID>`，不能只返回 baseID

## 数据格式规范

### ✅ 正确格式
```json
{
  "原始图片链接": {"link": "https://m.media-amazon.com/images/I/xxx.jpg", "text": ""},
  "1688 商品图链接": {"link": "https://cbu01.alicdn.com/O1CN01xxx.jpg", "text": ""},
  "商品链接": {"link": "https://s.1688.com/selloffer/offer_search.htm?keywords=...", "text": ""},
  "商品名称": "宠物垫子防水牛津布",
  "价格": "¥14.90",
  "起订量": "1"
}
```

### ❌ 错误格式
```json
{"商品链接": "", "1688 商品图链接": "", "起订量": null}
```

## JavaScript 提取脚本

完整脚本见[references/dom-selectors.md](./references/dom-selectors.md)，关键点:
- 使用`tr.ant-table-row`选择数据行
- 使用`td:nth-of-type(1) img`提取商品图链接
-商品链接暂时留空，后续构建搜索链接

## 错误处理

错误日志保存到`memory/1688-error.json`，重试策略和详细错误处理见[references/error-handling.md](./references/error-handling.md)

| 错误场景|处理方式 |
|----------|----------|
|浏览器无法打开|立即停止，检查网络/代理，重试最多2次|
| 1688 页面无搜索结果|告知"该图片在 1688 无同款"，跳过|
|字段缺失| HARD-GATE失败，记录到memory/1688-error.json，暂停|
|页面结构变化 |停止，提示需更新技能选择器|
| dws CLI认证失败|提示先执行`dws auth login`，不重试|

## 详细参考（按需读取）

- [references/dom-selectors.md](./references/dom-selectors.md) — DOM 选择器详解
- [references/field-mapping.md](./references/field-mapping.md) — 19字段映射规则
- [references/error-handling.md](./references/error-handling.md) —错误码和调试
- [references/table-schema.md](./references/table-schema.md) —表格字段类型和写入格式
- [references/product-link-solution.md](./references/product-link-solution.md) —商品链接解决方案
- [references/fixed-script.py](./references/fixed-script.py) —固定Python 脚本

## 版本历史

**v5.2** (当前)-商品链接优化版：新增搜索链接替代方案、固定Python 脚本、强化字段验证  
**v5.1** -错误处理增强版：新增错误日志格式+重试策略  
**v5.0** - dingtalk-neulink标准版：≤150 行、NEVER DO、决策树、HARD-GATE
