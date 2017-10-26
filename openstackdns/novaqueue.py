import sys
import os
import pika
import json
import logging
import cPickle

# attach to our global logger
logger = logging.getLogger("novadns")

def load_cache(file):
   if os.path.exists(file):
      return cPickle.load(open(file, "r"))
   else:
      return {}

def write_cache(file, cache):
   cPickle.dump(cache, open(file, "w"), -1)

class novaQueue:
   def __init__(self, config, pdns):
      self.config = config
      self.pdns = pdns

      self.broker = "amqp://" + self.config.get('AMQP', 'amqpuser')
      self.broker += ":" + self.config.get("AMQP", "amqppass")
      self.broker += "@" + self.config.get('AMQP', 'amqphost') 
      self.broker += ':' + self.config.get('AMQP', 'amqpport') + "/%2F"

      self.broker = pika.URLParameters(self.broker)
      self.connection = pika.BlockingConnection(self.broker)
      self.channel = self.connection.channel()
      self.channel.queue_declare("notifications.info")
      self.channel.basic_consume(self.get, queue="notifications.info", no_ack=True)
      self.channel.start_consuming()

   def get(self, ch, method, properties, body):
      message = json.loads(body)
      try:
         assert 'oslo.message' in message
         message = json.loads(message['oslo.message'])
         # pull out the messages that we care about 
         if message['event_type']:
            if message['event_type'] == 'compute.instance.create.end':
               instance = message['payload']
               name = instance['hostname']
#               tenant = message['_context_project_name']
#               name = name + "-" + tenant
               if not "fixed_ips" in instance:
                  logger.warning("VM %s does not have an IP address, skipping" % name)
                  return
               logger.info("Queue Add Message: %s %s %s" % (instance['instance_id'], name.lower(), instance['fixed_ips'][0]['address']))
               self.pdns.update(name.lower(), instance['fixed_ips'][0]['address'], instance['instance_id'])
               cache = load_cache(self.config.get('CACHE', 'cache_file'))
               cache[instance['instance_id']] = (name.lower(), instance['fixed_ips'][0]['address'])
               write_cache(self.config.get('CACHE', 'cache_file'), cache)
            elif message['event_type'] == 'compute.instance.delete.end':
               instance = message['payload']
               logger.info("Queue Remove Message: %s" % (instance['instance_id']))
               cache = load_cache(self.config.get('CACHE', 'cache_file'))
               if instance['instance_id'] in cache:
                  name = cache[instance['instance_id']][0]
                  ip = cache[instance['instance_id']][1]
                  self.pdns.remove(name.lower(), ip, instance['instance_id'])
                  del cache[instance['instance_id']]
                  write_cache(self.config.get('CACHE', 'cache_file'), cache)
      except:
         logger.exception("Exception handling message")
         logger.debug(message)

