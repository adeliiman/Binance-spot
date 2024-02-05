import json, time
from database import SessionLocal
from binance.spot import Spot 


from setLogger import get_logger
logger = get_logger(__name__)


with open('config.json') as f:
    config = json.load(f)

base_url='https://testnet.binance.vision'

client = Spot(base_url=base_url, api_key=config['api_key'], api_secret=config['api_secret'])


class Binance:
	bot: str = 'Stop' # 'Run'
      

binance = Binance()

def place_order(symbol, qty, price, stopPrice, clientID, side='BUY', type_='TAKE_PROFIT_LIMIT'):
	print(clientID, '................................')
	params = {
		'symbol': symbol,
		'side': side,
		'type': type_, #STOP_LOSS_LIMIT/ TAKE_PROFIT_LIMIT
		'timeInForce': 'GTC',
		'quantity': qty,
		'price': price,
		'stopPrice': stopPrice,
		'newClientOrderId' : clientID
	}
	response = client.new_order(**params)
	logger.info(response)
	return response


def place_sell_order(symbol, qty, price):
	params = {
		'symbol': symbol,
		'side': 'SELL',
		'type': 'LIMIT', #STOP_LOSS_LIMIT/ TAKE_PROFIT_LIMIT/ STOP_LOSS
		'timeInForce': 'GTC',
		'quantity': qty,
		'price': price
		#'newClientOrderId' : 'iman'
	}
	response = client.new_order(**params)
	logger.info(response)
	return response
