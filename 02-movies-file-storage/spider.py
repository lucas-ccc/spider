# 爬取电影基本信息，并存入 movies.txt
# 电影名称，类别，上映时间，评分

import requests
from pyquery import PyQuery as pq
import re

url = 'https://ssr1.scrape.center/'
html = requests.get(url).text
doc = pq(html)
items = doc('.el-card').items()

with open('movies.txt', 'w', encoding='utf-8') as f:
    for item in items:
        # 提取电影名称
        name = item.find('a > h2').text()
        # print(name)
        f.write(f'电影名称：{name}\n')
        # 类别
        categories = [
            item.text() for item in item.find('.categories button span').items()
        ]
        f.write(f'电影类别：{categories}\n')
        # 上映时间
        published_at = item.find('.info:contains(上映)').text()
        pat = r'(\d{4}-\d{2}-\d{2})'
        published_at = re.search(
            pat, published_at
        ).group(1) if published_at and re.search(pat, published_at) else None
        f.write(f'上映时间：{published_at}\n')
        # 评分
        score = item.find('p.score').text()
        f.write(f'电影评分：{score}\n')

        f.write(f'{"=" * 50}\n')
