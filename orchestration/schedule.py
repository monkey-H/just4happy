from orchestration.db.db_model import DBModel
import random


def random_schedule(service_list):
    machines = DBModel.Machine.get_machines()
    print len(machines)
    for service in service_list:
        if 'host' not in service:
            index = random.randint(0, len(machines) - 1)
            print index
            machine = DBModel.Machine.get_machine(index)
            service['host'] = machine
    return service_list
