from config import irc_channel, irc_port, irc_server, irc_nick, github, version
import functions
import socket
import re
import check_command
import services
import refresh

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc.connect((irc_server, irc_port))

def archive(command, user):
    functions.archive.main(command, user)

def periodical_job(command, user):
    functions.periodical_job.main(command, user)

def find_command_service(command):
    return check_command.find_command_service(command)

def new_socket():
    global irc
    irc.close()
    irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    irc.connect((irc_server, irc_port))
    irc_bot_join()
    threading.Thread(target = irc_bot_listener.start())

def irc_bot_join():
    irc.send('USER ' + irc_nick + ' ' + irc_nick + ' ' + irc_nick + ' :This is the bot for ' + irc_channel + '. ' + github + '.\n')
    irc.send('NICK ' + irc_nick + '\n')
    irc.send('JOIN ' + irc_channel + '\n')

def irc_bot_print(channel, message):
    try:
        irc.send("PRIVMSG " + channel + " :" + message + "\n")
    except Exception as exception:
        with open('exceptions', 'a') as exceptions:
            exceptions.write(str(version) + '\n' + str(exception) + '\n\n')
        new_socket()
    print("IRC BOT: " + message)

def irc_bot_listener():
    while True:
        irc_message = irc.recv(2048)
        with open('irclog', 'a') as file:
            file.write(irc_message)
        if irc_message.startswith('PING :'):
            message = re.search(r'^[^:]+:(.*)$', irc_message).group(1)
            irc.send('PONG :' + message + '\n')
        elif re.search(r'^:.+PRIVMSG[^:]+:!.*', irc_message):
            command = re.search(r'^:.+PRIVMSG[^:]+:(!.*)', irc_message).group(1).replace('\r', '').replace('\n', '').split(' ')
            user = re.search(r'^:([^!]+)!', irc_message).group(1)
            if command[0] in ('!a', '!archive'):
                archive(command, user)
            elif command[0] in ('!perjob', '!periodical-job'):
                periodical_job(command, user)
            elif command[0] == '!version':
                irc_bot_print(irc_channel, user + ': Current version of videobot is ' + str(version) + '.')
            elif command[0] in ('!update-services', '!us'):
                irc_bot_print(irc_channel, user + ': Services are resfreshing.')
                threading.Thread(target = refresh.refresh_services).start()
            else:
                command_short = command[0].replace('!', '')
                service = find_command_service(command_short)
                if service != None:
                    for irc_bot_message in eval('services.' + service + '.process(service, command, user)'):
                        irc_bot_print(irc_channel, irc_bot_message)
                else:
                    irc_bot_print(irc_channel, user + ': Command \'' + command[0] + '\' does not exist.')

