## ICBC Credit Suisse Intern Project

### 使用说明：
> python main.py --name "上证50" --index 000001
主函数，用于对指数的收益率进行比较和计算
1. name 是指数名称，如 上证50 上证180 上证380 等
2. index 是上证指数（沪深300 akshare 没法获取到数据）

> python toolclass.spider.spider.py --name "上证50"
辅助函数，爬虫爬取指数调整信息
1. name 是指数名称，如 上证50 上证180 上证380 等
