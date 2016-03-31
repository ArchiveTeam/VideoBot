import re
import os
import sys
import download_page
import url
import irc_message
import check_valid
import periodical_jobs
import refresh

extract_info = lambda regexes, url: download_page.extract_info(regexes, url)
job_finished = lambda user, name, title, id: irc_message.job_finished(user, name, title, id)
job_failed = lambda user, name, title, id: irc_message.job_failed(user, name, title, id)
job_added = lambda user, name, title, id: irc_message.job_added(user, name, title, id)
job_aborted = lambda user, name, id: irc_message.job_added(user, name, id)
failed_extraction = lambda user, name, id: irc_message.failed_extraction(user, name, id)
check_create_url = lambda url_, prefix, suffix: url.check_create_url(url_, prefix, suffix)
check_num = lambda string: check_valid.check_num(string)
check_temp_perjob_variable = lambda ticket, command: periodical_jobs.check_temp_perjob.check_temp_perjob_variable(ticket, command)
periodical_job_args = lambda filename, args: refresh.periodical_job_args(filename, args)

service_name = 'website or webpage'
commands = ['webpage']

def add_url(url, ticket_id, user):
    yield(['add', 'url', '\'' + url + '\''])
    yield(['add', 'type', commands])
    yield(['message', user + ': Added URL \'' + url + '\' to ticket ID \'' + ticket_id + '\'.'])
    yield(['message', user + ': Set the commands. For help use \'!perjob help <Ticket ID>\'. To finish ticket ID use command \'finish\'.'])

def periodical_job(service_name, command, user):
    default_commands = ['url', 'type']
    required_commands = ['refreshtime', 'depth', 'description']
    optional_commands = []
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
    elif command[1] == 'description':
        description = ' '.join(command[3:])
        yield(['add', 'description', '\'' + description + '\''])
        yield(['message', user + ': Added description \'' + description + '\' to ticket ID \'' + command[2] + '\'.'])
    elif command[1] == 'help':
        yield(['message', user + ': The required commands are ' + ', '.join(required_commands) + '.'])
        yield(['message', user + ': The optional commands are ' + ', '.join(optional_commands) + '.'])
        yield(['message', user + ': Set a command using \'!perjob <command> <ticket ID> <command option>\'.'])
    elif command[1] == 'finish':
        for required_command in required_commands + default_commands:
            if check_temp_perjob_variable(command[2], required_command) == None:
                yield(['message', user + ': You are missing \'' + required_command + '\'.'])
                break
        else:
            yield(['add', 'finished', True])
            yield(['finish'])
            yield(['message', user + ': Periodical job with ticket ID \'' + command[2] + '\' is finished.'])
    else:
        pass

def periodical_job_start(filename, user, _):
    depth, url = periodical_job_args(filename, ['depth', 'url'])
    yield(['message', user + ': Periodical job for ' + service_name + ' ' + url + ' with ticket ID ' + filename[:-10] + ' has started.'])
    yield(['execute', '~/.local/bin/grab-site ' + url + ' --level=' + str(depth) + ' --ua="ArchiveTeam; Googlebot/2.1" --concurrency=5 --warc-max-size=524288000 --wpull-args="--no-check-certificate --timeout=300" > /dev/null 2>&1'])
