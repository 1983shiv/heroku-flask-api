from flask import Flask, jsonify, request, session
from helper import get_nifty_data, voi, prmdecay
import time
import random
from datetime import datetime, timedelta
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

global prvtime

def get_random():
    # random_num = random.random()
    random_num = random.uniform(5, 50)
    # Multiply the random float by 10 to get a value between 0 and 10
    # random_num *= 10

    # Round the random number to 2 decimal places
    random_num = round(random_num, 0)
    return random_num

def add_time_interval(time_str):
    interval = 5 # 1 minute
    # Convert time string to datetime object
    time_obj = datetime.strptime(time_str, '%H:%M:%S')
    # Add interval to datetime object
    new_time_obj = time_obj + timedelta(seconds=interval)
    # Convert datetime object back to time string
    new_time_str = new_time_obj.strftime('%H:%M:%S')
    return new_time_str

def coi_data():
    return [{"sp": dd['strikePrice'], "ccoi": dd['CE']['coi'], "pcoi": dd['PE']['coi']} for dd in voi(get_nifty_data()['filter_data'])]

def oi_data():
    return [{"sp": dd['strikePrice'], "ccoi": dd['CE']['openInterest'], "pcoi": dd['PE']['openInterest']} for dd in voi(get_nifty_data()['filter_data'])]

def voi_data():
    return [{"sp": dd['strikePrice'], "ccoi": dd['CE']['voi'], "pcoi": dd['PE']['voi']} for dd in voi(get_nifty_data()['filter_data'])]


@app.route('/api/voi', methods=['GET'])
def voi_data():
    if not prvtime:
        prvtime = "02:48:00"
    time_str = request.args.get(prvtime)
    prvtime = time_str
    data = {
        "cp": get_nifty_data()['cp'],
        "csp": get_nifty_data()['currentStrikePrice'],
        "voi": voi(get_nifty_data()['filter_data']),
        "time": get_nifty_data()['formatted_timestamp'],
        "tmp": time_str
        }
    return jsonify(data)
   

@app.route('/api/ruff', methods=['GET'])
def simulate_data():
    time_str = request.args.get('time_str')
    data = {
        'timestamp': add_time_interval(time_str),
        'value': str(get_random())
    }
    return jsonify(data)
    

@app.route('/api/data', methods=['GET'])
def get_data():
    data = {
        "cp": get_nifty_data()['cp'],
        "csp": get_nifty_data()['currentStrikePrice'],
        # "v1": get_nifty_data()['filter_data'],
        "voi": voi(get_nifty_data()['filter_data']),
        "time": get_nifty_data()['formatted_timestamp'],
        "coi": coi_data(),
        "oi": oi_data(),
        "voi_data": voi_data(),
        "prmdecay": prmdecay(get_nifty_data()['filter_data'], get_nifty_data()['currentStrikePrice'], get_nifty_data()['formatted_timestamp'])
    }
    return jsonify(data)

@app.route('/api/ssp', methods=['GET'])
def get_ssp():
    ssp = request.args.get('ssp')
    if ssp:
        data = {            
            "sdata": get_nifty_data(ssp)['sdata']
        }
        return jsonify(data)
    else:
        return 'Please provide a selected strike Prices parameter'

if __name__ == '__main__':
    app.run()
