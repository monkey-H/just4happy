from orchestration.db import db_model
import random


def random_schedule(service_list):
    machines = db_model.get_machines()
    print len(machines)
    for service in service_list:
        if 'host' not in service:
            index = random.randint(0, len(machines)-1)
            print index
            machine = db_model.get_machine(index)
            service['host'] = machine
    return service_list
