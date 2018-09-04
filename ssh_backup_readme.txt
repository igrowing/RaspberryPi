Pull method (run on Server, must have root open to SSH on Raspi):
time rsync -aEv --delete --exclude-from=exclude_backup.txt root@yourpi.ip:/ /share/distr/backup/yourpi.ip/ > /share/distr/backup/yourpi.ip.rsync.log                    

Push method (run on Raspi):
cp /boot/config.txt ~/boot_config.txt
time sudo rsync -aEv --delete --exclude-from=exclude_backup.txt / admin@yourserver.ip:/share/distr/backup/`hostname`/ > /tmp/rsync.log