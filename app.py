from fastapi import FastAPI , Depends
from starlette.background import BackgroundTasks
from sqlalchemy.orm import Session
import uvicorn
from models import  SignalAdmin, ReportView
from database import get_db, engine, Base
from sqladmin import Admin
from setLogger import get_logger
from fastapi.responses import RedirectResponse
from main import binance
from BinanceWebsocket import BinanceStream
from contextlib import asynccontextmanager
import httpx, threading
from typing import Union
import time


from setLogger import get_logger
logger = get_logger(__name__)



@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)
admin = Admin(app, engine)

admin.add_view(ReportView)
# admin.add_view(SettingAdmin)
admin.add_view(SignalAdmin)



@app.get('/run')
async def run(tasks: BackgroundTasks, db: Session=Depends(get_db)):
    if binance.bot == "Stop":
        binance.bot = "Run"
        threading.Thread(target=BinanceStream).start()
        
        logger.info("binance started ... ... ...")
    return  RedirectResponse(url="/admin/home")


@app.get('/stop')
def stop():
    binance.bot = "Stop"
    logger.info("binance stoped. ................")
    return  RedirectResponse(url="/admin/home")


# @app.get('/closeAll')
# def closeAll():
#     from main import api
#     res = api.closeAllPositions()
#     logger.info("Close All Positions." + str(res))
#     res = api.closeAllOrders()
#     logger.info("Close All Orders." + str(res))
#     return  RedirectResponse(url="/admin/home")


# @app.get('/placeOrder')
# async def place_order(background_tasks: BackgroundTasks, 
#                       symbol: str, 
#                       qty: float,
#                       price: float,
#                       stopPrice: float,
#                       type_:  Union[str, None] = None,
#                       side: Union[str, None] = None,
#                       ):
#     from main import place_order
#     background_tasks.add_task(place_order, symbol, qty, price, stopPrice)


# @app.get('/placeSellOrder')
# async def place_sell_order(background_tasks: BackgroundTasks, 
#                       symbol: str, 
#                       qty: float,
#                       price: float,
#                       ):
#     from main import place_sell_order
#     background_tasks.add_task(place_sell_order, symbol, qty, price)


@app.get('/')
async def index():
     return  RedirectResponse(url="/admin/home")



if __name__ == '__main__':
	uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)



