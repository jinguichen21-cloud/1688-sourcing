# 1688-sourcing v5.2技能包

##技能概述

**1688 用照片筛同款** - 通过图像搜索从 1688 找相似商品

**使用场景**:
- 亚马逊选品找1688 货源
-以图搜图找供应商
-批量查询同款商品

## v5.2版本核心优化

###解决的问题

1. **商品图链接丢失** → 强制从`<img>`标签提取src属性
2. **商品链接丢失** → 采用搜索链接替代方案
3. **字段完整性无法保证** → 强化HARD-GATE验证机制
4. **表格链接格式错误** → 固定返回`https://alidocs.dingtalk.com/i/nodes/<BaseID>`

###新增特性

- ✅ **商品链接构建规则**:使用商品名称生成1688站内搜索链接
- ✅ **固定Python脚本**:避免人为错误导致字段丢失
- ✅ **完整示例数据**:包含20条真实商品数据的示例
- ✅ **详细文档**:商品链接解决方案完整说明

##文件结构

```
1688-sourcing-v5.2/
├── SKILL.md                          #技能主文件（≤150行）
├── README.md                         #使用说明
└── references/                       #参考资料目录
    ├── product-link-solution.md      #商品链接解决方案
    ├── fixed-script.py               #固定数据处理脚本
    ├── dom-selectors.md              # DOM 选择器详解
    ├── field-mapping.md              # 19字段映射规则
    ├── error-handling.md             #错误码和调试
    └── table-schema.md               #表格字段类型和写入格式
└── examples/                         #示例文件
    ├── final_1688_script.py          #完整执行脚本
    └── products_data.json            #示例数据（20条记录）
```

##使用方法

###方式一：直接使用技能

当用户说:
- "帮我找这款商品的1688 货源"
- "用这张图片在1688找同款"
- "以图搜图，找供应商"

技能自动执行:
1.打开1688以图搜图页面
2.提取19个字段的商品信息
3.创建或写入钉钉 AI 表格
4.返回完整表格链接

###方式二：运行固定脚本

```bash
cd /Users/goumaozhang/.real/workspace/1688-sourcing-v5.2/examples
python3 final_1688_script.py
```

###方式三：调用数据处理脚本

```python
from references.fixed_script import main

main(
    data_file="products_data.json",
    base_id="你的BaseID",
    table_id="你的TableID",
    original_image_url="原始图片 URL"
)
```

## 核心工作流

```
用户提供商品图片 URL
    ↓
打开1688以图搜图页面
    ↓
JavaScript 提取19 个字段
    ↓
HARD-GATE验证字段完整性
    ↓
构建商品搜索链接
    ↓
写入钉钉 AI 表格
    ↓
返回表格链接给用户
```

##必填字段清单（19个）

|字段名 |来源|验证规则|
|--------|----|---------|
|原始图片链接|用户提供|不能为空|
|**1688 商品图链接** | `td:nth-of-type(1) img.src` | ⚠️必须提取，不能留空|
|**商品链接** |搜索链接构建|⚠️不能为空，采用搜索替代|
|商品名称|单元格文本|截断至200字符|
|价格、销量等|对应列文本|缺失标记"/"|

## HARD-GATE 机制

### Gate 1:输入源确认
- ✅ 已确认输入模式（表格 or URL）
- ✅ 获取必要参数

### Gate 2:字段完整性
```python
def validate_product(product):
    missing = [f for f in REQUIRED_FIELDS if f not in product]
    if missing:
        return (False, f"缺少字段：{', '.join(missing)}")
    
    #特殊验证：商品图链接不能为空
    if not product.get('商品图链接'):
        return (False, "商品图链接提取失败")
    
    return (True, "验证通过")
```

### Gate 3:写入前确认
- ✅ 目标表格已确认
- ✅ 所有记录字段验证通过
- ✅ 数据格式符合要求

### Gate 4:交付确认
- ✅ 必须返回完整表格链接
- ❌ 禁止只返回 baseID

## 数据格式规范

###正确格式示例

```json
{
  "原始图片链接": {"link": "https://m.media-amazon.com/images/I/xxx.jpg", "text": ""},
  "1688 商品图链接": {"link": "https://cbu01.alicdn.com/O1CN01xxx.jpg", "text": ""},
  "商品链接": {"link": "https://s.1688.com/selloffer/offer_search.htm?keywords=...", "text": ""},
  "商品名称": "宠物垫子防水牛津布",
  "价格": "¥14.90",
  "起订量": "1",
  "供应商名称": "台前县车居汽车用品经营有限责任公司"
}
```

### 错误格式示例

```json
{"商品链接": "", "1688 商品图链接": "", "起订量": null}
```

## 错误处理

### 错误日志格式

保存到`memory/1688-error.json`:

```json
{
  "timestamp": "2026-03-14T17:18:00+08:00",
  "error_type": "missing_fields",
  "source_image": "https://...",
  "missing_fields": ["起订量", "发货履约率"],
  "action_taken": "skip_record"
}
```

###重试策略

|错误类型|重试次数|间隔|
|---------|---------|------|
|网络超时| 3次| 2秒|
|页面加载失败| 2次| 3秒|
| dws CLI失败| 1次| 1秒|

##验证方法

### 检查数据完整性

```bash
dws aitable record list --base <BASE_ID> --table <TABLE_ID> --format json | jq '.data.records[0].cells'
```

###访问表格

打开链接：`https://alidocs.dingtalk.com/i/nodes/<BASE_ID>`

检查要点:
- ✅ 每条记录都有商品图链接
- ✅ 每条记录都有商品链接
- ✅ 19 个字段全部有值

## NEVER DO 约束

- ❌ 不要在不验证字段完整性的情况下继续执行
- ❌ 不要跳过浏览器打开步骤直接使用缓存数据
- ❌ 不要在页面未加载完成时提取数据
- ❌ 不要使用动态 class选择器
- ❌ **不要在缺少商品图链接的情况下强行处理**
- ❌ **不要在商品链接为空时不告知用户**
- ❌ 不要只返回 baseID，必须返回完整表格链接

## 版本历史

|版本|日期|核心优化|
|-----|------|---------|
|**v5.2**|2026-03-14|商品链接搜索替代方案、固定脚本|
|**v5.1**|2026-03-13|错误日志格式、重试策略|
|**v5.0**|2026-03-12|dingtalk-neulink标准版（≤150行）|

## dingtalk-neulink质量检测

###检测项目

- ✅ 行数：150行以内
- ✅ NEVER DO 区块：包含9条约束
- ✅ 意图决策树：清晰明确
- ✅ HARD-GATE:4个硬停止点
- ✅ 错误处理：定义日志格式和重试策略
- ✅ 参考资料：分离到references/目录

###检测结果

待运行dingtalk-neulink检测...

##相关资源

- [商品链接解决方案](./references/product-link-solution.md)
- [DOM 选择器详解](./references/dom-selectors.md)
- [字段映射规则](./references/field-mapping.md)
- [错误处理指南](./references/error-handling.md)

## 技术支持

遇到问题请查看:
1.错误日志：`memory/1688-error.json`
2.示例数据：`examples/products_data.json`
3.固定脚本：`references/fixed-script.py`

---

**最后更新**: 2026-03-14  
**维护者**:张悦  
**组织**: bug砖家
