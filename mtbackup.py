#!/usr/bin/python
# vim:encoding=utf8

"""RouterOS (Mikrotik) Backup over SSH"""

__author__ = "Jiří Zapletal"
__license__ = "MIT"

import sys
from os import path
from time import sleep
import socket

try:
        import paramiko
except ImportError:
        print "ERROR: missing paramiko module (pip install paramiko)"
        sys.exit(1)

# parse args
from optparse import OptionParser
parser = OptionParser()
parser.add_option("-c", dest="config", help="configuration file",
                  metavar="FILE", default="mtbackup.conf")
parser.add_option("-o", dest="output", help="output directory",
                  default="backups")
parser.add_option("-n", dest="keep", help="keep n recent backups", default=5,
                  type="int")
parser.add_option("-a", dest="autokey", help="accept all ssh server keys",
                  action="store_true", default=False)
parser.add_option("-s", dest="skip_backup_cmd",
                  help="skip backup command (run it via ros scheduler)",
                  action="store_true", default=False)
parser.add_option("-d", dest="debug", help="log debug info into ssh.log",
                  action="store_true", default=False)


def download_backups(hostname, port, username, password, key_fn, options):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    if options.autokey:
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print "[%s] connecting" % (hostname, )
    try:
        client.connect(hostname, port=port, username=username,
                       password=password, key_filename=key_fn,
                       allow_agent=False, look_for_keys=False)
    except paramiko.SSHException as e:
        print "[%s] ERROR: %s" % (hostname, e)
        return
    except socket.gaierror as e:
        print "[%s] ERROR: %s" % (hostname, e)
        return
    print "[%s] connected" % (hostname, )

    # run backup command
    if not options.skip_backup_cmd:
        print "[%s] running backup command" % (hostname, )
        stdin, stdout, stderr = client.exec_command('/system backup save')
        stdout.read(), stderr.read()
        # wait for completion
        sleep(5)

    # downloads all backups
    sftp = client.open_sftp()
    for fn in sftp.listdir():
        outfn = path.join(options.output, fn)
        if fn.endswith('.backup') and not path.exists(outfn):
            print "[%s] downloading backup: %s" % (hostname, fn)
            sftp.get(fn, outfn)
    sftp.close()

    # remove old backups, keep last 5
    sftp = client.open_sftp()
    lst = sftp.listdir_attr()
    # filter only *.backup
    lst = filter(lambda x: x.filename.endswith('.backup'), lst)
    # sort by create time
    lst = sorted(lst, key=lambda x: x.st_mtime, reverse=True)[options.keep:]
    for fn in lst:
        print "[%s] removing old backups: %s" % (hostname, fn.filename)
        sftp.remove(fn.filename)
    sftp.close()

    client.close()

if __name__ == "__main__":
    (options, args) = parser.parse_args()

    # enable debugging
    if options.debug:
        print "logging debugging output into ssh.log"
        paramiko.util.log_to_file('ssh.log')

    # sanity check
    if options.keep < 0:
        options.keep = 5

    # read config file
    for line in open(options.config):
        # skip comments
        if line.startswith("#"):
            continue

        line = line.strip().split()
        # skip blank lines
        if len(line) == 0:
            continue

        # unwrap and download
        (hostname, port, user, password, key_fn) = line
        if password == '-':
            password = None
        if key_fn == '-':
            key_fn = None
        download_backups(hostname, int(port), user, password, key_fn, options)

    sys.exit(0)
