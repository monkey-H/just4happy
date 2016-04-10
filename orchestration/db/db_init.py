import MySQLdb

# not use again, all users use one db
def create_basetable(username, password):
    db = MySQLdb.connect(config.database_url, config.rootname, config.rootpass)
    cursor = db.cursor()
    cursor.execute("create db '%s';" % username)
    cursor.execute("create user '%s'@'%s' identified by '%s';" % (username, '%', password))
    cursor.execute("grant all on '%s'.* to '%s'@'%s';" % (username, username, '%'))
    db.commit()
    db.close()

    # create some tables for this user
    user_db = MySQLdb.connect(config.database_url, username, password, username)
    user_cursor = user_db.cursor()
    user_cursor.execute("create table info(name char(50) not null, net char(50), volume char(50));")
    user_cursor.execute("create table machine(id int unsigned not null, ip char(50));")
    user_cursor.execute(
        "create table project(id int unsigned not null auto_increment primary key, name char(50), url char(50));")
    user_cursor.execute("create table service(name char(50), machine int unsigned, project char(50));")
    user_cursor.execute("insert into info values('%s', '%s', '%s_volume');" % (username, username, username))
    client_id = 0
    for client in config.client_list:
        user_cursor.execute("insert into machine values(%d, '%s');" % (client_id, client))
        client_id += 1
    # user_cursor.execute("insert into machine values(0, '192.168.56.105:2376');")
    # user_cursor.execute("insert into machine values(1, '192.168.56.106:2376');")
    user_db.commit()
    user_db.close()

