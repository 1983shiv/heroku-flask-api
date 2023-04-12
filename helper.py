import random
from nsepy import get_history
from nsepy.derivatives import get_expiry_date
from datetime import datetime
import datetime as dt
from datetime import date
import time
import pandas as pd
from nsepython import nse_optionchain_scrapper

def add_time_interval(time_str):
    interval = 120 # 1 minute
    # Convert time string to datetime object
    time_obj = datetime.strptime(time_str, '%H:%M:%S')
    # Add interval to datetime object
    new_time_obj = time_obj + dt.timedelta(seconds=interval)
    # Convert datetime object back to time string
    new_time_str = new_time_obj.strftime('%H:%M:%S')
    return new_time_str

def generate_random_time():
    start_time = dt.time(hour=9, minute=0, second=0)
    end_time = dt.time(hour=15, minute=30, second=0)
    # Generate a random time within the specified duration
    time_delta = dt.datetime.combine(dt.date.today(), end_time) - dt.datetime.combine(dt.date.today(), start_time)
    random_time = dt.datetime.combine(dt.date.today(), start_time) + dt.timedelta(seconds=random.randint(0, time_delta.seconds))
    return random_time.time()

def get_random():
    # random_num = random.random()
    random_num = random.uniform(0, 5)
    # Multiply the random float by 10 to get a value between 0 and 10
    # random_num *= 10

    # Round the random number to 2 decimal places
    random_num = round(random_num, 2)
    return random_num

def cedecay(ltp, sp, csp):
    if(csp > sp):
        return ((ltp - (csp - sp))/sp)*100
    else:
        return ((ltp + (sp - csp))/sp)*100

def pedecay(ltp, sp, csp):
    if(csp > sp):
        return ((ltp + (csp - sp))/sp)*100
    else:
        return ((ltp - (sp - csp))/sp)*100

def prmdecay(datalist, currentStrikePrice, formatted_timestamp):
    pdecay = []
    now = datetime.now()
    time_str = now.strftime('%H:%M:%S')
    for data in datalist:
        d={
            "celtp": data['CE']['lastPrice'],
            "cedecay": cedecay(data['CE']['lastPrice'], data['strikePrice'], currentStrikePrice ),
            "strikePrice": data['strikePrice'],
            "pedecay": pedecay(data['PE']['lastPrice'], data['strikePrice'], currentStrikePrice ),
            "peltp": data['PE']['lastPrice'],
            "time": formatted_timestamp
        }
        pdecay.append(d)

    return pdecay


def get_nifty_data(ssp=None):
    payload=nse_optionchain_scrapper('NIFTY')
    expiryDate=payload['records']['expiryDates'][0]
    cp = payload['records']['underlyingValue']
    timestamp = payload['records']['timestamp']
    datetime_obj = datetime.strptime(timestamp, '%d-%b-%Y %H:%M:%S')
    formatted_timestamp = datetime_obj.strftime("%H:%M:%S")
    currentStrikePrice = int(cp) - ((int(cp)))%50
    # data = payload['records']['data']
    sdata = []
    if ssp:
        sdata = [formatted_timestamp, [data for data in payload['filtered']['data'] if data['strikePrice'] == ssp]]

    print("ssp", ssp)
    # if ssp is not None:
    #    sdata = [formatted_timestamp, [data for data in payload['filtered']['data'] if data['strikePrice'] == ssp]]
    # else:
    #   sdata = []

    cdata = [formatted_timestamp, [data for data in payload['filtered']['data'] if data['strikePrice'] == currentStrikePrice]]
    filter_data = [d for d in payload['filtered']['data'] if d['strikePrice'] > (currentStrikePrice-199) and d['strikePrice'] < (currentStrikePrice+201)]
    return {
        "filter_data": filter_data,
        "cdata": cdata,
        "sdata": sdata,
        "currentStrikePrice" : currentStrikePrice, 
        "formatted_timestamp": formatted_timestamp, 
        "cp": cp, 
        "expiryDate": expiryDate
    }


def voi(filter_data):
    new_arr = []
    for dd in filter_data:
        new_data = {
            "strikePrice": dd['strikePrice'],
            "CE": {
                "impliedVolatility": dd['CE']['impliedVolatility'],
                "openInterest": dd['CE']['openInterest'],
                "totalTradedVolume": dd['CE']['totalTradedVolume'],
                "coi": dd['CE']['changeinOpenInterest'],
                "pcoi": dd['CE']['pchangeinOpenInterest'],
                "ltpch": dd['CE']['change'],
                "pltpch": dd['CE']['pChange'],
                "voi": round((dd['CE']['openInterest'] / dd['CE']['totalTradedVolume'] if dd['CE']['totalTradedVolume'] != 0 else 0)  + get_random(),3)

            },
            "PE": {
                "impliedVolatility": dd['PE']['impliedVolatility'],
                "openInterest": dd['PE']['openInterest'],
                "totalTradedVolume": dd['PE']['totalTradedVolume'],
                "coi": dd['PE']['changeinOpenInterest'],
                "pcoi": dd['PE']['pchangeinOpenInterest'],
                "ltpch": dd['PE']['change'],
                "pltpch": dd['PE']['pChange'],
                "voi": round((dd['PE']['openInterest'] / dd['PE']['totalTradedVolume'] if dd['PE']['totalTradedVolume'] != 0 else 0) + get_random(), 3)
            }
        }
        new_arr.append(new_data)
    return new_arr


def nse_optionchain_ltp(payload,strikePrice,optionType,inp=0,intent=""):
    expiryDate=payload['records']['expiryDates'][inp]
    for x in range(len(payload['records']['data'])):
      if((payload['records']['data'][x]['strikePrice']==strikePrice) & (payload['records']['data'][x]['expiryDate']==expiryDate)):
          if(intent==""): return payload['records']['data'][x][optionType]['lastPrice']
          if(intent=="sell"): return payload['records']['data'][x][optionType]['bidprice']
          if(intent=="buy"): return payload['records']['data'][x][optionType]['askPrice']



def get_oc_live(symbol, expiry_date, strike_price1):
    # Get the current time and round it to the nearest minute
    now = datetime.now()
    now = now.replace(second=0, microsecond=0)

    # Fetch the option chain for the specified symbol and expiry date
    option_chain = pd.DataFrame(get_history(symbol=symbol, start=now, end=now, index=True, expiry_date=expiry_date, option_type='CE', strike_price=strike_price1))

    # Print the option chain data
    return (option_chain)

__all__ = ['voi', 'nse_optionchain_ltp', 'get_oc_live', 'generate_random_time', 'get_nifty_data', 'prmdecay', 'add_time_interval']