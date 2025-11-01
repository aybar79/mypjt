#!/usr/bin/env python3
"""
测试CS:GO价格查询服务器
"""

import urllib.request
import urllib.parse
import json
import sys

def test_api(url, description):
    """测试API端点"""
    print(f"\n🧪 测试: {description}")
    print(f"URL: {url}")
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            status_code = response.getcode()
            data = response.read().decode('utf-8')
            
            print(f"状态码: {status_code}")
            
            if status_code == 200:
                try:
                    json_data = json.loads(data)
                    print("✅ JSON响应:")
                    print(json.dumps(json_data, indent=2, ensure_ascii=False)[:500] + "...")
                except json.JSONDecodeError:
                    print("✅ HTML响应:")
                    print(data[:200] + "...")
            else:
                print(f"❌ 错误状态码: {status_code}")
                
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def main():
    base_url = "http://localhost:8000"
    
    print("🎮 CS:GO价格查询器服务器测试")
    print("=" * 50)
    
    # 测试主页
    test_api(f"{base_url}/", "主页访问")
    
    # 测试搜索API
    test_api(f"{base_url}/api/search?q=AK-47", "搜索API")
    
    # 测试价格API
    test_api(f"{base_url}/api/price/AK-47%20%7C%20Redline", "价格查询API")
    
    # 测试图表API
    test_api(f"{base_url}/api/chart/AK-47%20%7C%20Redline", "图表数据API")
    
    print("\n" + "=" * 50)
    print("🏁 测试完成")

if __name__ == "__main__":
    main()
