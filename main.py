#if os.path.isdir('./services'):
#    shutil.rmtree('./services')
#    os.makedirs('./services')
#if not os.path.isfile('./services/__init__.py'):
#    open('./services/__init__.py', 'w').close()
import os
import threading
import irc_bot
import refresh
import upload
import time

def dashboard():
    os.system('~/.local/bin/gs-server')

def irc_bot_listener():
    irc_bot.irc_bot_listener()

def irc_bot_join():
    irc_bot.irc_bot_join()

def refresh_services():
    refresh.refresh_services()

def process_warcs():
    while True:
        try:
            upload.move_warcs()
            threading.Thread(target = upload.uploader).start()
        except:
            pass #for now
        time.sleep(300)

def main():
    if not os.path.isdir('./to_be_uploaded/ia_items'):
        os.makedirs('./to_be_uploaded/ia_items')
    if not os.path.isdir('./to_be_uploaded/ia_warcs'):
        os.makedirs('./to_be_uploaded/ia_warcs')
    irc_bot_join()
    refresh.refresh_services()
    threading.Thread(target = refresh.refresh_periodical_jobs).start()
    threading.Thread(target = refresh.refresh_periodical_jobs_start).start()
    threading.Thread(target = irc_bot_listener).start()
    threading.Thread(target = dashboard).start()
    threading.Thread(target = process_warcs).start()

if __name__ == '__main__':
	main()
