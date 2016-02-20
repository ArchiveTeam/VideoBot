import refresh

def find_command_service(command):
    services_list = refresh.services_list
    for service in services_list:
        if command in service[2]:
            return service[0]
    else:
        return None
