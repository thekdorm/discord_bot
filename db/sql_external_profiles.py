import sqlite3


def create_db(db, close=True):
    accounts = ['steam', 'battlenet', 'epic', 'origin']
    try:
        get_record(db)
    except (sqlite3.OperationalError, TypeError):
        action = "CREATE TABLE IF NOT EXISTS users (user PRIMARY KEY, "
        for account in accounts:
            if account == accounts[-1]:
                action = action + f'{account} DEFAULT None)'
            else:
                action = action + f'{account} DEFAULT None, '
        db = sqlite3.connect(db)
        c = db.cursor()
        c.execute(action)

        if close:
            db.commit()
            db.close()
        return 1
    return 0


def add_user(db, user):
    db = sqlite3.connect(db)
    c = db.cursor()
    c.execute(f'SELECT * FROM users WHERE user="{user}"')
    if len(c.fetchall()) == 0:  # if user doesn't already exist, create row for user
        c.execute(f'INSERT INTO users ("user") VALUES ("{user}")')
    else:
        pass
    db.commit()
    db.close()


def modify_user(db, user, column, value):
    db = sqlite3.connect(db)
    c = db.cursor()
    c.execute(f'SELECT * FROM users WHERE user="{user}"')
    if len(c.fetchall()) == 0:
        return 0
    c.execute(f'UPDATE users SET {column}="{value}" where user="{user}"')
    db.commit()
    db.close()
    return 1


def get_record(db, user='all', column='all'):
    db = sqlite3.connect(db)
    c = db.cursor()

    if column.lower() == 'all' and user.lower() == 'all':  # get all accounts for all users
        c.execute(f'SELECT * FROM users')
    elif column.lower() == 'all' and user.lower() != 'all':  # get all accounts for specified user
        c.execute(f'SELECT * FROM users WHERE user="{user}"')
    elif column.lower() != 'all' and user.lower() == 'all':  # get specified account for all users
        c.execute(f'SELECT user, {column} FROM users')
    else:  # get specified account for specified user
        c.execute(f'SELECT {column} from users WHERE user="{user}"')
    result = c.fetchall()
    db.commit()
    db.close()
    return result


def delete_user(db, user):
    db = sqlite3.connect(db)
    c = db.cursor()
    c.execute(f'DELETE FROM users WHERE user="{user}"')
    db.commit()
    db.close()


def modify_column(db, mode, column):
    data = db
    db = sqlite3.connect(db)
    c = db.cursor()
    if mode.lower() == 'add':
        c.execute(f'ALTER TABLE users ADD COLUMN {column} DEFAULT None')
    elif mode.lower() == 'drop':
        if check_table(data, '_old', c=c) != 0:
            c.execute('DROP TABLE _old')
        else:
            pass
        action = "CREATE TABLE IF NOT EXISTS _old (user PRIMARY KEY, "
        accounts = [account for account in get_columns(db, 'users', c)]
        if column not in accounts:
            pass
        else:
            for account in accounts:  # go through _old table columns, some bad logic here to prevent issues
                if account == accounts[0]:  # but it works?
                    pass
                elif account == accounts[-2]:
                    if accounts[-1] == column:
                        action = action + f'{account} DEFAULT None)'
                elif account == accounts[-1]:
                    pass
                else:
                    action = action + f'{account} DEFAULT None, '
            db = sqlite3.connect(data)
            c = db.cursor()
            c.execute(action)  # create the old table
            accounts.pop(accounts.index(column))
            account_string = ''
            for account in accounts:
                if account == accounts[-1]:
                    account_string += account
                else:
                    account_string += f'{account}, '
            c.execute(f'INSERT INTO _old ({account_string}) SELECT {account_string} FROM users')
            c.execute('DROP TABLE users')
            c.execute('ALTER TABLE _old RENAME TO users')
    db.commit()
    db.close()


def get_columns(db, table, c=None):
    if not c:
        db = sqlite3.connect(db)
        c = db.cursor()
    columns = [item[0] for item in c.execute(f'SELECT * FROM {table}').description]
    db.commit()
    db.close()
    return columns


def check_table(db, table, c=None):
    if not c:
        db = sqlite3.connect(db)
        c = db.cursor()
    try:
        c.execute(f'SELECT * FROM {table}')
        return len(c.fetchall())
    except Exception as e:
        return len(c.fetchall())
