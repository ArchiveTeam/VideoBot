from config import irc_channel
from config import github
import os
import services
import time
import re
import irc_bot
import periodical_jobs
import random
import string
import threading
import functions

periodical_job_start = lambda filename, type_, user: functions.periodical_job.periodical_job_start(filename, type_, user)

services_count = 0
services_list = [['service_name', 'service_regex', ['service_commands']]]
periodical_jobs_list = [['perjob_name', 'refreshtime']]
periodical_jobs_start = {}

def irc_bot_print(channel, message):
    irc_bot.irc_bot_print(channel, message)

def refresh_services():
    global services_list
    global services_count
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
                if service[:-3] in services_list:
                    break
                else:
                    try:
                        url_regex = eval('services.' + service[:-3] + '.url_regex')
                    except AttributeError:
                        url_regex = None
                    service_commands = eval('services.' + service[:-3] + '.service_commands')
                    services_list.append([service[:-3], url_regex, service_commands])
                    new_services += 1
                    print('Found service ' + service[:-3] + '.')
    new_count = new_services-services_count
    services_count = new_services
    if new_count == 1:
        irc_bot_print(irc_channel, 'Found and updated ' + str(new_count) + ' service.')
    elif new_count != 0:
        irc_bot_print(irc_channel, 'Found and updated ' + str(new_count) + ' services.')

def refresh_periodical_jobs():
    global periodical_jobs_list
    while True:
        periodical_jobs_list_ = [['perjob_name', 'refreshtime']]
        random_string = ''.join(random.choice(string.ascii_lowercase) for num in range(10))
        for filename in os.listdir('periodical_jobs'):
            if filename.endswith('.py') and filename not in ('check_temp_perjob.py', '__init__.py'):
                filename_ = filename.replace('.py', random_string + '.py')
                os.rename('periodical_jobs/' + filename, 'periodical_jobs/' + filename_)
        reload(periodical_jobs)
        time.sleep(10)
        for filename in os.listdir('periodical_jobs'):
            if filename.endswith(random_string + '.py'):
                filename_ = filename.replace(random_string + '.py', '.py')
                os.rename('periodical_jobs/' + filename, 'periodical_jobs/' + filename_)
                for periodical_job_list_ in periodical_jobs_list_:
                   if filename[:-3] in periodical_job_list_:
                        break
                else:
                    periodical_jobs_list_.append([filename[:-3], eval('periodical_jobs.' + filename[:-3] + '.refreshtime')])
                    print('Found periodical job ' + filename[:-13] + '.')
                os.remove('periodical_jobs/' + filename + 'c')
        periodical_jobs_list = list(periodical_jobs_list_)
        time.sleep(300)

def refresh_periodical_jobs_start():
    global periodical_jobs_list
    global periodical_jobs_start
    while True:
        for periodical_job_list in periodical_jobs_list:
            if periodical_job_list[0] != 'perjob_name':
                periodical_job_name = periodical_job_list[0][:-10]
                if periodical_job_name in periodical_jobs_start:
                    last_start = periodical_jobs_start[periodical_job_name]
                else:
                    last_start = 0
                current_time = int(time.time())
                if last_start + periodical_job_list[1] <= current_time:
                    periodical_jobs_start[periodical_job_name] = current_time
                    threading.Thread(target = periodical_job_start, args = (periodical_job_list[0], eval('periodical_jobs.' + periodical_job_list[0] + '.type'), eval('periodical_jobs.' + periodical_job_list[0] + '.user'),)).start()
        time.sleep(1)

def periodical_job_args(filename, args):
    args_ = []
    for arg in args:
        try:
            variable_content = eval('periodical_jobs.' + filename + '.' + arg)
        except AttributeError:
            variable_content = ''
        args_.append(variable_content)
    return args_
