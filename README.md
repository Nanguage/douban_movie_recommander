# DouRecommander
这是一个简单的python命令行程序，它能够根据你给出的douban“想看”页面url获取所有你想看的电影的列表，并从中随机选取一个推荐给你。早日摆脱选择困难#_#

## 实现思路
爬取“想看”页面的上所有条目的标题、url、tags信息，在本地使用pickle对爬取到的信息进行持久化，此后请求时从中获取信息进行推荐或打印。
## 设置与使用

#### 第三方库依赖
BeautifulSoup
```
pip install bs4
```

#### 设置
在源代码文件中将MY_WISH_URL、BROWSER_COMMAND、CACHE_FILE_PATH三个变量值分别设置为豆瓣“想看”页面的url、打开浏览器的命令(例如firefox)和缓存地址(默认为当前目录)

#### [-h]显示帮助信息: 
	⋊> ~ python movie_recommender -h
	usage: m_ovie_recommend [-h] [-i] [-u] [-c] [-t [TAGS [TAGS ...]]]
	
	optional arguments:
	  -h, --help            show this help message and exit
	  -i, --info            Display the wish list's infomatiom.
	  -u, --update          Update local cache.
	  -c, --clean           Clean local cache.
	  -t [TAGS [TAGS ...]], --tags [TAGS [TAGS ...]]
 	                       Specify the tags.

#### [-u]更新本地缓存
为了提高程序运行速度，在本地设置了缓存。使用"-u"参数对本地缓存进行更新，第一次运行时自动获取缓存。"-c"参数可以清除本地缓存。
    ⋊> ~ python movie_recommender -u
    Updating ...
    Local updated!(in '/home/1.mr_cache') run again with other option!

#### 使用


#### [-i]打印信息

#### [-t]指定tag对结果进行筛选
