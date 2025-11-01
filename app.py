from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import requests
import json
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from fuzzywuzzy import fuzz, process
import threading
import time
import schedule

app = Flask(__name__)
CORS(app)

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

# 导入多源爬虫系统
from crawlers import multi_crawler, search_all_markets

# CS:GO常见物品数据库（用于模糊搜索）
CSGO_ITEMS = [
    "AK-47 | Redline", "AK-47 | Vulcan", "AK-47 | Asiimov", "AK-47 | Bloodsport",
    "M4A4 | Asiimov", "M4A4 | Howl", "M4A4 | Dragon King", "M4A4 | Neo-Noir",
    "AWP | Dragon Lore", "AWP | Asiimov", "AWP | Hyper Beast", "AWP | Lightning Strike",
    "Glock-18 | Water Elemental", "Glock-18 | Fade", "Glock-18 | Wasteland Rebel",
    "Desert Eagle | Blaze", "Desert Eagle | Code Red", "Desert Eagle | Printstream",
    "USP-S | Kill Confirmed", "USP-S | Neo-Noir", "USP-S | Orion"
]

def get_db_connection():
    conn = sqlite3.connect('csgo_prices.db')
    conn.row_factory = sqlite3.Row
    return conn

def save_item_price(item_name, price_data, source="steam"):
    """保存物品价格到数据库"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 插入或获取物品
    cursor.execute('INSERT OR IGNORE INTO items (name, display_name) VALUES (?, ?)', 
                   (item_name, item_name))
    
    cursor.execute('SELECT id FROM items WHERE name = ?', (item_name,))
    item_id = cursor.fetchone()['id']
    
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

# API路由
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search')
def search_items():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400
    
    # 模糊搜索本地数据库
    matches = process.extract(query, CSGO_ITEMS, limit=10, scorer=fuzz.partial_ratio)
    suggestions = [match[0] for match in matches if match[1] > 60]
    
    # 搜索所有市场
    steam_results = search_all_markets(query)
    
    return jsonify({
        'suggestions': suggestions,
        'steam_results': steam_results
    })

@app.route('/api/price/<path:item_name>')
def get_item_price(item_name):
    # 从多个数据源获取价格
    market_data = multi_crawler.get_best_price(item_name)
    
    if market_data and market_data.get('all_sources'):
        # 保存所有数据源的价格到数据库
        for source_name, price_data in market_data['all_sources'].items():
            save_item_price(item_name, price_data, source_name)
        
        # 获取历史价格数据
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.price, p.timestamp, p.source
            FROM prices p
            JOIN items i ON p.item_id = i.id
            WHERE i.name = ?
            ORDER BY p.timestamp DESC
            LIMIT 100
        ''', (item_name,))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                'price': row['price'],
                'timestamp': row['timestamp'],
                'source': row['source']
            })
        
        conn.close()
        
        # 使用最佳价格作为当前价格，如果没有则使用第一个可用的价格
        current_price = market_data.get('best_price', {})
        if not current_price:
            # 使用第一个可用的价格源
            first_source = next(iter(market_data['all_sources'].values()))
            current_price = first_source
        
        return jsonify({
            'current_price': current_price,
            'all_sources': market_data['all_sources'],
            'history': history,
            'item_name': item_name
        })
    
    return jsonify({'error': 'Item not found'}), 404

@app.route('/api/chart/<path:item_name>')
def get_price_chart(item_name):
    """获取价格图表数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取最近30天的价格数据
    thirty_days_ago = datetime.now() - timedelta(days=30)
    cursor.execute('''
        SELECT p.price, p.timestamp
        FROM prices p
        JOIN items i ON p.item_id = i.id
        WHERE i.name = ? AND p.timestamp >= ?
        ORDER BY p.timestamp ASC
    ''', (item_name, thirty_days_ago))
    
    data = cursor.fetchall()
    conn.close()
    
    chart_data = {
        'labels': [row['timestamp'] for row in data],
        'prices': [row['price'] for row in data]
    }
    
    return jsonify(chart_data)

# 后台价格更新任务
def update_prices():
    """定期更新热门物品价格"""
    popular_items = CSGO_ITEMS[:5]  # 更新前5个热门物品（减少请求量）
    
    for item in popular_items:
        try:
            market_data = multi_crawler.get_best_price(item)
            if market_data and market_data.get('all_sources'):
                # 保存所有数据源的价格
                for source_name, price_data in market_data['all_sources'].items():
                    save_item_price(item, price_data, source_name)
                time.sleep(3)  # 避免请求过快
        except Exception as e:
            print(f"Error updating price for {item}: {e}")

def run_scheduler():
    schedule.every(30).minutes.do(update_prices)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    init_db()
    
    # 启动后台价格更新线程
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
