from config import ia_access_key, ia_secret_key, max_warc_item_size
import os
import shutil
import threading
import internetarchive
import time
import codecs

def upload(ia_args, ia_files, ia_identifier):
    ia_files_new = []
    for filename in ia_files:
        if not os.path.isfile(filename + '.upload'):
            ia_files_new.append(filename)
    ia_files = list(ia_files_new)
    if len(ia_files) > 0:
        for filename in ia_files:
            with open(filename + '.upload', 'w') as file:
                pass
        upload_response = internetarchive.upload(ia_identifier, ia_files, metadata = ia_args, access_key = ia_access_key, secret_key = ia_secret_key, queue_derive = True, verify = True, verbose = True, delete = True, retries = 5, retries_sleep = 300)
        for filename in ia_files:
            os.remove(filename + '.upload')

def upload_items():
    for folder in [name for name in os.listdir(os.path.join('to_be_uploaded', 'ia_items')) if os.path.isdir(os.path.join('to_be_uploaded', 'ia_items', name))]:
        files = os.listdir(os.path.join('to_be_uploaded', 'ia_items', folder))
        if 'ia_metadata.py' in files and len(files) > 1 and not 'no_upload' in files:
            if len(files) == 1:
                continue
            with codecs.open(os.path.join('to_be_uploaded', 'ia_items', folder, 'ia_metadata.py'), 'r') as file:
                args = file.read().splitlines()
                ia_args = {}
                ia_files = []
                ia_identifier = None
                for arg in args:
                    a, b = arg.split(' = ')
                    if a == 'files':
                        for filename in eval(b):
                            if os.path.isfile(os.path.join('to_be_uploaded', 'ia_items', folder, filename)) and not os.path.isfile(os.path.join('to_be_uploaded', 'ia_items', folder, filename + '.upload')):
                                ia_files.append(os.path.join('to_be_uploaded', 'ia_items', folder, filename))
                    elif a == 'identifier':
                        ia_identifier = eval(b)
                    else:
                        ia_args[a] = eval(b)
                threading.Thread(target = upload, args = (ia_args, ia_files, ia_identifier)).start()
        elif len(files) == 1 and 'ia_metadata.py' in files:
            shutil.rmtree(os.path.join('to_be_uploaded', 'ia_items', folder))

def firstrun():
    for folder in [name for name in os.listdir(os.path.join('to_be_uploaded', 'ia_items')) if os.path.isdir(os.path.join('to_be_uploaded', 'ia_items', name))]:
        for filename in os.listdir(os.path.join('to_be_uploaded', 'ia_items', folder)):
            if filename.endswith('.upload'):
                os.remove(os.path.join('to_be_uploaded', 'ia_items', folder, filename))

def warcs_items():
    max_item_size = max_warc_item_size
    item_size = 0
    new_item_dir = os.path.join('to_be_uploaded', 'ia_warcs', 'new_item')
    new_item_files = []
    if not os.path.isdir(new_item_dir):
        os.makedirs(new_item_dir)
    for file in os.listdir(new_item_dir):
        new_item_files.append(file)
        item_size += os.path.getsize(os.path.join(new_item_dir, file))
    for file in [name for name in os.listdir(os.path.join('to_be_uploaded', 'ia_warcs')) if not name == 'new_item']:
        file_path = os.path.join('to_be_uploaded', 'ia_warcs', file)
        file_path_item = os.path.join('to_be_uploaded', 'ia_warcs', 'new_item', file)
        file_size = os.path.getsize(file_path)
        item_size += file_size
        new_item_files.append(file)
        os.rename(file_path, file_path_item)
        if item_size >= max_item_size:
            timestamp = time.strftime('%Y%m%d%H%M%S')
            date = timestamp[:4] + '-' + timestamp[4:6] + '-' + timestamp[6:11]
            ia_metadata = {'identifier': 'archiveteam_videobot_web_' + timestamp, 'title': 'Archive Team VideoBot Crawls: ' + timestamp, 'date': date, 'collection': 'archiveteam_videobot', 'mediatype': 'web', 'files': new_item_files, 'description': 'Crawls by VideoBot.', 'subject': 'videobot;archiveteam'}
            new_item_dir_ready = os.path.join('to_be_uploaded', 'ia_items', 'archiveteam_videobot_web_' + timestamp)
            for a, b in ia_metadata.items():
                print(a, b)
                with open(os.path.join(new_item_dir, 'ia_metadata.py'), 'a') as meta_file:
                    if type(b) is list:
                        content_string = str(b)
                    else:
                        content_string = '\'' + str(b).replace('\'', '\\\'') + '\''
                    meta_file.write(str(a) + ' = ' + content_string + '\n')
            os.rename(new_item_dir, new_item_dir_ready)
            os.makedirs(new_item_dir)
            item_size = 0
            new_item_files = []
            time.sleep(1)

def move_warcs():
    list = []
    done = True
    maindir = '.'
    for folder in [name for name in os.listdir(maindir) if os.path.isdir(os.path.join(maindir, name))]:
        files = [name for name in os.listdir(os.path.join(maindir, folder)) if (os.path.isfile(os.path.join(maindir, folder, name)) and name.endswith('.warc.gz'))]
        grab_finished = False
        for file in files:
            if file.endswith('-meta.warc.gz'):
                grab_finished = True
        for file in files:
            file_location = os.path.join(maindir, folder, file)
            if grab_finished:
                os.rename(file_location, os.path.join('to_be_uploaded', 'ia_warcs', file))
            else:
                warc_num = int(file[-13:-8])
                warc_num_second = (5-len(str(warc_num + 1))) * '0' + str(warc_num + 1)
                if file[:-13] + warc_num_second + '.warc.gz' in files:
                    os.rename(file_location, os.path.join('to_be_uploaded', 'ia_warcs', file))
        if grab_finished:
           shutil.rmtree(os.path.join(maindir, folder))
    warcs_items()
