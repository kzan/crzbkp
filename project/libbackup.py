#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import json
import os
import shutil
import tarfile

class BackupModel:
  def __init__(self,backup_time,config_file='/var/kzan.backup/config_backup.json',base_path='/var/kzan.backup'):
    self.cfile=config_file
    self.loglavel=1 #May be this statement set in init param?
    self.backup_time=backup_time
    self.LOGFILE=(open('kzanbackup.log','a'),sys.stdout)[self.loglavel] #This var must read from config file. If no in file, then write to stdout
    self.bt_path = base_path + '/' + backup_time + '/'
    self.arch_name = self.bt_path[:-1] + ".tar.gz"
    self.saved_day = 5; self.saved_day -= 1; self.saved_day *= 3600*24 #Correct date and Convert seconds to day
    self.know_methods = {'file':self.backup_file,
                         'mysql':self.backup_mysql}

    with open(self.cfile) as self.fd:
      try:
        self.config = json.loads(self.fd.read())
      except Exception, e:
        print >> self.LOGFILE,"BackupError#1: Wrong format json config file: "

  def __iter__(self):
    self.value = self.cgen()
    return self
  def next(self):
    return self.value.next()
  def cgen(self):
    for itm in self.config:
      yield {itm:self.config[itm]}

  def lets_backup_it(self,param):
    return self.know_methods.get(param.values()[0]['type'],self.wrong_param)(param.values()[0],param.keys()[0])

  def wrong_param(self,p0,p1):
    print >> self.LOGFILE,"Unknow statement."

  def mk_data_dir(self):
    try:
      os.mkdir(self.bt_path)
      return 0
    except:
      return 1

  def backup_file(self,bconfig=None,item=None):
    if os.path.isdir(bconfig['path']):
      print >> self.LOGFILE,'Copy is directory ' + self.bt_path + item + '/' + bconfig['path'].split('/')[-1]
      try:
        shutil.copytree(bconfig['path'],self.bt_path + item + '/' + bconfig['path'].split('/')[-1])
      except OSError as e:
        print >> self.LOGFILE,"OS(dst:{2}) error({0}): {1}".format(e.errno, e.strerror,bt_path+item)
      except:
        print >> self.LOGFILE,"Unexpected error:", sys.exc_info()[0]
    else:
        print >> self.LOGFILE,'Copy file. It`s jast a test function. No file is copy in fact'
    #print "{0}  {1}".format(bconfig,item)
    return 'Function to backup GIT'

  def backup_mysql(self,bconfig=None,item=None):
    print >> self.LOGFILE,"Backup MySQL database " + ' '.join(db for db in bconfig['db'])
    os.system("mysqldump -u root -p11 -B " + ' '.join(db for db in bconfig['db']) + " > " + self.bt_path + "/db.sql")
    #print "{0}  {1}".format(bconfig,item)
    return 'Function to backup MySQL'

  def backup_pg(self,bconfig=None,item=None):
    """Backup Postgresql database. pg_dump имя_БД | gzip > имя_файла.gz"""
    print >> self.LOGFILE,"Backup pgSQL database " + ' '.join(db for db in bconfig['pgdb'])
	#os.system("pg_dump -U dtest -Ppgpass " + ' '.join(db for db in bconfig['db']) + " > " + self.bt_path + "/db.sql")
    return 'Function to backup pgSQL'

  def pls_arch_backup(self):
    #arch_name = self.bt_path[:-1] + ".tar.gz"
    print >> self.LOGFILE, "Create archive " + self.arch_name
    tar = tarfile.open(self.arch_name, "w:gz")
    tar.add(self.bt_path)
    tar.close()
    shutil.rmtree(self.bt_path[:-1])

    return 1

  def pls_clean_old_files(self):
    base_list = os.listdir('/'.join(n for n in self.bt_path.split('/')[:-2]))
    for fname in base_list:
      if fname[-7:] == ".tar.gz":
        print >> self.LOGFILE, fname[:-7]
        if time.mktime(time.strptime(self.backup_time,'%Y.%m.%d_%H:%M')) - time.mktime(time.strptime(fname[:-7],'%Y.%m.%d_%H:%M')) > self.saved_day:
          print >> self.LOGFILE,'Remove arch -' + fname[:-7]
          os.remove('/'.join(n for n in self.bt_path.split('/')[:-2]) + '/' + fname)

    return 1


if __name__ == ‘__main__’:
    import time
    md = BackupModel(time.strftime('%Y.%m.%d_%H:%M',time.localtime()))

    if md.mk_data_dir() == 1:
        print "Problem with create directory"

    for n in md: md.lets_backup_it(n)

    md.pls_arch_backup()
    md.pls_clean_old_files()
