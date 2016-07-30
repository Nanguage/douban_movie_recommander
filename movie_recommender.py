#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import sys
import pickle
import random
import argparse
import datetime
import webbrowser

import gevent
from gevent.queue import Queue
from gevent import monkey; monkey.patch_all()
import requests
from requests.exceptions import MissingSchema
from pyquery import PyQuery

MY_URL = "https://www.douban.com/people/115693512/" # 这里填入豆瓣主页url
MY_WISH_URL = MY_URL.replace('www', 'movie') + 'wish'
CACHE_FILE_PATH = './' \
        + re.search('.+/(.+)/.*$',MY_WISH_URL).group(1) + '.mr_cache'


s = requests.Session()
headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36",
        "Referer": MY_URL,
        }


def get_movie_list(url):
    """get the movie's info from the url

    :returns: [{'title':'', 'url':'', 'tags':['','',...]},{},...]

    """
    movie_list = []
    page_queue = get_page_queue(url)
    def get_one_page_info():
        """get one page's info and add to movie_list"""
        while not page_queue.empty():
            p = page_queue.get()
            print(p)
            html = s.get(p, headers=headers).text
            doc = PyQuery(html)
            item_nodes = doc('div.item')
            for item in item_nodes:
                item = doc(item)
                info = {}
                title = item('li.title').text()
                item_url = item('li.title a').attr('href')
                tag_node = item('span.tags')
                tags = [] if tag_node == [] else tag_node.text().split(' ')[1:]
                info['title'] = re.sub('\s', '', title)
                info['url'] = item_url
                info['tags'] = tags
                movie_list.append(info)
    # start 4 greenlets
    gevent_list = [gevent.spawn(get_one_page_info) for i in range(4)]
    gevent.joinall(gevent_list)
    return movie_list


def get_page_queue(url):
    """get all wish page to a queue"""
    page_queue = Queue()
    try:
        html = s.get(url, headers=headers).text
    except MissingSchema as e:
        print(e)
        print('请填入正确的url')
    doc = PyQuery(html)
    # amount of items
    item_count = int(doc('.subject-num').text().split('/')[1])
    pages_count = item_count // 15
    for i in range(pages_count + 1):
        page_url = url + "?start=%s&sort=time&rating=all&filter=all&mode=grid"%(i * 15)
        page_queue.put(page_url)
    return page_queue


def save_movie_list(movie_list, file_path):
    """use pickle save movie_list"""
    with open(file_path, 'wb') as f:
        pickle.dump(movie_list, f)


def get_local_cache(file_path):
    """read the movie_list from cache"""
    with open(file_path, 'rb') as f:
        result = pickle.load(f)
    return result
    

def print_info(movie_list):
    '''print the information of all movies'''
    print(MY_WISH_URL)
    print()
    for i in movie_list:
        print("-----------------------------------------------------------------")
        print()
        print("\033[33m%s\033[0m"%i["title"])
        print("\033[31mTags    :\033[0m   " + " ".join(i['tags']))
        print("\033[32mdouban  :\033[0m  \"%s\""%i['url'])
        print("\033[34mbilibili:\033[0m  \"%s\""%get_bilibili_query(i['title']))
        print()


def get_bilibili_query(item_title):
    """get the bilibili query page url"""
    base_url = "http://search.bilibili.com/all?keyword="
    result = base_url + item_title.split('/')[0]
    return result


def get_one_movie_randomly(movie_list):
    random.seed(datetime.datetime.now())
    one_movie = random.choice(movie_list)
    return one_movie


def filiter_by_tags(movie_list, tags):
    result = []
    for movie in movie_list:
        for t in tags:
            if t not in movie['tags']:
                break
            result.append(movie)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--info', help="Display the wish list's infomatiom.", action="store_true")
    parser.add_argument('-u', '--update', help="Update local cache.", action="store_true")
    parser.add_argument('-c', '--clean', help="Clean local cache.", action="store_true")
    parser.add_argument('-t', '--tags', help="Specify the tags.", nargs='*')
    args = parser.parse_args()

    if args.clean:
        print("Cleaning ...")
        os.system("rm ./.*.mr_cache")
        sys.exit()

    if args.update or not os.path.exists(CACHE_FILE_PATH):
        print("Updating ...")
        movie_list = get_movie_list(MY_WISH_URL)
        save_movie_list(movie_list, CACHE_FILE_PATH)
        print("Local updated!(in '%s') run again with other option!"%CACHE_FILE_PATH)
        sys.exit()
    else:
        movie_list = get_local_cache(CACHE_FILE_PATH)

    if args.tags:
        tags = args.tags
        movie_list = filiter_by_tags(movie_list, tags)

    if args.info:
        print_info(movie_list)
    else:
        random_one = get_one_movie_randomly(movie_list)
        webbrowser.open_new(random_one['url'])
        webbrowser.open_new(get_bilibili_query(random_one['title']))
        print("Here is one movie you may be want to enjoy! It opened in your browser.")
