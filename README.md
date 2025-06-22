# 武汉理工大学 Python高级程序设计 大作业

> 项目二：爬取豆瓣电影 Top250 数据（二）  
> 目标任务：爬取[豆瓣电影TOP250](https://movie.douban.com/top250)的全部国内中文电影名、上映时间等（需绕过反爬机制，遵守robots.txt，控制爬取速度），并将电影海报图片存储到本地文件夹中。
> 1. 核心技术  
> - 爬虫技术：Requests/Scrapy库、HTML解析（XPath/BeautifulSoup）
> - 反爬策略：Headers设置、IP代理、请求延迟
> - 数据存储：文件夹创建、图片二进制保存
> - 数据分析：Pandas基础统计、Matplotlib可视化
>
> 2. 分阶段任务
> - 阶段1：网页爬取  
> 实现分页爬取TOP250的全部国内中文电影名、上映时间及电影海报图片（共10页，每页25条）  
> 处理异常（如HTTP 403、页面结构变动）  
> 添加随机延迟（1-3秒/页）    
> - 阶段2：数据存储  
> 图片存储于film_img文件夹中，图片文件名为中文电影名，如肖申克的救赎.jpg。  
> - 阶段3：数据分析  
> 统计每年上榜电影数量及变化，曲线图展示（年份为x轴，电影数量为y轴），图表基本元素完整（标题/轴标签等），保存图片为文件。

建议使用uv运行本项目。uv是一个方便，快速的Python项目管理 + 环境管理工具，使用Rust🦀编写。uv官网：[uv - Astral](https://docs.astral.sh/uv/)

uv安装命令（Windows）
```shell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

快速同步项目环境，执行以下命令
```shell
uv sync
```

运行程序，执行以下命令
```shell
uv run main.py
```