import sys
import time
import os
import re
import shutil
import time
import json
import html

wpull_hook = globals().get('wpull_hook')  # silence code checkers

counter = 0
firsturl = ''
ia_metadata = {'identifier': '', 'files': [], 'title': '', 'description': '', 'mediatype': 'movies', 'collection': 'archiveteam_videobot', 'date': '', 'original_url': '', 'creator': '', 'subject': ''}
orig_video = ''
added_to_list = []
item_id = ''
tempfiles = {}

def accept_url(url_info, record_info, verdict, reasons):
    global added_to_list
    if (firsturl == '' or url_info["url"] in added_to_list) and not '?lang=' in url_info["url"]:
        return True
    return False

def get_urls(filename, url_info, document_info):
    global counter
    global firsturl
    global ia_metadata
    global orig_video
    global added_to_list
    global item_id
    global tempfiles
    newurls = []
    if url_info["url"] in orig_video:
        filename_new = re.search(r'^https?://cdn\.liveleak\.com/.+?([^/]+\.[0-9a-zA-Z]+)\?', url_info["url"]).group(1)
        if not os.path.isdir('../ia_item'):
            os.makedirs('../ia_item')
        if not os.path.isfile('../ia_item/' + filename_new):
            shutil.copyfile(filename, '../ia_item/' + filename_new)
            ia_metadata['files'].append(filename_new)
    elif re.search('^https?://(?:www\.)?liveleak\.com/view\?i=[a-z0-9_]+', url_info["url"]) and firsturl == '':
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
            months = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
            item_description = re.sub('(?:<a\s+href=[^>]+>|</a>|<p>)', '', re.search(r'<div\s+id="body_text">(.+(?:\n.+)+)<style>', content).group(1).strip())
            item_title = re.search(r'<meta\s+property="og:title"\s+content="([^"]+)"/>', content).group(1).replace('LiveLeak.com - ', '')
            item_id = re.search(r'^https?://(?:www\.)?liveleak\.com/view\?i=([a-z0-9_]+)', url_info["url"]).group(1)
            item_name = re.search(r'By:.*?([0-9a-zA-Z-_]+)<\/a>', content).group(1)
            item_tags = [tag.replace('browse&q=', '') for tag in re.findall(r'"browse\?q=([^"]+)"', content)]
            item_date_ = re.search(r'/thumbs/([0-9]+/[A-Z][a-z]+/[0-9]+)/', content).group(1).replace('/', '-')
            item_date = item_date_.replace(re.search(r'-([A-Z][a-z]+)-', item_date_).group(1), months[re.search(r'-([A-Z][a-z]+)-', item_date_).group(1)])
            ia_metadata['title'] = item_title
            ia_metadata['identifier'] = 'archiveteam_videobot_liveleak_com_' + item_id
            ia_metadata['description'] = item_description
            ia_metadata['date'] = item_date
            ia_metadata['original_url'] = url_info["url"]
            ia_metadata['creator'] = item_name
            ia_metadata['subject'] = ';'.join(['videobot', 'archiveteam', 'liveleak', 'liveleak.com', item_id, item_name] + item_tags)
            orig_video = [''.join(parts) for parts in re.findall(r'file: "([^"]+)\.[^\.]+\.mp4(\?[^"]+)"', content)]
            print(orig_video)
            firsturl = url_info["url"]
            newurls += [{'url': url} for url in orig_video]
    if item_id in url_info["url"] and not re.search(r'^https?://cdn.liveleak.com', url_info["url"]):
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
            newurls += [{'url': re.search(r'^(https?://.+/)', url_info["url"]).group(1) + url.replace('&amp;', '&')} for url in re.findall(r"\.load\('([^']+)'\)", content)]
            newurls += [{'url': url} for url in extract_urls(content, url_info["url"]) if (re.search(r'^https?://(?:www\.)?liveleak\.com/view\?i=' + item_id, url) or not (re.search(r'^https?://(?:www\.)?liveleak\.com/view\?i=[a-z0-9_]+', url) or re.search(r'^https?://(?:www\.)?liveleak\.com/c/', url))) and not url in added_to_list]
    newurls += [{'url': newurl["url"] + '&ec_seek=0'} for newurl in newurls if re.search(r'ec_rate=[0-9]+$', newurl["url"])]
    for newurl in newurls:
        added_to_list.append(newurl["url"])
    return newurls + [{'url': newurl["url"] + '&ec_seek=0'} for newurl in newurls if re.search(r'ec_rate=[0-9]+$', newurl["url"])]

def exit_status(exit_code):
    global ia_metadata
    global tempfiles
    if os.path.isdir('../ia_item'):
        item_identifier = ia_metadata['identifier']
        for a, b in ia_metadata.items():
            with open('../ia_item/ia_metadata.py', 'a') as file:
                if type(b) is list:
                    content_string = str(b)
                else:
                    content_string = '\'' + str(b).replace('\'', '\\\'').replace('\n', '\\n').replace('\r', '\\r') + '\''
                file.write(str(a) + ' = ' + content_string + '\n')
        os.rename('../ia_item', '../../to_be_uploaded/ia_items/ia_item_' + item_identifier + '_' + str(int(time.time())))
    return exit_code

wpull_hook.callbacks.get_urls = get_urls
wpull_hook.callbacks.exit_status = exit_status
wpull_hook.callbacks.accept_url = accept_url

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
