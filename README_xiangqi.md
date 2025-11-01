# 中国象棋游戏

一个功能完整的中国象棋网页游戏，支持双人对局和人机对局，具有三个AI难度等级。

## 功能特点

### 🎮 游戏模式
- **双人对局 (PvP)**: 两个玩家在同一设备上轮流下棋
- **人机对局 (vs AI)**: 与计算机AI对弈
  - **简单级别**: 随机移动策略
  - **中等级别**: 基于评估函数的智能选择
  - **困难级别**: 使用极小极大算法和α-β剪枝的深度搜索

### 🎯 游戏功能
- ✅ 完整的中国象棋规则实现
- ✅ 棋子移动合法性检查
- ✅ 精美的棋盘界面设计
- ✅ 移动历史记录
- ✅ 悔棋功能
- ✅ 智能提示系统
- ✅ 游戏状态显示
- ✅ 响应式设计，支持移动端

### 🧠 AI特性
- **简单AI**: 随机选择合法移动
- **中等AI**: 优先吃子，基于棋子价值评估
- **困难AI**: 3层深度搜索，位置评估，α-β剪枝优化

## 安装和运行

### 方法一：使用启动脚本（推荐）

1. 确保已安装Python 3.6+
2. 运行启动脚本：
```bash
python start_xiangqi.py
```

启动脚本会自动：
- 检查依赖包
- 验证文件完整性
- 启动服务器
- 打开浏览器

### 方法二：手动安装

1. 安装依赖：
```bash
pip install flask flask-cors
```

2. 启动服务器：
```bash
python xiangqi_server.py
```

3. 打开浏览器访问：
```
http://localhost:5000
```

## 文件结构

```
.
├── xiangqi.html              # 游戏主页面
├── xiangqi_server.py         # Flask后端服务器
├── start_xiangqi.py          # 启动脚本
├── static/
│   └── js/
│       └── xiangqi.js        # 前端游戏逻辑
└── README_xiangqi.md         # 说明文档
```

## 游戏规则

### 棋子移动规则
- **帅/将**: 只能在九宫格内移动，每次一格，不能斜走
- **仕/士**: 只能在九宫格内斜走，每次一格
- **相/象**: 斜走两格，不能过河，不能被别的棋子挡住象眼
- **马**: 走"日"字，不能被别的棋子挡住马腿
- **车**: 横竖直走，不限格数，不能跳过别的棋子
- **炮**: 横竖直走，不限格数，吃子时必须跳过一个棋子
- **兵/卒**: 向前一格，过河后可左右移动

### 胜负判定
- 将死对方的帅/将即获胜
- 无子可动为负

## 技术特色

### 前端技术
- 纯JavaScript实现，无需额外框架
- Bootstrap 5响应式UI设计
- Canvas绘图和CSS3动画效果
- 事件驱动的游戏状态管理

### 后端技术
- Flask轻量级Web框架
- RESTful API设计
- 模块化AI算法实现
- CORS跨域支持

### AI算法
- **极小极大算法**: 经典的博弈树搜索
- **α-β剪枝**: 优化搜索效率
- **位置评估**: 考虑棋子位置价值
- **深度搜索**: 可配置的搜索深度

## API接口

### AI移动
```
POST /api/ai_move
Content-Type: application/json

{
    "board": [[...], ...],
    "difficulty": "easy|medium|hard"
}
```

### 获取提示
```
POST /api/hint
Content-Type: application/json

{
    "board": [[...], ...],
    "is_red_turn": true
}
```

### 局面评估
```
POST /api/evaluate
Content-Type: application/json

{
    "board": [[...], ...]
}
```

## 开发说明

### 扩展AI难度
可以通过修改`xiangqi_server.py`中的`XiangqiAI`类来添加新的AI策略：

```python
def get_best_move(self, board, difficulty='medium'):
    if difficulty == 'custom':
        # 添加自定义AI逻辑
        pass
```

### 自定义界面
修改`xiangqi.html`中的CSS样式或添加新的JavaScript功能。

### 添加新功能
- 网络对战模式
- 棋谱保存和回放
- 更复杂的AI算法
- 音效和动画

## 系统要求

- Python 3.6+
- 现代浏览器（Chrome、Firefox、Safari、Edge）
- 内存: 最少128MB
- 支持JavaScript的环境

## 许可证

本项目为开源项目，供学习和交流使用。

## 作者

中国象棋游戏 - 基于Web技术的完整实现

---

享受游戏！🎉
