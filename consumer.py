import pika, sys, os, time, json
import threading
from setLogger import get_logger
from random import randint
from setLogger import get_logger


logger = get_logger(__name__)



def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='binance')

    def callback(ch, method, properties, body):
        try:
            print(f" [x] Received {body}")
            data = json.loads(body.decode('utf-8').replace("'",'"'))
            #
            if data['orderType'] == "trigger":
                symbol = data['symbol']
                value = data['value']
                trigger_price = data['trigger_price']
                price = data['price']
                TP_price = data['TP_price']
                qty = round(value / price, 4)
                clientID = symbol + f"_{int(TP_price*10**9)}_" + f"{randint(1000, 90000)}"
                from main import place_order
                place_order(symbol=symbol, price=price, stopPrice=trigger_price, qty=qty, clientID=clientID)
                logger.info('trigger done ... ... ...')
            elif data['orderType'] == "TP_order":
                symbol = data['symbol']
                qty = data['qty']
                clientID = data['clientID']
                price = float(clientID.splite("_")[1])/10**9
                from main import place_sell_order
                place_sell_order(symbol=symbol, qty=qty, price=price)


        except Exception as e:
            logger.exception(f"{e}")

    channel.basic_consume(queue='binance', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

threading.Thread(target=main).start()
threading.Thread(target=main).start()




