import sys
import time
import os
import re
import shutil
import time

wpull_hook = globals().get('wpull_hook')  # silence code checkers

counter = 0
firsturl = True
ia_metadata = {'identifier': '', 'files': [], 'title': '', 'description': '', 'mediatype': 'movies', 'collection': 'opensource', 'date': '', 'original_url': '', 'creator': '', 'subject': '', 'url': ''}

def get_urls(filename, url_info, document_info):
    global counter
    global firsturl
    global ia_metadata
    newurls = []
    if re.search(r'^https?://v\.cdn\.vine\.co/r/video.+\.mp4\?', url_info["url"]):
        filename_new = re.search(r'^https?://v\.cdn\.vine\.co/r/([^/]+)', url_info["url"]).group(1) + '.mp4'
        if not os.path.isdir('../ia_item'):
            os.makedirs('../ia_item')
        if not os.path.isfile('../ia_item/' + filename_new):
            shutil.copyfile(filename, '../ia_item/' + filename_new)
            ia_metadata['files'].append(filename_new)
    if firsturl:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
            item_id = re.search(r'^https?://(?:www\.)?vine\.co/v/([0-9a-zA-Z]+)', url_info["url"]).group(1)
            item_name = re.search(r'"name": "([^"]+)"', content).group(1)
            item_url = re.search(r'"url": "([^"]+)"', content).group(1)
            item_date = re.search(r'"datePublished": "([^"]+)"', content).group(1).replace('T', ' ')
            item_description = re.search(r'"articleBody": "([^"]+)"', content).group(1)
            ia_metadata['identifier'] = 'videobot_vine_co_' + item_id + '_test'
            ia_metadata['title'] = item_description
            ia_metadata['description'] = item_description
            ia_metadata['date'] = item_date
            ia_metadata['original_url'] = url_info["url"]
            ia_metadata['url'] = item_url
            ia_metadata['creator'] = item_name
            ia_metadata['subject'] = ';'.join(['videobot', 'archiveteam', 'vine', item_id, item_name])
            newurls = [{'url': url} for url in extract_urls(content, url_info["url"]) if not re.match(r'^https?://(?:www\.)?vine\.co/v/', url)]
            firsturl = False
    return newurls

def exit_status(exit_code):
    global ia_metadata
    if not os.path.isdir('ia_item'):
        os.makedirs('ia_item')
    item_identifier = ia_metadata['identifier']
    for a, b in ia_metadata.items():
        with open('../ia_item/ia_metadata.py', 'a') as file:
            if type(b) is list:
                content_string = str(b)
            else:
                content_string = '\'' + str(b) + '\''
            file.write(str(a) + ' = ' + content_string + '\n')
    os.rename('../ia_item', '../../to_be_uploaded/ia_items/ia_item_' + item_identifier + '_' + str(int(time.time())))
    return exit_code

wpull_hook.callbacks.get_urls = get_urls
wpull_hook.callbacks.exit_status = exit_status

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
    return extractedurls
