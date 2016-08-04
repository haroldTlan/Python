#!/usr/bin/env python

import sys
import os
from util import *
import db
import adm
import time

#To get the failed raids
def get_failed_raids():
    raids = []
    results = adm.Raid.all()
    for i in results:
        if i.health == 'failed':
            raids.append(i)     
    return raids

#To judge if all the disks in the raid with uuid 'raid_uuid' are plugged
#recovery_logs comes from the raid_recoveries in mysqldump
#raid_uuid is the uuid of the failed raid
def check_disk_nr(recovery_logs, raid_uuid):
    recs_about_raid = [rec for rec in recovery_logs if rec['raid_uuid'] == raid_uuid]

    disks_in_db = {}
    failed_disks = []
    disks = adm.Disk.all()
    for i in disks:
        if i.raid:
            if i.raid.uuid == raid_uuid:
                failed_disks.append(i)

    for disk in failed_disks:
        disks_in_db[disk.uuid] = disk.dev_name

    _, disks_exist_now = execute('ls /dev/sd[a-z]')
    for disk_uuid in recs_about_raid[-1]['data_disks']:
        if disks_in_db[disk_uuid] in disks_exist_now:
            continue
        else:
            return False

    return True

def unicode_str(uni):
    if isinstance(uni, list):
        return [str(i) for i in uni]
    if isinstance(uni, unicode):
        return str(uni)

#To find the latest recovery log about the raid with the raid_uuid input
def check_raid_recovery_log():  
    recs = []
    results = db.RaidRecovery().all()
#    results = adm.Raid.all()
    if results == '':
        return False
    
    for result in results:
        r_uuid = unicode_str(result.uuid)
        r_name = unicode_str(result.name)
        d_disks = unicode_str(result.raid_disks.split(','))
        s_disks = unicode_str(result.spare_disks)
        time = result.created_at.strftime("%Y-%m-%d %H:%M:%S")
        recs.append({'raid_uuid': r_uuid, 'raid_name': r_name, 'data_disks': d_disks, 'spare_disks': s_disks, 'time': time})

    return recs
#    for result in results:
#        if result.health == 'failed':
#            d_disks = [i.uuid for i in result.disks]
#            s_disks = [i.uuid for i in result.spare_disks]
#            r_uuid = result.uuid
#            r_name = result.name
#            recs.append({'raid_uuid': r_uuid, 'raid_name': r_name, 'data_disks': d_disks, 'spare_disks': s_disks})

#    return recs

#According to the raid_rec input to change information in database
def add_disk(recovery_logs, raid_uuid):
    recs_about_raid = [rec for rec in recovery_logs if rec['raid_uuid'] == raid_uuid]
    raid_rec = recs_about_raid[-1]
    
    try:
        for disk_uuid in raid_rec['data_disks']:
            disk = adm.Disk.lookup(uuid=disk_uuid)
            disk.save(health='normal', role='data', unplug_seq=0)
        rd = adm.Raid.lookup(uuid=raid_rec['raid_uuid'])
        rd.save(health='normal', unplug_seq=0)

        _, results = execute("echo 'use speediodb; flush privileges;' |mysql -uroot -ppasswd")
        return True
    except:
        return False

def touch_file():
    os.system('touch /home/zonion/boot')

if __name__ == "__main__":
    failed_raids = get_failed_raids()
    recs = check_raid_recovery_log()
    if check_disk_nr(recs, failed_raids[0].uuid):
        print 'OK! all the disk in the failed raid are plugged'
    else:
        print 'Please plug all the disk of the failed raid %s. And try again.' % failed_raids[0].name
        exit(1)

    if add_disk(recs, failed_raids[0].uuid):
        print 'Added disks success!'
    else:
        print 'Added disks failed!'
        exit(1)

    touch_file()

    for i in range(0, 10):
        print '.'
        time.sleep(1)
    execute('/sbin/reboot')

