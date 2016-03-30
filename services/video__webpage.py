import re
import os
import sys
import download_page
import url
import irc_message
import check_valid
import periodical_jobs

extract_info = lambda regexes, url: download_page.extract_info(regexes, url)
job_finished = lambda user, name, title, id: irc_message.job_finished(user, name, title, id)
job_failed = lambda user, name, title, id: irc_message.job_failed(user, name, title, id)
job_added = lambda user, name, title, id: irc_message.job_added(user, name, title, id)
job_aborted = lambda user, name, id: irc_message.job_added(user, name, id)
failed_extraction = lambda user, name, id: irc_message.failed_extraction(user, name, id)
check_create_url = lambda url_, prefix, suffix: url.check_create_url(url_, prefix, suffix)
check_num = lambda string: check_valid.check_num(string)
check_temp_perjob_variable = lambda ticket, command: periodical_jobs.check_temp_perjob.check_temp_perjob_variable(ticket, command)

service_name = 'website or webpage'
commands = ['webpage']

def add_url(url, ticket_id, user):
    yield(['add', 'url', '\'' + url + '\''])
    yield(['add', 'type', commands])
    yield(['message', user + ': Added URL \'' + url + '\' to ticket ID \'' + ticket_id + '\'.'])
    yield(['message', user + ': Set refresh time using \'!perjob refreshtime <ticket ID> <refreshtime>\''])
    yield(['message', user + ': Use \'auto\' as <refreshtime> to let videobot decide on the refreshtime.'])

def periodical_job(service_name, command, user):
    if command[1] == 'refreshtime':
        if check_num(command[3]):
            yield(['add', 'refreshtime', command[3]])
            yield(['message', user + ': Added refreshtime ' + command[3] + ' to ticket ID \'' + command[2] + '\'.'])
        else:
            yield(['message', user + ': Refreshtime should be a number for a ' + service_name + '.'])
    elif command[1] == 'depth':
        if check_num(command[3]):
            yield(['add', 'depth', command[3]])
            yield(['message', user + ': Added crawl depth ' + command[3] + ' to ticket ID \'' + command[2] + '\'.'])
        else:
            yield(['message', user + ': Crawl depth should be a number for a ' + service_name + '.'])
    elif command[1] == 'finish':
        required_commands = ['refreshtime', 'url', 'depth', 'type']
        for required_command in required_commands:
            if check_temp_perjob_variable(command[2], required_command) == None:
                yield(['message', user + ': You are missing \'' + required_command + '\'.'])
                break
        else:
            yield(['add', 'finished', True])
            yield(['finish'])
            yield(['message', user + ': Periodical job with ticket ID \'' + command[2] + '\' is finished.'])
    else:
        pass
