# quant-data

Data collectors for quant. 数据收集、清洗和存储等功能。

高质量的数据是量化的立足之本，谨防“Garbage in, garbage out”。

项目roadmap、技术cheatsheet和API文档：[quant-data WIKI](https://github.com/X0Leon/quant-data/wiki)。

阶段I：专注于高频数据(tick)的收集、存储和再加工（如计算分钟bar）。

# Dependencies:

* pandas
* tushare
* requests (optional)

# Changelog:

2017年01月17日，Version 0.2:

* 高频tick数据，及转化为各类bar数据的功能；

2016年12月13日，Version 0.1：

* 多线程收集股票日线数据到HDF5文件系统；

Author: X0Leon (Leon Zhang), pku09leon[@]gmail[dot]com.