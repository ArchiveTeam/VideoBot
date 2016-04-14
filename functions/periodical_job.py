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
import subprocess
import time
import sys

irc_bot_print = lambda irc_channel, irc_bot_message: irc_bot.irc_bot_print(irc_channel, irc_bot_message)
check_temp_perjob_variable = lambda ticket_id, var: periodical_jobs.check_temp_perjob.check_temp_perjob_variable(ticket_id, var)
get_temp_perjob_variables = lambda ticket_id: periodical_jobs.check_temp_perjob.get_temp_perjob_variables(ticket_id)
check_valid_url = lambda url: check_valid.check_valid_url(url)
find_url_service = lambda url_: url.find_url_service(url_)
find_url_title = lambda url_service, url_: url.find_url_title(url_service, url_)
find_url_service_name = lambda url_service: url.find_url_service_name(url_service)
find_url_id = lambda url_service, url_: url.find_url_id(url_service, url_)
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
                if check_temp_perjob_variable(ticket_id, 'url') != 'var not found':
                    irc_bot_print(irc_channel, user + ': You already provided an URL for ticket ID \'' + ticket_id + '\'.')
                    irc_bot_print(irc_channel, user + ': Create a new ticket ID to use a new URL.')
                elif check_valid_url(url) == False:
                    irc_bot_print(irc_channel, user + ': URL \'' + url + '\' doesn\'t seem to be valid.')
                else:
                    url_service = find_url_service(url)
                    if url_service != None:
                        service_name = find_url_service_name(url_service)
                        url_id = find_url_id(url_service, url)
                        url_title = find_url_title(url_service, url)
                        if url_id != None:
                            url_id_string =  'with ID \'' + url_id + '\''
                        else:
                            url_id_string = 'with URL \'' + url + '\''
                        if url_title != None:
                            url_title_string =  '\'' + url_title + '\' '
                        else:
                            url_title_string = ''
                        irc_bot_print(irc_channel, user + ': Found ' + service_name + ' ' + url_title_string + url_id_string + '.')
                        threading.Thread(target = process_messages, args = ('add_url', url, ticket_id, user, ticket_id, url_service)).start()
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
                if check_temp_perjob_variable(ticket_id, 'url') != 'var not found':
                    irc_bot_print(irc_channel, user + ': You already provided an URL for ticket ID \'' + ticket_id + '\'.')
                elif check_valid_url(url) == False:
                    irc_bot_print(irc_channel, user + ': URL \'' + url + '\' doesn\'t seem to be valid.')
                else:
                    url_service = 'video__webpage'
                    service_name = find_url_service_name(url_service)
                    irc_bot_print(irc_channel, user + ': Found ' + service_name + ' \'' + url + '\'.')
                    threading.Thread(target = process_messages, args = ('add_url', url, ticket_id, user, ticket_id, url_service)).start()
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
            if os.path.isfile('periodical_jobs/' + ticket_id + '.pyc'):
                os.remove('periodical_jobs/' + ticket_id + '.pyc')
            elif os.path.isfile('temp_perjobs/' + ticket_id + '.pyc'):
                os.remove('temp_perjobs/' + ticket_id + '.pyc')
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
            if variable_content == 'var not found':
                irc_bot_print(irc_channel, user + ': Periodical job with ticket ID ' + ticked_id + '')
        else:
            irc_bot_print(irc_channel, user + ': I don\'t understand your command. Please review it.')
    else:
        ticket_id = message[2]
        if not os.path.isfile('temp_perjobs/'+ticket_id+'.py'):
            irc_bot_print(irc_channel, user + ': Ticket ID \'' + ticket_id + '\' does not exist.')
        else:
            perjob_commands = check_temp_perjob_variable(ticket_id, 'type')
            if perjob_commands == 'var not found':
                irc_bot_print(irc_channel, user + ': Please provide an URL first for ticket ID \'' + ticket_id + '\'.')
            else:
                service = find_command_service(perjob_commands[0])
                if service != None:
                    threading.Thread(target = process_messages, args = ('periodical_job', service, message, user, ticket_id, service)).start()
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
            required_commands = service_message[1]
            default_commands = service_message[2]
            user = service_message[3]
            for required_command in required_commands + default_commands:
                if check_temp_perjob_variable(b[2], required_command) == 'var not found':
                    irc_bot_print(irc_channel, user + ': You are missing \'' + required_command + '\'.')
                    break
            else:
                os.rename('temp_perjobs/' + ticket_id + '.py', 'periodical_jobs/' + ticket_id + '.py')
                irc_bot_print(irc_channel, user + ': Periodical job with ticket ID \'' + b[2] + '\' is finished.')
        elif service_message[0] == 'execute':
            os.system(service_message[1])
        elif service_message[0] == 'bad_command':
            bad_command = service_message[1]
            user = service_message[2]
            irc_bot_print(irc_channel, user + ': I don\'t understand command \'' + bad_command + '\'.')
        elif service_message[0] == 'write_metadata':
            ia_metadata = service_message[1]
            fulldir = service_message[2]
            if not os.path.isdir(fulldir):
                os.makedirs(fulldir)
            for a, b in ia_metadata.items():
                with open(fulldir + 'ia_metadata.py', 'a') as file:
                    if type(b) is list:
                        content_string = str(b)
                    else:
                        content_string = '\'' + str(b).replace('\'', '\\\'') + '\''
                    file.write(str(a) + ' = ' + content_string + '\n')
        elif service_message[0] == 'help':
            required_commands = service_message[1]
            optional_commands = service_message[2]
            user = service_message[3]
            irc_bot_print(irc_channel, user + ': The required commands are ' + ', '.join(required_commands) + '.')
            irc_bot_print(irc_channel, user + ': The optional commands are ' + ', '.join(optional_commands) + '.')
            irc_bot_print(irc_channel, user + ': Set a command using \'!perjob <command> <ticket ID> <command option>\'.')
        elif service_message[0] == 'execute_timeout':
            # Do not use for grab-site processes
            command = service_message[1].split(' ')
            timeout = int(service_message[2])
            dir_ = service_message[3]
            with open(dir_ + 'no_upload', 'w') as file:
                pass
            process = subprocess.Popen(command)
            time.sleep(timeout)
            os.remove(dir_ + 'no_upload')
            if process.poll() is None:
                process.terminate()
                exit_code = -1
            else:
                exit_code = process.poll()

def process_url(url, user):
    services_list = refresh.services_list
    for service in services_list:
        print(service)
        if re.search(service[1], url):
            for irc_bot_message in eval('services.' + service[0] + '.process(service[0].replace("video__", ""), url, user)'):
                irc_bot_print(irc_channel, irc_bot_message)

def periodical_job_start(filename, type_, user):
    service = find_command_service(type_[0])
    if service != None:
        threading.Thread(target = process_messages, args = ('periodical_job_start', filename, user, None, None, service)).start()

def periodical_job_auto_remove():
    while True:
        for temp_periodical_job in [name for name in os.listdir('./temp_perjobs/') if name.endswith('.py') and not name == '__init__.py']:
            creation_date = os.path.getctime('./temp_perjobs/' + temp_periodical_job)
            ticket_id = temp_periodical_job[:-3]
            user = check_temp_perjob_variable(ticket_id, 'user')
            if int(creation_date) + periodical_job_open_time < int(time.time()):
                os.remove('./temp_perjobs/' + temp_periodical_job)
                if os.path.isfile('./temp_perjobs/' + temp_periodical_job + 'c'):
                    os.remove('./temp_perjobs/' + temp_periodical_job + 'c')
                irc_bot_print(irc_channel, user + ': Unfinished periodical job with ticket ID ' + ticket_id + ' is expired.')
        time.sleep(3600)
