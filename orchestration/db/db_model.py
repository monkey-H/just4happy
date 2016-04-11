# -*- coding: utf-8 -*-

from db_helper import DBHelper as Db


# todo: 考虑增加redis/memcached等缓存层以提高性能


class DBModel(object):
    ################################################################################
    # 由于添加用户时会创建默认的overlay网络，所有该用户的容器都接入该默认网络
    # 暂不支持更多的overlay网络
    # not use temporarily
    class Network(object):
        # todo: sql string need quot '%s' ?

        @staticmethod
        def get(user_id):
            data = Db.exec_cmd("select net from info where name='%s'",
                               user_id)  # todo: check tuple usage
            return data[0]

        @staticmethod
        def create(user_id, net_id):
            Db.exec_cmd("insert into info(net) values('%s') where name='%s'",
                        (net_id, user_id))  # todo: check tuple usage

    # not use temporarily
    class Volume(object):
        @staticmethod
        def get(user_id):
            return Db.exec_list("select volume from info where name='%s'", user_id)

        @staticmethod
        def create(user_id, volume_path):
            Db.exec_cmd("insert into info(volume) values('%s') where name='%s'",
                        (user_id, volume_path))

    class Service(object):
        # todo: name or id?
        @staticmethod
        def get_list(user_id, project_name):
            prj_id = Db.exec_one("select id from projects "
                                 "where name = '%s' and userID=(select id from user where name='%s')",
                                 (project_name, user_id))

            if prj_id is None:
                raise Exception("Project does not exist for %s, %s" % (user_id, project_name))

            return Db.exec_list("select name from services where projectID='%s'", prj_id)
            # todo: why not use single sql cmd?
            # sql = "select name from services "
            #          "where projectID in "
            #          "(select id from projects "
            #          " where name='%s' and userID in (select id from user where name = '%s')))",
            #          (project_name, username)
            #
            # return Db.exec_list(sql)

        @staticmethod
        def create(user_name, service_name, machine_ip, project_name):
            prj_id = Db.exec_one("select id from projects "
                                 "where name='%s' and userID in (select id from user where name = '%s')",
                                 (project_name, user_name))
            Db.exec_cmd("insert into services(name, projectID, IP) values('%s', %s, '%s')",
                        (service_name, prj_id, machine_ip))

        # todo: db 表名应改为英文名词单数
        @staticmethod
        def get_host_ip(user_id, project_name, service_name):
            prj_id = Db.exec_one("select id from projects "
                                 "where name='%s' and userID='%s')",
                                 (project_name, user_id))

            return Db.exec_one("select IP from services "
                               "where name='%s' and projectID='%s'",
                               (service_name, prj_id))

    class Project(object):
        @staticmethod
        def exists(user_name, project_name):
            prj = Db.exec_one("select 1 from projects "
                              "where name='%s' and userID = (select id from user where name = '%s')",
                              (project_name, user_name))

            return prj is not None

        @staticmethod
        def delete(user_id, password, project_name):
            # todo: 删除容器考虑在上层实现?
            srv_list = DBModel.Service.get_list(user_id, password, project_name)
            if len(srv_list) != 0:
                for service_name in srv_list:
                    ip = DBModel.Service.get_host_ip(user_id, project_name, service_name)
                    if ip == '-':
                        continue
                    else:
                        # rm this container
                        # cli = Client(base_url=url, version=config.c_version)
                        # full_name = username + config.split_mark + project_name + config.split_mark + service_name
                        # if container_exists(cli, full_name):
                        #     logs = logs + full_name + '\n' + cli.logs(container=full_name) + '\n'
                        #     cli.stop(container=full_name)
                        #     cli.remove_container(container=full_name)
                        pass

            Db.exec_cmd("delete from service where project='%s'", project_name)
            Db.exec_cmd("delete from project where name='%s'", project_name)

        @staticmethod
        def create(user_id, project_name, url):
            Db.exec_cmd("insert into projects(name, userID, url) values('%s', '%s', '%s')",
                        (project_name, user_id, url))

        @staticmethod
        def delete(user_id, project_name):
            Db.exec_cmd("delete from projects where name ='%s' and userID='%s'", (project_name, user_id))

        @staticmethod
        def get_info(user_id, project_name):
            # todo: name已经知道了，url是git repo的url吗？
            return Db.exec_one("select name, url from projects where userID = '%s' and name = '%s'",
                               (user_id, project_name))

        @staticmethod
        def get_list(user_id, start_index, count):
            """
            返回用于分页的某个用户的所有项目;
            如果count <= 0，则忽略 start_index，返回全部列表
            """
            if count <= 0:
                return Db.exec_list("select name, url from projects "
                                    "where userID = '%s'",
                                    user_id)
            else:
                return Db.exec_list("select name, url from projects "
                                    "where userID = '%s' limit %s,%s",
                                    (user_id, start_index, count))

        @staticmethod
        def delete_all_services(user_name, project_name):
            prj_id = Db.exec_one("select id from projects "
                                 "where name='%s' and userID = (select id from user where name = '%s')",
                                 (project_name, user_name))
            if prj_id is None:
                raise Exception("Project does not exist for %s, %s" % (user_name, project_name))

            Db.exec_cmd("delete from services where projectID = '%s'", prj_id)

    class User(object):
        @staticmethod
        def add_user(user_name, email):
            Db.exec_cmd("insert into user(name, email) values('%s', '%s')",
                        (user_name, email))
            # todo: 添加用户后创建默认网络和volume由上层负责
            # todo: return user_id?

        @staticmethod
        def delete_user_and_projects(user_name):
            """
            删除用户及该用户的所有项目和所属服务
            """
            # todo: 删除所有项目和所属服务是否有上层负责，或以事务方式执行？
            # todo: 合并下面的多条sql cmds?
            user_id = Db.exec_one("select id from user where name='%s'", user_name)

            Db.exec_cmd("delete from services where projectID in "
                        "(select id from projects where userID='%s')", user_id)
            Db.exec_cmd("delete from projects where userID='%s'", user_id)
            Db.exec_cmd("delete from user where name='%s'", user_id)

    class Machine(object):
        @staticmethod
        def add_machine_list(ip_list):
            for ip in ip_list:
                Db.exec_cmd("insert into machine(ip) values('%s')", ip)

        @staticmethod
        def get_machine_list():
            return Db.exec_list("select ip from machine")

        @staticmethod
        def get_machine(index):
            # todo: what is this?
            # todo: 用于随机调度？
            return Db.exec_one("select ip from machine limit %s,1" % index)
