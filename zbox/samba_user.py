# coding:utf-8
#!/usr/bin/env python
from env import config
import log
import error
from peewee import *
import threading
from caused import *

__author__ = 'bary'

db = MySQLDatabase('samba_user', autocommit=True, user='root',\
        passwd=config.database.passwd, threadlocals=True, connect_timeout=30)

_local = threading.local()

def local():
    if not hasattr(_local, 'connect_nr'):
        _local.connect_nr = 0
        _local.transaction_nr = 0
        _local.transaction_end = ''
    return _local

inited = False

def begin():
    if local().transaction_nr == 0:
        local().transaction_end = ''
        db.set_autocommit(False)
        db.begin()
    local().transaction_nr += 1

def commit():
    local().transaction_nr -= 1
    if local().transaction_nr == 0:
        db.set_autocommit(True)
        if local().transaction_end == 'rollback':
            log.info('transaction end, nested rollback, so give up commit.')
            db.rollback()
        else:
            db.commit()
    elif local().transaction_nr < 0:
        db.set_autocommit(True)
        raise error.DB.TransactionUnmatch()

def rollback():
    local().transaction_end = 'rollback'
    local().transaction_nr -= 1
    if local().transaction_nr == 0:
        db.set_autocommit(True)
        db.rollback()
    elif local().transaction_nr < 0:
        db.set_autocommit(True)
        raise error.DB.TransactionUnmatch()

def connect():
    if local().connect_nr == 0:
        db.connect()
    local().connect_nr += 1

def close():
    local().connect_nr -= 1
    if local().connect_nr == 0:
        db.close()
    elif local().connect_nr < 0:
        raise error.DB.ConnectionUnmatch()

class transaction(object):
    def __enter__(self):
        connect()
        begin()

    def __exit__(self, type, value, traceback):
        if not traceback:
            commit()
        else:
            rollback()
        close()


def with_transaction(func):
    def _with_transaction(*vargs, **kv):
        try:
            connect()
            begin()
            ret = func(*vargs, **kv)
        except Exception as e:
            rollback()
            raise caused(e)
        else:
            commit()
        finally:
            close()
        return ret
    return _with_transaction

def with_db(func):
    def _with_db(*vargs, **kv):
        connect()
        try:
            s = func(*vargs, **kv)
        except Exception as e:
            raise caused(e)
        finally:
            close()
        return s
    return _with_db


class Group(Model):
    groupname = CharField(primary_key=True)
    groupid = IntegerField()
    class Meta:
        # get a error when using 'group' as table name
        db_table = 'groups'
        database = db


class User(Model):
    username = CharField(primary_key=True)
    uid = IntegerField()
    gid = IntegerField()
    group = ForeignKeyField(Group, related_name='group', null=True, db_column='group')
    shell = CharField(default='/sbin/nologin')
    comment = CharField()

    @classmethod
    def exists(cls, expr):
        return cls.select().where(expr).exists()

    class Meta:
        db_table = 'users'
        database = db

# {'comment' : 'haha', 'share' : "test",'path' : "/tmp", "browsable":"yes", 'read_only':'no',
# "guest_ok":"yes","admin_users":"n411","shadow_copy":"false"}

class SambaConfig(Model):
    comment = CharField(default="")
    share = CharField(primary_key=True)
    path = CharField()
    browsable = CharField(default="yes")
    read_only = CharField(default="no")
    guest_ok = CharField(default="yes")
    admin_users = CharField(default="")
    shadow_copy = CharField(default="false")

    class Meta:
        db_table = 'sambaconfigs'
        database = db

#db.connect()
#db.create_table(SambaConfig)
#db.close()
#config = SambaConfig.get(SambaConfig.share == "test")
#print config.comment
#for con in SambaConfig.select():
#    print config.comment, config.path, config.share
















#db.connect()
#db.drop_table(Group)
#print db.create_table(Group)
#group = Group(groupname='root', groupid=0)
#print group.save()
#group = Group.get(Group.groupname == 'root')
#group = Group.create(groupname='root', groupid=0)
#print group.save()
#print group.groupid
#print group.select()
#print group.get_id()













































































