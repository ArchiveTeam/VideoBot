import temp_perjobs
import os
import random
import string

def check_temp_perjob_variable(ticket_id, var):
    ticket_id_ = ''.join(random.choice(string.ascii_lowercase) for num in range(10))
    os.rename('temp_perjobs/' + ticket_id + '.py', 'temp_perjobs/' + ticket_id + ticket_id_ + '.py')
    reload(temp_perjobs)
    try:
        if eval('temp_perjobs.' + ticket_id + ticket_id_ + '.' + var):
            variable = eval('temp_perjobs.' + ticket_id + ticket_id_ + '.' + var)
            os.rename('temp_perjobs/' + ticket_id + ticket_id_ + '.py', 'temp_perjobs/' + ticket_id + '.py')
            return variable
    except:
        os.rename('temp_perjobs/' + ticket_id + ticket_id_ + '.py', 'temp_perjobs/' + ticket_id + '.py')
        return False
