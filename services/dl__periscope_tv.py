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
video_id = ''
added_to_list = []
tempfiles = []

def accept_url(url_info, record_info, verdict, reasons):
    global added_to_list
    global firsturl
    if firsturl == '' or url_info["url"] in added_to_list:
        return True
    return False

def get_urls(filename, url_info, document_info):
    global counter
    global firsturl
    global ia_metadata
    global video_id
    global added_to_list
    global tempfiles
    newurls = []
    if firsturl == '':
        firsturl = url_info["url"]
    if re.search(r'^https?://replay\.periscope\.tv/.+/playlist\.m3u8$', url_info["url"]):
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.replace('\r', '').replace('\n', '')
                if line.endswith('.ts'):
                    newurls.append({'url': re.search(r'^(https?://replay\.periscope\.tv/.+/)playlist\.m3u8$', url_info["url"]).group(1) + line})
                    tempfiles.append(line)
    elif re.search(r'^https?://replay\.periscope\.tv/.+/chunk_[0-9]+\.ts$', url_info["url"]):
        filename_new = re.search(r'^https?://replay\.periscope\.tv/.+/(chunk_[0-9]+\.ts)$', url_info["url"]).group(1)
        if not os.path.isdir('../ia_item'):
            os.makedirs('../ia_item')
        if not os.path.isfile('../ia_item/' + filename_new):
            shutil.copyfile(filename, '../ia_item/' + filename_new)
    elif re.search(r'^https?://(?:www\.)?periscope\.tv/w/[0-9a-zA-Z]+$', url_info["url"]):
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
            content_json = html.unescape(re.search(r'data-store="({[^"]+})"', content).group(1))
            json_ = json.loads(content_json)
            api_session = json_['SessionToken']['thumbnailPlaylist']['token']['session_id']
            item_description = json_['UserBroadcast']['broadcast']['status']
            item_id = json_['UserBroadcast']['broadcast']['id']
            item_location_city = json_['UserBroadcast']['broadcast']['city']
            item_location_country = json_['UserBroadcast']['broadcast']['country']
            item_location_country_state = json_['UserBroadcast']['broadcast']['country_state']
            item_location = (item_location_city + (', ' if item_location_country != '' else '') if item_location_city != '' else '') + item_location_country if item_location_city + item_location_country != '' else ''
            item_language = json_['UserBroadcast']['broadcast']['language']
            item_name_id = json_['User']['user']['id']
            item_name_description = json_['User']['user']['description']
            item_name = json_['User']['user']['display_name']
            item_username = json_['User']['user']['username']
            item_twitter = json_['User']['user']['twitter_screen_name']
            item_date = json_['UserBroadcast']['broadcast']['created_at'].split('.')[0].replace('T', ' ')
            ia_metadata['identifier'] = 'archiveteam_videobot_periscope_tv_' + item_id
            ia_metadata['description'] = item_description + '\n\n' + item_name_description
            ia_metadata['date'] = item_date
            ia_metadata['original_url'] = url_info["url"]
            ia_metadata['twitter'] = item_twitter
            ia_metadata['creator'] = item_name
            ia_metadata['creator_username'] = item_username
            ia_metadata['creator_id'] = item_name_id
            ia_metadata['title'] = item_description + (' — ' + item_location if item_location != '' else '')
            ia_metadata['language'] = item_language
            ia_metadata['creator_description'] = item_name_description
            ia_metadata['city'] = item_location_city
            ia_metadata['country'] = item_location_country
            ia_metadata['country_state'] = item_location_country_state
            ia_metadata['location'] = item_location
            ia_metadata['subject'] = ';'.join(['videobot', 'archiveteam', 'periscope', 'periscope.tv', item_id, item_name])
            newurls.append({'url': 'https://api.periscope.tv/api/v2/accessVideoPublic?broadcast_id=' + item_id})
            newurls.append({'url': 'https://api.periscope.tv/api/v2/publicReplayThumbnailPlaylist?broadcast_id=' + item_id + '&session_id=' + api_session})
            newurls.append({'url': 'https://api.periscope.tv/api/v2/getBroadcastPublic?broadcast_id=' + item_id})
            newurls += [{'url': url} for url in extract_urls(content, url_info["url"]) if ((re.search(r'^https?://(?:www\.)?periscope\.tv/w/[0-9a-zA-Z]+', url) and item_id in url) or not re.search(r'^https?://(?:www\.)?periscope\.tv/w/[0-9a-zA-Z]+', url)) and not url in added_to_list]
            newurls += [{'url': url} for url in extract_urls(content_json, url_info["url"]) if not url in added_to_list]
    elif re.search(r'^https://api\.periscope\.tv/api/v2/publicReplayThumbnailPlaylist', url_info["url"]) or re.search(r'^https://api\.periscope\.tv/api/v2/accessVideoPublic', url_info["url"]) or re.search(r'^https?://(?:www\.)?periscope\.tv/w/[0-9a-zA-Z]+', url_info["url"]):
        with open(filename, 'r', encoding='utf-8') as file:
            content = html.unescape(file.read())
            newurls += [{'url': url} for url in extract_urls(content, url_info["url"]) if not url in added_to_list]
    for newurl in newurls:
        added_to_list.append(newurl["url"])
    return newurls

def exit_status(exit_code):
    global ia_metadata
    global tempfiles
    tempfiles_ = list(tempfiles)
    if os.path.isdir('../ia_item'):
        lists = []
        listsnames = []
        while len(tempfiles) > 0:
            if len(tempfiles) < 500:
                lists.append(list(tempfiles))
                tempfiles = []
            else:
                lists.append(list(tempfiles[:500]))
                tempfiles = list(tempfiles[500:])
        for i in range(len(lists)):
            os.system('ffmpeg -i "concat:' + '|'.join(['../ia_item/' + file for file in lists[i]]) + '" -c copy ../ia_item/video' + str(i) + '.ts')
            listsnames.append('video' + str(i) + '.ts')
        os.system('ffmpeg -i "concat:' + '|'.join(['../ia_item/' + file for file in listsnames]) + '" -c copy ../ia_item/video.ts')
        print(lists)
        print(listsnames)
        if os.path.isfile('../ia_item/video.ts'):
            ia_metadata['files'].append('video.ts')
        for filename in ['../ia_item/' + file for file in tempfiles_] + ['../ia_item/' + file for file in listsnames]:
            os.remove(filename)
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
    return [extractedurl.replace('&amp;', '&').replace(r'\u0026', '&') for extractedurl in extractedurls]