# CS:GO 皮肤价格查询器

一个功能完整的CS:GO皮肤价格查询网站，支持多个交易平台的实时价格获取、历史价格追踪和价格趋势图表。

## 🎮 功能特点

- **多平台价格聚合**: 集成Steam市场、Buff163、CS.Money、BitSkins等多个交易平台
- **实时价格查询**: 获取最新的皮肤价格信息
- **价格历史追踪**: 存储并展示历史价格变化
- **智能搜索**: 支持模糊搜索和自动完成功能
- **价格趋势图表**: 使用Chart.js展示价格波动趋势
- **响应式设计**: 支持桌面和移动设备
- **后台自动更新**: 定期更新热门物品价格

## 🛠️ 技术栈

### 后端
- **Flask**: Python Web框架
- **SQLite**: 轻量级数据库
- **requests**: HTTP请求库
- **BeautifulSoup**: 网页解析
- **fuzzywuzzy**: 模糊字符串匹配

### 前端
- **HTML5/CSS3**: 网页结构和样式
- **JavaScript (ES6+)**: 交互逻辑
- **Bootstrap 5**: UI框架
- **Chart.js**: 图表库
- **Font Awesome**: 图标库
- **Axios**: HTTP客户端

## 📦 安装和运行

### 1. 克隆项目
```bash
git clone <项目地址>
cd myproject
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 运行应用
```bash
python app.py
```

### 4. 访问网站
打开浏览器访问: http://localhost:5000

## 🎯 使用方法

### 搜索皮肤
1. 在搜索框中输入皮肤名称（支持中文和英文）
2. 系统会自动提供搜索建议
3. 点击搜索或按回车键开始查询

### 查看价格信息
- **当前价格**: 显示最低价格和中位价格
- **多平台对比**: 展示不同交易平台的价格
- **价格趋势图**: 显示最近30天的价格变化
- **历史记录**: 查看详细的价格历史数据

### 快速搜索
点击侧边栏的热门皮肤按钮，可以快速查询常见物品的价格。

## 🌐 支持的交易平台

1. **Steam Market** - Steam官方市场
2. **Buff163** - 国内最大的CS:GO交易平台
3. **CS.Money** - 国际知名交易平台
4. **BitSkins** - 老牌皮肤交易网站

*注意：部分平台可能需要API密钥或特殊认证*

## 📊 API接口

### 搜索物品
```
GET /api/search?q=<查询词>
```

### 获取价格
```
GET /api/price/<物品名称>
```

### 获取图表数据
```
GET /api/chart/<物品名称>
```

## 🔧 配置说明

### 数据库配置
系统使用SQLite数据库，首次运行时会自动创建必要的表结构。

### 爬虫配置
- 默认每30分钟更新一次热门物品价格
- 请求间隔设置为3秒，避免被反爬虫系统检测
- 支持自定义User-Agent和请求头

## 🚀 部署建议

### 生产环境部署
1. 使用Gunicorn作为WSGI服务器
2. 配置Nginx作为反向代理
3. 使用PostgreSQL或MySQL替代SQLite
4. 添加Redis缓存层

### Docker部署
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## ⚠️ 注意事项

1. **API限制**: 某些交易平台有API调用频率限制
2. **法律合规**: 使用爬虫时请遵守相关网站的robots.txt和服务条款
3. **数据准确性**: 价格数据仅供参考，实际交易以平台显示为准
4. **网络环境**: 部分国外平台可能需要网络代理访问

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进这个项目。

### 开发环境设置
1. Fork项目仓库
2. 创建功能分支
3. 提交代码更改
4. 创建Pull Request

## 📄 许可证

本项目使用MIT许可证，详情请查看LICENSE文件。

## 📞 支持

如果您在使用过程中遇到问题，请通过以下方式获取帮助：
- 创建GitHub Issue
- 发送邮件到项目维护者
- 查看项目Wiki文档

---

**免责声明**: 本工具仅用于学习和研究目的，请合理使用并遵守相关法律法规。
