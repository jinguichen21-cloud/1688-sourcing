#钉钉 AI 表格字段类型和写入格式

##表格结构

### Base信息

- **Base ID**: `G1DKw2zgV2o9YzjnhBoAx1MkJB5r9YAn`
- **Base名称**: 1688 同款选品
- **Table ID**: `o4OnnQo`
- **Table名称**: 1688 同款选品

###字段定义

|序号| 字段名|Field ID|类型|说明|
|-----|--------|--------|----|------|
|1|原始图片链接|LLH6f63|URL|用户提供的商品图片 URL|
|2|1688 商品图链接|tTvtWvz|URL|从1688页面提取的商品图片|
|3|商品链接|GVWnzbV|URL|1688 商品详情页或搜索页链接|
|4|商品名称|tuVyvtk|文本|商品标题（≤200字符） |
|5|价格|GdBsoTK|文本|商品价格（含¥符号） |
|6|近90 天销量|bwbdmBm|文本|最近90天的销售数量|
|7|近14 天销量|a8SYLI5|文本|最近14天的销售数量|
|8|工厂年限|fbxgnQb|文本|供应商工厂经营年限|
|9|回头率|8NEwurV|文本|客户复购率百分比|
|10|综合服务分|GYV1wE4|文本|1688平台综合评分|
|11|客服响应率|18kNDNl|文本|客服响应速度百分比|
|12|起订量|Pn8g4YL|文本|最小起订数量|
|13|发货履约率|S2UDmWW|文本|按时发货率百分比|
|14|48h 揽收率|2ggEZOS|文本| 48小时内揽收率|
|15|首次上架时间|UON8MwY|文本|商品首次上架日期|
|16|评价数|LtliWoE|文本|用户评价总数|
|17|源头厂家|sAJtHjS|文本|是否生产型厂家|
|18|供应商名称|1lyES7F|文本|公司或个人名称|
|19|发货地|STZAMeP|文本|商品发货地址|

##字段类型说明

### URL类型

**存储格式**:
```json
{
  "fieldId": {"link": "https://example.com", "text": ""}
}
```

**示例**:
```json
{
  "LLH6f63": {
    "link": "https://images-na.ssl-images-amazon.com/images/I/71Tg1wI7YFL.jpg",
    "text": ""
  },
  "tTvtWvz": {
    "link": "https://cbu01.alicdn.com/O1CN01BKOvRN1E0rl6YxZwz_!!973060290-0-cib.jpg",
    "text": ""
  },
  "GVWnzbV": {
    "link": "https://s.1688.com/selloffer/offer_search.htm?keywords=...",
    "text": ""
  }
}
```

**注意事项**:
- ✅必须使用对象格式，不能是字符串
- ✅`link`字段包含完整URL
- ✅`text`字段可以为空字符串
- ❌不能是`null`或`undefined`

###文本类型

**存储格式**:
```json
{
  "fieldId": "值"
}
```

**示例**:
```json
{
  "tuVyvtk": "Cross-Border Exclusive Dehumidifier Boxes",
  "GdBsoTK": "¥68.60",
  "bwbdmBm": "9",
  "fbxgnQb": "23年",
  "8NEwurV": "0%",
  "GYV1wE4": "5.0"
}
```

**注意事项**:
- ✅可以是数字、百分比、货币等格式
- ✅缺失值用"/"标记
- ❌不能是`null`或空对象

##数据写入命令

###单条记录

```bash
dws aitable record create \
  --base G1DKw2zgV2o9YzjnhBoAx1MkJB5r9YAn \
  --table o4OnnQo \
  --data '[{
    "cells": {
      "LLH6f63": {"link": "https://...", "text": ""},
      "tTvtWvz": {"link": "https://...", "text": ""},
      "GVWnzbV": {"link": "https://...", "text": ""},
      "tuVyvtk": "商品名称",
      "GdBsoTK": "¥68.60"
    }
  }]' \
  --format json
```

###批量记录（最多100条）

```bash
dws aitable record create \
  --base G1DKw2zgV2o9YzjnhBoAx1MkJB5r9YAn \
  --table o4OnnQo \
  --data '[
    {"cells": {...}},
    {"cells": {...}},
    ...
  ]' \
  --format json
```

## Python写入示例

```python
import json
import subprocess

def write_to_table(records: list, base_id: str, table_id: str):
    """将数据写入钉钉 AI 表格"""
    
    records_json = json.dumps(records, ensure_ascii=False)
    
    cmd = [
        "dws", "aitable", "record", "create",
        "--base", base_id,
        "--table", table_id,
        "--data", records_json,
        "--format", "json"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        response = json.loads(result.stdout)
        if response.get('status') == 'success':
            new_ids = response.get('data', {}).get('newRecordIds', [])
            print(f"✅ 成功写入{len(new_ids)}条记录")
            return True, new_ids
    
    print(f"❌ 写入失败：{result.stderr}")
    return False, []


#使用示例
records = [
    {
        "cells": {
            "LLH6f63": {"link": "https://...", "text": ""},
            "tTvtWvz": {"link": "https://...", "text": ""},
            "GVWnzbV": {"link": "https://...", "text": ""},
            "tuVyvtk": "商品名称",
            "GdBsoTK": "¥68.60",
            # ...其他字段
        }
    }
]

success, ids = write_to_table(
    records, 
    "G1DKw2zgV2o9YzjnhBoAx1MkJB5r9YAn",
    "o4OnnQo"
)
```

##数据验证

###查询记录

```bash
dws aitable record list \
  --base G1DKw2zgV2o9YzjnhBoAx1MkJB5r9YAn \
  --table o4OnnQo \
  --format json
```

###验证字段完整性

```python
import json

REQUIRED_FIELDS = [
    '原始图片链接', '1688 商品图链接', '商品链接', '商品名称', '价格',
    '近 90 天销量', '近 14 天销量', '工厂年限', '回头率', '综合服务分',
    '客服响应率', '起订量', '发货履约率', '48h 揽收率', '首次上架时间',
    '评价数', '源头厂家', '供应商名称', '发货地'
]

def validate_record(record: dict) -> tuple:
    """验证记录完整性"""
    cells = record.get('cells', {})
    
    missing = []
    for field in REQUIRED_FIELDS:
        field_id = get_field_id(field)  #获取Field ID
        if field_id not in cells:
            missing.append(field)
        elif cells[field_id] in [None, '', '/']:
            # URL 类型特殊处理
            if isinstance(cells[field_id], dict):
                if not cells[field_id].get('link'):
                    missing.append(field)
    
    if missing:
        return (False, f"缺少字段：{', '.join(missing)}")
    return (True, "验证通过")
```

##常见错误

### 错误1:使用字符串而非对象

❌错误:
```json
{
  "LLH6f63": "https://example.com"
}
```

✅正确:
```json
{
  "LLH6f63": {"link": "https://example.com", "text": ""}
}
```

### 错误2:使用fields而非cells

❌错误:
```json
{
  "fields": {...}
}
```

✅正确:
```json
{
  "cells": {...}
}
```

### 错误3:使用id而非recordId

❌错误（update时）:
```json
{
  "id": "record123",
  "cells": {...}
}
```

✅正确:
```json
{
  "recordId": "record123",
  "cells": {...}
}
```

### 错误4:字段名有空格

❌错误:
```
近90 天销量（有空格）
```

✅正确:
```
近90 天销量（无空格）
```

##性能优化

###分批写入

当记录数超过100条时，分批处理:

```python
BATCH_SIZE = 100

for i in range(0, len(records), BATCH_SIZE):
    batch = records[i:i + BATCH_SIZE]
    write_to_table(batch, base_id, table_id)
    print(f"已写入批次{i // BATCH_SIZE + 1}")
```

###并发控制

避免同时写入过多请求:

```python
import time

for batch in batches:
    write_to_table(batch, base_id, table_id)
    time.sleep(1)  #等待1秒
```

##最佳实践

1. **使用 Field ID 而非字段名**:更可靠，不受字段名变更影响
2. **始终使用cells键名**:符合钉钉 API规范
3. **URL 类型用对象格式**: `{"link": "...", "text": ""}`
4. **缺失值标记为"/"**:保持数据一致性
5. **批量操作控制在100条以内**:避免超限
6. **写入前充分验证**:确保所有必填字段都有值
7. **保存操作日志**:便于问题排查
