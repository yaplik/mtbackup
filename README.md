RouterOS (Mikrotik) Backup over SSH
===================================

This utility connects to RouterOS via SSH, creates new backup and downloads it.
It also removes old backups while keeping 5 recent ones.

Usage
-----

Create `mt_backup.conf` like this:

    # hostname             port  user   passwd     key_fn
    myrouter1.domain.com   22    admin  Password.  -
    myrouter2.domain.com   22    admin  -          sshkey

where `sshkey` is filename with dsa key. DSA key can be generated:

    ssh-keygen -t dsa -f sshkey

and then copied and imported into router:

    scp sshkey.pub myrouter1.domain.com:
    ssh myrouter1.domain.com
    > /user ssh-keys import user=admin public-key-file=sshkey.pub

Run

    $ ./mtbackup.py -c mtbackup.conf
    [myrouter1.domain.com] connecting
    [myrouter1.domain.com] connected
    [myrouter1.domain.com] running backup command
    [myrouter1.domain.com] downloading backup: myrouter1.domain.com-xxxxxxxx-xxxx.backup
    [myrouter1.domain.com] removing old backups: myrouter1.domain.com-xxxxxxxx-xxxx.backup

Backups are downloaded into `backups/`

    $ ls backups/
    myrouter1.domain.com-xxxxxxxx-xxxx.backup

Arguments
---------

    $ ./mtbackup.py -h
    Usage: mtbackup.py [options]
    
    Options:
      -h, --help  show this help message and exit
      -c FILE     configuration file
      -o OUTPUT   output directory
      -n KEEP     keep n recent backups
      -a          accept all ssh server keys
      -s          skip backup command (run it via ros scheduler)
      -d          log debug info into ssh.log
