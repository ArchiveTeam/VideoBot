import re
import os
import sys
import download_page

def extract_info(regexes, url):
    return download_page.extract_info(regexes, url)

name = 'YouTube user'
commands = ['youtube-user', 'yt-user']
regex = r'^https?:\/\/(?:www\.)?youtube\.(?:com|nl)\/user\/[0-9a-zA-Z_-]+'
prefix_id = 'https://www.youtube.com/user/'
title = lambda url: extract_info(r'"og:title" content="([^"]+)"', url)
url_id = lambda url: re.search(r'^https?:\/\/(?:www\.)?youtube\.(?:com|nl)\/user\/([0-9a-zA-Z_-]+)', url).group(1)

def process(service_name, command, user):
    if command[1].startswith('https://') or command[1].startswith('http://'):
        url = command[1]
    else:
        url = prefix_id + command[1]
    usertitle = title(url)
    userid = url_id(url)
    yield(user + ': YouTube user \'' + usertitle + '\' with ID ' + userid + ' will be saved.')
    # grabscripts
    yield(user + ': Your job for YouTube user \'' + usertitle + '\' with ID ' + userid + ' is finished.')

def add_url(url, ticket_id, user):
    yield(['add', 'url', '\'' + url + '\''])
    yield(['add', 'type', commands])
    yield(['message', user + ': Added ' + name + ' \'' + title(url) + '\' with ID \'' + url_id(url) + '\' to ticket ID \'' + ticket_id + '\'.'])
    yield(['message', user + ': Set refresh time using \'!perjob refreshtime <ticket ID> <refreshtime>\''])
    yield(['message', user + ': Use \'auto\' as <refreshtime> to let videobot decide on the refreshtime.'])

def periodical_job(service_name, command, user):
    if command[1] == 'refreshtime':
        if command[3] == 'auto':
            yield(['message', user + ': WIP'])
    else:
        pass
