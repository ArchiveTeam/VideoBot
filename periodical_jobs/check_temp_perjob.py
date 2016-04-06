import temp_perjobs
import os
import random
import string

def check_temp_perjob_variable(ticket_id, var):
    ticket_id_ = ''.join(random.choice(string.ascii_lowercase) for num in range(10))
    os.rename('temp_perjobs/' + ticket_id + '.py', 'temp_perjobs/' + ticket_id + ticket_id_ + '.py')
    reload(temp_perjobs)
    try:
        variable = eval('temp_perjobs.' + ticket_id + ticket_id_ + '.' + var)
        os.rename('temp_perjobs/' + ticket_id + ticket_id_ + '.py', 'temp_perjobs/' + ticket_id + '.py')
        os.remove('temp_perjobs/' + ticket_id + ticket_id_ + '.pyc')
        return variable
    except:
        os.rename('temp_perjobs/' + ticket_id + ticket_id_ + '.py', 'temp_perjobs/' + ticket_id + '.py')
        os.remove('temp_perjobs/' + ticket_id + ticket_id_ + '.pyc')
        return 'var not found'

def get_temp_perjob_variables(ticket_id):
    file_location = None
    if os.path.isfile('temp_perjobs/' + ticket_id + '.py'):
        file_location = 'temp_perjobs/' + ticket_id + '.py'
    elif os.path.isfile('periodical_jobs/' + ticket_id + '.py'):
        file_location = 'periodical_jobs/' + ticket_id + '.py'
    if file_location != None:
        variables = []
        with open('temp_perjobs/' + ticket_id + '.py', 'r') as file:
            for line in file:
                line = line.replace('\n', '').replace('\r', '')
                if ' = ' in line:
                    variables.append(line.split(' = ')[0])
        return variables
    else:
        return None
