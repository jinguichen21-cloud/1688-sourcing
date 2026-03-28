#错误处理和调试指南

##错误日志格式

保存到`memory/1688-error.json`:

```json
{
  "timestamp": "2026-03-14T17:18:00+08:00",
  "error_type": "missing_fields",
  "source_image": "https://images-na.ssl-images-amazon.com/images/I/71Tg1wI7YFL.jpg",
  "missing_fields": ["起订量", "发货履约率"],
  "action_taken": "skip_record"
}
```

### error_type枚举值

|值|说明|处理方式|
|---|------|---------|
|`missing_fields`|字段缺失|HARD-GATE失败，记录到日志，暂停|
|`browser_failed`|浏览器打开失败|检查网络/代理，重试最多2次|
|`no_results`|1688页面无搜索结果|告知用户"该图片在 1688 无同款"，跳过|
|`page_changed`|页面结构变化|停止，提示需更新技能选择器|
|`auth_failed`|dws CLI认证失败|提示先执行`dws auth login`，不重试|
|`write_failed`|写入表格失败|停止，检查权限，告知用户手动创建|

##重试策略

|错误类型|重试次数|间隔|超过最大重试|
|---------|---------|------|------------|
|网络超时| 3次| 2秒|标记"处理失败"，记日志，继续|
|页面加载失败| 2次| 3秒|同上|
| dws CLI失败| 1次| 1秒|同上|

###重试实现示例

```python
import time
from functools import wraps

def retry(max_attempts=3, delay=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

@retry(max_attempts=3, delay=2)
def extract_from_browser():
    #提取逻辑
    pass
```

##常见错误场景及处理

### 1.浏览器无法打开

**错误信息**:
```
Error: Failed to navigate to URL
```

**可能原因**:
-网络连接问题
-代理配置错误
-1688网站暂时不可访问

**处理流程**:
```
1.检查网络连接
2.重试（最多2次，间隔3秒）
3.仍然失败 → 报告给用户
```

**用户提示**:
```
❌ 无法打开1688以图搜图页面

可能原因:
-网络连接不稳定
- 1688网站暂时维护

建议:
1.检查网络连接
2.稍后重试
```

### 2.商品图链接提取失败

**错误信息**:
```
商品图链接为空
```

**可能原因**:
-页面未完全加载
- DOM 选择器不匹配
-图片使用懒加载

**处理流程**:
```
1.等待更长时间（5000ms→10000ms）
2.尝试不同的选择器
3.仍然失败 → HARD-GATE失败，记录日志
```

**JavaScript调试**:
```javascript
//检查是否有img元素
const img = document.querySelector('td.ant-table-cell img');
console.log('Image found:', !!img);
console.log('Image src:', img?.src);

//检查dataset
console.log('Dataset:', img?.dataset);
```

### 3.dws CLI命令失败

**错误信息**:
```
Error: unknown flag: --base
```

**可能原因**:
-dws CLI版本过旧
-参数格式错误

**处理流程**:
```
1.检查dws版本：dws --version
2.查看帮助：dws aitable record create --help
3.修正参数格式
4.重试1次
5.仍然失败 → 提示用户
```

**用户提示**:
```
❌ dws CLI执行失败

错误信息：{具体错误}

建议:
1.执行`dws auth login`重新登录
2.检查dws版本是否为最新
3.联系管理员检查权限
```

### 4.表格创建失败

**错误信息**:
```
Error: Failed to create base
```

**可能原因**:
-用户没有创建表格的权限
-钉钉 API限流
- Base名称重复

**处理流程**:
```
1.重试1次
2.仍然失败 → 提示用户手动创建
```

**用户提示**:
```
❌ 无法自动创建表格

可能原因:
-当前账号没有创建表格的权限
- 钉钉 API暂时限流

建议:
1.手动创建钉钉 AI 表格，命名为"1688 同款选品"
2.将表格链接发送给我
3.我会将数据写入您创建的表格
```

### 5.字段验证失败

**错误信息**:
```
缺少字段：起订量，发货履约率
```

**可能原因**:
-页面结构与预期不符
-某些列被隐藏
-数据本身确实为空

**处理流程**:
```
1.检查页面结构是否变化
2.确认是否为普遍现象
3.如果是个别商品 → 标记为"/"
4.如果所有商品都缺失 → HARD-GATE失败
```

**日志记录**:
```json
{
  "timestamp": "2026-03-14T17:18:00+08:00",
  "error_type": "missing_fields",
  "source_image": "https://...",
  "missing_fields": ["起订量", "发货履约率"],
  "affected_records": [1, 5, 12],
  "action_taken": "mark_as_slash"
}
```

##调试技巧

### 1.启用详细日志

在脚本中添加:
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 2.保存中间结果

```python
#保存提取的原始数据
with open('/tmp/extracted_products.json', 'w') as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

#保存验证后的数据
with open('/tmp/validated_products.json', 'w') as f:
    json.dump(validated, f, ensure_ascii=False, indent=2)
```

### 3.使用curl测试API

```bash
#测试dws CLI
dws aitable doc search "1688" --format json

#测试钉钉 API
curl -X GET "https://api.dingtalk.com/v1.0/aitable/bases" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### 4.浏览器开发者工具

1.打开1688以图搜图页面
2.按F12打开开发者工具
3.在Console中执行:
```javascript
//检查表格行数
document.querySelectorAll('tr.ant-table-row').length

//检查第一行的单元格数
document.querySelector('tr.ant-table-row td.ant-table-cell').length

//提取商品图链接
document.querySelector('td.ant-table-cell img')?.src
```

## 错误恢复流程

```
错误发生
    ↓
记录错误日志(memory/1688-error.json)
    ↓
判断错误类型
    ├─ 可恢复错误 → 重试（按重试策略）
    ├─ 字段缺失 → HARD-GATE失败，报告用户
    └─ 系统错误 → 停止，报告用户
    ↓
用户修复后继续
```

##监控和告警

###关键指标

-成功率：应≥95%
-平均处理时间：<30秒/商品
-字段完整率：应=100%

###告警阈值

|指标|警告|严重|
|-----|------|------|
|成功率|<90%|<80%|
|字段完整率|<95%|<90%|
|平均处理时间|>60秒|>120秒|

##最佳实践

1. **预防优于修复**:在写入前充分验证数据
2. **快速失败**:遇到不可恢复错误立即停止
3. **详细日志**:记录足够的信息用于排查问题
4. **用户友好**:错误提示清晰明确，给出解决建议
5. **优雅降级**:能处理部分字段缺失的情况
