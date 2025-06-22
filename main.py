import csv
import logging
import os
import random
import time
from typing import Counter, Optional

import requests
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt
from rich.progress import track


def base_url() -> str:
    """获取豆瓣电影 Top 250 的基础 URL

    Returns:
        str: 基础URL
    """
    return "https://movie.douban.com/top250"


def get_params(page: int) -> dict:
    """通过页码获取请求的参数

    Args:
        page (int): 页码，从0开始

    Returns:
        dict: 请求参数
    """
    return {
        "start": page * 25,
    }


def get_headers() -> dict:
    """获取请求头，防止爬虫请求被网站屏蔽

    Returns:
        dict: 请求头
    """
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0"
    }


def get_soup(page: int) -> Optional[BeautifulSoup]:
    """通过页码获取对应页面的 BeautifulSoup 对象

    Args:
        page (int): 页码，从0开始

    Returns:
        Optional[BeautifulSoup]: BeautifulSoup 对象，如果请求失败则返回 None
    """
    try:
        response = requests.get(base_url(), params=get_params(page), headers=get_headers())
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        logging.error(f"请求失败 {page=}: {e}")
        return None


def get_chinese_items(soup: BeautifulSoup) -> list:
    """从 BeautifulSoup 对象中提取国产电影条目(<div class="item">)

    Args:
        soup (BeautifulSoup): BeautifulSoup 对象

    Returns:
        list: 所有的国产电影条目
    """
    items = soup.find_all("div", class_="item")
    chinese_items = []
    for item in items:
        if "中国" in item.find("div", class_="bd").find("p").get_text():  # type: ignore
            chinese_items.append(item)
    return chinese_items


def get_movie_infos(items: list) -> list[tuple[str, str]]:
    """从电影条目列表中提取电影名称和上映年份

    Args:
        items (list): 电影条目列表

    Returns:
        list[tuple[str, str]]: （电影名称，上映年份）组成的列表
    """
    movie_infos = []
    for item in items:
        name = item.find("div", class_="hd").find("span", class_="title").get_text()
        year = item.find("div", class_="bd").find("p").get_text().strip().splitlines()[1].strip()[:4]
        movie_infos.append((name, year))
    return movie_infos


def get_movie_posters(items: list) -> list[tuple[str, str]]:
    """从电影条目列表中提取电影名称和海报链接

    Args:
        items (list): 电影条目列表

    Returns:
        list[tuple[str, str]]: （电影名称，海报链接）组成的列表
    """
    movie_posters = []
    for item in items:
        img = item.find("div", class_="pic").find("img")
        name = img.get("alt")
        poster_url = img.get("src")
        movie_posters.append((name, poster_url))
    return movie_posters


def write_csv_header():
    """写入 CSV 文件的表头"""
    with open("douban.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["电影名称", "上映年份", "海报链接"])


def write_to_csv(movie_infos: list[tuple[str, str]], movie_posters: list[tuple[str, str]]):
    """将电影名称，上映年份，海报链接写入 CSV 文件

    Args:
        movie_infos (list[tuple[str, str]]): （电影名称，上映年份）组成的列表
        movie_posters (list[tuple[str, str]]): （电影名称，海报链接）组成的列表
    """
    with open("douban.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for (name, year), (_, poster_url) in zip(movie_infos, movie_posters):
            writer.writerow([name, year, poster_url])


def write_to_img(movie_posters: list[tuple[str, str]]):
    """将电影海报下载到本地

    Args:
        movie_posters (list[tuple[str, str]]): （电影名称，海报链接）组成的列表
    """
    for name, poster_url in movie_posters:
        try:
            response = requests.get(poster_url)
            response.raise_for_status()
            with open(f"film_img/{name}.jpg", "wb") as f:
                f.write(response.content)
        except requests.RequestException as e:
            logging.error(f"下载海报失败 {poster_url=}: {e}")


def handle_one_page(page: int):
    """完成一页的爬取工作

    Args:
        page (int): 页码，从0开始
    """
    soup = get_soup(page)
    if soup is None:
        return
    chinese_items = get_chinese_items(soup)
    movie_infos = get_movie_infos(chinese_items)
    movie_posters = get_movie_posters(chinese_items)
    write_to_csv(movie_infos, movie_posters)
    write_to_img(movie_posters)
    logging.info(f"第`{page + 1}`页处理完成，共`{len(chinese_items)}`部国产电影")


def random_sleep():
    """进行随机休眠，防止请求过于频繁被封禁。休眠时间范围：[1, 3] 秒"""
    sleep_time = random.uniform(1, 3)
    time.sleep(sleep_time)


def analyze_data():
    """进行年份与上映电影数量的可视化分析"""
    plt.rcParams["font.sans-serif"] = ["SimSun"]
    plt.rcParams["axes.unicode_minus"] = False

    with open("douban.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # 跳过表头
        years = [int(row[1]) for row in reader]
    counter = Counter(years)
    sorted_data = sorted(counter.items(), key=lambda x: x[0])
    years = [year for year, _ in sorted_data]
    counts = [count for _, count in sorted_data]
    plt.figure(figsize=(12, 8))
    plt.plot(years, counts, marker=".")
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.title("豆瓣电影Top250国产电影每年上榜数量变化趋势", fontsize=16)
    plt.xlabel("年份", fontsize=12)
    plt.ylabel("电影数量", fontsize=12)
    plt.savefig("douban.png", dpi=300)
    plt.show()


def main():
    """主函数，用于进行程序初始化工作以及执行爬取任务"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename="douban.log",
        encoding="utf-8",
    )
    image_dir = "film_img"
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    write_csv_header()
    for page in track(range(10)):
        handle_one_page(page)
        random_sleep()
    analyze_data()


if __name__ == "__main__":
    main()
