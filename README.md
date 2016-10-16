# quant-data
Data collectors for quant using Python3. 数据收集、清洗和存储等功能。

高质量的数据是量化的立足之本，谨防“Garbage in, garbage out”。

有些数据可以商业购买，但抓取开放数据也必不可少，也是必备技能。

### 数据分类

对我们感兴趣的数据大致分类（未必准确）：

* 交易数据：主要是带事件戳的OHLC+volume的bar，或者分笔成交的数据，或者实时bid/ask数据
* 扩展交易数据：交易数据背后信息，如龙虎榜、融资融券、股东持股变动等
* 财务数据：公司基本面的数据，如营业额、净利润、现金流、净资产、周转率等
* 公司归类：行业板块、概念、各类指数等
* 宏观数据：GDP、利率、广义货币、CPI、工业品出厂价格指数等
* 新闻研报：滚动新闻、信息地雷及研究员报告等
* 舆情数据：雪球、微博、搜索引擎等反映市场心理的数据

### 数据源

主要关注中国市场相关，国际金融部分也考虑，因为会有联动和冲击。

* Yahoo! Finance (使用广泛)：交易数据
* Sina finance (新浪财经)：交易数据
* xueqiu （雪球）：舆情数据、投资参考等
* Sina weibo（新浪微博）：舆情数据

### Python库

稳定可靠的python库，我们不重复造轮子，且可供学习。

* Tushare [源码](https://github.com/waditu/tushare): 含股票实时/历史交易数据、龙虎榜等扩展交易数据、行业分类、财务、宏观、新闻事件等
* pandas-datareader [源码](https://github.com/pydata/pandas-datareader)：Yahoo!/Google Finance、世界银行等数据

## 功能与规划

如果需要的数据已经稳定、快速、健康，则直接使用或者简单封装，否则需要实现。

目前处于开发中，任何相关代码或建议都欢迎。
