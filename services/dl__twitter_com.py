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
video_title = ''
added_to_list = []
vmap = ''
tempfiles = {}
tries = {}

ignored_urls = []

with open(os.path.join('..', '..', 'services', 'dl__ignores__twitter_com'), 'r') as f:
    for line in f:
        ignored_urls.append(line.strip())

def accept_url(url_info, record_info, verdict, reasons):
    global added_to_list
    if (firsturl == '' or url_info["url"] in added_to_list) and not ('?lang=' in url_info["url"] or '\\' in url_info["url"]):
        return True
    return False

def get_urls(filename, url_info, document_info):
    global counter
    global firsturl
    global ia_metadata
    global video_id
    global added_to_list
    global vmap
    global tempfiles
    global video_title

    newurls = []

    def url_allowed(url, parent_url=None):
        if re.search(r'^https?://(?:www\.)?twitter\.com/[^/]+/status/' + video_id, url):
            return True

        elif not re.search(r'^https?://(?:www\.)?twitter\.com/[^/]+/status/[0-9]+', url):
            video_user = re.search(r'^https?://(?:www\.)?twitter\.com/([^/]+)/status/[0-9]+', firsturl).group(1)
            if re.search(r'^https?://(?:www\.)?twitter\.com/[^/]+(?:/status/)?$', url) and not video_user in url:
                return False
            return True

        return False

    def add_url(url, parent_url=None):
        if url in added_to_list or url in ignored_urls:
            return None
        if url_allowed(url, parent_url):
            added_to_list.append(url)
            newurls.append({'url': url})

    if re.search(r'^https?://video\.twimg\.com.+/[0-9a-zA-Z_-]+\.mp4', url_info["url"]):
        if re.search(r'^https?://video\.twimg\.com.+/[0-9]+x[0-9]+/[0-9a-zA-Z_-]+\.mp4', url_info["url"]):
            filename_new = re.search(r'^https?://video\.twimg\.com.+/([0-9]+x[0-9]+)/[0-9a-zA-Z_-]+\.mp4', url_info["url"]).group(1) + '.mp4'
        else:
            filename_new = re.search(r'^https?://video\.twimg\.com.+/([0-9a-zA-Z_-]+\.mp4)', url_info["url"]).group(1)

        if not os.path.isdir('../ia_item'):
            os.makedirs('../ia_item')
        if not os.path.isfile('../ia_item/' + filename_new):
            shutil.copyfile(filename, '../ia_item/' + filename_new)
            ia_metadata['files'].append(filename_new)

    # Rename .mp4 video from akamaihd.
    elif re.search(r'^https?://(?:snappytv[^\.]+\.akamaihd\.net|amp\.twimg\.com).+/[^/]+\.mp4', url_info["url"]):
        filename_new = re.search(r'^https?://(?:snappytv[^\.]+\.akamaihd\.net|amp\.twimg\.com).+/([^/]+\.mp4)', url_info["url"]).group(1)

        if not os.path.isdir('../ia_item'):
            os.makedirs('../ia_item')
        if not os.path.isfile('../ia_item/' + filename_new):
            shutil.copyfile(filename, '../ia_item/' + filename_new)
            ia_metadata['files'].append(filename_new)

    # Queue videos from .m3u8 playlists.
    elif re.search(r'^https?://video\.twimg\.com/(?:ext_tw_video|amplify_video).+/[0-9a-zA-Z_-]+\.m3u8', url_info["url"]):
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                part = re.search(r'^(https://video\.twimg\.com)', url_info["url"]).group(1)

                if (line.startswith('/ext_tw_video') or line.startswith('/amplify_video')) and line.strip().endswith('.m3u8'):
                    print(part + line.strip())
                    newurls.append({'url': part + line.strip()})

                elif (line.startswith('/ext_tw_video') or line.startswith('/amplify_video')) and line.strip().endswith('.ts'):
                    if re.search(r'/[0-9]+x[0-9]+/[0-9a-zA-Z_-]+\.ts', line):
                        newurl = part + line.strip()
                        size = re.search(r'/([0-9]+x[0-9]+)/[0-9a-zA-Z_-]+\.ts', line).group(1)
                        if not size in tempfiles:
                            tempfiles[size] = []
                        tempfiles[size].append(re.search(r'/([0-9a-zA-Z_-]+\.ts)', line).group(1))
                        newurls.append({'url': newurl})

    # Prepare .ts videos from .m3u8 playlist for merging.
    elif re.search(r'^https://video\.twimg\.com/(?:ext_tw_video|amplify_video).+/[0-9]+x[0-9]+/[0-9a-zA-Z_-]+\.ts', url_info["url"]):
        filename_new = re.search(r'/([0-9a-zA-Z_-]+\.ts)', url_info["url"]).group(1)
        if not os.path.isdir('../ia_item'):
            os.makedirs('../ia_item')
        if not os.path.isfile('../ia_item/' + filename_new):
            shutil.copyfile(filename, '../ia_item/' + filename_new)

    # The vmap URL contains videos.
    elif url_info["url"] == vmap:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
            newurls += [{'url': url} for url in extract_urls(content, url_info["url"]) if not url in added_to_list]

    # Prepare the metadata and queue new URLs.
    elif re.search('^https://twitter\.com/i/videos/tweet/[0-9]+\?embed_source=clientlib&player_id=0&rpc_init=1', url_info["url"]):
        with open(filename, 'r', encoding='utf-8') as file:
            months = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
            content = file.read()
            content_json = html.unescape(re.search(r'data-config="([^"]+)"', content).group(1))
            json_ = json.loads(content_json)

            if 'vmap_url' in json_:
                vmap = json_['vmap_url']

            item_description = video_title

            if json_['videoInfo']['title']:
                item_description += '\n\n' + str(json_['videoInfo']['title'])

            if json_['videoInfo']['description']:
                item_description += '\n\n' + str(json_['videoInfo']['description'])

            item_id = json_['status']['id_str']
            item_name = json_['videoInfo']['publisher']['name']
            item_url_t_co = json_['cardUrl']
            item_date_ = json_['status']['created_at'].replace('T', ' ')
            item_date = item_date_[-4:] + '-' + str(months[item_date_[4:7]]).zfill(2) + '-' + item_date_[8:10] + ' ' + item_date_[11:19]
            ia_metadata['identifier'] = 'archiveteam_videobot_twitter_com_' + item_id
            ia_metadata['title'] = video_title
            ia_metadata['description'] = item_description
            ia_metadata['date'] = item_date
            ia_metadata['original_url'] = firsturl
            ia_metadata['url_t_co'] = item_url_t_co
            ia_metadata['user_name'] = json_['user']['name']
            ia_metadata['user_screen_name'] = json_['user']['screen_name']
            ia_metadata['creator'] = item_name
            ia_metadata['tweet_id'] = video_id
            ia_metadata['subject'] = ';'.join(['videobot', 'archiveteam', 'twitter', 'twitter.com', item_id, item_name]
                + re.findall(r'(#[^#\s]+)', ia_metadata['title'])
                + re.findall(r'#([^#\s]+)', ia_metadata['title']))

            if ia_metadata['user_name'] != ia_metadata['creator']:
                ia_metadata['creator'] = [item_name, ia_metadata['user_name']]

            if not os.path.isdir('../ia_item'):
                os.makedirs('../ia_item')
            json.dump(json_, open('../ia_item/data_video.json', 'w'), indent = 4, ensure_ascii = False)
            ia_metadata['files'].append('data_video.json')

            for url in extract_urls(' '.join([content, content_json]), url_info["url"]):
                add_url(url)

    # Queue first-URL new urls.
    if re.search('^https?://(?:www\.)?twitter\.com/[^/]+/status/[0-9]+', url_info["url"]) and video_id == '':
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()

            if not os.path.isdir('../ia_item'):
                os.makedirs('../ia_item')
            json.dump(json.loads(html.unescape(re.search(r'class="json-data"\s+value="([^"]+)"', content).group(1))), open('../ia_item/data.json', 'w'), indent = 4, ensure_ascii = False)
            ia_metadata['files'].append('data.json')

            video_title = html.unescape(re.search(r'<meta\s+property="og:description"\s+content=".([^"]+).">', content).group(1))

        video_id = re.search('^https?://(?:www\.)?twitter\.com/[^/]+/status/([0-9]+)', url_info["url"]).group(1)
        if not 'https://twitter.com/i/videos/tweet/' + video_id + '?embed_source=clientlib&player_id=0&rpc_init=1' in added_to_list:
            newurls.append({'url': 'https://twitter.com/i/videos/tweet/' + video_id + '?embed_source=clientlib&player_id=0&rpc_init=1'})
        if not 'https://twitter.com/i/videos/' + video_id in added_to_list:
            newurls.append({'url': 'https://twitter.com/i/videos/' + video_id})
        if not 'https://twitter.com/i/videos/' + video_id + '?embed_source=facebook' in added_to_list:
            newurls.append({'url': 'https://twitter.com/i/videos/' + video_id + '?embed_source=facebook'})

    if firsturl == '':
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
            firsturl = url_info["url"]
            for url in extract_urls(content, url_info["url"]):
                add_url(url)

    for newurl in newurls:
        added_to_list.append(newurl["url"])

    return [newurl for newurl in newurls if not '?lang=' in newurl['url']]

def exit_status(exit_code):
    global ia_metadata
    global tempfiles
    if os.path.isdir('../ia_item'):
        item_identifier = ia_metadata['identifier']
        print(tempfiles)

        if len(tempfiles) > 0:
            for size, files in tempfiles.items():
                os.system('ffmpeg -i "concat:' + '|'.join(['../ia_item/' + file for file in files]) + '" -c copy ../ia_item/' + size + '.ts')
                ia_metadata['files'].append(size + '.ts')
                for file in ['../ia_item/' + file for file in files]:
                    os.remove(file)

        for a, b in ia_metadata.items():
            with open('../ia_item/ia_metadata.py', 'a') as file:
                if type(b) is list:
                    content_string = str(b)
                else:
                    content_string = '\'' + str(b).replace('\'', '\\\'').replace('\n', '\\n').replace('\r', '\\r') + '\''
                file.write(str(a) + ' = ' + content_string + '\n')

        if len(os.listdir('../ia_item')) > 3:
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