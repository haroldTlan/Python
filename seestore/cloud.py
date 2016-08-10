from peewee import *
from models import User, Ipc

# db = MySQLDatabase('cloud')

data_1 = [{"useraccount": "bary",
           "devid": "66609781",
           "storage": 5120,
           "spacetype": 1,
           "ak": "666",
           "sk": "888"
           },
          {"useraccount": "Tim",
           "devid": "6660978111",
           "storage": 7,
           "spacetype": 2,
           "ak": "23",
           "sk": "900"}]


# a.list	{}
# a['list'] {}
# a[0]	[]

# 8.1

def AddData(data):
    try:
        account = User.select().where(User.Account == data['Account']).get()
    except Exception as e:
        print e
        return 1

    if account.Password == data['Password']:
        if 0 < data['SpaceType'] < 3:
            if data['StorageSpace']:
                new_dev = Ipc(**data)
                new_dev.save()

                return 0

            else:
                return 4
        else:
            return 3
    else:
        return 2


# 8.2

def LogOutData(data):
    try:
        account = User.select().where(User.Account == data['Account']).get()
    except Exception as e:
        print e
        return 1

    if account.Password == data['Password']:
        try:
            dev = Ipc.select().where((Ipc.UserAccount == data['UserAccount']) & (Ipc.DevID == data['DevID'])).get()
        except Exception as e:
            return 3

        dev.delete_instance()
        return 0
    else:
        return 2


# 8.3

def ModData(data):
    try:
        account = User.select().where(User.Account == data['Account']).get()
    except Exception as e:
        print e
        return 1

    if account.Password == data['Password']:
        if 0 < data['SpaceType'] < 3:
            if data['NewStorageSpace']:
                try:
                    dev = Ipc.select().where(
                            (Ipc.UserAccount == data['UserAccount']) & (Ipc.DevID == data['DevID'])).get()
                except Exception as e:
                    print e
                    return 5
                dev.StorageSpace = data['NewStorageSpace']
                dev.SpaceType = data['SpaceType']
                dev.save()
                return 0
            else:
                return 4
        else:
            return 3
    else:
        return 2


# 8.4

def QueryData(data):
    try:
        account = User.select().where(User.Account == data['Account']).get()
    except Exception as e:
        print e
        return 1

    if account.Password == data['Password']:
        try:
            dev = Ipc.select().where((Ipc.UserAccount == data['UserAccount']) & (Ipc.DevID == data['DevID'])).get()
        except Exception as e:
            return 3

        return 0
    else:
        return 2


def GetAKandSK(DevID):
    # dev = Ipc.select().where((Ipc.UserAccount == UserAccount) & (Ipc.DevID == DevID)).get()
    dev = Ipc.select().where(Ipc.DevID == DevID).get()
    return dev.AK, dev.SK


# 8.5

def IpcBytimeData(data):
    try:
        account = User.select().where(User.Account == data['Account']).get()
    except Exception as e:
        print e
        return 1

    if account.Password == data['Password']:
        try:
            dev = Ipc.select().where((Ipc.UserAccount == data['UserAccount']) & (Ipc.DevID == data['DevID'])).get()
        except Exception as e:
            return 3

        return 0
    else:
        return 2


def DevIDExist(devid):
    try:
        Ipc.select().where(Ipc.DevID == devid).get()
        return True
    except Exception:
        return False


def AddDataa(data):
    if True:
        for ipc in Data:
            try:
                a = Ipc(**ipc)
                a.save()
            except Exception as e:
                print e

    else:
        for user in Data:
            try:
                b = User(**user)
                b.save()
            except Exception as e:
                print e + ":" + user.DevID


def DelData(data):
    for i in data:
        cancel = Ipc.get(Ipc.devid == "%s" % i.DevID)
        try:
            cancel.delete_instance()
        except Exception as e:
            print e + ":" + i.DevID


def ModDataa(data):
    if True:
        aim = Ipc(get(Ipc.devid == data.UserAccount))
        #		aim = Ipc.select().where(Ipc.devid==data.UserAccount).get()
        #		aim = Ipc.select().join(Ipc).where((Ipc.devid==data.UserAccount)&(Ipc.sk=="666")).get()
        aim.useraccount = "sam"
        aim.save()


def QueryyData():
    for i in Ipc.select(Ipc):
        print i.UserAccount, i.DevID, i.StorageSpace, i.SpaceType
    for i in User.select(User):
        print i.Account, i.Password


if __name__ == "__main__":
    QueryyData()
