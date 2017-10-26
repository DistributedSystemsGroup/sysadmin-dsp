#!/usr/bin/python
import sys
import pika
import json
import pprint

pp = pprint.PrettyPrinter(indent=4)

class novaQueue:
   def __init__(self, pw):
      self.broker = pika.URLParameters("amqp://guest:" + pw + "@localhost:5672/%2F")

      self.connection = pika.BlockingConnection(self.broker)
      self.channel = self.connection.channel()
      self.channel.queue_declare("notifications.info")
#      self.channel.exchange_declare(exchange='nova',type='topic')
#      self.channel.queue_bind(exchange='nova',queue=self.queue_name, routing_key = 'notifications.#')
#      self.channel.queue_bind(exchange='nova',queue=self.queue_name, routing_key = 'compute.#')

      self.channel.basic_consume(self.get, queue="notifications.info", no_ack=True)
      self.channel.start_consuming()

   def get(self, ch, method, properties, body):
      message = json.loads(body)
      try:
         print(message['event_type'])
      except:
         pp.pprint(message)
#      print "\n"
       # pull out the messages that we care about
      if message['event_type'] == 'compute.instance.update':
         pp.pprint(message)
         #instance = message['payload']
         #pp.pprint(instance)

q = novaQueue(sys.argv[1])

