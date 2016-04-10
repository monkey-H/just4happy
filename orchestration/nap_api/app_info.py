# coding=utf-8
import commands

import MySQLdb
from docker import Client

from orchestration import config
from orchestration.container.client import Client
from orchestration.container.container import Container
from orchestration.db import db_model
from orchestration.project import Project


def tuple_in_tuple(db_tuple):
    ret_data = []
    for item in db_tuple:
        ret_data.append(item[0])
    return ret_data


def create_user(username, email):
    for client in config.client_list:
        # still need mfsmount
        commands.getstatusoutput("ssh %s@%s 'docker run -d --name %s -v %s/%s:%s %s'" % (
            config.hostname, client.split(":")[0], username + "_volume", config.project_path, username,
            config.container_path, config.volume_image))

    commands.getstatusoutput("ssh %s@%s 'docker network create -d overlay %s'" % (
        config.hostname, config.client_list[0].split(":")[0], username))
    commands.getstatusoutput("ssh %s@%s 'cd %s && mkdir %s'" % (
        config.hostname, config.client_list[0].split(":")[0], config.project_path, username))

    return db_model.create_user(username, email)


def delete_user(username):
    try:
        db_model.delete_user(username)
    except MySQLdb.OperationalError as e:
        return False, e.message

    for client in config.client_list:
        # still need mfsmount
        commands.getstatusoutput(
            "ssh %s@%s 'docker rm %s'" % (config.hostname, client.split(":")[0], username + "_volume"))

    commands.getstatusoutput(
        "ssh %s@%s 'cd %s && rm -r %s'" % (config.hostname, client.split(":")[0], config.project_path, username))
    a, b = commands.getstatusoutput(
        "ssh %s@%s 'docker network rm %s'" % (config.hostname, config.client_list[0].split(":")[0], username))

    return True, 'Delete user success'


def service_name_list(username, project_name):
    data = db_model.service_list(username, project_name)

    return data


def get_service(username, project_name, service_name):
    url = db_model.service_ip(username, project_name, service_name)
    full_name = service_name + config.split_mark + project_name + config.split_mark + username

    cli = Client(url, config.c_version)
    con = Container.get_container_by_name(cli, full_name)

    srv_dict = {'name': service_name, 'ip': str(url).split(":")[0]}

    if con is None:
        srv_dict['status'] = 'not create'
        srv_dict['ports'] = '-'
        srv_dict['image'] = '-'
        srv_dict['create_time'] = '-'
        srv_dict['id'] = '-'
    else:
        srv_dict['status'] = con.status
        srv_dict['image'] = con.image
        srv_dict['create_time'] = con.create_time
        srv_dict['id'] = con.id
        if len(con.ports) == 0:
            srv_dict['shell'] = '-'
            ports = '-'
        else:
            ports = con.ports
            if '4200' in con.ports:
                srv_dict['shell'] = con.ports['4200']
                del ports['4200']

        srv_dict['ports'] = ports

    return srv_dict


def service_list(username, project_name):
    name_list = db_model.service_list(username, project_name)
    if name_list is None:
        return '-'

    srv_list = []
    for service_name in name_list:
        url = db_model.service_ip(username, project_name, service_name[0])
        full_name = service_name[0] + config.split_mark + project_name + config.split_mark + username

        cli = Client(url, config.c_version)
        print (full_name, url)
        con = Container.get_container_by_name(cli, full_name)

        # if not container_exists(cli, full_name):
        #     print 'no container: %s in hosts' % full_name
        #     continue

        srv_dict = {'name': service_name[0], 'ip': str(url).split(":")[0]}

        if con is None:
            srv_dict['status'] = 'not create'
            srv_dict['ports'] = '-'
            srv_dict['image'] = '-'
            srv_dict['create_time'] = '-'
            srv_dict['id'] = '-'
        else:
            srv_dict['status'] = con.status
            srv_dict['image'] = con.image
            srv_dict['create_time'] = con.create_time
            srv_dict['id'] = con.id
            if len(con.ports) == 0:
                srv_dict['shell'] = '-'
                ports = '-'
            else:
                ports = con.ports
                if '4200' in con.ports:
                    srv_dict['shell'] = con.ports['4200']
                    del ports['4200']

            srv_dict['ports'] = ports

        # ports = get_port(username, password, project_name, service_name)
        # if ports is None:
        #     srv_dict['port'] = '-'
        #     srv_dict['shell'] = '-'
        # elif not len(ports):
        #     srv_dict['port'] = '-'
        #     srv_dict['shell'] = '-'
        # else:
        #     expose_port = []
        #     for key in ports:
        #         if not ports[key] is None:
        #             if key == '4200/tcp':
        #                 srv_dict['shell'] = ports[key][0]['HostPort']
        #             else:
        #                 expose_port.append(ports[key][0]['HostPort'])
        #         else:
        #             expose_port.append('-')
        #     srv_dict['port'] = expose_port

        srv_list.append(srv_dict)
    return srv_list


def project_list(username, begin, length):
    data = db_model.project_list(username, begin, length)
    return data


def get_project(username, project_name):
    data = db_model.get_project(username, project_name)
    return data


def kill_project(username, project_name):
    services = get_project_service(username, project_name)

    project = Project.get_project_by_name(project_name, services)
    project.stop()


def restart_project(username, project_name):
    services = get_project_service(username, project_name)

    project = Project.get_project_by_name(project_name, services)
    project.restart()


def get_project_service(username, project_name):
    services = []

    service_name = service_name_list(username, project_name)

    for service in service_name:
        print ("service: %s" % service[0])
        ip = db_model.service_ip(username, project_name, service[0])
        item = {"name": service[0] + config.split_mark + project_name + config.split_mark + username, "ip": ip}
        print (item)
        services.append(item)

    return services


# 注意，这里以后用project stop 来实现
# 已经用project stop 实现
def destroy_project(username, project_name):
    # if os.path.exists('%s/%s/%s' % (config.project_path, username, project_name)):
    #     shutil.rmtree('%s/%s/%s' % (config.project_path, username, project_name))

    services = get_project_service(username, project_name)

    project = Project.get_project_by_name(project_name, services)
    project.stop()
    project.remove()

    # data = database_update.service_list(username, project_name)
    #
    # if data:
    #     for service_name in data:
    #         url = str(database_update.service_ip(username, project_name, service_name))
    #         if url == '-':
    #             continue
    #         cli = Client(url, config.c_version)
    #         full_name = username + config.split_mark + project_name + config.split_mark + service_name
    #         con = Container.getContainerByName(cli, full_name)
    #         con.stop
    #         if container_exists(cli, full_name):
    #             cli.stop(container=full_name)
    #             cli.remove_container(container=full_name)

    db_model.delete_service(username, project_name)
    db_model.delete_project(username, project_name)

    return True, 'Destroy project: %s success' % project_name


# not use again
def get_status(username, password, project_name, service_name):
    cip = db_model.service_ip(username, project_name, service_name)
    if cip == '-':
        return 'no such project or service'

    cli = Client(cip, config.c_version)
    full_name = service_name + config.split_mark + project_name + config.split_mark + username
    # full_name = username + config.split_mark + project_name + config.split_mark + service_name

    if container_exists(cli, full_name):
        detail = cli.inspect_container(full_name)
        return detail['State']['Status']
    else:
        return 'no such container'


# not use again
def get_port(username, project_name, service_name):
    cip = db_model.service_ip(username, project_name, service_name)
    if cip == '-':
        return 'no such project or service'

    cli = Client(base_url=cip, version=config.c_version)
    full_name = username + config.split_mark + project_name + config.split_mark + service_name

    if container_exists(cli, full_name):
        detail = cli.inspect_container(full_name)
        return detail['NetworkSettings']['Ports']
    else:
        return 'no such container'


def container_exists(cli, container_name):
    containers = cli.containers(all=True)
    for k in containers:
        if '/' + container_name in k['Names']:
            return True
    return False


def get_logs(username, project_name, service_name):
    cip = db_model.service_ip(username, project_name, service_name)

    if cip == '-':
        return 'no such project or service'

    cli = Client(cip, config.c_version)
    full_name = service_name + config.split_mark + project_name + config.split_mark + username

    con = Container.get_container_by_name(cli, full_name)

    return con.client.logs(con.id)

    # if container_exists(cli, full_name):
    #     logs = cli.logs(container=full_name)
    #     return logs
    # else:
    #     return 'no such container'
