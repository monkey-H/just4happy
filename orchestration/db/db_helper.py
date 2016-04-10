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

    data = ()
    if need_fetch:
        data = curs.fetchall()
        if data is None:
            logging.warning("No results for SQL '%s' with param '%s'" % (sql, str(param_tuple)))
    else:
        db.commit()

    db.close()

    return list(data)


def exec_list(sql, param_tulple):
    """
    执行select查询语句
    todo: 返回python格式的列表？
    """
    return _exec_sql(True, sql, param_tulple, config.db_url, config.db_user, config.db_password, config.db_name)


def exec_cmd(sql, param_tulple):
    """
    执行无返回值的语句，如 insert, update, delete
    """
    _exec_sql(False, sql, param_tulple, config.db_url, config.db_user, config.db_password, config.db_name)
    return None


# 之前设计为每个用户一个单独的db，现已更改为所有用户共用一个db，故该函数不再使用

# def db_exist():
#     db_list = _exec_sql(True, "show databases;", (), config.db_url, config.db_root_user, config.db_root_password)
#
#     for user in db_list:
#         if user == "dbname":
#             return True
#
#     return False
