import re
import os
import sys
import time
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
long_string = lambda command: ' '.join(command[3:]).replace('\'', '\\\'')

service_name = 'stream'
service_commands = ['mms', 'mmsh', 'rtsp', 'rtmp', 'MMS', 'MMSH', 'RTSP', 'RTMP']
url_regex = r'^(?:mms|mmsh|rtsp|rtmp|MMS|MMSH|RTSP|RTMP):\/\/'

def add_url(url, ticket_id, user):
    print('bla' + url)
    yield(['add', 'url', '\'' + url + '\''])
    yield(['add', 'type', service_commands])
    yield(['message', user + ': Added URL \'' + url + '\' to ticket ID \'' + ticket_id + '\'.'])
    yield(['message', user + ': Set the commands. For help use \'!perjob help <Ticket ID>\'. To finish ticket ID use command \'finish\'.'])

def periodical_job(service_name, command, user):
    default_commands = ['url', 'type']
    required_commands = ['piecelength', 'title', 'description']
    optional_commands = ['creator', 'subject', 'licenseurl', 'notes', 'rights', 'publisher', 'language', 'coverage', 'credits']
    if command[1] == 'piecelength':
        if check_num(command[3]):
            yield(['add', 'piecelength', command[3]])
            yield(['add', 'refreshtime', command[3]])
            yield(['message', user + ': Added piecelength ' + command[3] + ' to ticket ID \'' + command[2] + '\'.'])
        else:
            yield(['message', user + ': Piecelength should be a number for a ' + service_name + '.'])
    elif command[1] == 'title':
        title = long_string(command)
        yield(['add', 'title', '\'' + title + '\''])
        yield(['message', user + ': Added title \'' + title + '\' to ticket ID \'' + command[2] + '\'.'])
    elif command[1] == 'description':
        description = long_string(command)
        yield(['add', 'description', '\'' + description + '\''])
        yield(['message', user + ': Added description \'' + description + '\' to ticket ID \'' + command[2] + '\'.'])
    elif command[1] == 'creator':
        creator = long_string(command)
        yield(['add', 'creator', '\'' + creator + '\''])
        yield(['message', user + ': Added creator \'' + creator + '\' to ticket ID \'' + command[2] + '\'.'])
    elif command[1] == 'subject':
        subject = long_string(command)
        yield(['add', 'subject', '\'' + subject + '\''])
        yield(['message', user + ': Added subject \'' + subject + '\' to ticket ID \'' + command[2] + '\'.'])
    elif command[1] == 'licenseurl':
        licenseurl = long_string(command)
        yield(['add', 'licenseurl', '\'' + licenseurl + '\''])
        yield(['message', user + ': Added licenseurl \'' + licenseurl + '\' to ticket ID \'' + command[2] + '\'.'])
    elif command[1] == 'notes':
        notes = long_string(command)
        yield(['add', 'notes', '\'' + notes + '\''])
        yield(['message', user + ': Added notes \'' + notes + '\' to ticket ID \'' + command[2] + '\'.'])
    elif command[1] == 'rights':
        rights = long_string(command)
        yield(['add', 'rights', '\'' + rights + '\''])
        yield(['message', user + ': Added rights \'' + rights + '\' to ticket ID \'' + command[2] + '\'.'])
    elif command[1] == 'publisher':
        publisher = long_string(command)
        yield(['add', 'publisher', '\'' + publisher + '\''])
        yield(['message', user + ': Added publisher \'' + publisher + '\' to ticket ID \'' + command[2] + '\'.'])
    elif command[1] == 'language':
        language = long_string(command)
        yield(['add', 'language', '\'' + language + '\''])
        yield(['message', user + ': Added language \'' + language + '\' to ticket ID \'' + command[2] + '\'.'])
    elif command[1] == 'coverage':
        coverage = long_string(command)
        yield(['add', 'coverage', '\'' + coverage + '\''])
        yield(['message', user + ': Added coverage \'' + coverage + '\' to ticket ID \'' + command[2] + '\'.'])
    elif command[1] == 'credits':
        credits = long_string(command)
        yield(['add', 'credits', '\'' + credits + '\''])
        yield(['message', user + ': Added credits \'' + credits + '\' to ticket ID \'' + command[2] + '\'.'])

    # Do not change this.
    elif command[1] == 'help':
        yield(['help', required_commands, optional_commands, user])
    elif command[1] == 'finish':
        yield(['finish', required_commands, default_commands, user])
    else:
        yield(['bad_command', command[1], user])

def periodical_job_start(filename_, user, _):
    optional_commands = ['creator', 'subject', 'licenseurl', 'notes', 'rights', 'publisher', 'language', 'coverage', 'credits']
    title, url, piecelength, description = periodical_job_args(filename_, ['title', 'url', 'piecelength', 'description'])
    piecelength = int(piecelength) + 120 # an overlap of 120 seconds.
    date = time.strftime('%Y%m%d_%H%M')
    metadata_date = date[:4] + '-' + date[4:6] + '-' + date[6:11].replace('_', ' ') + ':' + date[11:]
    itemdir = 'archiveteam_videobot_' + re.sub(r'[^0-9a-zA-Z]', r'_', title) + '_' + date
    fulldir = 'to_be_uploaded/ia_items/' + itemdir + '/'
    filename = re.sub(r'[^0-9a-zA-Z]', r'_', title) + '_' + date + '.asf'
    ia_metadata = {'identifier': itemdir, 'title': title + ' ' + metadata_date, 'date': metadata_date, 'url': url, 'collection': 'archiveteam_videobot', 'mediatype': 'movies', 'files': [filename], 'description': description, 'subject': 'videobot;archiveteam'}
    for command in optional_commands:
        content = periodical_job_args(filename_, [command])[0]
        if command == 'subject':
            ia_metadata['subject'] += ';' + content
        else:
            ia_metadata[command] = content
    yield(['write_metadata', ia_metadata, fulldir])
    yield(['execute_timeout', 'mplayer -dumpstream ' + url + ' -dumpfile ' + fulldir + filename, piecelength, fulldir])
