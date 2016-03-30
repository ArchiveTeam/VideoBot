import re

def check_valid_url(url):
    if re.search(r'^https?:\/\/[^\/]+?\.[^\/]+', url):
        return True
    else:
        return False

def check_num(string):
    try:
        int(string)
        return True
    except:
        return False
