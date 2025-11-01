# CS:GO 皮肤价格爬虫系统
import requests
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PriceCrawler:
    """价格爬虫基类"""
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

class SteamMarketCrawler(PriceCrawler):
    """Steam市场价格爬虫"""
    def __init__(self):
        super().__init__()
        self.base_url = "https://steamcommunity.com/market/priceoverview/"
        self.search_url = "https://steamcommunity.com/market/search/render/"
    
    def get_item_price(self, market_hash_name):
        """获取Steam市场价格"""
        params = {
            'appid': 730,
            'currency': 1,
            'market_hash_name': market_hash_name
        }
        
        try:
            response = self.session.get(self.base_url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return {
                        'source': 'Steam',
                        'lowest_price': data.get('lowest_price'),
                        'median_price': data.get('median_price'),
                        'volume': data.get('volume'),
                        'timestamp': datetime.now().isoformat()
                    }
        except Exception as e:
            logger.error(f"Steam价格获取失败 {market_hash_name}: {e}")
        
        return None
    
    def search_items(self, query, limit=20):
        """搜索Steam市场物品"""
        params = {
            'appid': 730,
            'query': query,
            'start': 0,
            'count': limit,
            'search_descriptions': 0,
            'sort_column': 'popular',
            'norender': 1
        }
        
        try:
            response = self.session.get(self.search_url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    items = []
                    for item in data.get('results', []):
                        items.append({
                            'name': item.get('hash_name'),
                            'display_name': item.get('name'),
                            'icon_url': f"https://steamcommunity-a.akamaihd.net/economy/image/{item.get('asset_description', {}).get('icon_url')}",
                            'price': item.get('sell_price_text'),
                            'source': 'Steam'
                        })
                    return items
        except Exception as e:
            logger.error(f"Steam搜索失败: {e}")
        
        return []

class BuffMarketCrawler(PriceCrawler):
    """Buff市场价格爬虫（模拟，因为需要特殊认证）"""
    def __init__(self):
        super().__init__()
        self.base_url = "https://buff.163.com/api/market/goods"
    
    def get_item_price(self, item_name):
        """获取Buff市场价格（演示版本）"""
        # 注意：实际使用需要Buff API认证
        try:
            # 这里是模拟数据，实际应用需要真实API
            import random
            
            # 模拟价格数据
            base_price = random.uniform(10, 500)
            return {
                'source': 'Buff163',
                'lowest_price': f"¥{base_price:.2f}",
                'median_price': f"¥{base_price * 1.1:.2f}",
                'volume': str(random.randint(50, 500)),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Buff价格获取失败: {e}")
        
        return None

class CSMoneyAPI(PriceCrawler):
    """CS.Money API 爬虫"""
    def __init__(self):
        super().__init__()
        self.base_url = "https://cs.money/1.0/market/sell-orders"
    
    def get_item_price(self, item_name):
        """获取CS.Money价格"""
        try:
            params = {
                'limit': 1,
                'name': item_name
            }
            
            response = self.session.get(self.base_url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get('items'):
                    item = data['items'][0]
                    price = item.get('price', 0) / 100  # 价格通常以分为单位
                    
                    return {
                        'source': 'CS.Money',
                        'lowest_price': f"${price:.2f}",
                        'median_price': f"${price * 1.05:.2f}",
                        'volume': '1',
                        'timestamp': datetime.now().isoformat()
                    }
        except Exception as e:
            logger.error(f"CS.Money价格获取失败: {e}")
        
        return None

class BitSkinsAPI(PriceCrawler):
    """BitSkins API 爬虫（演示）"""
    def __init__(self):
        super().__init__()
        self.base_url = "https://bitskins.com/api/v1/get_price_data_for_items_on_sale/"
    
    def get_item_price(self, item_name):
        """获取BitSkins价格（演示版本）"""
        try:
            # 演示数据，实际需要API密钥
            import random
            
            price = random.uniform(5, 200)
            return {
                'source': 'BitSkins',
                'lowest_price': f"${price:.2f}",
                'median_price': f"${price * 1.08:.2f}",
                'volume': str(random.randint(20, 100)),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"BitSkins价格获取失败: {e}")
        
        return None

class MultiSourceCrawler:
    """多数据源价格聚合器"""
    def __init__(self):
        self.crawlers = {
            'steam': SteamMarketCrawler(),
            'buff': BuffMarketCrawler(),
            'csmoney': CSMoneyAPI(),
            'bitskins': BitSkinsAPI()
        }
    
    def get_all_prices(self, item_name):
        """从所有数据源获取价格"""
        results = {}
        
        for source_name, crawler in self.crawlers.items():
            try:
                price_data = crawler.get_item_price(item_name)
                if price_data:
                    results[source_name] = price_data
                
                # 避免请求过快
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"从{source_name}获取价格失败: {e}")
        
        return results
    
    def get_best_price(self, item_name):
        """获取最优价格"""
        all_prices = self.get_all_prices(item_name)
        
        if not all_prices:
            return None
        
        # 提取数值价格进行比较
        price_comparisons = []
        for source, data in all_prices.items():
            try:
                if data.get('lowest_price'):
                    price_str = data['lowest_price'].replace('$', '').replace('¥', '').replace(',', '')
                    price_val = float(price_str)
                    price_comparisons.append((price_val, source, data))
            except:
                continue
        
        if price_comparisons:
            # 返回最低价格的数据源
            price_comparisons.sort(key=lambda x: x[0])
            best_price = price_comparisons[0]
            
            return {
                'best_price': best_price[2],
                'all_sources': all_prices,
                'comparison': price_comparisons
            }
        
        return {'all_sources': all_prices}

# 创建全局爬虫实例
multi_crawler = MultiSourceCrawler()

def get_market_data(item_name):
    """获取市场数据的便捷函数"""
    return multi_crawler.get_best_price(item_name)

def search_all_markets(query):
    """在所有市场中搜索物品"""
    # 主要使用Steam的搜索功能
    steam_crawler = SteamMarketCrawler()
    return steam_crawler.search_items(query)

if __name__ == "__main__":
    # 测试爬虫功能
    test_item = "AK-47 | Redline (Field-Tested)"
    
    print("测试多源价格获取:")
    results = get_market_data(test_item)
    
    if results:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print("未找到价格数据")
