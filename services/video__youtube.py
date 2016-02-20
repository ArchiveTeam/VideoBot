import re
import os
import sys
import download_page

def extract_info(regexes, url):
    return download_page.extract_info(regexes, url)

name = 'YouTube video'
commands = ['youtube', 'yt']
regex = r'^https?:\/\/(?:www\.)?youtube\.(?:com|nl)\/watch\?v=[0-9a-zA-Z_-]+'
prefix_id = 'https://www.youtube.com/watch?v='
title = lambda url: extract_info(r'"og:title" content="([^"]+)"', url)
url_id = lambda url: re.search(r'^https?:\/\/(?:www\.)?youtube\.(?:com|nl)\/watch\?v=([0-9a-zA-Z_-]+)', url).group(1)

def process(service_name, command, user):
    if command[1].startswith('https://') or command[1].startswith('http://'):
        url = command[1]
    else:
        url = prefix_id + command[1]
    videotitle = title(url)
    videoid = url_id(url)
    yield(user + ': ' + name + ' \'' + videotitle + '\' with ID ' + videoid + ' will be saved.')
    # grabscripts
    yield(user + ': Your job for YouTube video \'' + videotitle + '\' with ID ' + videoid + ' is finished.')

def add_url(url, ticket_id, user):
    yield(['message', user + ': You cannot create a periodical job for a ' + name + '.'])
    
