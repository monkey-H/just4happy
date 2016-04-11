# -*- coding: utf-8 -*-

import logging
import MySQLdb

# from

# todo: refactor import/package path
from orchestration import config


# todo: check why this 'tuple_in_tuple' func?
# does it convert tuple to list? then just use builtin `list()` func instead
#
# def tuple_in_tuple(db_tuple):
#     """
#
#     :param db_tuple:
#     :return:
#     """
#     ret_data = []
#     for item in db_tuple:
#         ret_data.append(item[0])
#     return ret_data


class DBHelper(object):
    @staticmethod
    def _exec_sql(need_fetch, sql, param_tuple, db_url, db_user, db_password, db_name):
        """
        考虑防止sql注入：http://bobby-tables.com/python.html
        cmd = "update people set name=%s where id=%s"
        curs.execute(cmd, (name, id))
        """
        db = MySQLdb.connect(db_url, db_user, db_password, db_name)
        curs = db.cursor
        curs.execute(sql, param_tuple)

        logging.info("Execute SQL '%s' with param '%s'" % (sql, str(param_tuple)))

        data = []
        if need_fetch:
            data = list(curs)
            if len(data) == 0:
                logging.warning("No results for SQL '%s' with param '%s'" % (sql, str(param_tuple)))
        else:
            db.commit()

        db.close()

        return data

    @staticmethod
    def exec_list(sql, param_tulple):
        """
        执行查询语句（select），返回结果的python list；如果没有结果，返回空列表[]
        """
        return DBHelper._exec_sql(True, sql, param_tulple,
                                  config.db_url, config.db_user, config.db_password, config.db_name)

    # todo: 返回的一行值是什么类型，tuple or dict？
    @staticmethod
    def exec_one(sql, param_tulple):
        """
        执行查询语句（select），返回结果的第一个值；如果没有结果，返回None

        """
        data = DBHelper.exec_list(sql, param_tulple)
        if len(data) == 0:
            return None
        else:
            return data[0]

    @staticmethod
    def exec_cmd(sql, param_tulple):
        """
        执行无返回值的sql语句，如 insert, update, delete
        """
        DBHelper._exec_sql(False, sql, param_tulple, config.db_url, config.db_user, config.db_password, config.db_name)
        return None

    @staticmethod
    def init_db():
        """
        初始化数据库和用户，创建空的表格；
        初始化操作只需执行一次！
        """
        if DBHelper.db_exist():
            raise NameError("Error: DB with name '%s' already exists!", config.db_name)

        DBHelper._exec_sql(True, "create db '%s';"
                                 "create user '%s'@'%s' identified by '%s';"
                                 "grant all on '%s'.* to '%s'@'%s';",
                           (config.db_name,
                            config.db_user,
                            config.db_user,
                            '%'),
                           config.db_url, config.db_root_user, config.db_root_password)

        # create tables
        # todo: sync db schema with below sql cmds
        DBHelper.exec_cmd("create table info(name char(50) not null, net char(50), volume char(50));", ())
        # todo: do we need a empty tuple () ?

        DBHelper.exec_cmd("create table machine(id int unsigned not null, ip char(50));", ())
        DBHelper.exec_cmd(
            "create table project(id int unsigned not null auto_increment primary key, name char(50), url char(50));")

        DBHelper.exec_cmd("create table service(name char(50), machine int unsigned, project char(50));")
        DBHelper.exec_cmd("insert into info values('%s', '%s', '%s_volume');",
                          (config.db_user, config.db_user, config.db_user))
        # DBHelper.exec_cmd("insert into machine values(%s, '%s');", (host_ip)) # todo: add hosts

    # 之前设计为每个用户一个单独的db，现已更改为所有用户共用一个db
    @staticmethod
    def db_exist():
        db_list = DBHelper._exec_sql(True, "show databases;", (),
                                     config.db_url, config.db_root_user, config.db_root_password)

        for db in db_list:
            if db == config.db_name:
                return True

        return False
