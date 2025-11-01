#!/usr/bin/env python3
"""
中国象棋游戏启动脚本
"""

import os
import sys
import subprocess
import webbrowser
import time
from threading import Timer

def check_dependencies():
    """检查依赖"""
    required_packages = ['flask', 'flask-cors']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'flask-cors':
                import flask_cors
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 缺少以下依赖包:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n安装命令:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def open_browser():
    """延迟打开浏览器"""
    time.sleep(2)
    try:
        webbrowser.open('http://localhost:5000')
        print("🌐 已自动打开浏览器")
    except Exception as e:
        print(f"⚠️  无法自动打开浏览器: {e}")
        print("请手动访问: http://localhost:5000")

def main():
    """主函数"""
    print("🎮 中国象棋游戏启动器")
    print("=" * 50)
    
    # 检查依赖
    print("🔍 检查依赖...")
    if not check_dependencies():
        sys.exit(1)
    
    print("✅ 依赖检查通过")
    
    # 检查文件
    required_files = [
        'xiangqi.html',
        'xiangqi_server.py',
        'static/js/xiangqi.js'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ 缺少以下文件:")
        for file in missing_files:
            print(f"   - {file}")
        sys.exit(1)
    
    print("✅ 文件检查通过")
    
    # 启动服务器
    print("🚀 启动游戏服务器...")
    
    # 延迟打开浏览器
    timer = Timer(3, open_browser)
    timer.start()
    
    try:
        # 启动Flask服务器
        subprocess.run(['python3', 'xiangqi_server.py'])
    except KeyboardInterrupt:
        print("\n🛑 游戏服务器已停止")
        timer.cancel()

if __name__ == '__main__':
    main()
