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

service_name = 'YouTube video'
service_commands = ['youtube', 'yt']
url_regex = r'^https?:\/\/(?:www\.)?youtube\.(?:com|nl)\/watch\?v=[0-9a-zA-Z_-]+'
url_prefix = 'https://www.youtube.com/watch?v='
url_suffix = ''
url_id = lambda url: re.search(r'^https?:\/\/(?:www\.)?youtube\.(?:com|nl)\/watch\?v=([0-9a-zA-Z_-]+)', url).group(1)
item_title = lambda url: extract_info(r'"og:title" content="([^"]+)"', url)[0]

def process(service_file_name, command, user):
    url = check_create_url(command[1], url_prefix, url_suffix)
    videotitle = item_title(url)
    videoid = url_id(url)
    if videotitle != None:
        yield(user + ': ' + service_name + ' \'' + videotitle + '\' with ID ' + videoid + ' will be saved.')
        if grab(url) in (0, 256):
            if not '--no-ia' in command:
                if internet_archive_grab(url) == True:
                    yield(job_added(user, service_name, item_title, url_id))
                else:
                    yield(job_failed(user, service_name, item_title, url_id)) 
            else:
                yield(job_finished(user, service_name, item_title, url_id))
        else:
            yield(job_failed(user, service_name, item_title, url_id))
    else:
        yield(failed_extraction(user, service_name, url_id))
        yield(job_aborted(user, service_name, url_id))

def grab(url):
    return 0

def internet_archive_grab(url):
    item_info = extract_info([r'<p\s+id="eow-description"\s*>(.*?)<\/p>',
                         r'<meta\s+itemprop="date[pP]ublished"\s+content="([0-9-]+)">',
                         r'<meta\s+property="og:video:tag"\s+content="([^"]+)">',
                         r'<meta\s+itemprop="paid"\s+content="([^"]+)">',
                         r'<meta\s+itemprop="channel[iI]d"\s+content="([^"]+)">',
                         r'<meta\s+itemprop="duration"\s+content="([^"]+)">',
                         r'<meta\s+itemprop="unlisted"\s+content="([^"]+)">',
                         r'<meta\s+itemprop="width"\s+content="([0-9]+)">',
                         r'<meta\s+itemprop="height"\s+content="([0-9]+)">',
                         r'<meta\s+itemprop="is[fF]amily[fF]riendly"\s+content="([^"]+)">',
                         r'<meta\s+itemprop="regions[aA]llowed"\s+content="([^"]+)">',
                         r'<meta\s+itemprop="genre"\s+content="([^"]+)">'], url)
    item_description = ''
    if item_info[0][0]:
        item_description = re.sub(r'<a\s+href="([^"]+)".+?<\/a>', r'\1', info[0][0])
    item_date = item_info[1][0]
    item_tags = ';'.join(item_info[2])
    item_paid_video = item_info[3][0]
    item_channel_id = item_info[4][0]
    item_duration = item_info[5][0]
    item_unlisted = item_info[6][0]
    item_width = item_info[7][0]
    item_height = item_info[8][0]
    item_family_friendly = item_info[9][0]
    item_regions = item_info[10][0]
    item_genre = item_info[11][0]
    item_username = extract_info(r'data-ytid="{}">([^<]+)</span>'.format(re.escape(item_channel_id)), url)
    return True

def add_url(url, ticket_id, user):
    yield(['message', user + ': You cannot create a periodical job for a ' + name + '.'])
    
