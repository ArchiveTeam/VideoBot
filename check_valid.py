import re

def check_valid_url(url):
    if re.search(r'^http:\/\/[^\/]+?\.[^\/]+', url):
        return 'http'
    elif re.search(r'^https:\/\/[^\/]+?\.[^\/]+', url):
        return 'https'
    elif re.search(r'^rtsp:\/\/[^\/]+?\.[^\/]+', url):
        return 'rtsp'
    elif re.search(r'^rtmp:\/\/[^\/]+?\.[^\/]+', url):
        return 'rtmp'
    elif re.search(r'^mms:\/\/[^\/]+?\.[^\/]+', url):
        return 'mms'
    elif re.search(r'^mmsh:\/\/[^\/]+?\.[^\/]+', url):
        return 'mmsh'
    else:
        return False

def check_num(string):
    try:
        int(string)
        return True
    except:
        return False
