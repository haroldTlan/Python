# coding:utf-8
import re
import os
import subprocess
import shutil
from tempfile import mkstemp
import time
from socket import inet_ntoa
from struct import pack
import hashlib
import logging
import chardet
import pwd
import grp
from shutil import move
from tempfile import mkstemp
import fcntl

HOSTS_FILE = '/etc/hosts'
MKDIR = '/bin/mkdir'
RMDIR = '/bin/rmdir'
CHMOD = '/bin/chmod'
MOUNT = '/bin/mount'
UMOUNT = '/bin/umount'
EXPORTFS = '/usr/sbin/exportfs'
RESTART = '/sbin/restart'
SERVICE = '/sbin/service'
HOSTID = '/usr/bin/hostid'
DEFAULT_MNT_DIR = '/mnt2/'
SHUTDOWN = '/usr/sbin/shutdown'
GRUBBY = '/usr/sbin/grubby'
CAT = '/usr/bin/cat'
UDEVADM = '/usr/sbin/udevadm'
GREP = '/usr/bin/grep'
NMCLI = '/usr/bin/nmcli'
HOSTNAMECTL = '/usr/bin/hostnamectl'
LSBLK = '/usr/bin/lsblk'
HDPARM = '/usr/sbin/hdparm'
SYSTEMCTL_BIN = '/usr/bin/systemctl'
USERADD = '/usr/sbin/useradd'
GROUPADD = '/usr/sbin/groupadd'
USERDEL = '/usr/sbin/userdel'
GROUPDEL = '/usr/sbin/groupdel'
PASSWD = '/usr/bin/passwd'
USERMOD = '/usr/sbin/usermod'
SMBPASSWD = '/usr/bin/smbpasswd'
CHOWN = '/usr/bin/chown'

__author__ = 'bary'


class CommandException(Exception):
    def __init__(self, cmd, out, err, rc):
        self.cmd = cmd
        self.out = out
        self.err = err
        self.rc = rc

    def __str__(self):
        return ('Error running a command. cmd = %s. rc = %d. stdout = %s. '
                'stderr = %s' % (self.cmd, self.rc, self.out, self.err))


def run_command(cmd, shell=False, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, stdin=subprocess.PIPE, throw=True,
                log=False, input=None):
    try:
        cmd = map(str, cmd)
        p = subprocess.Popen(cmd, shell=shell, stdout=stdout, stderr=stderr,
                             stdin=stdin)
        out, err = p.communicate(input=input)
        out = out.split('\n')
        err = err.split('\n')
        rc = p.returncode
    except Exception, e:
        msg = ('Exception while running command(%s): %s' % (cmd, e.__str__()))
        raise Exception(msg)

    if rc != 0:
        if log:
            e_msg = ('non-zero code(%d) returned by command: %s. output: %s error:'
                     ' %s' % (rc, cmd, out, err))
            # todo add logger
            # logger.error(e_msg)
        if throw:
            raise CommandException(cmd, out, err, rc)
    return (out, err, rc)


def get_users(max_wait=90):
    t0 = time.time()
    users = {}
    p = subprocess.Popen(['/usr/bin/getent', 'passwd'], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    fcntl.fcntl(p.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)
    alive = True
    user_data = ''
    while alive:
        try:
            if p.poll() is not None:
                alive = False
            user_data += p.stdout.read()
        except IOError:
            if time.time() - t0 < max_wait:
                continue
        except Exception, e:
            # todo add logger
            # logger.exception(e)
            p.terminate()
        uf = user_data.split('\n')
        # If the feed ends in \n, the last element will be '', if not, it will
        # be a partial line to be processed next time around.
        user_data = uf[-1]
        for u in uf[:-1]:
            ufields = u.split(':')
            if len(ufields) > 3:
                charset = chardet.detect(ufields[0])
                uname = ufields[0].decode(charset['encoding'])
                users[uname] = (int(ufields[2]), int(ufields[3]))
            if time.time() - t0 > max_wait:
                p.terminate()
                break
    return users


def get_groups(*gids):
    groups = {}
    if len(gids) > 0:
        for g in gids:
            entry = grp.getgrgid(g)
            charset = chardet.detect(entry.gr_name)
            # #why decoding?
            gr_name = entry.gr_name.decode(charset['encoding'])
            groups[gr_name] = entry.gr_gid
    else:
        for g in grp.getgrall():
            charset = chardet.detect(g.gr_name)
            gr_name = g.gr_name.decode(charset['encoding'])
            groups[gr_name] = g.gr_gid
    return groups


def userdel(uname):
    try:
        pwd.getpwnam(uname)
    except KeyError:
        # user doesn't exist
        return

    return run_command([USERDEL, '-r', uname])


def groupdel(groupname):
    try:
        return run_command([GROUPDEL, groupname])
    except CommandException, e:
        if e.rc != 6:
            raise e


def get_epasswd(username):
    with open('/etc/shadow') as sfo:
        for l in sfo.readlines():
            fields = l.split(':')
            if re.match(fields[0], username) is not None:
                return fields[1]
    return None


def usermod(username, passwd):
    cmd = [PASSWD, '--stdin', username]
    p = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    out, err = p.communicate(input=passwd)
    rc = p.returncode
    if rc != 0:
        raise CommandException(cmd, out, err, rc)
    return (out, err, rc)


def smbpasswd(username, passwd):
    cmd = [SMBPASSWD, '-s', '-a', username]
    p = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    pstr = ('%s\n%s\n' % (passwd, passwd))
    out, err = p.communicate(input=pstr)
    rc = p.returncode
    if rc != 0:
        raise CommandException(cmd, out, err, rc)
    return (out, err, rc)


def update_shell(username, shell):
    return run_command([USERMOD, '-s', shell, username])


def useradd(username, shell, uid=None, gid=None):
    pw_entry = None
    try:
        pw_entry = pwd.getpwnam(username)
    except:
        pass
    if pw_entry is not None:
        if (uid is not None and
                    uid != pw_entry.pw_uid):
            raise Exception('User(%s) already exists, but her uid(%d) is different from the input(%d).' % (
                username, pw_entry.pw_uid, uid))
        if (gid is not None and
                    gid != pw_entry.pw_gid):
            raise Exception('User(%s) already exists, but her gid(%d) is different from the input(%d).' % (
                username, pw_entry.pw_gid, gid))
        if (shell != pw_entry.pw_shell):
            raise Exception('User(%s) already exists, but her shell(%s) is different from the input(%s).' % (
                username, pw_entry.shell, shell))
        return ([''], [''], 0)

    cmd = [USERADD, '-s', shell, '-m', username]
    if (uid is not None):
        cmd.insert(-1, '-u')
        cmd.insert(-1, str(uid))
    if (gid is not None):
        cmd.insert(-1, '-g')
        cmd.insert(-1, str(gid))
    return run_command(cmd)


def groupadd(groupname, gid=None):
    cmd = ([GROUPADD, groupname])
    if (gid is not None):
        cmd.insert(-1, '-g')
        cmd.insert(-1, gid)
    return run_command(cmd)


def getusersname():
    return get_users().keys()

if __name__ == '__main__':
    print get_groups(0)
    import speedweb
    print speedweb.__all__
