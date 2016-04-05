import re
import os
import sys
import download_page
import url
import irc_message

extract_info = lambda regexes, url: download_page.extract_info(regexes, url)
job_finished = lambda user, name, title, id: irc_message.job_finished(user, name, title, id)
job_failed = lambda user, name, title, id: irc_message.job_failed(user, name, title, id)
job_added = lambda user, name, title, id: irc_message.job_added(user, name, title, id)
job_aborted = lambda user, name, id: irc_message.job_added(user, name, id)
failed_extraction = lambda user, name, id: irc_message.failed_extraction(user, name, id)
check_create_url = lambda url_, prefix, suffix: url.check_create_url(url_, prefix, suffix)

service_name = 'Vine video'
service_commands = ['vine']
url_regex = r'^https?://(?:www\.)?vine\.co/v/[0-9a-zA-Z]+'
url_prefix = 'https://vine.co/v/'
url_suffix = ''
url_id = lambda url: re.search(r'^https?://(?:www\.)?vine\.co/v/([0-9a-zA-Z]+)', url).group(1)
item_title = lambda url: extract_info(r'"articleBody": "([^"]+)"', url)[0]

def process(service_file_name, command, user):
    url = check_create_url(command[1], url_prefix, url_suffix)
    videotitle = item_title(url)
    videoid = url_id(url)
    if videotitle != None:
        yield(job_added(user, service_name, videotitle, url))
        if grab(url) == 0:
            yield(job_finished(user, service_name, videotitle, url))
        else:
            yield(job_failed(user, service_name, videotitle, url))
    else:
        yield(failed_extraction(user, service_name, url))
        yield(job_aborted(user, service_name, url))

def grab(url):
    exit_code = os.system('~/.local/bin/grab-site ' + url + ' --level=0 --custom-hooks=services/dl__vine_co.py --ua="ArchiveTeam; Googlebot/2.1" --no-sitemaps --concurrency=5 --warc-max-size=524288000 --wpull-args="--no-check-certificate --timeout=300" > /dev/null 2>&1')
    return exit_code

def add_url(url, ticket_id, user):
    yield(['message', user + ': You cannot create a periodical job for a ' + name + '.'])
