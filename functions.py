import sqlite3 as sl
import json
import os
import shutil
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
import random
from config import config


def createDataFolder():
    data = 'data/'
    if not os.path.exists(data):
        os.makedirs(data)
    return True    

def createRecordDB():
    data = 'data'
    # if not os.path.exists(data):
    #     os.makedirs(data)

    con = sl.connect(data + '/cmdi_records.db')
    cur = con.cursor()   
    cur.execute("""
            CREATE TABLE IF NOT EXISTS cmdi (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                uuid TEXT,
                profile TEXT,
                created TEXT,
                modified TEXT
            );
        """) 
    con.commit()
    cur.close()
    con.close()    


def get_now():
    now = datetime.now(tz=ZoneInfo("Europe/Amsterdam"))
    return now.strftime("%Y-%m-%d %H:%M:%S")

def newRecord(profile):
    name = createFileName();
    now = get_now();
    insertRecord(profile, name, now)
    return {"status": "OK", "profile": profile, "filename": name}

def deleteRecord(fn):
    con = sl.connect(config['DB_DIR'] + config['DB_NAME'])
    cur = con.cursor()
    sql = "DELETE FROM cmdi WHERE filename = '" + fn + "'"
    cur.execute(sql)
    con.commit()
    status = {"status": "OK"}
    cur.close()
    con.close()
    remove_file(fn);
    return status

def remove_file(name):
    file_path = config["DATA_DIR"] + name[0] + "/" + name
    if os.path.isfile(file_path):
        os.remove(file_path)

def insertRecord(profile, file, now):
    con = sl.connect(config['DB_DIR'] + config['DB_NAME'])
    cur = con.cursor()

    sql = "INSERT INTO cmdi (filename, profile, created, modified) values(?, ?, ?, ?)"
    value = (file, profile, now, now)

    cur.execute(sql, value)
    con.commit()
    cur.close()
    con.close()

def createFileName():
    file_exists = True
    while file_exists:
        name = rand_x_digit_num(5).__str__()
        dir = name[0]
        file = name + '.xml'
        path = config["DATA_DIR"] + dir + "/" + file
        if not os.path.exists(path):
            file_exists = False
        # open(path, 'a').close()
    return file

def rand_x_digit_num(x, leading_zeroes=True):
    if not leading_zeroes:
        return random.randint(10**(x-1), 10**x-1)
    else:
        return '{0:0{x}d}'.format(random.randint(0, 10**x-1), x=x)

def getRecordDB():
    con = sl.connect(config['DB_DIR'] + config['DB_NAME'])
    cur = con.cursor()   
    sql = "SELECT * FROM cmdi"
    cur.execute(sql)
    names = list(map(lambda x: x[0], cur.description)) # ergens opgezocht
    #print('names', names)
    result = cur.fetchall()

    cur.close()
    con.close()

    #print('result', result)
    struct = []
    for x in result:
        # print('x', x[1])
        # id = x[1]
        # structure.append({'uuid': id})
        row = {}
        # namen in het resultaat plakken y is een rangnummer in de namenlijst
        for y in range(0, len(names)):
            key = names[y]
            value = x[y]
            row[key] = value
            # s.append({key: value})
            
        struct.append(row)
    #print('struct', struct)
    return struct

def save_cmdi(xml_content, filename):
    dir = filename[0]
    path = config["DATA_DIR"] + dir + "/" + filename
    f = open(path, "w")
    f.write(xml_content)
    f.close()


def get_json_data(filename):
    error_msg = {"status": "error"}
    profile = get_profile(filename)
    if profile == None:
        return error_msg
    dir = filename[0]
    path = config["DATA_DIR"] + dir + "/" + filename
    if not os.path.exists(path):
        url = config["CMDI_API"] + "get_json/" + profile
        req = requests.get(url)
        return req.json()
    return {"profile": profile}

def get_profile(filename):
    ret_val = None
    con = sl.connect(config['DB_DIR'] + config['DB_NAME'])
    cur = con.cursor()
    sql = "SELECT profile FROM cmdi WHERE filename = ?"
    values = [filename]
    cur.execute(sql, values)
    result = cur.fetchone()
    if result != None:
        ret_val = result[0]
    cur.close()
    con.close()
    return ret_val
