from config import irc_channel
import irc_bot
import refresh
import threading
import re
import url
import services

def irc_bot_print(irc_channel, irc_bot_message):
    irc_bot.irc_bot_print(irc_channel, irc_bot_message)

def find_url_service(url):
    return url.find_url_service(url)

def main(command, user):
    if len(command) == 1:
        irc_bot_print(irc_channel, user + ': Please specify an URL.')
    elif command[1].startswith('http://') or command[1].startswith('https://'):
        print(command)
        threading.Thread(target = process_url, args = (command, user)).start()
    else:
        irc_bot_print(irc_channel, user + ': I can only handle http:// and https://')

def process_url(command, user):
    url_service = find_url_service(command[1])
    for irc_bot_message in eval('services.' + url_service + '.process(url_service, command, user)'):
        irc_bot_print(irc_channel, irc_bot_message)
