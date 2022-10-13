from time import sleep
import requests
import re
from lxml import etree

urls = [f'https://cs.newhouse.fang.com/house/s/b9{i}/' for i in range(1, 44)]

for url in urls:
    resp = requests.get(url)

    e = etree.HTML(resp.text)

    names = [n.strip() for n in e.xpath('//div[@class="nlcd_name"]/a/text()')]
    addrs = e.xpath('//div[@class="address"]/a/@title')
    prices = [
        d.xpath('string(.)').strip()
        for d in e.xpath('//div[@class="nhouse_price"]')
    ]
    comments = e.xpath('//span[@class="value_num"]/text()')

    regex = re.compile(r'[\n\t\s]')
    house_types = [
        regex.sub('', t.xpath('string(.)'))
        for t in e.xpath('//div[@class="house_type clearfix"]')
    ]
    status = [
        regex.sub('', s.xpath('string(.)'))
        for s in e.xpath('//div[@class="fangyuan"]')
    ]

    with open('./res/fang-yuan.txt', 'a+', encoding='utf-8') as f:
        for name, addr, htype, price, st, comment in zip(
            names, addrs, house_types, prices, comments, status
        ):
            print(name, addr, htype, price, st, comment, sep=',', file=f)
            # print(name, addr, htype, price, comment, st, sep=',')

    sleep(0.5)
