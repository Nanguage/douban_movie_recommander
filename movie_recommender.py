#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import sys
import pickle
import random
import urllib2
import argparse
import datetime
import subprocess
from bs4 import BeautifulSoup

MY_WISH_URL = "https://movie.douban.com/people/xxxxxxxxxxxxxx/wish" # 这里填入豆瓣“想看”页面的url
BROWSER_COMMAND = "firefox" # 这里填入开启浏览器的命令
CACHE_FILE_PATH = './' \ # 这里填入本地缓存路径
        + re.search('.+/(.+)/.*$',MY_WISH_URL).group(1) + '.mr_cache'

def get_movie_list(url):
    """get the movie from the url

    :url: string
    :returns: [{'title':'', 'url':'', 'tags':['','',...]},{},...]

    """
    movie_list = []
    page_list = get_page_list(url)
    for p in page_list:
        soup = BeautifulSoup(urllib2.urlopen(p).read(), "html.parser")
        item_nodes = soup.find_all("div", class_='item')
        for item in item_nodes:
            info = {}
            title = item.find('li', class_='title').a.get_text()
            info['title'] = re.sub('\s', '', title)
            info['url'] = item.find('li', class_='title').a['href']
            tag_node = item.find('span', class_='tags')
            info['tags'] =  [] if tag_node is None else tag_node.get_text().split(' ')[1:]
            movie_list.append(info)
    return movie_list

def save_movie_list(movie_list, file_path):
    """use pickle save movie_list

    :movie_list:
    :file_path: string

    """
    with open(file_path, 'w') as f:
        pickle.dump(movie_list, f)

def get_local_cache(file_path):
    """read the movie_list from cache

    :file_path: string
    :return: 

    """
    with open(file_path, 'r') as f:
        result = pickle.load(f)
    return result
    

def get_page_list(url):
    """get all wish page

    :douban_url: srting
    :returns: string

    """
    try:
        soup = BeautifulSoup(urllib2.urlopen(url).read(), "html.parser")
        page_list = [i['href'] for i in soup.find('div', class_='paginator').find_all('a')]
    except Exception as e:
        #print e
        page_list = []
    page_list.append(url)
    return page_list

def print_info(movie_list):
    '''print the information of all movies'''
    print MY_WISH_URL
    print
    for i in movie_list:
        print "-----------------------------------------------------------------"
        print
        print "\033[33m%s\033[0m"%i["title"]
        print "\033[31mTags    :\033[0m   " + " ".join(i['tags'])
        print "\033[32mdouban  :\033[0m  \"%s\""%i['url']
        print "\033[34mbilibili:\033[0m  \"%s\""%get_bilibili_query(i['title'])
        print

def get_bilibili_query(item_title):
    """get the bilibili query page url

    :item_title: string
    :returns: string

    """
    base_url = "http://search.bilibili.com/all?keyword="
    result = base_url + item_title.encode('utf-8').split('/')[0]
    return result

def get_one_movie_randomly(movie_list):
    """get one movie forom movie_list randomly

    :movie_list: list
    :returns: dict

    """
    random.seed(datetime.datetime.now())
    one_movie = random.choice(movie_list)
    return one_movie

def filiter_by_tags(movie_list, tags):
    """
    :movie_list
    :tags: ["","", ...]
    :return:
    """
    result = []
    for movie in movie_list:
        for t in tags:
            t = t.decode('utf-8')
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
        print "Cleaning ..."
        os.system("rm ./.*.mr_cache")
        sys.exit()

    if args.update or not os.path.exists(CACHE_FILE_PATH):
        print "Updating ..."
        movie_list = get_movie_list(MY_WISH_URL)
        save_movie_list(movie_list, CACHE_FILE_PATH)
        print "Local updated!(in '%s') run again with other option!"%CACHE_FILE_PATH
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
        subprocess.Popen([BROWSER_COMMAND, random_one['url']])
        subprocess.Popen([BROWSER_COMMAND, get_bilibili_query(random_one['title'])])
        print "Here is one movie you may be want to enjoy! It opened in your browser."
