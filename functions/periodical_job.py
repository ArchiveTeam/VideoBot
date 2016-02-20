from config import irc_channel
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
import check_url
import services

def irc_bot_print(irc_channel, irc_bot_message):
    irc_bot.irc_bot_print(irc_channel, irc_bot_message)

def check_temp_perjob_variable(ticket_id, var):
    return periodical_jobs.check_temp_perjob.check_temp_perjob_variable(ticket_id, var)

def check_valid_url(url):
    return check_valid.check_valid_url(url)

def find_url_service(url):
    return check_url.find_url_service(url)

def find_url_title(url_service, url):
    return check_url.find_url_title(url_service, url)

def find_url_service_name(url_service):
    return check_url.find_url_service_name(url_service)

def find_url_id(url_service, url):
    return check_url.find_url_id(url_service, url)

def find_command_service(command):
    return check_command.find_command_service(command)

def main(message, user):
    if len(message) == 1:
        ticket_id = ''.join(random.choice(string.ascii_lowercase) for num in range(10))
        with open('temp_perjobs/'+ticket_id+'.py', 'a') as file:
            file.write('user = \'' + user + '\'\n')
        irc_bot_print(irc_channel, user + ': Your ticket ID is \'' + ticket_id + '\'. The ticket is open for 24 hours.')
        irc_bot_print(irc_channel, user + ': For single URL \'!perjob single-url <ticket ID> <URL>\'.')
    elif message[1] == 'single-url':
        if len(message) != 4:
            irc_bot_print(irc_channel, user + ': For single URL \'!perjob single-url <ticket ID> <URL>\'.')
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
    else:
        ticket_id = message[2]
        if not os.path.isfile('temp_perjobs/'+ticket_id+'.py'):
            irc_bot_print(irc_channel, user + ': Ticket ID \'' + ticket_id + '\' does not exist.')
        else:
            perjob_commands = check_temp_perjob_variable(ticket_id, 'type')
            if perjob_commands == False:
                irc_bot_print(irc_channel, user + ': Please provide an URL first for ticket ID \'' + ticket_id + '\'.')
            else:
                service = find_command_service(perjob_commands[0])
                if service != None:
                    process_messages('periodical_job', service, message, user, ticket_id, service)
                else:
                    irc_bot_print(irc_channel, user + ': Command \'' + command[0] + '\' was removed. Please create a new periodical job.')

def process_messages(name, a, b, c, ticket_id, service):
    for service_message in eval('services.' + service + '.' + name + '(a, b, c)'):
        with open('temp_perjobs/'+ticket_id+'.py', 'a') as file:
            if service_message[0] == 'add':
                file.write(service_message[1] + ' = ' + str(service_message[2]) + '\n')
            elif service_message[0] == 'message':
                irc_bot_print(irc_channel, str(service_message[1]))

def process_url(url, user):
    services_list = refresh.services_list
    for service in services_list:
        print(service)
        if re.search(service[1], url):
            for irc_bot_message in eval('services.' + service[0] + '.process(service[0].replace("video__", ""), url, user)'):
                irc_bot_print(irc_channel, irc_bot_message)
