import multiprocessing
import requests
import logging
import re
import json
from os import makedirs
from os.path import exists
from urllib.parse import urljoin

logging.basicConfig(
    level=logging.INFO,
    filename='spider.log',
    filemode='a',
    encoding='utf-8',
    format='%(asctime)s - %(levelname)s: %(message)s'
)


def scrape_page(url):
    """通过传入的 url，爬取对应的 html 并返回

    Arguments:
        url {str} -- page url

    Returns:
        str -- html of page
    """
    logging.info('scraping %s...', url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        logging.error(
            'get invalid status code %s while scraping %s',
            response.status_code, url
        )
    except requests.RequestException:
        logging.error('error occurred while scraping %s', url, exc_info=True)


def scrape_index(page):
    """爬取对应 page 的 html 并返回

    Arguments:
        page {str} -- page of index page

    Returns:
        sts -- html of index page
    """
    index_url = f'{BASE_URL}/page/{page}'
    return scrape_page(index_url)


def parse_index(html):
    """解析 scrape_index(page) 返回的 html，返回每部电影对应的详情页 url

    Arguments:
        html {str} -- page 对应网页的 html 文本

    Yields:
        generator -- 当前页面所有电影详情页 url 的迭代器
    """
    pattern = re.compile('<a.*?href="(.*?)".*?class="name">')
    items = re.findall(pattern, html)
    if not items:
        return []
    for item in items:
        detail_url = urljoin(BASE_URL, item)
        logging.info('get detail url %s', detail_url)
        yield detail_url


def scrape_detail(url):
    """爬取详情页

    Arguments:
        url {str} -- 详情页 url

    Returns:
        function -- 爬取页面函数
    """
    return scrape_page(url)


def parse_detail(html):
    """解析详情页的 html，以 字典 形式返回需要爬取的信息

    Arguments:
        html {str} -- 详情页 html 文本

    Returns:
        dict -- 需要爬取的信息
    """
    cover_pattern = re.compile(
        'class="item.*?<img.*?src="(.*?)".*?class="cover">', re.S
    )
    name_pattern = re.compile('<h2.*?>(.*?)</h2>')
    categories_pattern = re.compile(
        '<button.*?category.*?<span>(.*?)</span>.*?</button>', re.S
    )
    published_at_pattern = re.compile(r'(\d{4}-\d{2}-\d{2})\s?上映')
    drama_pattern = re.compile('<div.*?drama.*?>.*?<p.*?>(.*?)</p>', re.S)
    score_pattern = re.compile('<p.*?.score.*?>(.*?)</p>', re.S)

    cover = re.search(cover_pattern, html).group(1).strip(
    ) if re.search(cover_pattern, html) else None
    # 将 英文 : 替换为 中文 ：，避免文件命名出错
    name = re.search(name_pattern, html).group(1).strip(
    ).replace(': ', '：') if re.search(name_pattern, html) else None
    categories = re.findall(categories_pattern,
                            html) if re.findall(categories_pattern,
                                                html) else []
    published_at = re.search(published_at_pattern, html).group(1) if re.search(
        published_at_pattern, html
    ) else None
    drama = re.search(drama_pattern, html).group(1).strip(
    ) if re.search(drama_pattern, html) else None
    score = float(re.search(score_pattern, html).group(1).strip()
                  ) if re.search(score_pattern, html) else None

    return {
        'cover': cover,
        'name': name,
        'categories': categories,
        'published_at': published_at,
        'drama': drama,
        'score': score,
    }


def save_data(data):
    """将爬取的 data 保存到文件内

    Arguments:
        data {dict} -- 爬取的数据
    """
    name = data.get('name')
    data_path = f'{RESULT_DIR}/{name}.json'
    json.dump(
        data,
        open(data_path, 'w', encoding='utf-8'),
        ensure_ascii=False,
        indent=2
    )


BASE_URL = 'https://ssr1.scrape.center'
TOTAL_PAGE = 10
RESULT_DIR = 'results'
# 利用 or 的短路特性，存在目录则 or 后代码不执行，不存在，则创建
exists(RESULT_DIR) or makedirs(RESULT_DIR)


def main(page):
    index_html = scrape_index(page)
    detail_urls = parse_index(index_html)
    # logging.info('detail urls %s', list(detail_urls))
    for detail_url in detail_urls:
        detail_html = scrape_detail(detail_url)
        data = parse_detail(detail_html)
        logging.info('get detail data %s', data)
        logging.info('saving data to json file')
        save_data(data)
        logging.info('data saved successfully')


if __name__ == '__main__':
    pool = multiprocessing.Pool()
    pages = range(1, TOTAL_PAGE + 1)
    pool.map(main, pages)
    pool.close()
    pool.join()
