// CS:GO皮肤价格查询器 JavaScript

class CSGOPriceTracker {
    constructor() {
        this.currentChart = null;
        this.searchTimeout = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupAutoComplete();
    }

    setupEventListeners() {
        // 搜索按钮点击事件
        document.getElementById('searchBtn').addEventListener('click', () => {
            this.searchItem();
        });

        // 搜索框回车事件
        document.getElementById('searchInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.searchItem();
            }
        });

        // 快速搜索按钮事件
        document.querySelectorAll('.quick-search').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const itemName = e.target.dataset.item;
                document.getElementById('searchInput').value = itemName;
                this.searchItem();
            });
        });

        // 搜索框实时搜索
        document.getElementById('searchInput').addEventListener('input', (e) => {
            this.handleAutoComplete(e.target.value);
        });
    }

    setupAutoComplete() {
        // 实时搜索建议
        const searchInput = document.getElementById('searchInput');
        searchInput.addEventListener('focus', () => {
            searchInput.classList.add('search-glow');
        });
        
        searchInput.addEventListener('blur', () => {
            setTimeout(() => {
                searchInput.classList.remove('search-glow');
                document.getElementById('suggestions').style.display = 'none';
            }, 200);
        });
    }

    async handleAutoComplete(query) {
        if (!query.trim() || query.length < 2) {
            document.getElementById('suggestions').style.display = 'none';
            return;
        }

        // 防抖处理
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(async () => {
            try {
                const response = await axios.get(`/api/search?q=${encodeURIComponent(query)}`);
                this.displaySuggestions(response.data);
            } catch (error) {
                console.error('搜索建议获取失败:', error);
            }
        }, 300);
    }

    displaySuggestions(data) {
        const suggestionsDiv = document.getElementById('suggestions');
        const suggestionsList = document.getElementById('suggestionsList');
        
        suggestionsList.innerHTML = '';
        
        if (data.suggestions && data.suggestions.length > 0) {
            data.suggestions.forEach(suggestion => {
                const badge = document.createElement('span');
                badge.className = 'suggestion-badge';
                badge.textContent = suggestion;
                badge.addEventListener('click', () => {
                    document.getElementById('searchInput').value = suggestion;
                    this.searchItem();
                    suggestionsDiv.style.display = 'none';
                });
                suggestionsList.appendChild(badge);
            });
            
            suggestionsDiv.style.display = 'block';
        } else {
            suggestionsDiv.style.display = 'none';
        }
    }

    async searchItem() {
        const query = document.getElementById('searchInput').value.trim();
        if (!query) {
            this.showError('请输入要搜索的皮肤名称');
            return;
        }

        this.showLoading(true);
        this.hideError();

        try {
            const response = await axios.get(`/api/price/${encodeURIComponent(query)}`);
            this.displayResults(response.data);
            await this.loadPriceChart(query);
        } catch (error) {
            console.error('搜索失败:', error);
            if (error.response && error.response.status === 404) {
                this.showError('未找到该皮肤，请检查名称或尝试其他搜索词');
            } else {
                this.showError('搜索失败，请稍后重试');
            }
        } finally {
            this.showLoading(false);
        }
    }

    displayResults(data) {
        // 显示结果区域
        document.getElementById('resultsSection').style.display = 'block';
        document.getElementById('resultsSection').classList.add('fade-in-up');

        // 更新物品信息
        document.getElementById('itemName').textContent = data.item_name;
        
        // 更新价格信息
        const currentPrice = data.current_price;
        if (currentPrice) {
            document.getElementById('lowestPrice').textContent = currentPrice.lowest_price || '-';
            document.getElementById('medianPrice').textContent = currentPrice.median_price || '-';
            document.getElementById('volume').textContent = currentPrice.volume || '-';
        }

        // 更新历史价格表格
        this.updateHistoryTable(data.history);
        
        // 隐藏建议
        document.getElementById('suggestions').style.display = 'none';
    }

    updateHistoryTable(history) {
        const tbody = document.getElementById('historyTable');
        tbody.innerHTML = '';

        if (history && history.length > 0) {
            history.slice(0, 20).forEach(record => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${new Date(record.timestamp).toLocaleString('zh-CN')}</td>
                    <td class="fw-bold">$${record.price.toFixed(2)}</td>
                    <td>
                        <span class="badge bg-primary">${record.source}</span>
                    </td>
                `;
                tbody.appendChild(row);
            });
        } else {
            const row = document.createElement('tr');
            row.innerHTML = '<td colspan="3" class="text-center text-muted">暂无历史价格数据</td>';
            tbody.appendChild(row);
        }
    }

    async loadPriceChart(itemName) {
        try {
            const response = await axios.get(`/api/chart/${encodeURIComponent(itemName)}`);
            this.createChart(response.data);
        } catch (error) {
            console.error('图表数据获取失败:', error);
        }
    }

    createChart(chartData) {
        const ctx = document.getElementById('priceChart').getContext('2d');
        
        // 销毁现有图表
        if (this.currentChart) {
            this.currentChart.destroy();
        }

        // 处理图表数据
        const labels = chartData.labels.map(label => {
            const date = new Date(label);
            return date.toLocaleDateString('zh-CN');
        });

        const prices = chartData.prices;

        // 创建渐变色
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, 'rgba(102, 126, 234, 0.8)');
        gradient.addColorStop(1, 'rgba(102, 126, 234, 0.1)');

        this.currentChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: '价格 (USD)',
                    data: prices,
                    borderColor: '#667eea',
                    backgroundColor: gradient,
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#667eea',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 20
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: '#667eea',
                        borderWidth: 1,
                        cornerRadius: 10,
                        displayColors: false,
                        callbacks: {
                            label: function(context) {
                                return `价格: $${context.parsed.y.toFixed(2)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: '日期'
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: '价格 (USD)'
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toFixed(2);
                            }
                        }
                    }
                },
                animation: {
                    duration: 1000,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }

    showLoading(show) {
        const loadingIndicator = document.getElementById('loadingIndicator');
        loadingIndicator.style.display = show ? 'block' : 'none';
    }

    showError(message) {
        const errorDiv = document.getElementById('errorMessage');
        const errorText = document.getElementById('errorText');
        errorText.textContent = message;
        errorDiv.style.display = 'block';
        errorDiv.classList.add('fade-in-up');
        
        // 5秒后自动隐藏错误消息
        setTimeout(() => {
            this.hideError();
        }, 5000);
    }

    hideError() {
        document.getElementById('errorMessage').style.display = 'none';
    }
}

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new CSGOPriceTracker();
    
    // 添加一些用户体验优化
    console.log('🎮 CS:GO皮肤价格查询器已加载');
    console.log('💡 提示：支持模糊搜索，输入部分皮肤名称即可获得建议');
});
