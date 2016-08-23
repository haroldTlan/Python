# coding:utf-8
import users
import grp
import chardet
from users import run_command
import shutil
from tempfile import mkstemp
import re
import os
import samba_user

__author__ = 'bary'

TESTPARM = '/usr/bin/testparm'
SMB_CONFIG = '/etc/samba/smb.conf'
SMBSERVICE = '/etc/init.d/smb'
CHMOD = '/bin/chmod'
RS_HEADER = '####BEGIN: Rockstor SAMBA CONFIG####'


def test_parm(config='/etc/samba/smb.conf'):
    cmd = [TESTPARM, '-s', config]
    o, e, rc = run_command(cmd, throw=False)
    return True


def rockstor_smb_config(fo, exports):
    fo.write('%s\n' % RS_HEADER)
    # for au in e.admin_users.all():
    #   admin_users = '%s%s ' % (admin_users, au.username)
    for e in exports:
        fo.write('[%s]\n' % e['share'])
        fo.write('    comment = %s\n' % e['comment'])
        fo.write('    path = %s\n' % e['path'])
        fo.write('    browseable = %s\n' % e['browsable'])
        fo.write('    read only = %s\n' % e['read_only'])
        fo.write('    guest ok = %s\n' % e['guest_ok'])
        fo.write('    admin users = %s\n' % e['admin_users'])
    fo.write('####END: Rockstor SAMBA CONFIG####\n')


def refresh_smb_config(exports):
    fh, npath = mkstemp()
    with open(SMB_CONFIG) as sfo, open(npath, 'w') as tfo:
        section = False
        for line in sfo.readlines():
            if re.match(RS_HEADER, line) is not None:
                section = True
                rockstor_smb_config(tfo, exports)
                break
            else:
                tfo.write(line)
        if (section is False):
            rockstor_smb_config(tfo, exports)
    test_parm(npath)
    shutil.move(npath, SMB_CONFIG)


def update_global_config(workgroup=None, realm=None, idmap_range=None, rfc2307=False):
    fh, npath = mkstemp()
    with open(SMB_CONFIG) as sfo, open(npath, 'w') as tfo:
        tfo.write('[global]\n')
        if (workgroup is not None):
            tfo.write('    workgroup = %s\n' % workgroup)
        tfo.write('    log file = /var/log/samba/log.%m\n')
        if (realm is not None):
            idmap_high = int(idmap_range.split()[2])
            default_range = '%s - %s' % (idmap_high + 1, idmap_high + 1000000)
            tfo.write('    security = ads\n')
            tfo.write('    realm = %s\n' % realm)
            tfo.write('    template shell = /bin/sh\n')
            tfo.write('    kerberos method = secrets and keytab\n')
            tfo.write('    winbind use default domain = false\n')
            tfo.write('    winbind offline logon = true\n')
            tfo.write('    winbind enum users = yes\n')
            tfo.write('    winbind enum groups = yes\n')
            tfo.write('    idmap config * : backend = tdb\n')
            tfo.write('    idmap config * : range = %s\n' % default_range)
            # enable rfc2307 schema and collect UIDS from AD DC
            # we assume if rfc2307 then winbind nss info too - collects AD DC home and shell for each user
            if (rfc2307):
                tfo.write('    idmap config %s : backend = ad\n' % workgroup)
                tfo.write('    idmap config %s : range = %s\n' % (workgroup, idmap_range))
                tfo.write('    idmap config %s : schema_mode = rfc2307\n' % workgroup)
                tfo.write('    winbind nss info = rfc2307\n')
            else:
                tfo.write('    idmap config %s : backend = rid\n' % workgroup)
                tfo.write('    idmap config %s : range = %s\n' % (workgroup, idmap_range))
        # @todo: remove log level once AD integration is working well for users.
        tfo.write('    log level = 3\n')
        tfo.write('    load printers = no\n')
        tfo.write('    cups options = raw\n')
        tfo.write('    printcap name = /dev/null\n\n')

        rockstor_section = False
        for line in sfo.readlines():
            if (re.match(RS_HEADER, line) is not None):
                rockstor_section = True
            if (rockstor_section is True):
                tfo.write(line)
    test_parm(npath)
    shutil.move(npath, SMB_CONFIG)


def restart_samba():
    """
    call whenever config is updated
    """
    return run_command([SMBSERVICE, 'restart'])


def start_samba():
    return run_command([SMBSERVICE, 'start'])


# {'comment' : 'haha', 'share' : "test",'path' : "/tmp", "browsable":"yes", 'read_only':'no',
# "guest_ok":"yes","admin_users":"n411","shadow_copy":"false"}
def createshare(share, path, comment="", browsable="yes", read_only="no", guset_ok="yes", admin_users=""):
    samba_user.db.connect()
    config = samba_user.SambaConfig.create(share=share, path=path, comment=comment, browsable=browsable, \
                                           read_only=read_only, guest_ok=guset_ok, admin_users=admin_users)
    config.save()
    samba_user.db.close()
    refresh_smb_config(get_all_config())
    restart_samba()
    return True


def refresh():
    samba_user.db.connect()
    for con in samba_user.SambaConfig.select():
        export = {'comment': con.comment, 'share': con.share, 'path': con.path, 'browsable': con.browsable, \
                  'read_only': con.read_only, "guest_ok": con.guest_ok, 'admin_users': con.admin_users, \
                  'shadow_copy': con.shadow_copy}
        refresh_smb_config(export)
    samba_user.db.close()
    return True


def get_all_config():
    all_config = []
    samba_user.db.connect()
    for con in samba_user.SambaConfig.select():
        export = {'comment': con.comment, 'share': con.share, 'path': con.path, 'browsable': con.browsable, \
                  'read_only': con.read_only, "guest_ok": con.guest_ok, 'admin_users': con.admin_users, \
                  'shadow_copy': con.shadow_copy}
        all_config.append(export)
    samba_user.db.close()
    return all_config


# print get_all_config()
# print refresh_smb_config(get_all_config())
