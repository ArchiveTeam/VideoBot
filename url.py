from config import irc_channel
import refresh
import re
import irc_bot
import services

def irc_bot_print(channel, message):
    irc_bot.irc_bot_print(channel, message)

def find_url_service(url):
    services_list = refresh.services_list
    for service in services_list:
        if re.search(service[1], url):
            return service[0]
    else:
        return None

def find_url_title(url_service, url):
    return eval('services.' + url_service + '.item_title(url)')

def find_url_service_name(url_service):
    print('services.' + url_service + '.service_name')
    return eval('services.' + url_service + '.service_name')

def find_url_id(url_service, url):
    return eval('services.' + url_service + '.url_id(url)')

def check_create_url(url, prefix, suffix):
    if url.startswith('https://') or url.startswith('http://'):
        return url
    else:
        return prefix + url + suffix
