#!/usr/bin/env python3
"""
CS:GO皮肤价格查询器 - 简化版本
使用Python内置库创建的HTTP服务器
"""

import http.server
import socketserver
import json
import urllib.parse
import urllib.request
import sqlite3
import os
import threading
import time
from datetime import datetime, timedelta

# 初始化数据库
def init_db():
    conn = sqlite3.connect('csgo_prices.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL,
            icon_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER,
            price REAL NOT NULL,
            source TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_id) REFERENCES items (id)
        )
    ''')
    
    conn.commit()
    conn.close()

class SteamAPI:
    @staticmethod
    def get_item_price(item_name):
        """获取Steam市场价格（演示版本）"""
        # 首先尝试真实API
        url = "https://steamcommunity.com/market/priceoverview/"
        params = {
            'appid': 730,
            'currency': 1,
            'market_hash_name': item_name
        }
        
        try:
            # 构建完整URL
            query_string = urllib.parse.urlencode(params)
            full_url = f"{url}?{query_string}"
            
            # 创建请求
            req = urllib.request.Request(full_url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            # 发送请求（减少超时时间）
            with urllib.request.urlopen(req, timeout=3) as response:
                if response.getcode() == 200:
                    data = json.loads(response.read().decode())
                    if data.get('success'):
                        return {
                            'lowest_price': data.get('lowest_price', 'N/A'),
                            'median_price': data.get('median_price', 'N/A'),
                            'volume': data.get('volume', 'N/A'),
                            'source': 'Steam Market'
                        }
        except Exception as e:
            print(f"Steam API连接失败，使用演示数据: {e}")
        
        # 如果Steam API失败，返回模拟数据
        return SteamAPI.get_demo_price(item_name)
    
    @staticmethod
    def get_demo_price(item_name):
        """获取演示价格数据"""
        import random
        import hashlib
        
        # 基于物品名称生成一致的随机价格
        seed = int(hashlib.md5(item_name.encode()).hexdigest()[:8], 16)
        random.seed(seed)
        
        # 根据物品名称设置价格范围
        if 'Dragon Lore' in item_name:
            base_price = random.uniform(2000, 5000)
        elif 'Howl' in item_name:
            base_price = random.uniform(1500, 3000)
        elif 'Fire Serpent' in item_name:
            base_price = random.uniform(800, 1500)
        elif 'AK-47' in item_name:
            base_price = random.uniform(20, 300)
        elif 'AWP' in item_name:
            base_price = random.uniform(50, 500)
        elif 'M4A4' in item_name:
            base_price = random.uniform(15, 200)
        else:
            base_price = random.uniform(5, 100)
        
        lowest = base_price * 0.9
        median = base_price * 1.1
        volume = random.randint(50, 500)
        
        return {
            'lowest_price': f'${lowest:.2f}',
            'median_price': f'${median:.2f}',
            'volume': str(volume),
            'source': 'Demo Data (Steam API限制时的演示)'
        }

def save_item_price(item_name, price_data, source="steam"):
    """保存价格到数据库"""
    conn = sqlite3.connect('csgo_prices.db')
    cursor = conn.cursor()
    
    # 插入或获取物品
    cursor.execute('INSERT OR IGNORE INTO items (name, display_name) VALUES (?, ?)', 
                   (item_name, item_name))
    
    cursor.execute('SELECT id FROM items WHERE name = ?', (item_name,))
    result = cursor.fetchone()
    if result:
        item_id = result[0]
        
        # 保存价格数据
        if price_data and price_data.get('median_price'):
            price_str = price_data['median_price'].replace('$', '').replace(',', '')
            try:
                price = float(price_str)
                cursor.execute('INSERT INTO prices (item_id, price, source) VALUES (?, ?, ?)',
                              (item_id, price, source))
            except ValueError:
                pass
    
    conn.commit()
    conn.close()

def get_price_history(item_name):
    """获取价格历史"""
    conn = sqlite3.connect('csgo_prices.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT p.price, p.timestamp, p.source
        FROM prices p
        JOIN items i ON p.item_id = i.id
        WHERE i.name = ?
        ORDER BY p.timestamp DESC
        LIMIT 50
    ''', (item_name,))
    
    history = []
    for row in cursor.fetchall():
        history.append({
            'price': row[0],
            'timestamp': row[1],
            'source': row[2]
        })
    
    conn.close()
    return history

class CSGOPriceHandler(http.server.SimpleHTTPRequestHandler):
    """自定义HTTP请求处理器"""
    
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query_params = urllib.parse.parse_qs(parsed_path.query)
        
        if path == '/':
            self.serve_index()
        elif path.startswith('/api/price/'):
            item_name = path[11:]  # 移除 '/api/price/' 前缀
            item_name = urllib.parse.unquote(item_name)
            self.handle_price_request(item_name)
        elif path.startswith('/api/search'):
            query = query_params.get('q', [''])[0]
            self.handle_search_request(query)
        elif path.startswith('/api/chart/'):
            item_name = path[11:]  # 移除 '/api/chart/' 前缀
            item_name = urllib.parse.unquote(item_name)
            self.handle_chart_request(item_name)
        elif path.startswith('/static/'):
            self.serve_static_file(path)
        else:
            self.send_error(404)
    
    def serve_index(self):
        """提供主页"""
        try:
            with open('templates/index.html', 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            # 如果模板文件不存在，提供简单的HTML页面
            html_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CS:GO 皮肤价格查询器</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .search-box { margin-bottom: 20px; }
        input[type="text"] { width: 70%; padding: 12px; font-size: 16px; border: 2px solid #ddd; border-radius: 5px; }
        button { padding: 12px 20px; font-size: 16px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .result { margin-top: 20px; padding: 20px; background: #f8f9fa; border-radius: 5px; }
        .error { color: red; }
        .success { color: green; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 CS:GO 皮肤价格查询器</h1>
        <div class="search-box">
            <input type="text" id="searchInput" placeholder="输入皮肤名称，例如：AK-47 | Redline">
            <button onclick="searchItem()">搜索</button>
        </div>
        <div id="result"></div>
    </div>
    
    <script>
        async function searchItem() {
            const query = document.getElementById('searchInput').value.trim();
            const resultDiv = document.getElementById('result');
            
            if (!query) {
                resultDiv.innerHTML = '<div class="error">请输入要搜索的皮肤名称</div>';
                return;
            }
            
            resultDiv.innerHTML = '<div>正在搜索中...</div>';
            
            try {
                const response = await fetch(`/api/price/${encodeURIComponent(query)}`);
                const data = await response.json();
                
                if (response.ok) {
                    resultDiv.innerHTML = `
                        <div class="success">
                            <h3>${data.item_name}</h3>
                            <p><strong>最低价格:</strong> ${data.current_price.lowest_price}</p>
                            <p><strong>中位价格:</strong> ${data.current_price.median_price}</p>
                            <p><strong>交易量:</strong> ${data.current_price.volume}</p>
                            <p><strong>数据源:</strong> ${data.current_price.source}</p>
                        </div>
                    `;
                } else {
                    resultDiv.innerHTML = `<div class="error">错误: ${data.error}</div>`;
                }
            } catch (error) {
                resultDiv.innerHTML = `<div class="error">请求失败: ${error.message}</div>`;
            }
        }
        
        document.getElementById('searchInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchItem();
            }
        });
    </script>
</body>
</html>"""
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
    
    def serve_static_file(self, path):
        """提供静态文件"""
        try:
            file_path = path[1:]  # 移除开头的 '/'
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                # 根据文件扩展名设置Content-Type
                if path.endswith('.css'):
                    content_type = 'text/css'
                elif path.endswith('.js'):
                    content_type = 'text/javascript'
                else:
                    content_type = 'text/plain'
                
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(404)
        except Exception as e:
            print(f"提供静态文件失败: {e}")
            self.send_error(500)
    
    def handle_price_request(self, item_name):
        """处理价格查询请求"""
        try:
            # 获取Steam价格
            price_data = SteamAPI.get_item_price(item_name)
            
            if price_data:
                # 保存到数据库
                save_item_price(item_name, price_data)
                
                # 获取历史数据
                history = get_price_history(item_name)
                
                response_data = {
                    'current_price': price_data,
                    'history': history,
                    'item_name': item_name
                }
                
                self.send_json_response(response_data)
            else:
                self.send_json_response({'error': 'Item not found'}, 404)
                
        except Exception as e:
            print(f"处理价格请求失败: {e}")
            self.send_json_response({'error': 'Internal server error'}, 500)
    
    def handle_search_request(self, query):
        """处理搜索请求"""
        try:
            # 简单的模糊搜索
            csgo_items = [
                "AK-47 | Redline", "AK-47 | Vulcan", "AK-47 | Asiimov",
                "M4A4 | Asiimov", "M4A4 | Howl", "AWP | Dragon Lore",
                "AWP | Asiimov", "Glock-18 | Water Elemental"
            ]
            
            suggestions = [item for item in csgo_items if query.lower() in item.lower()]
            
            response_data = {
                'suggestions': suggestions[:10],
                'steam_results': []
            }
            
            self.send_json_response(response_data)
            
        except Exception as e:
            print(f"处理搜索请求失败: {e}")
            self.send_json_response({'error': 'Search failed'}, 500)
    
    def handle_chart_request(self, item_name):
        """处理图表数据请求"""
        try:
            history = get_price_history(item_name)
            
            chart_data = {
                'labels': [record['timestamp'] for record in history],
                'prices': [record['price'] for record in history]
            }
            
            self.send_json_response(chart_data)
            
        except Exception as e:
            print(f"处理图表请求失败: {e}")
            self.send_json_response({'error': 'Chart data failed'}, 500)
    
    def send_json_response(self, data, status_code=200):
        """发送JSON响应"""
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json_data.encode('utf-8'))

def main():
    """主函数"""
    print("🎮 CS:GO皮肤价格查询器启动中...")
    
    # 初始化数据库
    init_db()
    print("✅ 数据库初始化完成")
    
    # 设置HTTP服务器
    PORT = 8000
    Handler = CSGOPriceHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🌐 服务器运行在 http://localhost:{PORT}")
        print("💡 提示：使用 Ctrl+C 停止服务器")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 服务器已停止")

if __name__ == "__main__":
    main()
