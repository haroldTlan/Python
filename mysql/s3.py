#!/usr/bin/env python
import MySQLdb

def main():
    try:
    	conn = MySQLdb.connect(
    	    host = 'localhost',
    	    port = 3306,
    	    user = 'root',
    	    passwd = 'passwd',
    	    db = 'cloud')

    	cur = conn.cursor()
        cur.execute("create table ipc( uid int(10) NOT NULL PRIMARY KEY AUTO_INCREMENT, UserAccount varchar(64) NULL, DevID varchar(64) NULL, StorageSpace int(10) NULL, SpaceType int(10) NULL, AK varchar(64) NULL, SK varchar(64) NULL, URL varchar(64) NULL);")

        cur.execute("create table user( uid int(10) NOT NULL PRIMARY KEY AUTO_INCREMENT, Account varchar(64) NULL, Password varchar(64) NULL);")
	cur.close()
    	conn.commit()
    	conn.close
    except Exception as e:
    	print e
if __name__ == "__main__":
    main()





