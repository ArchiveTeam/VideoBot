version = 20170916.01

irc_server = 'irc.underworld.no'
irc_port = 6667
irc_channel = '#videobot'
irc_nick = 'video'

github = 'https://github.com/ArchiveTeam/VideoBot'

periodical_job_open_time = 172800
max_warc_item_size = 5368709120

with open('keys', 'r') as file:
    ia_access_key, ia_secret_key = file.read().replace('\n', '').replace('\r', '').replace(' ', '').split(',')
    print(ia_access_key, ia_secret_key)
