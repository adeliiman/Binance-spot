import pika, time
from setLogger import get_logger


logger = get_logger(__name__)



def publish(body):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='binance')

    channel.basic_publish(exchange='', routing_key='binance', body=body)
    logger.info(" [x] Sent 'Hello World!'")

    connection.close()


