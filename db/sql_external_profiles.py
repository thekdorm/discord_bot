import sqlite3
import os.path
from pathlib import Path


def create_db(db, columns):
    try:
        get_record(db)
    except (sqlite3.OperationalError, TypeError):
        action = "create table if not exists users ("
        for column in columns:
            if column == columns[-1]:
                action = action + "'" + column + "')"
            else:
                action = action + "'" + column + "', "
        db = sqlite3.connect(db)
        c = db.cursor()
        c.execute(action)
        db.commit()
        db.close()


def add_record(db, user, columns, column=None, value=None):
    db = sqlite3.connect(db)
    c = db.cursor()
    # command = []
    # if column in columns:
    #     for i in range(len(columns)):
    #         command.append(None)
    #     command[columns.index(column)] = value
    print(f'columns={columns}, user={user}, command={value}')
    c.execute(f'INSERT INTO users ("user", "{column}") VALUES ("{user}", "{value}")')
    db.commit()
    db.close()


def get_record(db, user=None, column=None):
    columns = ['users', 'steam', 'battlenet']
    db = sqlite3.connect(db)
    c = db.cursor()
    if column:
        c.execute(f'SELECT {column} FROM users WHERE user="{user}"')
        result = c.fetchall()
    elif not user:
        c.execute("select * from users")
        result = c.fetchall()
    db.close()
    return result


def delete_record(db, user):
    db = sqlite3.connect(db)
    c = db.cursor()
    c.execute(f'DELETE FROM users WHERE user="{user}"')
    db.commit()
    db.close()


def modify_column(db, mode, column):
    db = sqlite3.connect(db)
    c = db.cursor()
    if mode.lower() == 'add':
        c.execute(f'alter table users add {column} char(100)')
    elif mode.lower() == 'drop':
        c.execute(f'alter table users drop {column}')
    db.commit()
    db.close()


# create_db('Bastion-371365591300440064.db', ['user', 'steam', 'battlenet'])
# db = sqlite3.connect('Bastion-371365591300440064.db')
# c = db.cursor()
# modify_column('Bastion-371365591300440064.db', 'drop', 'battle.net')
# print(get_record('Bastion-371365591300440064.db', 'Kygo Ren#2295', column='steam')[0][0])
# add_record('Bastion-371365591300440064.db', 'Kygo Ren#2295', columns=['user', 'steam', 'battlenet'], column='steam', value='https://steamcommunity.com/id/thekdorm')
# c.execute("pragma table_info(users)")
# c.execute("select * from users")
# print(c.fetchall())
# delete_record('Bastion-371365591300440064.db', 'Kygo Ren#2295')
# db.commit()
# db.close()
