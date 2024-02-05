
from sqlalchemy import Column,Integer,Numeric,String, DateTime, Boolean, Float
from database import Base
from sqladmin import Admin, ModelView
from sqladmin import BaseView, expose
import wtforms
import asyncio, json




# class Setting(Base):
#     __tablename__ = "setting"
#     id = Column(Integer,primary_key=True)  
#     TP_percent = Column(Float, default=1)
#     SL_percent = Column(Float, default=1)
#     trade_value = Column(Integer, default=50)


# class SettingAdmin(ModelView, model=Setting):
#     #form_columns = [User.name]
#     column_list = [Setting.leverage, Setting.TP_percent,
#                     Setting.SL_percent, Setting.trade_value]
#     name = "Setting"
#     name_plural = "Setting"
#     icon = "fa-solid fa-user"
#     # form_args = dict( )
#     # form_overrides =  dict(timeframe=wtforms.SelectField, use_symbols=wtforms.SelectField,
#     #                        margin_mode=wtforms.SelectField)

#     # async def on_model_change(self, data, model, is_created):
#     #     # Perform some other action
#     #     #print(data)
#     #     pass

#     # async def on_model_delete(self, model):
#     #     # Perform some other action
#     #     pass



class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer,primary_key=True,index=True)
    symbol = Column(String)
    side = Column(String)
    trigger_price = Column(Integer)
    price = Column(Integer)
    TP_price = Column(Integer)
    value = Column(Integer)
    

class SignalAdmin(ModelView, model=Signal):
    column_list = [Signal.id, Signal.symbol, Signal.trigger_price,  Signal.price, Signal.TP_price, Signal.value,]
    column_searchable_list = [Signal.symbol, Signal.trigger_price, Signal.price, Signal.TP_price, Signal.value]
    #icon = "fa-chart-line"
    icon = "fas fa-chart-line"
    form_overrides = dict(symbol=wtforms.StringField)
    form_args = dict(symbol=dict(validators=[wtforms.validators.regexp('.+[A-Z]USDT')], label="symbol(BTCUSDT)"),
                     )
 
    column_sortable_list = [Signal.id, Signal.price, Signal.symbol, Signal.value]
    # column_formatters = {Signal.level0 : lambda m, a: round(m.level0,4),
    #                      Signal.level1 : lambda m, a: round(m.level1,4),
    #                      Signal.level2 : lambda m, a: round(m.level2,4),
    #                      Signal.level3 : lambda m, a: round(m.level3,4),
    #                      Signal.SLPrice : lambda m, a:round(m.SLPrice,4)}
    
    async def after_model_change(self, data, model, is_created, request):
        # Perform some other action
        # print(data)
        # print(is_created)
        symbol = data['symbol']
        trigger_price = data['trigger_price']
        price = data['price']
        TP_price = data['TP_price']
        value = data['value']

        # import httpx
        # client = httpx.AsyncClient()
        # url = "http://0.0.0.0:8000/placeOrder?"
        # headers = {'accept' : 'application/json'}
        # r = await client.get(f"{url}symbol={symbol}&qty={value}&stopPrice={trigger_price}&price={price}",headers=headers)

        from producer import publish
        body = {}
        body['orderType'] = "trigger"
        body['symbol'] = symbol
        body['value'] = value
        body['trigger_price'] = trigger_price
        body['price'] = float(price)        
        body['TP_price'] = float(TP_price)        
        publish(body=json.dumps(body))
        # logger.info('tiggered ... ... ...')

    # async def on_model_delete(self, model):
    #     # Perform some other action
    #     print(model)
        


class ReportView(BaseView):
    name = "Home"
    icon = "fas fa-house-user"

    @expose("/home", methods=["GET"])
    async def report_page(self, request):
        from main import binance
        return await self.templates.TemplateResponse(name="base1.html", request=request, context={"request":request, "status":binance.bot})



