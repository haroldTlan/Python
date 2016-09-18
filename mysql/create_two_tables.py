#!/usr/bin/env python
import MySQLdb

def main():
    try:
    	conn = MySQLdb.connect(
    	    host = 'localhost',
    	    port = 3306,
    	    user = 'root',
    	    passwd = 'passwd',
    	    db = 'speediodb')

    	cur = conn.cursor()
    	cur.execute("create table disk( Uid  INT(10) AUTO_INCREMENT, Uuid  VARCHAR(64), Location  VARCHAR(64), MachineId  VARCHAR(64), Created DATETIME DEFAULT NULL, Status VARCHAR(64), Role VARCHAR(64), Raid VARCHAR(64), Size	VARCHAR(64), RawReadErrorRate VARCHAR(4), SpinUpTime VARCHAR(4), StartStopCount VARCHAR(4), ReallocatedSectorCt VARCHAR(4), SeekErrorRate VARCHAR(4), PowerOnHours VARCHAR(4), SpinRetryCount VARCHAR(4), PowerCycleCount VARCHAR(4), PowerOffRetractCount VARCHAR(4), LoadCycleCount VARCHAR(4), CurrentPendingSector VARCHAR(4), OfflineUncorrectable VARCHAR(4), UDMACRCErrorCount VARCHAR(4), PRIMARY KEY (`uid`))")
    	cur.execute("create table machine(Uid  INT(10) AUTO_INCREMENT, Uuid  VARCHAR(64), Ip  VARCHAR(64),Slotnr int(10), Created DATETIME DEFAULT NULL, PRIMARY KEY (`uid`))")
	    cur.close()
    	conn.commit()
    	conn.close
    except Exception as e:
    	print e
if __name__ == "__main__":
    main()





