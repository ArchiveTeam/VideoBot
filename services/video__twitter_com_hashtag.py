import re
import os
import sys
import download_page
import url
import irc_message
import json
import functions
import requests
import config
import time

extract_info = lambda regexes, url: download_page.extract_info(regexes, url)
job_finished = lambda user, name, title, id: irc_message.job_finished(user, name, title, id)
job_failed = lambda user, name, title, id: irc_message.job_failed(user, name, title, id)
job_added = lambda user, name, title, id: irc_message.job_added(user, name, title, id)
job_aborted = lambda user, name, id: irc_message.job_added(user, name, id)
failed_extraction = lambda user, name, id: irc_message.failed_extraction(user, name, id)
check_create_url = lambda url_, prefix, suffix: url.check_create_url(url_, prefix, suffix)

service_name = 'Twitter hashtag'
service_commands = ['twitterhashtag', 'twitter_hashtag', 'twitter-hashtag', 'twittertag', 'twitter_tag', 'twitter-tag', 'ta', 'tt']
url_regex = r'^https?://(?:www\.)?twitter\.com/hashtag/[^/]+$'
url_prefix = 'https://twitter.com/hashtag/'
url_suffix = '?f=videos'
url_user = lambda url: re.search(r'^https?://(?:www\.)?twitter\.com/hashtag/([^/]+)', url).group(1)

def process(service_file_name, command, user):
    url = check_create_url(command[1] + url_suffix, url_prefix, url_suffix)
    videotitle = '#' + url_user(url)

    yield(job_added(user, service_name, videotitle))

    response = requests.get(url)
    for tweet in re.findall(r'data-permalink-path="([^"]+)"', response.text):
        functions.archive.main(['!a', 'https://twitter.com' + tweet], config.irc_nick)
        time.sleep(10)
    if 'data-min-position' in response.text:
        max_position = re.search(r'data-min-position="([^"]+)"', response.text).group(1)
        while 'data-min-position' in response.text or response_json['min_position']:
            response = requests.get('https://twitter.com/i/search/timeline?f=videos&vertical=default&q=%23'
                + url_user(url) + '&include_available_features=1&include_entities=1&max_position='
                + max_position + '&reset_error_state=false')
            if response.status_code == 200:
                response_json = json.loads(response.text)
                max_position = response_json['min_position']
                for tweet in re.findall(r'data-permalink-path="([^"]+)"', response_json['items_html']):
                    functions.archive.main(['!a', 'https://twitter.com' + tweet], config.irc_nick)
                    time.sleep(10)
            else:
                yield(failed_extraction(user, service_name, videoid, 'nextpage'))
                break
        else:
            yield(job_finished(user, service_name, videotitle, videoid))

def add_url(url, ticket_id, user):
    yield(['message', user + ': You cannot create a periodical job for a ' + name + '.'])