import re
import os
import sys
import download_page
import url
import irc_message
import json
import requests

extract_info = lambda regexes, url: download_page.extract_info(regexes, url)
job_finished = lambda user, name, title, id: irc_message.job_finished(user, name, title, id)
job_failed = lambda user, name, title, id: irc_message.job_failed(user, name, title, id)
job_added = lambda user, name, title, id: irc_message.job_added(user, name, title, id)
job_aborted = lambda user, name, id: irc_message.job_added(user, name, id)
failed_extraction = lambda user, name, id: irc_message.failed_extraction(user, name, id)
check_create_url = lambda url_, prefix, suffix: url.check_create_url(url_, prefix, suffix)

service_name = 'Facebook media'
service_commands = ['facebook']
url_regex = r'^https?://(?:www\.)?facebook\.com/[^/]+/videos/[0-9]+/?'
url_prefix = 'https://www.facebook.com/video/video.php?v='
url_suffix = ''
url_user = lambda url: re.search(r'^https?://(?:www\.)?facebook\.com/([^/]+)/videos/[0-9]+/?', url).group(1)
url_id = lambda url: re.search(r'^https?://(?:www\.)?facebook\.com/[^/]+/videos/([0-9]+)/?', url).group(1)
item_title = lambda url: extract_info(r'<title\s+id="pageTitle">([^<]+(?:\.\.\.)?)\s+-\s+[^<]+</title>', url)[0]

def process(service_file_name, command, user):
    url = check_create_url(command[1], url_prefix, url_suffix)
    videotitle = item_title(url)
    videoid = url_id(url)

    if requests.get('https://archive.org/details/archiveteam_videobot_facebook_com_' + url_id(url)).status_code == 200:
        yield(job_finished(user, service_name, videotitle, url_id(url)))
    elif videotitle != None:
        yield(job_added(user, service_name, videotitle, url_id(url)))
        if grab(url) in [0, 4, 8]:
            yield(job_finished(user, service_name, videotitle, url_id(url)))
        else:
            yield(job_failed(user, service_name, videotitle, url_id(url)))
    else:
        yield(failed_extraction(user, service_name, url_id(url), 'title'))
        yield(job_aborted(user, service_name, url_id(url)))

def grab(url):
    exit_code = os.system('~/.local/bin/grab-site ' + url + ' --level=0 --custom-hooks=services/dl__facebook_com.py --ua="Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1" --no-sitemaps --concurrency=1 --warc-max-size=524288000 --wpull-args="--no-check-certificate --timeout=300"')
    return exit_code

def add_url(url, ticket_id, user):
    yield(['message', user + ': You cannot create a periodical job for a ' + name + '.'])
