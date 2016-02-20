import requests
import re

def extract_info(regexes, url):
    html = requests.get(url)
    if type(regexes) is str:
        regexes = [regexes]
    extracted = []
    for regex in regexes:
        if re.search(regex, html.text):
            extracted.append(re.search(regex, html.text).group(1))
        else:
            extracted.append(None)
    if len(extracted) == 1:
        extracted = extracted[0]
    return extracted
