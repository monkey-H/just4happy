import db_helper as db


################################################################################
# 由于添加用户时会创建默认的overlay网络，所有该用户的容器都接入该默认网络
# 暂不支持更多的overlay网络

# todo: sql string need quot '' ?

# not use temporarily
def get_net(user_id):
    data = db.exec_cmd("select net from info where name='%s'", user_id)  # todo: verify this
    return data[0]


# not use temporarily
def set_net(user_id, net_id):
    db.exec_cmd("insert into info(net) values('%s') where name='%s'", (net_id, user_id))  # todo: verify this


# not use temporarily
def get_volume(user_id):
    return db.exec_list("select volume from info where name='%s'", user_id)


# not use temporarily
def set_volume(user_id, volume_path):
    db.exec_cmd("insert into info(volume) values('%s') where name='%s'", (user_id, volume_path))


def get_service(user_id, project_id, service_name):
    # db.exec_list("select id from projects where name = '%s' and userID='%s'"
    #                % (project_name, username))
    #
    # cursor.execute("select name from services where projectID='%d' and name = " % data[0])
    # data = cursor.fetchall()
    #
    # if data is None:
    #     return None


def service_list(username, project_name):
    db = MySQLdb.connect(config.database_url, config.database_user, config.database_passwd, config.database)
    cursor = db.cursor()
    cursor.execute("select id from projects where name = '%s' and userID=(select id from user where name='%s')"
                   % (project_name, username))
    data = cursor.fetchall()

    if len(data) == 0:
        return None

    cursor.execute("select name from services where projectID='%d'" % data[0])
    data = cursor.fetchall()
    return data
    # clause = "select name from services " \
    #          "where projectID in " \
    #          "(select id from projects where name='%s' and userID in (select id from user where name = '%s')))" \
    #          % (project_name, username)
    #
    # data = database_get(clause)


def create_service(username, service_name, machine_ip, project_name):
    db = MySQLdb.connect(config.database_url, config.database_user, config.database_passwd, config.database)
    cursor = db.cursor()
    cursor.execute("select id from projects where name='%s' and userID in (select id from user where name = '%s')"
                   % (project_name, username))
    data = cursor.fetchone()
    cursor.execute("insert into services(name, projectID, IP) values('%s', %d, '%s')"
                   % (service_name, data[0], machine_ip))
    db.commit()
    db.close()


def delete_service(username, project_name):
    db = MySQLdb.connect(config.database_url, config.database_user, config.database_passwd, config.database)
    cursor = db.cursor()
    cursor.execute("select id from projects where name='%s' and userID = (select id from user where name = '%s')"
                   % (project_name, username))
    data = cursor.fetchall()
    cursor.execute("delete from services where projectID = '%s'" % data[0])
    db.commit()
    db.close()


def project_exists(username, project_name):
    db = MySQLdb.connect(config.database_url, config.database_user, config.database_passwd, config.database)
    cursor = db.cursor()
    cursor.execute("select * from projects where name='%s' and userID = (select id from user where name = '%s')"
                   % (project_name, username))
    data = cursor.fetchall()
    db.close()

    return True if data else False


def roll_back(username, password, project_name):
    db = MySQLdb.connect(config.database_url, config.database_user, config.database_passwd, config.database)
    cursor = db.cursor()

    logs = ''
    srv_list = service_list(username, password, project_name)
    if srv_list:
        for service_name in srv_list:
            url = service_ip(username, project_name, service_name)
            if url == '-':
                continue
            cli = Client(base_url=url, version=config.c_version)
            full_name = username + config.split_mark + project_name + config.split_mark + service_name
            if container_exists(cli, full_name):
                logs = logs + full_name + '\n' + cli.logs(container=full_name) + '\n'
                cli.stop(container=full_name)
                cli.remove_container(container=full_name)
        cursor.execute("delete from service where project='%s'" % project_name)
        cursor.execute("delete from project where name='%s'" % project_name)
        db.commit()
        db.close()

    return logs


def service_ip(username, project_name, service_name):
    db = MySQLdb.connect(config.database_url, config.database_user, config.database_passwd, config.database)
    cursor = db.cursor()
    cursor.execute("select id from projects where name='%s' and userID=(select id from user where name='%s')"
                   % (project_name, username))
    data = cursor.fetchone()
    print service_name
    cursor.execute("select IP from services where name='%s' and projectID='%d'" % (service_name, data[0]))
    data = cursor.fetchone()
    return data[0]


def get_machines():
    db = MySQLdb.connect(config.database_url, config.database_user, config.database_passwd, config.database)
    cursor = db.cursor()
    cursor.execute("select ip from machine")
    data = cursor.fetchall()
    db.close()
    return tuple_in_tuple(data)


def get_machine(index):
    db = MySQLdb.connect(config.database_url, config.database_user, config.database_passwd, config.database)
    cursor = db.cursor()
    cursor.execute("select ip from machine limit %d,1" % index)
    data = cursor.fetchone()
    db.close()
    return data[0]


def create_project(username, project_name, url):
    db = MySQLdb.connect(config.database_url, config.database_user, config.database_passwd, config.database)
    cursor = db.cursor()
    cursor.execute("select id from user where name='%s'" % username)
    data = cursor.fetchone()
    print data[0]
    cursor.execute("insert into projects(name, userID, url) values('%s', '%d', '%s')" % (project_name, data[0], url))
    db.commit()
    db.close()


def delete_project(username, project_name):
    db = MySQLdb.connect(config.database_url, config.database_user, config.database_passwd, config.database)
    cursor = db.cursor()
    cursor.execute("select id from user where name='%s'" % username)
    data = cursor.fetchone()
    if len(data) == 0:
        return
    cursor.execute("delete from projects where name ='%s' and userID='%d'" % (project_name, data[0]))
    db.commit()
    db.close()


def create_user(username, email):
    # if database_exist(username, password):
    #     return False, "username: %s already exists, please try anoter name"
    #
    # create_basetable(username, password)
    # return True, "insert into mysql"
    db = MySQLdb.connect(config.database_url, config.database_user, config.database_passwd, config.database)
    cursor = db.cursor()
    cursor.execute("insert into user(name, email) values('%s', '%s')" % (username, email))
    db.commit()
    db.close()


def create_machine(ip_list):
    db = MySQLdb.connect(config.database_url, config.database_user, config.database_passwd, config.database)
    cursor = db.cursor()
    for ip in ip_list:
        cursor.execute("insert into machine(ip) values('%s')" % ip)
    db.commit()
    db.close()


def delete_user(username):
    db = MySQLdb.connect(config.database_url, config.database_user, config.database_passwd, config.database)
    cursor = db.cursor()
    cursor.execute("select id from user where name='%s'" % username)
    data = cursor.fetchone()

    cursor.execute("delete from services where projectID in (select id from projects where userID='%d')" % data[0])
    cursor.execute("delete from projects where userID='%d'" % data[0])
    cursor.execute("delete from user where name='%s'" % username)
    db.commit()
    db.close()


def get_project(username, project_name):
    db = MySQLdb.connect(config.database_url, config.database_user, config.database_passwd, config.database)
    cursor = db.cursor()
    cursor.execute("select id from user where name='%s'" % username)
    data = cursor.fetchone()
    if len(data) == 0:
        return None

    cursor.execute("select name,url from projects where userID = '%d' and name = '%s'" % (data[0], project_name))

    data = cursor.fetchone()
    db.close()

    if data is None:
        return None
    return data


def project_list(username, begin, length):
    db = MySQLdb.connect(config.database_url, config.database_user, config.database_passwd, config.database)
    cursor = db.cursor()
    cursor.execute("select id from user where name='%s'" % username)
    data = cursor.fetchone()
    if len(data) == 0:
        return None

    cursor.execute("select name, url from projects where userID = '%d' limit %d,%d" % (data[0], begin, length))

    data = cursor.fetchall()
    db.close()
    return data
