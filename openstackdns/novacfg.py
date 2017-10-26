#!/usr/bin/python

from configobj import ConfigObj


class novaConfig:
   def __init__(self, configFile=''):
      self.configFile = '/opt/openstack/dns.conf'
      if configFile:
         self.configFile = configFile 

      print("Loading config from %s" % self.configFile)
      self.config = ConfigObj(self.configFile)

   def get(self, key, value):
      if self.config[key][value]:
         return(self.config[key][value])
