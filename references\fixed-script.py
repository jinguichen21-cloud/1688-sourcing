#!/usr/bin/env python3
"""
1688 同款商品数据固定处理脚本v4.0
用于1688-sourcing v5.2技能

核心功能:
1.从JSON文件读取浏览器提取的商品数据
2.验证19个字段完整性
3.构建商品搜索链接
4.写入钉钉 AI 表格
5.返回完整表格链接
"""

import json
import subprocess
from urllib.parse import quote

# ==========配置区域==========
BASE_ID = "G1DKw2zgV2o9YzjnhBoAx1MkJB5r9YAn"
TABLE_ID = "o4OnnQo"
ORIGINAL_IMAGE_URL = ""  #运行时设置

#字段ID映射（钉钉 AI 表格）
FIELD_MAP = {
    "原始图片链接": "LLH6f63",
    "1688 商品图链接": "tTvtWvz",
    "商品链接": "GVWnzbV",
    "商品名称": "tuVyvtk",
    "价格": "GdBsoTK",
    "近 90 天销量": "bwbdmBm",
    "近 14 天销量": "a8SYLI5",
    "工厂年限": "fbxgnQb",
    "回头率": "8NEwurV",
    "综合服务分": "GYV1wE4",
    "客服响应率": "18kNDNl",
    "起订量": "Pn8g4YL",
    "发货履约率": "S2UDmWW",
    "48h 揽收率": "2ggEZOS",
    "首次上架时间": "UON8MwY",
    "评价数": "LtliWoE",
    "源头厂家": "sAJtHjS",
    "供应商名称": "1lyES7F",
    "发货地": "STZAMeP"
}


def build_product_search_url(product_name: str) -> str:
    """使用商品名称构建1688搜索链接"""
    if not product_name or product_name == '/':
        return ""
    keyword = product_name[:50] if len(product_name) > 50 else product_name
    return f"https://s.1688.com/selloffer/offer_search.htm?keywords={quote(keyword)}"


def validate_products(products: list, original_image_url: str) -> list:
    """验证商品数据完整性"""
    validated = []
    
    for product in products:
        enriched = {'原始图片链接': original_image_url}
        
        #商品图链接
        img_link = product.get('商品图链接', '').strip()
        enriched['商品图链接'] = img_link if img_link else '/'
        
        #商品链接-通过搜索构建
        product_name = product.get('商品名称', '')
        detail_link = build_product_search_url(product_name)
        enriched['商品链接'] = detail_link if detail_link else '/'
        
        #其他字段
        other_fields = [
            '价格', '近 90 天销量', '近 14 天销量',
            '工厂年限', '回头率', '综合服务分', '客服响应率',
            '起订量', '发货履约率', '48h 揽收率', '首次上架时间',
            '评价数', '源头厂家', '供应商名称', '发货地'
        ]
        
        for field in other_fields:
            value = product.get(field, '').strip()
            enriched[field] = value if value else '/'
        
        validated.append(enriched)
    
    return validated


def convert_to_table_format(products: list) -> list:
    """转换为钉钉 AI 表格格式"""
    records = []
    
    for product in products:
        cells = {}
        for field_name, field_id in FIELD_MAP.items():
            value = product.get(field_name, '/')
            
            if field_name in ['原始图片链接', '1688 商品图链接', '商品链接']:
                cells[field_id] = {"link": value, "text": ""} if value and value != '/' else {"link": "", "text": ""}
            else:
                cells[field_id] = value
        
        records.append({"cells": cells})
    
    return records


def write_to_dingtalk_table(records: list, base_id: str, table_id: str) -> tuple:
    """写入钉钉 AI 表格"""
    print(f"\n💾 正在写入{len(records)}条记录到钉钉 AI 表格...")
    
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
        try:
            response = json.loads(result.stdout)
            if response.get('status') == 'success':
                new_ids = response.get('data', {}).get('newRecordIds', [])
                print(f"✅ 成功写入{len(new_ids)}条记录")
                return True, new_ids
        except json.JSONDecodeError:
            pass
    
    print(f"❌ 写入失败：{result.stderr if result.stderr else result.stdout}")
    return False, []


def main(data_file: str, base_id: str, table_id: str, original_image_url: str):
    """主函数"""
    print("=" * 60)
    print("1688 同款商品数据处理脚本v4.0")
    print("=" * 60)
    
    #读取数据
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            products = json.load(f)
        print(f"📊 已加载{len(products)}条商品记录")
    except FileNotFoundError:
        print(f"❌ 找不到数据文件：{data_file}")
        return
    except json.JSONDecodeError:
        print(f"❌ 数据文件格式错误：{data_file}")
        return
    
    #验证和丰富数据
    print("\n🔍 验证数据完整性...")
    validated_products = validate_products(products, original_image_url)
    
    #转换为表格格式
    records = convert_to_table_format(validated_products)
    
    #写入表格
    success, record_ids = write_to_dingtalk_table(records, base_id, table_id)
    
    if success:
        table_link = f"https://alidocs.dingtalk.com/i/nodes/{base_id}"
        
        print("\n" + "=" * 60)
        print("✅ 任务完成！")
        print("=" * 60)
        print(f"📊 表格链接：{table_link}")
        print(f"📝 记录数量：{len(records)}")
        print(f"🏷️ 字段数量：19")
        print("=" * 60)
    else:
        print("\n❌ 数据保存失败")


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 5:
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        #默认参数
        main(
            "/Users/goumaozhang/.real/workspace/products_data.json",
            "G1DKw2zgV2o9YzjnhBoAx1MkJB5r9YAn",
            "o4OnnQo",
            "https://images-na.ssl-images-amazon.com/images/I/71Tg1wI7YFL._AC_UL900_SR900,600_.jpg"
        )
