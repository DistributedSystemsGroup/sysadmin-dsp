#!/usr/bin/python

import MySQLdb
import sys

import logging

# attach to our global logger
logger = logging.getLogger("novadns")

# lets talk to the powerdns database...
class pdnsDatabase:
   def __init__(self, config):
      self.config = config
      self.connection = None
      self.reconnectTries = 2

      self.forwardName = self.config.get('DNSZONE', 'forwardzone')
      self.reverseName = self.config.get('DNSZONE', 'reversezone')
      self.dbHost = self.config.get('MYSQL', 'mysqlhost')
      self.dbUser = self.config.get('MYSQL', 'mysqluser')
      self.dbPass = self.config.get('MYSQL', 'mysqlpass')
      self.dbName = self.config.get('MYSQL', 'mysqldatabase')

      logger.info("ZONES: forward: %s reverse: %s" % (self.forwardName, self.reverseName))
      logger.info("DB: host: %s user: %s db: %s" % (self.dbHost, self.dbUser, self.dbName))

      # try to connect to mysql to check credentials
      self.get_cursor()

      self.forwardID = self.getDomainID(self.forwardName)
      self.reverseID = self.getDomainID(self.reverseName)

   def get_cursor(self):
      # close down an existing connection
      if not self.connection is None:
         try:
            cursor = self.connection.cursor()
            cursor.execute("DO 1;")
         except:
            self.connection.close()
            self.connection = None
         else:
            return cursor

      # and now make a new connection
      try:
         self.connection = MySQLdb.connect(self.dbHost, self.dbUser, self.dbPass, self.dbName);
         self.connection.autocommit(True)
      except MySQLdb.Error, e:
         logger.info("MySQL error: %s" % (str(e)))
         sys.exit()
      return self.connection.cursor()

   def getDomainID(self, domain):
      cursor = self.get_cursor()
      cursor.execute("SELECT id FROM domains WHERE name=%s", (domain))

      rows = cursor.fetchall()
      return(rows[0][0])

   def putRecord(self, name, content, type, domainID, instance):
         cursor = self.get_cursor()

         cursor.execute("SELECT count(*) from records where domain_id=%s and name=%s", (domainID, name))
         row = cursor.fetchone()
         if row[0] > 0:
            sql = "UPDATE records set content = %s, instance=%s, change_date=UNIX_TIMESTAMP() where domain_id=%s and name=%s;"
            cursor.execute(sql, (content, domainID, name, instance))
         else:
            sql = "INSERT INTO records (domain_id,name,content,type,ttl,prio,change_date,instance,auth) VALUES (%s,%s,%s,%s,120,NULL,UNIX_TIMESTAMP(),%s,1);"
            cursor.execute(sql, (domainID, name, content, type, instance))

   def parsePTR(self, ip):
      fields = ip.split('.')
      fields.reverse()
      ptr = ".".join(fields) + '.in-addr.arpa'
      return(ptr)

   def update(self, hostname, ip, instance):
      name = ''
      ptr = self.parsePTR(ip)

      try:
         if hostname.endswith(self.forwardName):
            name = hostname
         else:
            name = hostname + '.' + self.forwardName
      except:
         name = hostname + '.' + self.forwardName

      logger.info("DNS Change: %s %s" % (name, ip))
      try:
         if self.forwardID != None:
            self.putRecord(name, ip, 'A', self.forwardID, instance)
         if self.reverseID != None:
            self.putRecord(ptr, name, 'PTR', self.reverseID, instance)
      except MySQLdb.Error, e:
         logger.info("MySQL Error %d: %s" % (e.args[0], e.args[1]))


   def remove(self, instance):
      sql = "DELETE from records where instance=%s;"
      cursor = self.get_cursor()
      cursor.execute(sql, (instance))

