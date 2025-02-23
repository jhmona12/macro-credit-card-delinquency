import numpy as np
import pandas as pd
import yfinance as yf
from fredapi import Fred

import requests

fred = Fred(api_key='f137a7f2802f84117668a8931892dab9')

def fetch_fred_data(series_id, start_date):
    data = fred.get_series(series_id, start_date)
    return data

start_date = '2010-01-01'

delinquency_rate = fetch_fred_data('DRCCLACBS', start_date)

print(delinquency_rate)