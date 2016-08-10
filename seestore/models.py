from peewee import *

db = MySQLDatabase('cloud', autocommit=True, user='root',
                   passwd='passwd', threadlocals=True, connect_timeout=30)

db.register_fields({'primary_key': 'INTEGER AUTOINCREMENT'})


class MySQLModel(Model):
    class Meta:
        database = db


class User(MySQLModel):
    uid = IntegerField(primary_key=True)
    Account = CharField()
    Password = CharField()


class Ipc(MySQLModel):
    uid = IntegerField(primary_key=True)
    UserAccount = CharField()
    DevID = CharField()
    StorageSpace = DateField()
    SpaceType = DateField()
    AK = CharField()
    SK = CharField()
    URL = CharField()


if __name__ == "__main__":
    db.connect()
    db.create_tables([User, Ipc])
    db.close()
