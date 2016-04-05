from config import irc_channel
from config import periodical_job_open_time
import periodical_jobs
import check_valid
import check_command
import irc_bot
import refresh
import threading
import re
import os
import random
import string
import url
import services

irc_bot_print = lambda irc_channel, irc_bot_message: irc_bot.irc_bot_print(irc_channel, irc_bot_message)
check_temp_perjob_variable = lambda ticket_id, var: periodical_jobs.check_temp_perjob.check_temp_perjob_variable(ticket_id, var)
get_temp_perjob_variables = lambda ticket_id: periodical_jobs.check_temp_perjob.get_temp_perjob_variables(ticket_id)
check_valid_url = lambda url: check_valid.check_valid_url(url)
find_url_service = lambda url: url.find_url_service(url)
find_url_title = lambda url_service, url: url.find_url_title(url_service, url)
find_url_service_name = lambda url_service: url.find_url_service_name(url_service)
find_url_id = lambda url_service, url: url.find_url_id(url_service, url)
find_command_service = lambda command: check_command.find_command_service(command)

command_url = ''

def main(message, user):
    '''Create a periodical job.

    Usage:
    !perjob
        to create a new periodical job.
    !perjob <command> <ticket ID> <command dependent>
        to specify a command for the job.
    
    With commands and command dependent variables:
    --service-url and <URL>
        to periodically scrape a service.
    --scrape-url and <URL>
        to periodically scrape links from a webpage.
    '''
    if len(message) == 1:
        ticket_id = ''.join(random.choice(string.ascii_lowercase) for num in range(10))
        with open('temp_perjobs/'+ticket_id+'.py', 'a') as file:
            file.write('user = \'' + user + '\'\n')
        open_time_hours = int(periodical_job_open_time/3600)
        irc_bot_print(irc_channel, user + ': Your ticket ID is \'' + ticket_id + '\'. The ticket is open for ' + str(open_time_hours) + ' hours without edits.')
        irc_bot_print(irc_channel, user + ': Configure your new periodical job using \'!perjob <command> <ticket ID> <command dependent>\'.')
        irc_bot_print(irc_channel, user + ': See ' + command_url + ' for available commands.')
    elif message[1] == '--service-url':
        if len(message) != 4:
            irc_bot_print(irc_channel, user + ': I don\'t understand your command. Please review it.')
        else:
            ticket_id = message[2]
            if not os.path.isfile('temp_perjobs/'+ticket_id+'.py'):
                irc_bot_print(irc_channel, user + ': Ticket ID \'' + ticket_id + '\' does not exist.')
            else:
                url = message[3]
                if check_temp_perjob_variable(ticket_id, 'url'):
                    irc_bot_print(irc_channel, user + ': You already provided an URL for ticket ID \'' + ticket_id + '\'.')
                elif check_valid_url(url) == False:
                    irc_bot_print(irc_channel, user + ': URL \'' + url + '\' doesn\'t seem to be valid.')
                else:
                    url_service = find_url_service(url)
                    if url_service != None:
                        service_name = find_url_service_name(url_service)
                        url_id = find_url_id(url_service, url)
                        url_title = find_url_title(url_service, url)
                        irc_bot_print(irc_channel, user + ': Found ' + service_name + ' \'' + url_title + '\' with ID \'' + url_id + '\'.')
                        process_messages('add_url', url, ticket_id, user, ticket_id, url_service)
                    else:
                        irc_bot_print(irc_channel, user + ': URL \'' + message[3] + '\' is currently not supported.')
    elif message[1] == '--scrape-url':
        if len(message) != 4:
            irc_bot_print(irc_channel, user + ': I don\'t understand your command. Please review it.')
        else:
            ticket_id = message[2]
            if not os.path.isfile('temp_perjobs/'+ticket_id+'.py'):
                irc_bot_print(irc_channel, user + ': Ticket ID \'' + ticket_id + '\' does not exist.')
            else:
                url = message[3]
                if check_temp_perjob_variable(ticket_id, 'url'):
                    irc_bot_print(irc_channel, user + ': You already provided an URL for ticket ID \'' + ticket_id + '\'.')
                elif check_valid_url(url) == False:
                    irc_bot_print(irc_channel, user + ': URL \'' + url + '\' doesn\'t seem to be valid.')
                else:
                    url_service = 'video__webpage'
                    service_name = find_url_service_name(url_service)
                    irc_bot_print(irc_channel, user + ': Found ' + service_name + ' \'' + url + '\'.')
                    process_messages('add_url', url, ticket_id, user, ticket_id, url_service)
    elif message[1] == '--edit':
        if len(message) != 3:
            irc_bot_print(irc_channel, user + ': I don\'t understand your command. Please review it.')
        else:
            ticket_id = message[2]
            if not os.path.isfile('periodical_jobs/' + ticket_id + '.py'):
                irc_bot_print(irc_channel, user + ': Ticket ID \'' + ticket_id + '\' does not exist.')
            else:
                os.rename('periodical_jobs/' + ticket_id + '.py', 'temp_perjobs/' + ticket_id + '.py')
                irc_bot_print(irc_channel, user + ': Ticket ID \'' + ticket_id + '\' is reopened for editing.')
    elif message[1] == '--remove':
        if len(message) != 3:
            irc_bot_print(irc_channel, user + ': I don\'t understand your command. Please review it.')
        else:
            ticket_id = message[2]
            if os.path.isfile('periodical_jobs/' + ticket_id + '.py'):
                os.remove('periodical_jobs/' + ticket_id + '.py')
                irc_bot_print(irc_channel, user + ': Periodical job with ticket ID ' + ticket_id + ' is removed.')
            elif os.path.isfile('temp_perjobs/' + ticket_id + '.py'):
                os.remove('temp_perjobs/' + ticket_id + '.py')
                irc_bot_print(irc_channel, user + ': Periodical job with ticket ID ' + ticket_id + ' is removed.')
            else:
                irc_bot_print(irc_channel, user + ': Ticket ID \'' + ticket_id + '\' does not exist.')
    elif message[1] in ('--info', '--information'):
        if len(message) == 3:
            ticket_id = message[2]
            variables = get_temp_perjob_variables(ticket_id)
            if variables == None:
                irc_bot_print(irc_channel, user + ': Periodical job with ticket ID ' + ticket_id + ' does not exist.')
            else:
                irc_bot_print(irc_channel, user + ': Periodical job with ticket ID ' + ticket_id + ' has variables ' + ', '.join(variables) + '.')
        elif len(message) == 4:
            ticket_id = message[2]
            variable = message[3]
            variable_content = check_temp_perjob_variable(ticket_id, variable)
            if variable_content == False:
                irc_bot_print(irc_channel, user + ': Periodical job with ticked ID ' + ticked_id + '')
        else:
            irc_bot_print(irc_channel, user + ': I don\'t understand your command. Please review it.')
    else:
        ticket_id = message[2]
        if not os.path.isfile('temp_perjobs/'+ticket_id+'.py'):
            irc_bot_print(irc_channel, user + ': Ticket ID \'' + ticket_id + '\' does not exist.')
        else:
            perjob_commands = check_temp_perjob_variable(ticket_id, 'type')
            if perjob_commands == False:
                irc_bot_print(irc_channel, user + ': Please provide an URL first for ticket ID \'' + ticket_id + '\'.')
            else:
                if perjob_commands[0] == 'webpage':
                    service = 'video__webpage'
                else:
                    service = find_command_service(perjob_commands[0])
                if service != None:
                    process_messages('periodical_job', service, message, user, ticket_id, service)
                else:
                    irc_bot_print(irc_channel, user + ': Command \'' + message[0] + '\' was removed. Please create a new periodical job.')

def process_messages(name, a, b, c, ticket_id, service):
    for service_message in eval('services.' + service + '.' + name + '(a, b, c)'):
        if service_message[0] == 'add':
            filelines = []
            with open('temp_perjobs/'+ticket_id+'.py', 'r') as file:
                added = False
                for line in file:
                    if not line.startswith(service_message[1]):
                        filelines.append(line)
                    else:
                        filelines.append(service_message[1] + ' = ' + str(service_message[2]))
                        added = True
                if not added:
                    filelines.append(service_message[1] + ' = ' + str(service_message[2]))
            with open('temp_perjobs/'+ticket_id+'.py', 'w') as file:
                file.write('\n'.join([fileline for fileline in filelines if not fileline == '']))
        elif service_message[0] == 'message':
            irc_bot_print(irc_channel, str(service_message[1]))
        elif service_message[0] == 'finish':
            os.rename('temp_perjobs/' + ticket_id + '.py', 'periodical_jobs/' + ticket_id + '.py')
        elif service_message[0] == 'execute':
            os.system(service_message[1])

def process_url(url, user):
    services_list = refresh.services_list
    for service in services_list:
        print(service)
        if re.search(service[1], url):
            for irc_bot_message in eval('services.' + service[0] + '.process(service[0].replace("video__", ""), url, user)'):
                irc_bot_print(irc_channel, irc_bot_message)

def periodical_job_start(filename, type_, user):
    if type_[0] == 'webpage':
        service = 'video__webpage'
    else:
        service = find_command_service(type_[0])
    if service != None:
        process_messages('periodical_job_start', filename, user, None, None, service)

def periodical_job_auto_remove():
    while True:
        for temp_periodical_job in os.listdir('./temp_perjobs/'):
            creation_date = os.path.getctime('./temp_perjobs/' + temp_periodical_job)
            ticket_id = temp_periodical_job[:-3]
            user = check_temp_perjob_variable(ticket_id, 'user')
            if int(creation_date) + periodical_job_open_time < int(time.time()):
                os.remove('./temp_perjobs/' + temp_periodical_job)
                irc_bot_print(irc_channel, user + ': Unfinished periodical job with ticket ID ' + ticket_id + ' is expired.')
