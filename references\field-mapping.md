# 19字段映射规则

##字段清单

|序号| 字段名 |类型|来源列|提取方式|验证规则|
|-----|--------|----|------|---------|---------|
|1|原始图片链接|URL|用户提供|直接使用|不能为空|
|2|**1688 商品图链接**|URL|第1列|`td:nth-of-type(1) img.src`|⚠️必须提取，不能留空|
|3|**商品链接**|URL|构建|搜索链接|⚠️不能为空，采用搜索替代|
|4|商品名称|文本|第1列|去除"预览"前缀|截断至200字符|
|5|价格|文本|第2列|直接提取|缺失标记"/"|
|6|近90 天销量|文本|第3列|直接提取|缺失标记"/"|
|7|近14 天销量|文本|第4列|直接提取|缺失标记"/"|
|8|工厂年限|文本|第5列|直接提取|缺失标记"/"|
|9|回头率|文本|第6列|直接提取|缺失标记"/"|
|10|综合服务分|文本|第7列|直接提取|缺失标记"/"|
|11|客服响应率|文本|第8列|直接提取|缺失标记"/"|
|12|起订量|文本|第9列|直接提取|缺失标记"/"|
|13|发货履约率|文本|第10列|直接提取|缺失标记"/"|
|14|48h揽收率|文本|第11列|直接提取|缺失标记"/"|
|15|首次上架时间|文本|第12列|直接提取|缺失标记"/"|
|16|评价数|文本|第13列|直接提取|缺失标记"/"|
|17|源头厂家|文本|第14列|直接提取|缺失标记"/"|
|18|供应商名称|文本|第15列|直接提取|缺失标记"/"|
|19|发货地|文本|第16列|直接提取|缺失标记"/"|

##关键字段说明

### 1.原始图片链接

**来源**:用户提供的商品图片URL

**格式**: 
```json
{"link": "https://m.media-amazon.com/images/I/xxx.jpg", "text": ""}
```

**示例**:
- `https://images-na.ssl-images-amazon.com/images/I/71Tg1wI7YFL._AC_UL900_SR900,600_.jpg`

### 2.1688 商品图链接 ⚠️

**来源**:从1688对比表格第1列的`<img>`标签提取

**提取脚本**:
```javascript
const img = firstCell.querySelector('img');
const imgUrl = img ? (img.src || (img.dataset && img.dataset.src) || '') : '';
```

**格式**:
```json
{"link": "https://cbu01.alicdn.com/O1CN01BKOvRN1E0rl6YxZwz_!!973060290-0-cib.jpg", "text": ""}
```

**常见图片 URL格式**:
- O1CN01开头：`https://cbu01.alicdn.com/O1CN01xxx_!!{seller_id}-0-cib.jpg`
- img/ibank路径：`https://cbu01.alicdn.com/img/ibank/{image_id}_{seller_id}.jpg`

**验证规则**:
- ✅不能为空字符串
- ✅必须是有效的http/https URL
- ❌不能是"/"或null

### 3.商品链接 ⚠️

**来源**:通过商品名称构建搜索链接（因为无法直接从页面提取）

**构建规则**:
```python
from urllib.parse import quote

def build_product_search_url(product_name: str) -> str:
    if not product_name or product_name == '/':
        return ""
    keyword = product_name[:50] if len(product_name) > 50 else product_name
    return f"https://s.1688.com/selloffer/offer_search.htm?keywords={quote(keyword)}"
```

**格式**:
```json
{"link": "https://s.1688.com/selloffer/offer_search.htm?keywords=Cross-Border+Exclusive+Dehumidifier+Boxes", "text": ""}
```

**为什么使用搜索链接**:
- 1688对比表格页面的商品信息通过JavaScript动态渲染
-商品标题和圖片所在的单元格没有直接包含可点击的`<a>`标签
-无法从图片 URL直接反推商品详情页ID
-搜索链接可以确保用户快速找到对应商品

### 4.商品名称

**来源**:第1列文本内容

**处理规则**:
```javascript
let productName = titleElement.textContent.trim().replace(/^预览\n/, '');
if (productName.length > 200) {
    productName = productName.substring(0, 200);
}
```

**示例**:
-原内容:`预览\nCross-Border Exclusive Dehumidifier Boxes...`
-处理后:`Cross-Border Exclusive Dehumidifier Boxes...`

##钉钉 AI 表格字段类型

### URL 类型

**格式要求**:
```json
{
  "fieldId": {"link": "https://example.com", "text": ""}
}
```

**示例**:
```json
{
  "LLH6f63": {"link": "https://m.media-amazon.com/images/I/xxx.jpg", "text": ""},
  "tTvtWvz": {"link": "https://cbu01.alicdn.com/O1CN01xxx.jpg", "text": ""},
  "GVWnzbV": {"link": "https://s.1688.com/selloffer/offer_search.htm?keywords=...", "text": ""}
}
```

###文本类型

**格式要求**:
```json
{
  "fieldId": "值"
}
```

**示例**:
```json
{
  "tuVyvtk": "宠物垫子防水牛津布",
  "GdBsoTK": "¥14.90",
  "bwbdmBm": "9"
}
```

## Field ID映射表

|字段名|Field ID|
|--------|--------|
|原始图片链接|LLH6f63|
|1688 商品图链接|tTvtWvz|
|商品链接|GVWnzbV|
|商品名称|tuVyvtk|
|价格|GdBsoTK|
|近90 天销量|bwbdmBm|
|近14 天销量|a8SYLI5|
|工厂年限|fbxgnQb|
|回头率|8NEwurV|
|综合服务分|GYV1wE4|
|客服响应率|18kNDNl|
|起订量|Pn8g4YL|
|发货履约率|S2UDmWW|
|48h 揽收率|2ggEZOS|
|首次上架时间|UON8MwY|
|评价数|LtliWoE|
|源头厂家|sAJtHjS|
|供应商名称|1lyES7F|
|发货地|STZAMeP|

**注意**: Field ID因表格而异，需要动态获取。以上仅为示例。

## 数据写入示例

###完整记录格式

```json
{
  "cells": {
    "LLH6f63": {"link": "https://m.media-amazon.com/images/I/71Tg1wI7YFL.jpg", "text": ""},
    "tTvtWvz": {"link": "https://cbu01.alicdn.com/O1CN01BKOvRN1E0rl6YxZwz.jpg", "text": ""},
    "GVWnzbV": {"link": "https://s.1688.com/selloffer/offer_search.htm?keywords=...", "text": ""},
    "tuVyvtk": "Cross-Border Exclusive Dehumidifier Boxes",
    "GdBsoTK": "¥68.60",
    "bwbdmBm": "9",
    "a8SYLI5": "7",
    "fbxgnQb": "23年",
    "8NEwurV": "0%",
    "GYV1wE4": "5.0",
    "18kNDNl": "96.0%",
    "Pn8g4YL": "1",
    "S2UDmWW": "/",
    "2ggEZOS": "/",
    "UON8MwY": "2016/04/08",
    "LtliWoE": "53条有内容53条",
    "sAJtHjS": "生产型厂家",
    "1lyES7F": "深圳市春旺新材料股份有限公司",
    "STZAMeP": "广东 深圳市龙岗区"
  }
}
```

##验证清单

在写入钉钉 AI 表格前，必须验证:

- [ ]所有19个字段都有值
- [ ] URL 类型字段使用对象格式`{"link": "...", "text": ""}`
- [ ]商品图链接不是空字符串
- [ ]商品链接不是空字符串（可以是搜索链接）
- [ ]缺失字段标记为"/"而不是null或空字符串
- [ ]商品名称长度不超过200字符
