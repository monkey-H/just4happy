#!/usr/bin/python

import time

from consul import Consul

from orchestration.container.client import Client


def update_status():
    consul = Consul(host=deploy.health_heck.config.consul_url)
    containers = Client.get_local_client().get_all_containers()
    while True:
        for c in containers:
            value = {'name': c.service_name, 'status': c['Status'], 'time': time.time()}
            consul.kv.put('nap_services/%s/%s/%s' % (c.user_name, c.project_name, c.service_name), str(value))

        time.sleep(deploy.health_heck.config.time_interval_in_seconds)

if __name__ == "__main__":
    update_status()
