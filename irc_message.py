def job_finished(user, name, title, id=None):
    if id:
        return user + ': Your job for ' + name + ' \'' + title + '\' with ID ' + id + ' is finished.'
    return user + ': Your job for ' + name + ' \'' + title + '\' is finished.'

def job_failed(user, name, title, id=None):
    if id:
        return user + ': Your job for ' + name + ' \'' + title + '\' with ID ' + id + ' failed.'
    return user + ': Your job for ' + name + ' \'' + title + '\' failed.'

def job_added(user, name, title, id=None):
    if id:
        return user + ': Your job for ' + name + ' \'' + title + '\' with ID ' + id + ' is added.'
    return user + ': Your job for ' + name + ' \'' + title + '\' is added.'

def job_aborted(user, name, id=None):
    if id:
        return user + ': Your job for ' + name + ' with ID ' + id + ' is aborted.'
    return user + ': Your job for ' + name + ' is aborted.'

def failed_extraction(user, name, extract, id=None):
    if id:
        return user + ': Failed to extract ' + extract + ' from ' + name + ' with ID ' + id + '.'
    return user + ': Failed to extract ' + extract + ' from ' + name + '.'