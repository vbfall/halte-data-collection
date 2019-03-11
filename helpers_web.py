import numpy
import sqlite3
import os
from datetime import date


def query_db(db_name, command_string):
    """Receives a db name, opens it with sqlite, executes a query on it as per command_string and returns results in format of lists - caller must know how many lists will be returned"""
    #Actually just found out it only works with two lists - look at it later
    db = sqlite3.connect(db_name)
    cur = db.cursor()
    cur.execute(command_string)
    results = cur.fetchall()
    if len(results) > 0:
        results = zip(*results)
    db.close()
    return results


def insert_into_db(db_name, table_name, row):
    """Receives a db and table name and a row dict, and inserts row into table"""
    # Sample row:
    # row = {'name':'\"THREEPWOOD, G\"', 'nationality':'\"LUC\"', 'fencing_since':'1992', 'fav_weapon':'\"rapier\"', 'birth_year':'1972'}
    # note escaped quotes for string fields and integer fields as simple strings
    db = sqlite3.connect(db_name)
    cur = db.cursor()
    # construct query
    fields = ','.join(list(row.keys()))
    values = ','.join(list(row.values()))
    query = 'INSERT INTO ' + table_name + ' (' + fields + ') VALUES (' + values + ')'
    # Send query to db
    cur.execute(query)
    db.commit()
    db.close()
    return 0


def list_to_inverse_prob(l):
    """Receives a list of positive values and returns a normalized numpy array with probabilities inverse to the lists values"""
    a = numpy.array(l)
    a = 1 / a
    total = a.sum()
    a = a / total
    return a


def get_image_path(index):
    """Receives a file number without extension and returns the full path to it"""
    path_to_images = '/static/image_data/'
    file_list = os.listdir('.'+path_to_images)
    path = path_to_images + file_list[index]
    return path


def get_form_optional_value(request, field_name):
    """Returns value of a form field from html, or '' if field empty"""
    try: result = request.form[field_name]
    except: result = ''
    return result


def get_user_info(request):
    """Retrieves user information from html form fields"""
    user_info = dict()

    # this one is necessary
    try: user_info['fencing_since'] = int(request.form['fencing_since'])
    except: user_info['fencing_since'] = int(date.today().year) - 2 # if no year given, assumes user has at least 2 years experience

    # all others are optional
    try:
        user_info['name'] = request.form['user_name'].upper()
        user_info['name'] = user_info['name'].replace('.','').replace(',','')\
                            .replace('SELECT ','').replace('TABLE ','').replace('INTO ','')\
                            .replace('\"','').strip()
    except: pass

    try:
        user_info['nationality'] = request.form['nationality'].upper()
        user_info['nationality'] = user_info['nationality'].replace('.','').replace(',','')\
                                    .replace('SELECT ','').replace('TABLE ','').replace('INTO ','')\
                                    .replace('\"','').strip()
    except: pass

    try: user_info['fav_weapon'] = request.form['favored_weapon']
    except: pass

    try: user_info['birth_year'] = int(request.form['yob'])
    except: pass

    return user_info
# end of get_user_info


def insert_user(request):
    """Inserts user into db if not there yet and returns user_id"""
    # (Save user to db if necessary and) retrieve user_id
    user_info = get_user_info(request)

    ids = []
    # assign anonymous user name if user name not provided
    if len(user_info['name']) == 0:
        user_count, name_count = query_db('halte.db','SELECT COUNT(*), COUNT(DISTINCT name) FROM users')
        user_info['name'] = 'anonymous_'+str(user_count[0]+1).zfill(6)

    user_id = 0
    while user_id==0:
        try: ids, names = query_db('halte.db','SELECT user_id, name FROM users WHERE name = \"' + user_info['name'] + '\" ORDER BY user_id')
        except: pass

        if len(ids) > 0:
            # Fetch user_id (gets latest user in list)
            user_id = ids[-1]
        else:
            # prepare row to save user into db
            row = dict()
            for key, value in user_info.items():
                if type(value) == int:
                    row[key] = str(value)
                else:
                    row[key] = '\"'+value+'\"'

            # Save user to db
            _ = insert_into_db('halte.db','users',row)

    return user_id
# end of insert_user
