#if os.path.isdir('./services'):
#    shutil.rmtree('./services')
#    os.makedirs('./services')
#if not os.path.isfile('./services/__init__.py'):
#    open('./services/__init__.py', 'w').close()
import os
import threading
import irc_bot
import refresh

def dashboard():
    os.system('~/.local/bin/gs-server')

def irc_bot_listener():
    irc_bot.irc_bot_listener()

def irc_bot_join():
    irc_bot.irc_bot_join()

def refresh_services():
    refresh.refresh_services()

def main():
    irc_bot_join()
    threading.Thread(target = refresh.refresh_services).start()
    threading.Thread(target = irc_bot_listener).start()
    threading.Thread(target = dashboard).start()

if __name__ == '__main__':
	main()
