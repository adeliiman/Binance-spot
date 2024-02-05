
import time, sys, json
import logging
# from binance.lib.utils import config_logging
from binance.spot import Spot as Client
from binance.websocket.spot.websocket_stream import SpotWebsocketStreamClient

from setLogger import get_logger


logger = get_logger(__name__)



def BinanceStream():
    base_url="https://testnet.binance.vision"
    stream_url="wss://testnet.binance.vision"

    with open('config.json') as f:
        config = json.load(f)

    api_key=config['api_key']    

    
    def message_handler(_, msg ):
        
        logger.info(msg, )
        msg = json.loads(msg)
        if 'e' in msg.keys() and msg['e'] == "executionReport":
            symbol = msg['s']
            side = msg['S']
            order_type = msg['o'] # MARKET/ LIMIT/ ...
            qty = msg['q']
            execution_type = msg['x'] # TRADE
            status = msg['X'] # FILLED
            price = msg['L']
            clientID = msg['c']

            if order_type == "MARKET" and status == "FILLED":
                print(symbol, side, order_type, qty, price)
                from producer import publish
                body = {}
                body['orderType'] = "TP_order"
                body['symbol'] = symbol
                body['qty'] = qty
                body['clientID'] = clientID
                # body['side'] = side
                # body['price'] = float(price)
                
                publish(body=json.dumps(body))
                logger.info('tiggered ... ... ...')





    # get listen key from testnet, make sure you are using testnet api key
    client = Client(api_key, base_url=base_url)
    
    response = client.new_listen_key()

    logger.info("Receving listen key : {}".format(response["listenKey"]))

    # create the websocket connection to testnet as well
    ws_client = SpotWebsocketStreamClient(
        stream_url=stream_url, on_message=message_handler
    )
 
    ws_client.user_data(listen_key=response["listenKey"])


    # from main import binance
    # if binance.bot == "Stop":
    #     ws_client.stop()

    

    


# BinanceStream()