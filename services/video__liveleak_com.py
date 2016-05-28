import re
import os
import sys
import download_page
import url
import irc_message
import json

extract_info = lambda regexes, url: download_page.extract_info(regexes, url)
job_finished = lambda user, name, title, id: irc_message.job_finished(user, name, title, id)
job_failed = lambda user, name, title, id: irc_message.job_failed(user, name, title, id)
job_added = lambda user, name, title, id: irc_message.job_added(user, name, title, id)
job_aborted = lambda user, name, id: irc_message.job_added(user, name, id)
failed_extraction = lambda user, name, id: irc_message.failed_extraction(user, name, id)
check_create_url = lambda url_, prefix, suffix: url.check_create_url(url_, prefix, suffix)

service_name = 'LiveLeak video'
service_commands = ['liveleak']
url_regex = r'^https?://(?:www\.)?liveleak\.com/view\?i=[a-z0-9_]+'
url_prefix = 'http://www.liveleak.com/view?i='
url_suffix = ''
url_id = lambda url: re.search(r'^https?://(?:www\.)?liveleak\.com/view\?i=([a-z0-9_]+)', url).group(1)
item_title = lambda url: extract_info(r'<meta\s+property="og:title"\s+content="([^"]+)"/>', url)[0].replace('LiveLeak.com - ', '').strip()

def process(service_file_name, command, user):
    url = check_create_url(command[1], url_prefix, url_suffix)
    videotitle = item_title(url)
    videoid = url_id(url)
    if videotitle != None:
        yield(job_added(user, service_name, videotitle, url_id(url)))
        if grab(url) == 0:
            yield(job_finished(user, service_name, videotitle, url_id(url)))
        else:
            yield(job_failed(user, service_name, videotitle, url_id(url)))
    else:
        yield(failed_extraction(user, service_name, url_id(url), 'title'))
        yield(job_aborted(user, service_name, url_id(url)))

def grab(url):
    exit_code = os.system('~/.local/bin/grab-site ' + url + ' --level=0 --custom-hooks=services/dl__liveleak_com.py --no-sitemaps --concurrency=1 --warc-max-size=524288000 --wpull-args="--no-check-certificate --timeout=300"')
    return exit_code

def add_url(url, ticket_id, user):
    yield(['message', user + ': You cannot create a periodical job for a ' + name + '.'])
