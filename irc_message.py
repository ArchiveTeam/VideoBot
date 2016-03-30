def job_finished(user, name, title, id):
    return user + ': Your job for ' + name + ' \'' + videotitle + '\' with ID ' + videoid + ' is finished.'

def job_failed(user, name, title, id):
    return user + ': Your job for ' + name + ' \'' + videotitle + '\' with ID ' + videoid + ' failed.'

def job_added(user, name, title, id):
    return user + ': Your job for ' + name + ' \'' + videotitle + '\' with ID ' + videoid + ' is added.'

def job_aborted(user, name, id):
    return user + ': Your job for ' + name + ' with ID ' + videoid + ' is aborted.'

def failed_extraction(user, name, id, extract):
    return user + ': Failed to extract ' + extract + ' from ' + name + ' with ID ' + id + '.'
