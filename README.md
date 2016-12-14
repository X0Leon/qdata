# quant-data

Data collectors for quant. 数据收集、清洗和存储等功能。

高质量的数据是量化的立足之本，谨防“Garbage in, garbage out”。

项目roadmap、技术cheatsheet和API文档：[quant-data WIKI](https://github.com/X0Leon/quant-data/wiki)。

Dependencies:

* pandas
* tushare
* PyMySQL (optional)
* SQLAlchemy (optional)

Changelog:

2016年12月13日，Version 0.1：

* 初始化股票日线数据到HDF5文件系统；
* 盘后自动收集、存储行情数据；

Author: X0Leon, pku09leon[@]gmail[dot]com, MIT LICENSE.