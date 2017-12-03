import sys
import time
import os
import re
import shutil
import time
import json
import html
import datetime

wpull_hook = globals().get('wpull_hook')

firsturl = ''
ia_metadata = {'identifier': '', 'files': [], 'title': '', 'description': '', 'mediatype': 'movies', 'collection': 'archiveteam_videobot', 'date': '', 'original_url': '', 'creator': '', 'subject': ''}
added_to_list = []
tries = {}
video_file = None
item_id = None

def accept_url(url_info, record_info, verdict, reasons):
    global added_to_list
    if (firsturl == '' or url_info["url"] in added_to_list) and not '\\' in url_info["url"]:
        return True
    return False

def get_urls(filename, url_info, document_info):
    global firsturl
    global item_id
    global ia_metadata
    global added_to_list
    global video_file

    newurls = []

    def url_allowed(url, parent_url=None):
        return True

    def add_url(url, parent_url=None):
        if url in added_to_list:
            return None
        if url_allowed(url, parent_url):
            added_to_list.append(url)
            newurls.append({'url': url})

    if video_file is not None and video_file in url_info["url"]:
        if not os.path.isdir('../ia_item'):
            os.makedirs('../ia_item')
        shutil.copyfile(filename, '../ia_item/' + video_file)
        ia_metadata['files'].append(video_file)

    if firsturl == '':
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
            firsturl = url_info['url']
            for url in extract_urls(content, url_info['url']):
                add_url(url)
            url_name = 'hd_src_no_ratelimit'
            if 'hd_src_no_ratelimit' not in content:
                url_name = 'sd_src_no_ratelimit'
            video_file = re.search(url_name + ':"https?://[^/]+/v/[^/]+/([a-zA-Z0-9-_]+\.mp4)', content).group(1)
            item_id = re.search('video_id:"([0-9]+)"', content).group(1)
            item_name = re.search('ownerName:"([^"]+)"', content).group(1)
            ia_metadata['identifier'] = 'archiveteam_videobot_facebook_com_' + item_id
            ia_metadata['title'] = re.search('<title\s+id="pageTitle">([^<]+(?:\.\.\.))\s+-\s+[^<]+</title>', content).group(1)
            ia_metadata['description'] = html.unescape(re.search('<div\s+class="[^"]+userContent"[^>]+>(.+?)</div>', content).group(1))
            ia_metadata['date'] = datetime.datetime.fromtimestamp(int(re.search('data-utime="([0-9]+)"', content).group(1))).strftime('%Y-%m-%d %H:%M:%S')
            ia_metadata['original_url'] = firsturl
            ia_metadata['creator'] = item_name
            ia_metadata['creator_id'] = re.search('^https?://[^/]+/([^/]+)/videos/', url_info["url"]).group(1)
            ia_metadata['video_id'] = item_id
            ia_metadata['subject'] = ['videobot', 'archiveteam', 'facebook', 'facebook.com', item_id, item_name]

    for newurl in newurls:
        added_to_list.append(newurl['url'])

    return newurls

def exit_status(exit_code):
    global ia_metadata

    if os.path.isdir('../ia_item'):
        item_identifier = ia_metadata['identifier']
        for a, b in ia_metadata.items():
            with open('../ia_item/ia_metadata.py', 'a') as file:
                if type(b) is list:
                    content_string = str(b)
                else:
                    content_string = '\'' + str(b).replace('\'', '\\\'').replace('\n', '\\n').replace('\r', '\\r') + '\''
                file.write(str(a) + ' = ' + content_string + '\n')

        if len(os.listdir('../ia_item')) > 1:
            print(ia_metadata['files'])
            os.rename('../ia_item', '../../to_be_uploaded/ia_items/ia_item_' + item_identifier + '_' + str(int(time.time())))

    return exit_code

handle_response_grabsite = wpull_hook.callbacks.handle_response
def handle_response(url_info, record_info, response_info):
    global tries

    if not url_info["url"] in tries:
        tries[url_info["url"]] = 0
    elif tries[url_info["url"]] > 5:
        return wpull_hook.actions.FINISH        

    tries[url_info["url"]] += 1

    return handle_response_grabsite(url_info, record_info, response_info)

wpull_hook.callbacks.get_urls = get_urls
wpull_hook.callbacks.exit_status = exit_status
wpull_hook.callbacks.accept_url = accept_url
wpull_hook.callbacks.handle_response = handle_response

def extract_urls(file, url):
    extractedurls = []
    for extractedurl in re.findall('((?:....=)?(?P<quote>[\'"]).*?(?P=quote))', file, re.I):
        extractedstart = ''
        if re.search('^....=[\'"](.*?)[\'"]$', extractedurl[0], re.I):
            extractedstart = re.search(r'^(....)', extractedurl[0], re.I).group(1)
            extractedurl = re.search('^....=[\'"](.*?)[\'"]$', extractedurl[0], re.I).group(1)
        else:
            extractedurl = extractedurl[0][1:-1]
        extractedurl = re.search(r'^([^#]*)', extractedurl, re.I).group(1)
        extractedurl = extractedurl.replace('%3A', ':').replace('%2F', '/')
        if extractedurl.startswith('http:\/\/') or extractedurl.startswith('https:\/\/') or extractedurl.startswith('HTTP:\/\/') or extractedurl.startswith('HTTPS:\/\/'):
            extractedurl = extractedurl.replace('\/', '/')
        if extractedurl.startswith('//'):
            extractedurls.append("http:" + extractedurl)
        elif extractedurl.startswith('/'):
            extractedurls.append(re.search(r'^(https?:\/\/[^\/]+)', url, re.I).group(1) + extractedurl)
        elif re.search(r'^https?:?\/\/?', extractedurl, re.I):
            extractedurls.append(extractedurl.replace(re.search(r'^(https?:?\/\/?)', extractedurl, re.I).group(1), re.search(r'^(https?)', extractedurl, re.I).group(1) + '://'))
        elif extractedurl.startswith('?'):
            extractedurls.append(re.search(r'^(https?:\/\/[^\?]+)', url, re.I).group(1) + extractedurl)
        elif extractedurl.startswith('./'):
            if re.search(r'^https?:\/\/.*\/', url, re.I):
                extractedurls.append(re.search(r'^(https?:\/\/.*)\/', url, re.I).group(1) + '/' + re.search(r'^\.\/(.*)', extractedurl, re.I).group(1))
            else:
                extractedurls.append(re.search(r'^(https?:\/\/.*)', url, re.I).group(1) + '/' + re.search(r'^\.\/(.*)', extractedurl, re.I).group(1))
        elif extractedurl.startswith('../'):
            tempurl = url
            tempextractedurl = extractedurl
            while tempextractedurl.startswith('../'):
                if not re.search(r'^https?://[^\/]+\/$', tempurl, re.I):
                    tempurl = re.search(r'^(.*\/)[^\/]*\/', tempurl, re.I).group(1)
                tempextractedurl = re.search(r'^\.\.\/(.*)', tempextractedurl).group(1)
            extractedurls.append(tempurl + tempextractedurl)
        elif extractedstart == 'href':
            if re.search(r'^https?:\/\/.*\/', url, re.I):
                extractedurls.append(re.search(r'^(https?:\/\/.*)\/', url, re.I).group(1) + '/' + extractedurl)
            else:
                extractedurls.append(re.search(r'^(https?:\/\/.*)', url, re.I).group(1) + '/' + extractedurl)
    for extractedurl in re.findall(r'>[^<a-zA-Z0-9]*(https?:?//?[^<]+)<', file, re.I):
        extractedurl = re.search(r'^([^#]*)', extractedurl, re.I).group(1)
        extractedurls.append(extractedurl.replace(re.search(r'^(https?:?\/\/?)', extractedurl, re.I).group(1), re.search(r'^(https?)', extractedurl, re.I).group(1) + '://'))
    for extractedurl in re.findall(r'\[[^<a-zA-Z0-9]*(https?:?//?[^\]]+)\]', file, re.I):
        extractedurl = re.search(r'^([^#]*)', extractedurl, re.I).group(1)
        extractedurls.append(extractedurl.replace(re.search(r'^(https?:?\/\/?)', extractedurl, re.I).group(1), re.search(r'^(https?)', extractedurl, re.I).group(1) + '://'))
    return [extractedurl.replace('&amp;', '&').replace('&amp;', '&') for extractedurl in extractedurls]
