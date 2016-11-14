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

service_name = 'Twitter account'
service_commands = ['twitteraccount', 'twitter_account', 'twitter-account', 'twitteruser', 'twitter_user', 'twitter-user', 'ta', 'tu']
url_regex = r'^https?://(?:www\.)?twitter\.com/[^/]+$'
url_prefix = 'https://twitter.com/'
url_suffix = '/media'
url_user = lambda url: re.search(r'^https?://(?:www\.)?twitter\.com/([^/]+)', url).group(1)
url_id = lambda url: re.sub('&quot;', '"', extract_info(r'data-user-id="([0-9]+)"', url)[0])
item_title = lambda url: re.sub('&quot;', '"', extract_info(r'data-name="([^"]+)"', url)[0])

def process(service_file_name, command, user):
    url = check_create_url(command[1] + '/media', url_prefix, url_suffix)
    videotitle = item_title(url)
    videoid = url_id(url)

    yield(job_added(user, service_name, videotitle, url_id(url)))

    response = requests.get(url)
    for tweet in re.findall(r'data-permalink-path="([^"]+)"', response.text):
        functions.archive.main(['!a', 'https://twitter.com' + tweet], config.irc_nick)
        time.sleep(5)
    if 'data-min-position' in response.text:
        max_position = re.search(r'data-min-position="([^"]+)"', response.text).group(1)
        while 'data-min-position' in response.text or response_json['min_position']:
            response = requests.get('https://twitter.com/i/profiles/show/'
                + url_user(url) + '/media_timeline?include_available_features=1&include_entities=1&max_position='
                + max_position + '&reset_error_state=false')
            if response.status_code == 200:
                response_json = json.loads(response.text)
                max_position = response_json['min_position']
                for tweet in re.findall(r'data-permalink-path="([^"]+)"', response_json['items_html']):
                    functions.archive.main(['!a', 'https://twitter.com' + tweet], config.irc_nick)
                    time.sleep(5)
            else:
                yield(failed_extraction(user, service_name, url_id(url), 'nextpage'))
                break
        else:
            yield(job_finished(user, service_name, videotitle, url_id(url)))

def grab(url):
    exit_code = os.system('~/.local/bin/grab-site ' + url + ' --level=0 --custom-hooks=services/dl__twitter_com_user.py --ua="ArchiveTeam; Googlebot/2.1" --no-sitemaps --concurrency=1 --warc-max-size=524288000 --wpull-args="--no-check-certificate --timeout=300"')
    return exit_code

def add_url(url, ticket_id, user):
    yield(['message', user + ': You cannot create a periodical job for a ' + name + '.'])