from config import irc_channel
import os
import services
import time
import re
import irc_bot

services_count = 0
services_list = [['service_name', 'service_regex', ['service_commands']]]

def irc_bot_print(channel, message):
    irc_bot.irc_bot_print(channel, message)

def refresh_services():
    global services_list
    global services_count
    while True:
        services_list = [['service_name', 'service_regex', ['service_commands']]]
        new_services = 0
        #if os.path.isdir('./services'):
        #    shutil.rmtree('./services')
        #os.system('git clone ' + github + '.git')
        #repository_name = re.search(r'([^\/]+)\/?$', github).group(1)
        #shutil.copytree('./' + repository_name + '/services', './services')
        #shutil.rmtree('./' + repository_name)
        reload(services)
        for root, dirs, files in os.walk("./services"):
            for service in files:
                if service.startswith("video__") and service.endswith(".py"):
                    for existing_service in services_list:
                        if service[:-3] == existing_service[0]:
                            break
                    else:
                        services_list.append([service[:-3], eval('services.' + service[:-3] + '.regex'), eval('services.' + service[:-3] + '.commands')])
                        new_services += 1
                        print('Found service ' + service[:-3] + '.')
        new_count = new_services-services_count
        services_count = new_services
        if new_count == 1:
            irc_bot_print(irc_channel, 'Found and updated ' + str(new_count) + ' service.')
        elif new_count != 0:
            irc_bot_print(irc_channel, 'Found and updated ' + str(new_count) + ' services.')
        time.sleep(300)
