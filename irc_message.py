def job_finished(user, name, title, id):
    return user + ': Your job for ' + name + ' \'' + title + '\' with ID ' + id + ' is finished.'

def job_failed(user, name, title, id):
    return user + ': Your job for ' + name + ' \'' + title + '\' with ID ' + id + ' failed.'

def job_added(user, name, title, id):
    return user + ': Your job for ' + name + ' \'' + title + '\' with ID ' + id + ' is added.'

def job_aborted(user, name, id):
    return user + ': Your job for ' + name + ' with ID ' + id + ' is aborted.'

def failed_extraction(user, name, id, extract):
    return user + ': Failed to extract ' + extract + ' from ' + name + ' with ID ' + id + '.'
